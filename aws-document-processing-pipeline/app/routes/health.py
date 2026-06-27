from fastapi import APIRouter
from app.services.s3_storage import S3Storage

router = APIRouter(tags=["Health"])

storage = S3Storage()


@router.get("/health")
def health():

    try:
        storage.client.list_buckets()

        return {
            "status": "healthy",
            "services": {
                "s3": "connected"
            }
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "services": {
                "s3": "disconnected"
            },
            "error": str(e)
        }