from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.routes.documents import router as documents_router

app = FastAPI(title="Document Processing API")

app.include_router(upload_router)
app.include_router(documents_router)

@app.get("/")
def root():
    return {
        "message": "Document Processing API is running"
    }