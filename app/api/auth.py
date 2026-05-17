"""
TILLU PIN Authentication
Single-user system. No registration. PIN-only (like phone lock screen).
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta

import jwt  # from PyJWT
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

TILLU_PIN = os.environ.get("TILLU_PIN", "123456")
SECRET_KEY = settings.secret_key
JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "168"))  # 7 days


class LoginRequest(BaseModel):
    pin: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int  # seconds
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """PIN login — returns JWT token. No username needed."""
    # Constant-time comparison to prevent timing attacks
    provided = req.pin.strip().encode()
    expected = TILLU_PIN.strip().encode()

    if not hmac.compare_digest(
        hashlib.sha256(provided).digest(), hashlib.sha256(expected).digest()
    ):
        logger.warning("Failed PIN attempt")
        raise HTTPException(status_code=401, detail="Invalid PIN")

    # Issue JWT
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": settings.single_user_id,
        "user_id": settings.single_user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    logger.info("PIN auth successful, token issued")
    return LoginResponse(
        token=token,
        expires_in=JWT_EXPIRE_HOURS * 3600,
        message="Welcome back. TILLU is ready.",
    )


@router.post("/logout")
async def logout():
    """Logout — client should discard token."""
    return {"success": True, "message": "Session ended."}


@router.get("/status")
async def auth_status():
    """Check if auth is configured."""
    pin_set = TILLU_PIN != "123456"
    return {
        "auth_configured": True,
        "pin_is_default": not pin_set,
        "warning": "Change TILLU_PIN in production!" if not pin_set else None,
    }
