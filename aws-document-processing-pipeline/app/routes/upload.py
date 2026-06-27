from fastapi import APIRouter, File, UploadFile
from app.services.sqs_services import SQSService
from app.services.s3_storage import S3Storage
from app.logger import logger
router = APIRouter()

storage = S3Storage()
queue = SQSService()



@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Received upload request for: {file.filename}")

    storage.save(file)

    queue.send_upload_event(file.filename, file.size)

    logger.info(f"Finished saving: {file.filename}")

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
    }