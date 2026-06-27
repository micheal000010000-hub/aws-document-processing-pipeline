from fastapi import APIRouter
from app.services.s3_storage import S3Storage

router = APIRouter(tags=["Statistics"])

storage = S3Storage()


@router.get("/stats")
def stats():

    files = storage.list_files()

    total_size = sum(file["size"] for file in files)

    return {
        "documents": len(files),
        "total_size": total_size
    }