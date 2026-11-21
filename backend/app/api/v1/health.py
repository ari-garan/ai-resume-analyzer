from fastapi import APIRouter

from app.core.config import settings
from app.core.responses import success_response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health():
    return success_response("Service is healthy.", {"service": settings.app_name, "status": "healthy"})
