import json
import time

import boto3

from app.config import (
    AWS_ENDPOINT,
    AWS_REGION,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
)
from app.logger import logger

QUEUE_NAME = "document-processing-queue"

def main():
    client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

    queue_url = client.get_queue_url(QueueName=QUEUE_NAME)["QueueUrl"]

    logger.info("🚀 Worker started...")
    logger.info("Waiting for messages...\n")

    while True:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])

        if not messages:
            continue

        for message in messages:
            body = json.loads(message["Body"])

            logger.info("=" * 60)
            logger.info("📩 New Event Received")
            logger.info(json.dumps(body, indent=4))
            logger.info("=" * 60)

            logger.info("Processing document...")
            time.sleep(2)

            logger.info("Processing completed!")

            client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )

            logger.info("Message deleted.\n")


if __name__ == "__main__":
    main()