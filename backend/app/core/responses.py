from typing import Any

from fastapi.responses import JSONResponse

from app.core.constants import API_STATUS_ERROR, API_STATUS_SUCCESS


def success_response(message: str, data: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"statusCode": status_code, "status": API_STATUS_SUCCESS, "message": message, "data": data},
    )


def error_response(status_code: int, message: str, error_code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "status": API_STATUS_ERROR,
            "message": message,
            "data": None,
            "errorCode": error_code,
        },
    )
