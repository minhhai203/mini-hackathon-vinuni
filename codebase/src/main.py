"""FastAPI application entry point.

The static frontend lives in ``src/static`` and is mounted last so API routes
can remain under ``/api``.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as api_router
from src.config import settings
from src.session_limit import check_and_admit


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Paths that must always be reachable (waiting page + its assets + status API)
_ALWAYS_ALLOW = {"/waiting.html", "/api/queue-status"}


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    @app.middleware("http")
    async def user_limit_middleware(request: Request, call_next):
        path = request.url.path
        if path in _ALWAYS_ALLOW or path.startswith("/assets/"):
            return await call_next(request)

        session_id = request.cookies.get("demo_session")
        admitted, new_session_id = check_and_admit(session_id)

        if not admitted:
            return RedirectResponse(url="/waiting.html", status_code=302)

        response = await call_next(request)

        if new_session_id and new_session_id != session_id:
            response.set_cookie(
                "demo_session",
                new_session_id,
                max_age=600,
                httponly=True,
                samesite="lax",
            )
        return response

    app.include_router(api_router, prefix="/api")
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
