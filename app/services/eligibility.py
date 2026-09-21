"""Eligibility evaluation and recommendation engine."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.core.course_catalog import COURSE_CATALOG
from app.models.schemas import AdmissionRequest


@dataclass(frozen=True)
class CourseEvaluation:
    eligible: bool
    required_subject_percentage: float | None
    reasons: list[str]


def _subject_frame(student: AdmissionRequest) -> pd.DataFrame:
    """Convert six subject records into a normalized pandas DataFrame."""
    frame = pd.DataFrame([subject.model_dump() for subject in student.subjects])
    frame["normalized_subject"] = frame["subject"].str.strip().str.casefold()
    frame["marks"] = pd.to_numeric(frame["marks"], errors="raise")
    return frame


def calculate_overall_percentage(student: AdmissionRequest) -> float:
    """Calculate 12th-grade average using NumPy."""
    marks = np.array([subject.marks for subject in student.subjects], dtype=float)
    return round(float(np.mean(marks)), 2)


def evaluate_course(student: AdmissionRequest, course_name: str) -> CourseEvaluation:
    """
        Evaluate a student against one course's predefined criteria.
        The evaluation checks the course-specific 12th-grade subject combination,
        calculates the average across only those required subjects, applies the
        configured cutoff when one exists, and verifies any required qualification
        exam such as JEE or NEET.

        Args:
            student: Validated admission request containing the student's subjects,
                marks, qualification exam results, and desired course information.
            course_name: Exact course name present in ``COURSE_CATALOG``.

        Returns:
            A ``CourseEvaluation`` containing whether the student is eligible,
            store computed required-subject average (or None if not applicable), and a list of
            human-readable reasons explaining the result.
        
    """
    criteria = COURSE_CATALOG[course_name]
    frame = _subject_frame(student)

    available = set(frame["normalized_subject"].tolist())
    required_subjects = criteria["required_subjects"]
    required_normalized = [subject.casefold() for subject in required_subjects]
    missing = [
        subject
        for subject, normalized in zip(required_subjects, required_normalized)
        if normalized not in available
    ]

    reasons: list[str] = []
    if missing:
        reasons.append("Missing required subject(s): " + ", ".join(missing) + ".")

    required_percentage: float | None = None
    if not missing:
        required_marks = frame.loc[
            frame["normalized_subject"].isin(required_normalized), "marks"
        ].to_numpy(dtype=float)
        required_percentage = round(float(np.mean(required_marks)), 2)

        cutoff = criteria["cutoff"]
        if cutoff is not None and required_percentage < cutoff:
            reasons.append(
                f"Required-subject average is {required_percentage:.2f}%, "
                f"below the {cutoff:.2f}% cutoff."
            )

    required_exam = criteria["required_exam"]
    if required_exam:
        exam_result = student.qualification_exams.get(required_exam)
        if exam_result is None:
            reasons.append(f"{required_exam} result was not provided.")
        elif not exam_result.qualified:
            reasons.append(f"{required_exam} has not been qualified.")

    eligible = not reasons
    if eligible:
        reasons.append(f"All eligibility criteria for {course_name} are satisfied.")

    return CourseEvaluation(
        eligible=eligible,
        required_subject_percentage=required_percentage,
        reasons=reasons,
    )


def recommend_courses(student: AdmissionRequest, limit: int = 5) -> list[str]:
    """
    Recommend other courses for which the student currently satisfies all criteria.

    Preference order:
    1. Same category as desired course.
    2. Other eligible categories.
    3. Higher subject-average courses first where comparable.
    """
    desired_category = COURSE_CATALOG[student.desired_course]["category"]
    candidates: list[tuple[int, float, str]] = []

    for course_name, criteria in COURSE_CATALOG.items():
        if course_name == student.desired_course:
            continue
        evaluation = evaluate_course(student, course_name)
        if not evaluation.eligible:
            continue

        category_priority = 0 if criteria["category"] == desired_category else 1
        subject_score = evaluation.required_subject_percentage or 0.0
        candidates.append((category_priority, -subject_score, course_name))

    candidates.sort()
    return [course_name for _, _, course_name in candidates[:limit]]
