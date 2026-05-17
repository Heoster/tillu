"""
TILLU Conversation API

Shared conversation history contract for web, mobile, and desktop. This reads
from the existing interactions table so all UIs can resume the same work state.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from app.security.dependencies import get_current_user
from app.utils.database import db
from app.utils.logging import get_logger

logger = get_logger("conversation_api")
router = APIRouter(prefix="/api/v1/chat", tags=["conversation"])


async def verify_auth(authorization: Optional[str] = Header(None)) -> dict:
    return await get_current_user(authorization)


def _message_pair(row: dict) -> list[dict]:
    created_at = row.get("created_at")
    return [
        {
            "id": f"{row.get('id', '')}:user",
            "role": "user",
            "content": row.get("input_text") or "",
            "timestamp": created_at,
            "session_id": row.get("session_id"),
        },
        {
            "id": f"{row.get('id', '')}:assistant",
            "role": "assistant",
            "content": row.get("response_text") or "",
            "timestamp": created_at,
            "session_id": row.get("session_id"),
            "sources": row.get("sources")
            or row.get("response_metadata", {}).get("sources", []),
        },
    ]


def _conversation_summary(session_id: str, rows: list[dict]) -> dict:
    first = rows[-1] if rows else {}
    latest = rows[0] if rows else {}
    title = (latest.get("input_text") or "New conversation").strip()[:80]
    return {
        "id": session_id,
        "session_id": session_id,
        "title": title,
        "created_at": first.get("created_at"),
        "updated_at": latest.get("created_at"),
        "message_count": len(rows) * 2,
        "last_message": latest.get("response_text") or latest.get("input_text") or "",
    }


@router.get("/history")
async def list_conversations(
    limit: int = 50,
    auth: dict = Depends(verify_auth),
):
    """List recent conversation sessions for sidebar/history screens."""
    user_id = auth["user_id"]
    safe_limit = max(1, min(limit, 200))

    rows = await db.fetch_many(
        "interactions",
        {"user_id": user_id},
        order_by="created_at",
        ascending=False,
        limit=1000,
    )

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        session_id = row.get("session_id") or "default"
        grouped[str(session_id)].append(row)

    conversations = [
        _conversation_summary(session_id, session_rows)
        for session_id, session_rows in grouped.items()
    ]
    conversations.sort(key=lambda item: item.get("updated_at") or "", reverse=True)

    return {"conversations": conversations[:safe_limit]}


@router.get("/history/{session_id}")
async def get_conversation(
    session_id: str,
    limit: int = 200,
    auth: dict = Depends(verify_auth),
):
    """Return messages for one conversation/session."""
    user_id = auth["user_id"]
    safe_limit = max(1, min(limit, 500))

    rows = await db.fetch_many(
        "interactions",
        {"user_id": user_id, "session_id": session_id},
        order_by="created_at",
        ascending=True,
        limit=safe_limit,
    )

    messages: list[dict] = []
    for row in rows:
        messages.extend(_message_pair(row))

    return {
        "id": session_id,
        "session_id": session_id,
        "messages": messages,
        "message_count": len(messages),
    }


@router.delete("/history/{session_id}")
async def delete_conversation(
    session_id: str,
    auth: dict = Depends(verify_auth),
):
    """Delete all stored interactions for a session."""
    user_id = auth["user_id"]
    deleted = await db.delete(
        "interactions", {"user_id": user_id, "session_id": session_id}
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "session_id": session_id}
