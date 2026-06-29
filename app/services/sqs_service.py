from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.config import AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_REGION, AWS_SECRET_KEY, SQS_QUEUE_NAME
from app.logger import logger


class SQSService:
    def __init__(self) -> None:
        self.queue_name = SQS_QUEUE_NAME
        self.client = boto3.client(
            "sqs",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )
        self.queue_url = self._ensure_queue_exists()

    def _ensure_queue_exists(self) -> str:
        try:
            response = self.client.get_queue_url(QueueName=self.queue_name)
            logger.info("Queue %s already exists", self.queue_name)
            return response["QueueUrl"]
        except ClientError:
            response = self.client.create_queue(QueueName=self.queue_name)
            logger.info("Created SQS queue %s", self.queue_name)
            return response["QueueUrl"]

    def send_upload_event(
        self,
        filename: str,
        size: int,
        bucket: str,
        content_type: str | None = None,
        key: str | None = None,
    ) -> dict[str, Any]:
        message = {
            "event": "DOCUMENT_UPLOADED",
            "filename": filename,
            "size": size,
            "bucket": bucket,
            "contentType": content_type,
            "key": key or filename,
        }

        self.client.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(message))
        logger.info("Queued upload event for %s", filename)
        return message

    def send_delete_event(
        self,
        filename: str,
        bucket: str | None = None,
        key: str | None = None,
    ) -> dict[str, Any]:
        message = {
            "event": "DOCUMENT_DELETED",
            "filename": filename,
            "bucket": bucket,
            "key": key or filename,
        }

        self.client.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(message))
        logger.info("Queued delete event for %s", filename)
        return message

    def receive_messages(self, max_number_of_messages: int = 10, wait_time_seconds: int = 10) -> list[dict[str, Any]]:
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
        )
        return response.get("Messages", [])

    def delete_message(self, receipt_handle: str) -> None:
        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)

    def get_queue_attributes(self) -> dict[str, str]:
        response = self.client.get_queue_attributes(
            QueueUrl=self.queue_url,
            AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
        )
        return response.get("Attributes", {})
