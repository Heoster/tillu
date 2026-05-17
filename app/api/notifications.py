"""
TILLU Notification API

Single-user push notification contract for mobile, web, and desktop. Stores
subscriptions/settings and can deliver Expo push notifications directly while
queueing all events in event_queue for history and other clients.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.security.dependencies import get_current_user, require_internal_secret
from app.utils.database import db
from app.utils.logging import get_logger

logger = get_logger("notifications_api")
router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


async def verify_auth(authorization: Optional[str] = Header(None)) -> dict:
    return await get_current_user(authorization)


async def verify_internal(x_internal_auth: Optional[str] = Header(None)) -> dict:
    return await require_internal_secret(x_internal_auth)


class NotificationRegisterRequest(BaseModel):
    platform: str = Field(..., description="expo, web_push, desktop, tauri")
    token: Optional[str] = None
    subscription: dict[str, Any] = Field(default_factory=dict)
    client_id: Optional[str] = None
    device_name: Optional[str] = None
    enabled: bool = True


class NotificationSettingsRequest(BaseModel):
    morning_briefing_enabled: Optional[bool] = None
    morning_briefing_time: Optional[str] = None
    interesting_finds_enabled: Optional[bool] = None
    weekly_evolution_enabled: Optional[bool] = None
    proactive_messages_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    channels: Optional[dict[str, bool]] = None


class NotificationSendRequest(BaseModel):
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    tillu_message: Optional[str] = None
    event_type: str = "proactive_message"
    urgency: int = Field(default=5, ge=1, le=10)
    data: dict[str, Any] = Field(default_factory=dict)
    target_platforms: list[str] = Field(default_factory=list)


@router.post("/register")
async def register_notification_target(
    request: NotificationRegisterRequest,
    auth: dict = Depends(verify_auth),
):
    """Register a mobile Expo token, Web Push subscription, or desktop target."""
    user_id = auth["user_id"]
    if not request.token and not request.subscription:
        raise HTTPException(status_code=400, detail="token or subscription is required")

    payload = {
        "user_id": user_id,
        "platform": request.platform,
        "token": request.token,
        "subscription": request.subscription,
        "client_id": request.client_id,
        "device_name": request.device_name,
        "enabled": request.enabled,
        "last_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    existing = None
    if request.token:
        existing = await db.fetch_one(
            "notification_subscriptions",
            {"user_id": user_id, "platform": request.platform, "token": request.token},
        )

    if existing:
        updated = await db.update(
            "notification_subscriptions",
            payload,
            {"id": existing["id"]},
        )
        row = updated[0] if updated else existing
    else:
        inserted = await db.insert("notification_subscriptions", payload)
        row = inserted[0] if isinstance(inserted, list) and inserted else inserted

    if not row:
        raise HTTPException(
            status_code=500, detail="Could not register notification target"
        )

    return {"success": True, "subscription": row}


@router.get("/settings")
async def get_notification_settings(auth: dict = Depends(verify_auth)):
    user_id = auth["user_id"]
    settings = await db.fetch_one("notification_settings", {"user_id": user_id})
    if settings:
        return settings
    return {
        "user_id": user_id,
        "morning_briefing_enabled": True,
        "morning_briefing_time": "07:00:00",
        "interesting_finds_enabled": True,
        "weekly_evolution_enabled": True,
        "proactive_messages_enabled": True,
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00:00",
        "quiet_hours_end": "08:00:00",
        "channels": {"expo": True, "web_push": True, "desktop": True},
    }


@router.put("/settings")
async def update_notification_settings(
    request: NotificationSettingsRequest,
    auth: dict = Depends(verify_auth),
):
    user_id = auth["user_id"]
    updates = request.dict(exclude_none=True)
    updates["user_id"] = user_id

    existing = await db.fetch_one("notification_settings", {"user_id": user_id})
    if existing:
        updated = await db.update(
            "notification_settings", updates, {"user_id": user_id}
        )
        row = updated[0] if updated else {**existing, **updates}
    else:
        inserted = await db.insert("notification_settings", updates)
        row = inserted[0] if isinstance(inserted, list) and inserted else inserted

    if not row:
        raise HTTPException(
            status_code=500, detail="Could not update notification settings"
        )
    return {"success": True, "settings": row}


@router.get("/history")
async def notification_history(
    limit: int = 50,
    auth: dict = Depends(verify_auth),
):
    user_id = auth["user_id"]
    rows = await db.fetch_many(
        "event_queue",
        {"user_id": user_id},
        order_by="generated_at",
        ascending=False,
        limit=max(1, min(limit, 200)),
    )
    return {"notifications": rows}


async def _send_expo_push(
    token: str, title: str, body: str, data: dict[str, Any]
) -> dict:
    payload = {
        "to": token,
        "title": title,
        "body": body,
        "data": data,
        "sound": "default",
        "priority": "high",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://exp.host/--/api/v2/push/send", json=payload
        )
    try:
        result = response.json()
    except Exception:
        result = {"raw": response.text}
    return {"status_code": response.status_code, "result": result}


@router.post("/internal/send")
async def send_notification_internal(
    request: NotificationSendRequest,
    auth: dict = Depends(verify_internal),
):
    """Internal n8n/watcher endpoint to queue and deliver proactive messages."""
    user_id = auth["user_id"]

    event = {
        "user_id": user_id,
        "event_type": request.event_type,
        "urgency": request.urgency,
        "source_agent": "watcher",
        "title": request.title,
        "body": request.body,
        "tillu_message": request.tillu_message or request.body,
        "structured_data": request.data,
        "status": "pending",
    }
    inserted = await db.insert("event_queue", event)

    filters = {"user_id": user_id, "enabled": True}
    subscriptions = await db.fetch_many(
        "notification_subscriptions", filters, limit=100
    )
    if request.target_platforms:
        subscriptions = [
            sub
            for sub in subscriptions
            if sub.get("platform") in request.target_platforms
        ]

    deliveries = []
    for sub in subscriptions:
        platform = sub.get("platform")
        token = sub.get("token")
        if platform == "expo" and token:
            try:
                result = await _send_expo_push(
                    token, request.title, request.body, request.data
                )
                deliveries.append({"platform": platform, "token": token, **result})
                await db.update(
                    "notification_subscriptions",
                    {"last_sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    {"id": sub["id"]},
                )
            except Exception as exc:
                logger.warning("Expo push failed", error=str(exc))
                deliveries.append(
                    {"platform": platform, "token": token, "error": str(exc)}
                )
        else:
            deliveries.append({"platform": platform, "queued_only": True})

    if isinstance(inserted, list) and inserted:
        await db.update(
            "event_queue",
            {
                "status": "delivered" if deliveries else "pending",
                "delivered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                if deliveries
                else None,
            },
            {"id": inserted[0]["id"]},
        )

    return {
        "success": True,
        "event": inserted[0] if isinstance(inserted, list) and inserted else inserted,
        "deliveries": deliveries,
    }
