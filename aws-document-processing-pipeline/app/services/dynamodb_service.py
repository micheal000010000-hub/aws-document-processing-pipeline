import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from app.logger import logger
from app.config import AWS_SECRET_KEY, AWS_ACCESS_KEY, AWS_REGION, AWS_ENDPOINT


class DynamoDBService:

    def __init__(self):

        self.client = boto3.client(
            "dynamodb",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )

        logger.info("=" * 60)
        logger.info("DynamoDB Endpoint:", self.client.meta.endpoint_url)
        logger.info("=" * 60)

        tables = self.client.list_tables()
        logger.info("Tables seen by boto3:")
        logger.info(tables)

    def _ensure_table_exists(self):

        try:
            self.client.describe_table(TableName=self.table_name)
            logger.info(f"Table '{self.table_name}' already exists.")

        except ClientError:

            logger.info(f"Creating table '{self.table_name}'...")

            self.client.create_table(
                TableName=self.table_name,
                AttributeDefinitions=[
                    {
                        "AttributeName": "documentId",
                        "AttributeType": "S"
                    }
                ],
                KeySchema=[
                    {
                        "AttributeName": "documentId",
                        "KeyType": "HASH"
                    }
                ],
                BillingMode="PAY_PER_REQUEST"
            )

            logger.info("Waiting for table to become active...")

            waiter = self.client.get_waiter("table_exists")
            waiter.wait(TableName=self.table_name)

    def save_metadata(self, filename, size):

        document_id = str(uuid.uuid4())

        uploaded_at = datetime.utcnow().isoformat()

        self.client.put_item(
            TableName=self.table_name,
            Item={
                "documentId": {
                    "S": document_id
                },
                "filename": {
                    "S": filename
                },
                "size": {
                    "N": str(size)
                },
                "uploadedAt": {
                    "S": uploaded_at
                }
            }
        )

        return {
            "documentId": document_id,
            "filename": filename,
            "size": size,
            "uploadedAt": uploaded_at
        }