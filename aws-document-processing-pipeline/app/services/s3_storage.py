import boto3
from botocore.exceptions import ClientError
import io

from fastapi import HTTPException
from app.logger import logger
from app.config import AWS_ENDPOINT, AWS_REGION, AWS_SECRET_KEY, S3_BUCKET, AWS_ACCESS_KEY

class S3Storage:
    def __init__(self):
        self.bucket_name = S3_BUCKET

        self.client = boto3.client(
            "s3",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """
        Create the bucket if it doesn't already exist.
        """

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' already exists.")

        except ClientError:
            logger.info(f"Creating bucket '{self.bucket_name}'...")
            self.client.create_bucket(Bucket=self.bucket_name)

    def save(self, file):
        logger.info(f"Uploading to S3: {file.filename}")

        self.client.upload_fileobj(
            Fileobj=file.file,
            Bucket=self.bucket_name,
            Key=file.filename,
        )

        return {
            "bucket": self.bucket_name,
            "filename": file.filename,
        }
    
    def list_files(self):

        response = self.client.list_objects_v2(
            Bucket=self.bucket_name
        )

        files = []

        for obj in response.get("Contents", []):

            files.append(
                {
                    "filename": obj["Key"],
                    "size": obj["Size"]
                }
            )

        return files
    
    def download(self, filename):

        stream = io.BytesIO()

        try:

            self.client.download_fileobj(
                Bucket=self.bucket_name,
                Key=filename,
                Fileobj=stream
            )

            stream.seek(0)

            return stream

        except ClientError:

            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
    def delete(self, filename):

        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=filename
        )

        return {
            "message": f"{filename} deleted successfully"
        }