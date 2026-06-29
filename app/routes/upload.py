from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.s3_storage import S3StorageService
from app.services.sqs_service import SQSService


router = APIRouter(tags=["upload"])


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A filename is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    storage_service = S3StorageService()
    upload_result = storage_service.upload_document(
        content=content,
        filename=file.filename,
        content_type=file.content_type,
    )

    queue_service = SQSService()
    queue_service.send_upload_event(
        filename=upload_result["filename"],
        size=upload_result["size"],
        bucket=upload_result["bucket"],
        content_type=upload_result["contentType"],
        key=upload_result["key"],
    )

    return {
        "message": "Document uploaded successfully",
        "document": upload_result,
    }
