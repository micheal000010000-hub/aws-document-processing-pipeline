from fastapi import APIRouter, File, UploadFile

from app.services.s3_storage import S3Storage

router = APIRouter()

storage = S3Storage()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    print(f"Received upload request for: {file.filename}", flush=True)

    storage.save(file)

    print(f"Finished saving: {file.filename}", flush=True)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
    }