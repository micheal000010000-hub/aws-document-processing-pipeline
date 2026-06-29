from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError

from app.config import AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_REGION, AWS_SECRET_KEY, DYNAMODB_TABLE_NAME
from app.logger import logger


class DynamoDBService:
    def __init__(self) -> None:
        self.table_name = DYNAMODB_TABLE_NAME
        self.client = boto3.client(
            "dynamodb",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )
        self._serializer = TypeSerializer()
        self._deserializer = TypeDeserializer()
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        try:
            self.client.describe_table(TableName=self.table_name)
            logger.info("Table %s already exists", self.table_name)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code != "ResourceNotFoundException":
                raise

            logger.info("Creating table %s", self.table_name)
            self.client.create_table(
                TableName=self.table_name,
                AttributeDefinitions=[
                    {
                        "AttributeName": "documentId",
                        "AttributeType": "S",
                    }
                ],
                KeySchema=[
                    {
                        "AttributeName": "documentId",
                        "KeyType": "HASH",
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )

            waiter = self.client.get_waiter("table_exists")
            waiter.wait(TableName=self.table_name)

    def _serialize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return {key: self._serializer.serialize(value) for key, value in item.items() if value is not None}

    def _deserialize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return {key: self._deserializer.deserialize(value) for key, value in item.items()}

    def _scan_all(self, **kwargs: Any) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        exclusive_start_key = None

        while True:
            scan_kwargs = dict(kwargs)
            if exclusive_start_key:
                scan_kwargs["ExclusiveStartKey"] = exclusive_start_key

            response = self.client.scan(TableName=self.table_name, **scan_kwargs)
            items.extend(response.get("Items", []))
            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                break

        return items

    def save_metadata(
        self,
        filename: str,
        size: int,
        bucket: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        document_id = str(uuid.uuid4())
        uploaded_at = datetime.now(timezone.utc).isoformat()

        item = self._serialize_item(
            {
                "documentId": document_id,
                "filename": filename,
                "size": Decimal(str(size)),
                "uploadedAt": uploaded_at,
                "bucket": bucket,
                "contentType": content_type,
            }
        )
        self.client.put_item(TableName=self.table_name, Item=item)

        logger.info("Stored metadata for %s", filename)
        return {
            "documentId": document_id,
            "filename": filename,
            "size": size,
            "uploadedAt": uploaded_at,
            "bucket": bucket,
            "contentType": content_type,
        }

    def list_documents(self) -> list[dict[str, Any]]:
        documents = [self._deserialize_item(item) for item in self._scan_all()]
        documents.sort(key=lambda item: item.get("uploadedAt", ""), reverse=True)
        return documents

    def delete_documents_by_filename(self, filename: str) -> int:
        documents = [
            self._deserialize_item(item)
            for item in self._scan_all(FilterExpression=Attr("filename").eq(filename))
        ]

        for document in documents:
            self.client.delete_item(
                TableName=self.table_name,
                Key={"documentId": self._serializer.serialize(document["documentId"])},
            )

        return len(documents)

    def get_stats(self) -> dict[str, Any]:
        documents = self.list_documents()
        total_documents = len(documents)
        total_size_bytes = sum(int(document.get("size", 0)) for document in documents)
        average_size_bytes = round(total_size_bytes / total_documents, 2) if total_documents else 0
        latest_uploaded_at = max((document.get("uploadedAt") for document in documents if document.get("uploadedAt")), default=None)

        return {
            "table": self.table_name,
            "totalDocuments": total_documents,
            "totalSizeBytes": total_size_bytes,
            "averageSizeBytes": average_size_bytes,
            "latestUploadedAt": latest_uploaded_at,
        }
