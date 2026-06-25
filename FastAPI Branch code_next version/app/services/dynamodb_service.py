import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError


class DynamoDBService:

    def __init__(self):

        self.client = boto3.client(
            "dynamodb",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

        print("=" * 60)
        print("DynamoDB Endpoint:", self.client.meta.endpoint_url)
        print("=" * 60)

        tables = self.client.list_tables()
        print("Tables seen by boto3:")
        print(tables)

    def _ensure_table_exists(self):

        try:
            self.client.describe_table(TableName=self.table_name)
            print(f"Table '{self.table_name}' already exists.")

        except ClientError:

            print(f"Creating table '{self.table_name}'...")

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

            print("Waiting for table to become active...")

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