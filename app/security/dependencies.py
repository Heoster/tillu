"""
Shared FastAPI security dependencies for TILLU.

TILLU is a single-user system: every authenticated UI maps to one configured
user ID. Tokens are still validated so every UI is protected by the phone-like
PIN/password unlock flow.
"""

from __future__ import annotations

from typing import Any, Optional

import jwt
from app.config import settings
from app.utils.logging import get_logger
from fastapi import Header, HTTPException, status

logger = get_logger("security_dependencies")


class CurrentUser(dict):
    """Simple dict subclass for type clarity in route dependencies."""


async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    """Validate bearer auth and return the single TILLU user identity.

    In production, PIN login issues HS256 JWTs using SECRET_KEY. During local
    development, token verification can be disabled via ENABLE_JWT_VERIFICATION=false,
    but a bearer token is still required.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is empty",
        )

    payload: dict[str, Any] = {}
    if settings.enable_jwt_verification:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError as exc:
            logger.warning("JWT verification failed", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        token_user = payload.get("user_id") or payload.get("sub")
        if token_user and token_user != settings.single_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token is not valid for this TILLU instance",
            )
    else:
        logger.warning(
            "JWT verification disabled; accepting bearer token for development"
        )

    return CurrentUser(
        user_id=settings.single_user_id,
        token=token,
        payload=payload,
    )


async def require_internal_secret(
    x_internal_auth: Optional[str] = Header(None),
) -> dict:
    """Validate internal automation calls from Cloudflare/n8n/watcher."""
    if not settings.internal_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_SECRET is not configured",
        )
    if not x_internal_auth or x_internal_auth != settings.internal_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing x-internal-auth",
        )
    return {"user_id": settings.single_user_id, "internal": True}
