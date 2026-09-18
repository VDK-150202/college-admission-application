"""Predefined course eligibility criteria."""
from __future__ import annotations

from typing import Final

COURSE_CATALOG: Final[dict[str, dict]] = {
    "Computer Science Engineering": {
        "category": "Engineering",
        "required_subjects": ["Physics", "Chemistry", "Mathematics"],
        "cutoff": 75.0,
        "required_exam": "JEE",
    },
    "Mechanical Engineering": {
        "category": "Engineering",
        "required_subjects": ["Physics", "Chemistry", "Mathematics"],
        "cutoff": 70.0,
        "required_exam": "JEE",
    },
    "Electrical Engineering": {
        "category": "Engineering",
        "required_subjects": ["Physics", "Chemistry", "Mathematics"],
        "cutoff": 70.0,
        "required_exam": "JEE",
    },
    "Civil Engineering": {
        "category": "Engineering",
        "required_subjects": ["Physics", "Chemistry", "Mathematics"],
        "cutoff": 65.0,
        "required_exam": "JEE",
    },
    "Electronics and Communication Engineering": {
        "category": "Engineering",
        "required_subjects": ["Physics", "Chemistry", "Mathematics"],
        "cutoff": 70.0,
        "required_exam": "JEE",
    },
    "MBBS": {
        "category": "Medicine",
        "required_subjects": ["Physics", "Chemistry", "Biology"],
        "cutoff": 85.0,
        "required_exam": "NEET",
    },
    "BDS (Dentistry)": {
        "category": "Medicine",
        "required_subjects": ["Physics", "Chemistry", "Biology"],
        "cutoff": 80.0,
        "required_exam": "NEET",
    },
    "BAMS (Ayurveda)": {
        "category": "Medicine",
        "required_subjects": ["Physics", "Chemistry", "Biology"],
        "cutoff": 75.0,
        "required_exam": "NEET",
    },
    "BHMS (Homeopathy)": {
        "category": "Medicine",
        "required_subjects": ["Physics", "Chemistry", "Biology"],
        "cutoff": 75.0,
        "required_exam": "NEET",
    },
    "BPT (Physiotherapy)": {
        "category": "Medicine",
        "required_subjects": ["Physics", "Chemistry", "Biology"],
        "cutoff": 70.0,
        "required_exam": "NEET",
    },
    "B.Com (Bachelor of Commerce)": {
        "category": "Commerce",
        "required_subjects": ["Accountancy", "Business Studies", "Economics"],
        "cutoff": None,
        "required_exam": None,
    },
    "BBA (Bachelor of Business Administration)": {
        "category": "Commerce",
        "required_subjects": ["Accountancy", "Business Studies", "Economics"],
        "cutoff": None,
        "required_exam": None,
    },
    "BBM (Bachelor of Business Management)": {
        "category": "Commerce",
        "required_subjects": ["Accountancy", "Business Studies", "Economics"],
        "cutoff": None,
        "required_exam": None,
    },
    "CA (Chartered Accountancy)": {
        "category": "Commerce",
        "required_subjects": ["Accountancy", "Business Studies", "Economics"],
        "cutoff": None,
        "required_exam": None,
    },
    "BA in History": {
        "category": "Humanities",
        "required_subjects": ["History", "Political Science", "Geography"],
        "cutoff": None,
        "required_exam": None,
    },
    "BA in Psychology": {
        "category": "Humanities",
        "required_subjects": ["Psychology", "Sociology", "English"],
        "cutoff": None,
        "required_exam": None,
    },
    "BA in Sociology": {
        "category": "Humanities",
        "required_subjects": ["Sociology", "Political Science", "History"],
        "cutoff": None,
        "required_exam": None,
    },
    "BA in Political Science": {
        "category": "Humanities",
        "required_subjects": ["Political Science", "History", "Geography"],
        "cutoff": None,
        "required_exam": None,
    },
    "BA in English": {
        "category": "Humanities",
        "required_subjects": ["English", "History", "Political Science"],
        "cutoff": None,
        "required_exam": None,
    },
}

ALLOWED_COURSES: Final[set[str]] = set(COURSE_CATALOG)
ALLOWED_GENDERS: Final[set[str]] = {"Male", "Female", "Other"}
ALLOWED_EXAMS: Final[set[str]] = {"JEE", "NEET"}
