"""FastAPI application entry point.

The static frontend lives in ``src/static`` and is mounted last so API routes
can remain under ``/api``.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as api_router
from src.config import settings


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(api_router, prefix="/api")
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
