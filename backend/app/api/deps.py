"""
FastAPI dependency injectors.

Defines reusable dependency aliases used by API routes, including the
database session dependency shown in generated OpenAPI documentation.
"""

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db

# Type alias for dependency-injected DB session
DB = Annotated[AsyncSession, Depends(get_db)]


async def require_admin(
    x_admin_api_key: str | None = Header(
        default=None,
        description=(
            "Admin API key required for write operations. "
            "Set via the ADMIN_API_KEY environment variable."
        ),
    ),
) -> None:
    """
    Enforce admin API key authentication for protected write endpoints.

    Raises 503 if ADMIN_API_KEY is not configured so the application
    never silently accepts unauthenticated requests in production.
    Raises 401 if the key is absent or does not match.

    Uses a constant-time comparison (``secrets.compare_digest``) to
    prevent timing attacks that could reveal the correct key length.
    """
    settings = get_settings()

    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ADMIN_KEY_NOT_CONFIGURED",
                "message": (
                    "Admin API key is not configured on this server. "
                    "Set ADMIN_API_KEY in the environment before using "
                    "admin-only endpoints."
                ),
            },
        )

    if x_admin_api_key is None or not secrets.compare_digest(
        x_admin_api_key, settings.admin_api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_ADMIN_KEY",
                "message": "Missing or invalid X-Admin-API-Key header.",
            },
            headers={"WWW-Authenticate": "ApiKey"},
        )

