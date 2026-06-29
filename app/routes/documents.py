from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError

from app.logger import logger
from app.services.dynamodb_service import DynamoDBService
from app.services.s3_storage import S3StorageService
from app.services.sqs_service import SQSService


router = APIRouter(tags=["documents"])


@router.get("/documents")
def list_documents() -> dict[str, object]:
    service = DynamoDBService()
    documents = service.list_documents()
    return {"count": len(documents), "documents": documents}


@router.get("/download/{filename}")
def download_document(filename: str) -> StreamingResponse:
    storage_service = S3StorageService()

    try:
        response = storage_service.get_document(filename)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"NoSuchKey", "404", "NotFound"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from exc
        raise

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    if response.get("ContentLength") is not None:
        headers["Content-Length"] = str(response["ContentLength"])

    logger.info("Streaming download for %s", filename)
    return StreamingResponse(
        response["Body"],
        media_type=response.get("ContentType", "application/octet-stream"),
        headers=headers,
    )


@router.delete("/documents/{filename}")
def delete_document(filename: str) -> dict[str, object]:
    storage_service = S3StorageService()
    database_service = DynamoDBService()
    queue_service = SQSService()

    try:
        storage_service.delete_document(filename)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"NoSuchKey", "404", "NotFound"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from exc
        raise

    deleted_count = database_service.delete_documents_by_filename(filename)
    queue_service.send_delete_event(filename=filename)

    return {
        "message": "Document deleted successfully",
        "filename": filename,
        "metadataDeleted": deleted_count,
    }
