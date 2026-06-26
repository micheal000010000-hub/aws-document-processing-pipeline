from fastapi import APIRouter

from app.services.s3_storage import S3Storage
from fastapi.responses import StreamingResponse

router = APIRouter()

storage = S3Storage()


@router.get("/documents")
def list_documents():

    return storage.list_files()

@router.get("/download/{filename}")
def download_document(filename: str):

    file_stream = storage.download(filename)

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition":
            f"attachment; filename={filename}"
        }
    )

@router.delete("/documents/{filename}")
def delete_document(filename: str):

    return storage.delete(filename)