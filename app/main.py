from fastapi import FastAPI

from app.logger import configure_logging, logger
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.stats import router as stats_router
from app.routes.upload import router as upload_router

configure_logging()

app = FastAPI(
    title="AWS Document Processing Pipeline",
    version="1.0.0",
    description="FastAPI service for uploading, tracking, and retrieving processed documents.",
)

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(health_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "message": "Document Processing Pipeline API is running"
    }