from __future__ import annotations

from fastapi import APIRouter

from app.services.dynamodb_service import DynamoDBService
from app.services.s3_storage import S3StorageService
from app.services.sqs_service import SQSService


router = APIRouter(tags=["stats"])


@router.get("/stats")
def stats() -> dict[str, object]:
    dynamodb_service = DynamoDBService()
    s3_service = S3StorageService()
    sqs_service = SQSService()

    return {
        "s3": {
            "bucket": s3_service.bucket_name,
            "documents": len(s3_service.list_documents()),
        },
        "dynamodb": dynamodb_service.get_stats(),
        "sqs": {
            "queue": sqs_service.queue_name,
            "attributes": sqs_service.get_queue_attributes(),
        },
    }
