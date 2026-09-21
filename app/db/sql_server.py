"""SQL Server connectivity and persistence using pyodbc."""
from __future__ import annotations

import json
import logging
from contextlib import closing

import pyodbc

from app.core.config import settings

logger = logging.getLogger(__name__)

# pyodbc pooling is enabled by default. Keep it explicit for clarity.
pyodbc.pooling = True


def _connection_string(database: str) -> str:
    return (
        f"DRIVER={{{settings.db_driver}}};"
        f"SERVER={settings.db_host},{settings.db_port};"
        f"DATABASE={database};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
        f"Encrypt={settings.db_encrypt};"
        f"TrustServerCertificate={settings.db_trust_server_certificate};"
        "Connection Timeout=5;"
    )


def get_connection(database: str | None = None) -> pyodbc.Connection:
    return pyodbc.connect(_connection_string(database or settings.db_name))


def initialize_database() -> None:
    """Create the application database and table if they do not exist."""
    safe_db_name = settings.db_name.replace("]", "]]" )

    with closing(get_connection("master")) as connection:
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(
            f"IF DB_ID(?) IS NULL EXEC('CREATE DATABASE [{safe_db_name}]')",
            settings.db_name,
        )

    create_table_sql = """
    IF OBJECT_ID('dbo.AdmissionAssessments', 'U') IS NULL
    BEGIN
        CREATE TABLE dbo.AdmissionAssessments (
            Id BIGINT IDENTITY(1,1) PRIMARY KEY,
            RequestId UNIQUEIDENTIFIER NOT NULL UNIQUE,
            StudentName NVARCHAR(100) NOT NULL,
            DesiredCourse NVARCHAR(150) NOT NULL,
            Eligible BIT NOT NULL,
            InputJson NVARCHAR(MAX) NOT NULL,
            OutputJson NVARCHAR(MAX) NOT NULL,
            CreatedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
        );
        CREATE INDEX IX_AdmissionAssessments_StudentName
            ON dbo.AdmissionAssessments(StudentName);
        CREATE INDEX IX_AdmissionAssessments_CreatedAtUtc
            ON dbo.AdmissionAssessments(CreatedAtUtc DESC);
    END;
    """

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()

    logger.info("SQL Server database initialization completed.")


def save_admission_record(request_id: str, input_data: dict, output_data: dict) -> None:
    """Persist one request/response pair using a parameterized INSERT."""
    sql = """
    INSERT INTO dbo.AdmissionAssessments
        (RequestId, StudentName, DesiredCourse, Eligible, InputJson, OutputJson)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            sql,
            request_id,
            input_data["name"],
            input_data["desired_course"],
            bool(output_data["eligible"]),
            json.dumps(input_data, ensure_ascii=False),
            json.dumps(output_data, ensure_ascii=False, default=str),
        )
        connection.commit()
