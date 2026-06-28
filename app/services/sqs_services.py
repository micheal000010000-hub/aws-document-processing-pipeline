import json
import logging
import boto3
from botocore.exceptions import ClientError

from app.config import (
    AWS_ENDPOINT,
    AWS_REGION,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
)


class SQSService:

    def __init__(self):

        self.queue_name = "document-processing-queue"

        self.client = boto3.client(
            "sqs",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )

        self.queue_url = self._ensure_queue_exists()

    def _ensure_queue_exists(self):

        try:
            response = self.client.get_queue_url(
                QueueName=self.queue_name
            )

            logging.info(f"Queue '{self.queue_name}' already exists.")

            return response["QueueUrl"]

        except ClientError:

            logging.info(f"Creating queue '{self.queue_name}'...")

            response = self.client.create_queue(
                QueueName=self.queue_name
            )

            return response["QueueUrl"]

    def send_upload_event(self, filename, size):

        message = {
            "event": "DOCUMENT_UPLOADED",
            "filename": filename,
            "size": size,
        }

        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
        )

        logging.info(f"Queued event for {filename}")

        return message