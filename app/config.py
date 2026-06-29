from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    aws_endpoint: str = os.getenv("AWS_ENDPOINT", "http://localhost:4566")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key: str = os.getenv("AWS_ACCESS_KEY", "test")
    aws_secret_key: str = os.getenv("AWS_SECRET_KEY", "test")
    s3_bucket: str = os.getenv("S3_BUCKET", "document-bucket")
    sqs_queue_name: str = os.getenv("SQS_QUEUE_NAME", "document-processing-queue")
    dynamodb_table_name: str = os.getenv("DYNAMODB_TABLE_NAME", "Documents")
    app_name: str = os.getenv("APP_NAME", "AWS Document Processing Pipeline")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

AWS_ENDPOINT = settings.aws_endpoint
AWS_REGION = settings.aws_region
AWS_ACCESS_KEY = settings.aws_access_key
AWS_SECRET_KEY = settings.aws_secret_key
S3_BUCKET = settings.s3_bucket
SQS_QUEUE_NAME = settings.sqs_queue_name
DYNAMODB_TABLE_NAME = settings.dynamodb_table_name
APP_NAME = settings.app_name
APP_VERSION = settings.app_version
LOG_LEVEL = settings.log_level
