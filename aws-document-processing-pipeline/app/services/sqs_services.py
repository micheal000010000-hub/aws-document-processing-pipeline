import json
import boto3

from app.config import (
    AWS_ENDPOINT,
    AWS_REGION,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
)


class SQSService:

    def __init__(self):

        self.queue_url = (
            "http://localhost:4566/000000000000/document-processing-queue"
        )

        self.client = boto3.client(
            "sqs",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )

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

        return message