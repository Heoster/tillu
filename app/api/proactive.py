"""
TILLU Proactive APIs
Briefing, personality panel, data export/clear.
"""

import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.security.dependencies import get_current_user
from app.utils.database import db
from app.utils.logging import get_logger

logger = get_logger("proactive")
router = APIRouter(prefix="/api/v1", tags=["proactive"])


async def verify_auth(authorization: Optional[str] = Header(None)):
    return await get_current_user(authorization)


# ── Briefing ──────────────────────────────────────────────────────────────────


@router.get("/briefing")
async def get_briefing(auth=Depends(verify_auth)):
    """Today's morning briefing."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    IST = ZoneInfo("Asia/Kolkata")
    now = datetime.now(IST)

    # Try to get from DB first
    try:
        briefings = await db.fetch_many(
            "proactive_messages",
            {"type": "morning_brief"},
            limit=1,
            order_by="created_at",
            ascending=False,
        )
        if briefings:
            b = briefings[0]
            return {
                "briefing": b.get("content", "Good morning! TILLU is ready."),
                "date": now.strftime("%Y-%m-%d"),
                "highlights": b.get("metadata", {}).get("highlights", []),
            }
    except Exception:
        pass

    # Fallback default
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return {
        "briefing": (
            f"{greeting}! TILLU is active and watching over things. "
            "Your AI companion is ready whenever you need it."
        ),
        "date": now.strftime("%Y-%m-%d"),
        "highlights": [
            "Memory systems active",
            "All loops running",
            "Ready for conversation",
        ],
    }


# ── Personality ───────────────────────────────────────────────────────────────


class PersonalityUpdate(BaseModel):
    curiosity: Optional[float] = None
    warmth: Optional[float] = None
    humor: Optional[float] = None
    analytical: Optional[float] = None
    empathy: Optional[float] = None


@router.get("/personality")
async def get_personality(auth=Depends(verify_auth)):
    """Get TILLU's current personality parameters."""
    user_id = auth["user_id"]
    try:
        profile = await db.fetch_one("user_profile", {"user_id": user_id})
        if profile and profile.get("personality_params"):
            params = profile["personality_params"]
            base = params.get("base", {})
            meta = params.get("meta", {})
            return {
                "curiosity": base.get("curiosity", 0.82),
                "warmth": base.get("warmth", 0.71),
                "humor": base.get("humor", 0.54),
                "analytical": base.get("analytical", 0.80),
                "empathy": base.get("empathy", 0.63),
                "evolution_notes": meta.get("notes", []),
                "last_evolved": meta.get("last_evolved"),
                "evolution_count": meta.get("evolution_count", 0),
                "growth_entries": params.get("journal", []),
            }
    except Exception as e:
        logger.warning(f"Could not fetch personality from DB: {e}")

    # Defaults
    return {
        "curiosity": 0.82,
        "warmth": 0.71,
        "humor": 0.54,
        "analytical": 0.80,
        "empathy": 0.63,
        "evolution_notes": ["TILLU is learning your preferences..."],
        "last_evolved": None,
        "evolution_count": 0,
        "growth_entries": [],
    }


@router.patch("/personality")
async def update_personality(update: PersonalityUpdate, auth=Depends(verify_auth)):
    """Update personality preferences."""
    user_id = auth["user_id"]
    try:
        profile = await db.fetch_one("user_profile", {"user_id": user_id})
        params = (profile or {}).get("personality_params", {})
        base = params.get("base", {})

        update_dict = update.dict(exclude_none=True)
        base.update(update_dict)
        params["base"] = base

        await db.update(
            "user_profile", {"personality_params": params}, {"user_id": user_id}
        )
        return {"success": True, "updated": update_dict}
    except Exception as e:
        logger.error(f"Personality update error: {e}")
        return {"success": False, "error": str(e)}


# ── Export / Clear ────────────────────────────────────────────────────────────


@router.get("/export")
async def export_data(auth=Depends(verify_auth)):
    """Export all user data as JSON."""
    user_id = auth["user_id"]
    try:
        memories = await db.fetch_many(
            "knowledge_base", {"user_id": user_id}, limit=10000
        )
        interactions = await db.fetch_many(
            "interactions", {"user_id": user_id}, limit=10000
        )
        profile = await db.fetch_one("user_profile", {"user_id": user_id})

        import json

        from fastapi.responses import JSONResponse

        data = json.dumps(
            {
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "user_id": user_id,
                "profile": profile,
                "memories": memories,
                "interactions": interactions,
            },
            default=str,
        )

        return JSONResponse(
            content={"data": data},
            headers={"Content-Disposition": "attachment; filename=tillu-export.json"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memory/clear")
async def clear_memory(auth=Depends(verify_auth)):
    """Clear all memories."""
    user_id = auth["user_id"]
    try:
        await db.delete("knowledge_base", {"user_id": user_id})
        return {"success": True, "message": "All memories cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
