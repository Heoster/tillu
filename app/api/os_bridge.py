"""
TILLU OS Bridge API

Backend-facing contract for controlled Linux OS operations through the local
TILLU daemon / desktop relay. The daemon itself stays localhost-only and
key-gated; this bridge is disabled by default until explicitly configured.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.security.dependencies import get_current_user
from app.utils.logging import get_logger

logger = get_logger("os_bridge")
router = APIRouter(prefix="/api/v1/os", tags=["os-bridge"])


# ---------------------------------------------------------------------------
# Auth / guards
# ---------------------------------------------------------------------------


async def verify_auth(authorization: Optional[str] = Header(None)) -> dict:
    """Single-user bearer-token guard used by all UI-facing OS routes."""
    return await get_current_user(authorization)


def require_bridge_enabled() -> None:
    if not settings.os_bridge_enabled:
        raise HTTPException(
            status_code=503,
            detail=(
                "OS bridge is disabled. Set OS_BRIDGE_ENABLED=true and "
                "OS_DAEMON_KEY to enable local OS control."
            ),
        )
    if not settings.os_daemon_key:
        raise HTTPException(
            status_code=503,
            detail="OS_DAEMON_KEY is not configured.",
        )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class PathRequest(BaseModel):
    path: str = Field(..., min_length=1)


class FileWriteRequest(BaseModel):
    path: str = Field(..., min_length=1)
    content: str
    create_backup: bool = True


class ShellExecuteRequest(BaseModel):
    command: str = Field(..., min_length=1)
    timeout: int = Field(default=30, ge=1, le=120)


class NotifyRequest(BaseModel):
    title: str = Field(default="TILLU")
    message: str = Field(..., min_length=1)


class SessionSaveRequest(BaseModel):
    reason: str = "manual"
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Daemon client
# ---------------------------------------------------------------------------


async def daemon_request(
    method: str,
    path: str,
    *,
    json_body: Optional[dict[str, Any]] = None,
) -> Any:
    """Call the local daemon/relay with strict timeout and daemon key."""
    require_bridge_enabled()

    base = settings.os_daemon_url.rstrip("/")
    url = f"{base}{path}"
    headers = {"X-Daemon-Key": settings.os_daemon_key or ""}
    timeout = httpx.Timeout(settings.os_request_timeout_seconds)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                url,
                json=json_body,
                headers=headers,
            )
    except httpx.RequestError as exc:
        logger.error("OS daemon unreachable", error=str(exc), path=path)
        raise HTTPException(
            status_code=502,
            detail=f"OS daemon unreachable: {exc}",
        )

    if response.status_code >= 400:
        detail: Any
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    if not response.content:
        return {"success": True}

    try:
        return response.json()
    except Exception:
        return {"content": response.text}


# ---------------------------------------------------------------------------
# Routes: health / presence / system
# ---------------------------------------------------------------------------


@router.get("/bridge/status")
async def bridge_status(auth: dict = Depends(verify_auth)):
    """Show whether OS bridge is configured without contacting the daemon."""
    return {
        "enabled": settings.os_bridge_enabled,
        "daemon_url": settings.os_daemon_url,
        "daemon_key_configured": bool(settings.os_daemon_key),
        "shell_enabled": settings.os_shell_enabled,
        "file_delete_enabled": settings.os_file_delete_enabled,
    }


@router.get("/health")
async def os_health(auth: dict = Depends(verify_auth)):
    return await daemon_request("GET", "/health")


@router.get("/system/info")
async def os_system_info(auth: dict = Depends(verify_auth)):
    return await daemon_request("GET", "/os/system/info")


@router.get("/user/activity")
async def os_user_activity(auth: dict = Depends(verify_auth)):
    return await daemon_request("GET", "/os/user/activity")


# ---------------------------------------------------------------------------
# Routes: files
# ---------------------------------------------------------------------------


@router.post("/file/read")
async def file_read(request: PathRequest, auth: dict = Depends(verify_auth)):
    return await daemon_request("POST", "/os/file/read", json_body=request.dict())


@router.post("/file/list")
async def file_list(request: PathRequest, auth: dict = Depends(verify_auth)):
    return await daemon_request("POST", "/os/file/list", json_body=request.dict())


@router.post("/file/write")
async def file_write(request: FileWriteRequest, auth: dict = Depends(verify_auth)):
    payload = request.dict()
    result = await daemon_request("POST", "/os/file/write", json_body=payload)
    logger.info(
        "OS file write requested",
        user_id=auth["user_id"],
        path=request.path,
        create_backup=request.create_backup,
    )
    return result


@router.post("/file/delete")
async def file_delete(request: PathRequest, auth: dict = Depends(verify_auth)):
    if not settings.os_file_delete_enabled:
        raise HTTPException(
            status_code=403,
            detail="File delete is disabled. Set OS_FILE_DELETE_ENABLED=true to allow it.",
        )
    return await daemon_request("POST", "/os/file/delete", json_body=request.dict())


# ---------------------------------------------------------------------------
# Routes: shell / notifications / session
# ---------------------------------------------------------------------------


@router.post("/shell/execute")
async def shell_execute(
    request: ShellExecuteRequest,
    auth: dict = Depends(verify_auth),
):
    if not settings.os_shell_enabled:
        raise HTTPException(
            status_code=403,
            detail="Shell execution is disabled. Set OS_SHELL_ENABLED=true to allow it.",
        )
    timeout = min(request.timeout, settings.os_request_timeout_seconds)
    payload = request.dict()
    payload["timeout"] = timeout
    return await daemon_request("POST", "/os/shell/execute", json_body=payload)


@router.post("/notify")
async def notify(request: NotifyRequest, auth: dict = Depends(verify_auth)):
    return await daemon_request("POST", "/os/notify", json_body=request.dict())


@router.post("/session/save")
async def save_session(
    request: SessionSaveRequest,
    auth: dict = Depends(verify_auth),
):
    payload = {
        "reason": request.reason,
        "metadata": request.metadata,
        "requested_by": auth["user_id"],
        "requested_at": int(time.time()),
    }
    return await daemon_request("POST", "/os/session/save", json_body=payload)
