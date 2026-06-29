from __future__ import annotations

import json
import time

from botocore.exceptions import BotoCoreError, ClientError

from app.logger import configure_logging, logger
from app.services.dynamodb_service import DynamoDBService
from app.services.sqs_service import SQSService


class QueueWorker:
    def __init__(self) -> None:
        self.queue_service = SQSService()
        self.database_service = DynamoDBService()


    def process_message(self, message: dict[str, object]) -> None:
        body = json.loads(message["Body"])
        filename = body.get("filename")
        size = body.get("size")
        bucket = body.get("bucket")
        content_type = body.get("contentType")
        event_name = body.get("event", "DOCUMENT_UPLOADED")

        if not filename:
            raise ValueError("Message is missing filename")

        if event_name == "DOCUMENT_DELETED":
            deleted_count = self.database_service.delete_documents_by_filename(str(filename))
            logger.info("Deleted %s metadata records for %s", deleted_count, filename)
        else:
            metadata = self.database_service.save_metadata(
                filename=str(filename),
                size=int(size or 0),
                bucket=str(bucket) if bucket else None,
                content_type=str(content_type) if content_type else None,
            )
            logger.info("Saved metadata for %s: %s", filename, metadata)

        self.queue_service.delete_message(message["ReceiptHandle"])
        logger.info("Deleted processed SQS message for %s", filename)

    def run(self, poll_interval_seconds: int = 1) -> None:
        logger.info("Queue worker started")

        while True:
            try:
                messages = self.queue_service.receive_messages(max_number_of_messages=10, wait_time_seconds=10)
            except (ClientError, BotoCoreError):
                logger.exception("Failed to poll SQS")
                time.sleep(poll_interval_seconds)
                continue

            if not messages:
                continue

            for message in messages:
                try:
                    self.process_message(message)
                except (ClientError, BotoCoreError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                    logger.exception("Failed to process SQS message")


def main() -> None:
    configure_logging()
    QueueWorker().run()


if __name__ == "__main__":
    main()
