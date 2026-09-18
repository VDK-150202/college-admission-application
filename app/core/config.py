"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "College Admission Eligibility API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/admissions.log")

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "1433")
    db_name: str = os.getenv("DB_NAME", "CollegeAdmissions")
    db_user: str = os.getenv("DB_USER", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "YourStrong!Passw0rd")
    db_driver: str = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    db_encrypt: str = os.getenv("DB_ENCRYPT", "yes")
    db_trust_server_certificate: str = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")


settings = Settings()
