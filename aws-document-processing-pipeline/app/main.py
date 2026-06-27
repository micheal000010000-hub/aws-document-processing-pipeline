from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.stats import router as stats_router

app = FastAPI(title="Document Processing API")

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(health_router)
app.include_router(stats_router)

@app.get("/")
def root():
    return {
        "message": "Document Processing API is running"
    }