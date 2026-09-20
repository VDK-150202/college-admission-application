"""FastAPI routes."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.course_catalog import COURSE_CATALOG
from app.db.sql_server import save_assessment
from app.models.schemas import AdmissionRequest, AdmissionResponse
from app.services.eligibility import (
    calculate_overall_percentage,
    evaluate_course,
    recommend_courses,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/courses", tags=["Admissions"])
async def list_courses() -> dict[str, list[str]]:
    return {"courses": sorted(COURSE_CATALOG.keys())}


@router.post(
    "/eligibility",
    response_model=AdmissionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Admissions"],
)
async def check_eligibility(student: AdmissionRequest) -> AdmissionResponse:
    """Validate input, evaluate eligibility, recommend alternatives and persist results."""
    request_id = str(uuid4())
    assessed_at = datetime.now(timezone.utc)

    evaluation = evaluate_course(student, student.desired_course)
    overall_percentage = calculate_overall_percentage(student)
    recommendations = [] if evaluation.eligible else recommend_courses(student)

    response = AdmissionResponse(
        request_id=request_id,
        student_name=student.name,
        desired_course=student.desired_course,
        eligible=evaluation.eligible,
        overall_percentage=overall_percentage,
        required_subject_percentage=evaluation.required_subject_percentage,
        reasons=evaluation.reasons,
        recommended_courses=recommendations,
        assessed_at_utc=assessed_at,
        persisted_to_database=False,
    )

    input_dict = student.model_dump(mode="json")
    output_dict = response.model_dump(mode="json")

    logger.info(
        "Admission request | request_id=%s | input=%s",
        request_id,
        json.dumps(input_dict, ensure_ascii=False),
    )

    try:
        # pyodbc is synchronous, so run DB I/O in FastAPI's thread pool.
        # This prevents a database call from blocking the event loop and allows
        # multiple API requests to be served concurrently.
        await run_in_threadpool(save_assessment, request_id, input_dict, output_dict)
        response.persisted_to_database = True
    except Exception as exc:
        logger.exception("Database persistence failed | request_id=%s", request_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Eligibility was calculated, but the result could not be stored in the database.",
        ) from exc

    logger.info(
        "Admission response | request_id=%s | output=%s",
        request_id,
        response.model_dump_json(),
    )
    return response
