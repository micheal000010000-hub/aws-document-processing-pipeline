import boto3
from botocore.exceptions import ClientError


class S3Storage:
    def __init__(self):
        self.bucket_name = "document-bucket"

        self.client = boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """
        Create the bucket if it doesn't already exist.
        """

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket '{self.bucket_name}' already exists.")

        except ClientError:
            print(f"Creating bucket '{self.bucket_name}'...")
            self.client.create_bucket(Bucket=self.bucket_name)

    def save(self, file):
        print(f"Uploading to S3: {file.filename}", flush=True)

        self.client.upload_fileobj(
            Fileobj=file.file,
            Bucket=self.bucket_name,
            Key=file.filename,
        )

        return {
            "bucket": self.bucket_name,
            "filename": file.filename,
        }