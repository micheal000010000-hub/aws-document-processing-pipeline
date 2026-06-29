from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.config import AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_REGION, AWS_SECRET_KEY, S3_BUCKET
from app.logger import logger


class S3StorageService:
    def __init__(self) -> None:
        self.bucket_name = S3_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )
        self._ensure_bucket_exists()

    @staticmethod
    def _safe_filename(filename: str) -> str:
        safe_filename = PurePosixPath(filename).name
        if not safe_filename:
            raise ValueError("Filename is required")
        return safe_filename

    def _ensure_bucket_exists(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code not in {"404", "NoSuchBucket", "NotFound", "400"}:
                raise

        create_kwargs: dict[str, Any] = {"Bucket": self.bucket_name}
        if AWS_REGION != "us-east-1":
            create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": AWS_REGION}

        self.client.create_bucket(**create_kwargs)
        logger.info("Created S3 bucket %s", self.bucket_name)

    def upload_document(self, content: bytes, filename: str, content_type: str | None = None) -> dict[str, Any]:
        object_key = self._safe_filename(filename)
        extra_args: dict[str, str] = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=content,
            **extra_args,
        )

        logger.info("Uploaded %s to bucket %s", object_key, self.bucket_name)
        return {
            "bucket": self.bucket_name,
            "key": object_key,
            "filename": object_key,
            "size": len(content),
            "contentType": content_type or "application/octet-stream",
        }

    def get_document(self, filename: str) -> dict[str, Any]:
        object_key = self._safe_filename(filename)
        return self.client.get_object(Bucket=self.bucket_name, Key=object_key)

    def delete_document(self, filename: str) -> None:
        object_key = self._safe_filename(filename)
        self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
        logger.info("Deleted %s from bucket %s", object_key, self.bucket_name)

    def list_documents(self) -> list[dict[str, Any]]:
        response = self.client.list_objects_v2(Bucket=self.bucket_name)
        documents: list[dict[str, Any]] = []
        for item in response.get("Contents", []):
            documents.append(
                {
                    "filename": item["Key"],
                    "size": int(item.get("Size", 0)),
                    "lastModified": item.get("LastModified").isoformat() if item.get("LastModified") else None,
                    "etag": item.get("ETag", "").strip('"'),
                }
            )
        return documents
