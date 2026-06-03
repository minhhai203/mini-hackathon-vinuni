"""HTTP API routes."""

from fastapi import APIRouter

from src.models.health import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
