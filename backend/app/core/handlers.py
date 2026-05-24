"""Global exception handlers for FastAPI application."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AIServiceUnavailableError,
    AppError,
    ConflictError,
    EntityNotFoundError,
    InternalServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _error_response(status_code: int, code: str, message: str, details: dict) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                }
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""

    # Register every AppError subclass explicitly so FastAPI routes them
    # correctly regardless of MRO/middleware ordering issues.
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error("%s: %s", exc.error_code, exc.message)
        return _error_response(exc.status_code, exc.error_code, exc.message, exc.details or {})

    for exc_class in (
        EntityNotFoundError,
        ConflictError,
        ValidationError,
        InternalServerError,
        AIServiceUnavailableError,
        AppError,  # catch-all for any future AppError subclasses
    ):
        app.add_exception_handler(exc_class, app_exception_handler)

    # Request validation errors (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning("Validation error: %s", exc.errors())
        return _error_response(422, "VALIDATION_ERROR", "Request validation failed.", exc.errors())

    # True catch-all for unexpected errors (must be last)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return _error_response(500, "INTERNAL_SERVER_ERROR", "An unexpected error occurred.", {})