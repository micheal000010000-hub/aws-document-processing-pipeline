import json
import logging
import time

import boto3

from app.config import (
    AWS_ENDPOINT,
    AWS_REGION,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
)

from app.services.dynamodb_service import DynamoDBService

QUEUE_URL = "http://localhost:4566/000000000000/document-processing-queue"

client = boto3.client(
    "sqs",
    endpoint_url=AWS_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

database = DynamoDBService()

logging.info("Queue Worker Started...")


while True:

    response = client.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5,
    )

    messages = response.get("Messages", [])

    if not messages:
        continue

    for message in messages:

        body = json.loads(message["Body"])

        logging.info("=" * 60)
        logging.info("Received Event:")
        logging.info(body)

        metadata = database.save_metadata(
            filename=body["filename"],
            size=body["size"]
        )

        logging.info("\nSaved Metadata:")
        logging.info(metadata)

        client.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=message["ReceiptHandle"],
        )

        logging.info("\nMessage Deleted")
        logging.info("=" * 60)

    time.sleep(1)