import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.constants import FRONTEND_BUILD_PATH
from app.core.exceptions import AppError
from app.core.frontend_build import frontend_build_is_current
from app.core.responses import error_response
from app.core.rate_limiter import limiter
from app.database.base import Base
from app.database.connection import engine
from app import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", debug=settings.debug, lifespan=lifespan)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit(request: Request, exc: RateLimitExceeded):
    return error_response(429, "Request rate limit exceeded.", "RATE_LIMIT_EXCEEDED")


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    return error_response(exc.status_code, str(exc.detail), exc.error_code)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    return error_response(422, "Request validation failed.", "VALIDATION_ERROR")


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return error_response(exc.status_code, message, "HTTP_ERROR")


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled request error", exc_info=exc)
    return error_response(500, "An unexpected server error occurred.", "INTERNAL_ERROR")


app.include_router(v1_router, prefix=settings.api_v1_prefix)
if FRONTEND_BUILD_PATH.is_dir() and frontend_build_is_current():
    app.mount("/", StaticFiles(directory=FRONTEND_BUILD_PATH, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def frontend_build_hint():
        return HTMLResponse(
            "<h1>SkillBridge frontend build is missing or stale</h1><p>Run <code>npm run build</code> in the frontend directory, or start Vite with <code>npm run dev</code>.</p>",
            status_code=503,
        )
