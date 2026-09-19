"""Pydantic request and response schemas."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.course_catalog import ALLOWED_COURSES, ALLOWED_EXAMS, ALLOWED_GENDERS

NAME_PATTERN = re.compile(r"^[A-Za-z ]+$")
SUBJECT_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .&()/-]*$")


class SubjectMark(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    subject: str = Field(..., min_length=2, max_length=100)
    marks: float = Field(..., ge=0, le=100)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        if not SUBJECT_PATTERN.fullmatch(value):
            raise ValueError("Subject name contains invalid characters.")
        return value


class QualificationExamResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qualified: bool
    score: float | None = Field(default=None, ge=0, le=100)


class AdmissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=17, le=25)
    gender: str
    subjects: Annotated[list[SubjectMark], Field(min_length=6, max_length=6)]
    qualification_exams: dict[str, QualificationExamResult] = Field(default_factory=dict)
    desired_course: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("Name must contain only letters and spaces.")
        return re.sub(r"\s+", " ", value).strip()

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        if value not in ALLOWED_GENDERS:
            raise ValueError(f"Gender must be one of: {sorted(ALLOWED_GENDERS)}")
        return value

    @field_validator("desired_course")
    @classmethod
    def validate_course(cls, value: str) -> str:
        if value not in ALLOWED_COURSES:
            raise ValueError("Desired course is not supported.")
        return value

    @field_validator("qualification_exams")
    @classmethod
    def validate_exam_names(
        cls, value: dict[str, QualificationExamResult]
    ) -> dict[str, QualificationExamResult]:
        invalid = set(value) - ALLOWED_EXAMS
        if invalid:
            raise ValueError(f"Unsupported qualification exam(s): {sorted(invalid)}")
        return value

    @model_validator(mode="after")
    def validate_unique_subjects(self) -> "AdmissionRequest":
        normalized = [item.subject.casefold() for item in self.subjects]
        if len(normalized) != len(set(normalized)):
            raise ValueError("All six 12th-grade subjects must be unique.")
        return self


class AdmissionResponse(BaseModel):
    request_id: str
    student_name: str
    desired_course: str
    eligible: bool
    overall_percentage: float
    required_subject_percentage: float | None
    reasons: list[str]
    recommended_courses: list[str]
    assessed_at_utc: datetime
    persisted_to_database: bool
