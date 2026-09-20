"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from app.api.routes import router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.sql_server import initialize_database

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database objects when the API starts."""
    try:
        await run_in_threadpool(initialize_database)
    except Exception:
        logger.exception(
            "Database initialization failed. Verify SQL Server, credentials and ODBC Driver 18."
        )
        raise
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Checks college-admission eligibility from 12th-grade subjects, marks, "
        "qualification exams and the requested course."
    ),
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
