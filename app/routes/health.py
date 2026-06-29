from __future__ import annotations

from fastapi import APIRouter

from app.config import APP_NAME, APP_VERSION


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
    }
