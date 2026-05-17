"""
Memory API endpoints for semantic search and storage
"""

import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from app.models.api import MemoryItem, MemorySearchRequest, MemorySearchResponse
from app.security.dependencies import get_current_user, require_internal_secret
from app.utils.cache import cache
from app.utils.database import db
from app.utils.logging import get_logger

logger = get_logger("memory_api")
router = APIRouter(prefix="/api/v1/memory")


def _client_memory(row: dict) -> dict:
    """Normalize DB/search rows for web, mobile, and desktop clients."""
    created_at = row.get("created_at") or row.get("timestamp") or row.get("fetched_at")
    return {
        "id": str(row.get("id", "")),
        "content": row.get("content")
        or row.get("executive_summary")
        or f"{row.get('title', '')}: {row.get('summary', '')}".strip(": "),
        "category": row.get("category") or row.get("content_type") or "memory",
        "tags": row.get("tags") or [],
        "created_at": created_at,
        "timestamp": created_at,
        "importance": row.get("importance") or row.get("confidence_score") or 0.7,
        "relevance": row.get("similarity") or row.get("relevance_score"),
    }


async def verify_auth(authorization: Optional[str] = Header(None)):
    return await get_current_user(authorization)


@router.get("")
async def list_memories(
    limit: int = 100,
    offset: int = 0,
    auth: dict = Depends(verify_auth),
):
    """Return recent memories for Memory Vault screens across all UIs."""
    user_id = auth["user_id"]
    safe_limit = max(1, min(limit, 500))

    try:
        rows = await db.fetch_many(
            "knowledge_base",
            {"user_id": user_id},
            order_by="created_at",
            ascending=False,
            limit=safe_limit,
            offset=offset,
        )
        memories = [_client_memory(row) for row in rows]
        return {
            "memories": memories,
            "total": len(memories),
            "limit": safe_limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error("Memory list error", error=str(e))
        raise HTTPException(status_code=500, detail="Could not list memories")


@router.get("/search")
async def search_memory_get(
    q: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    auth: dict = Depends(verify_auth),
):
    """GET alias for semantic memory search used by web/mobile clients."""
    text = (query or q or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="query or q is required")

    result = await search_memory(
        MemorySearchRequest(query=text, limit=max(1, min(limit, 50))), auth
    )
    results = [item.dict() for item in result.results]
    memories = [_client_memory(item) for item in results]
    return {
        "query": result.query,
        "results": results,
        "memories": memories,
        "total_found": result.total_found,
        "search_time_ms": result.search_time_ms,
    }


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(
    request: MemorySearchRequest, auth: dict = Depends(verify_auth)
):
    """
    Semantic memory query across all stores.
    Uses pgvector similarity search with embeddings.
    """
    user_id = auth["user_id"]
    start_time = time.time()

    logger.info("Memory search", query=request.query, limit=request.limit)

    try:
        # PHASE 2: Semantic search with embeddings
        from app.memory.semantic_search import semantic_search

        results = await semantic_search.search_all(
            user_id=user_id, query=request.query, max_results_per_source=request.limit
        )

        # Format results from all sources
        items = []

        # Add knowledge base results
        for item in results.get("knowledge", []):
            items.append(
                MemoryItem(
                    id=item["id"],
                    content=item["content"],
                    content_type=item.get("content_type", "fact"),
                    category=item.get("category"),
                    source_type="knowledge_base",
                    confidence_score=item.get("confidence_score", 0.8),
                    similarity=item.get("similarity", 0.75),
                    created_at=item["created_at"],
                )
            )

        # Add news results
        for item in results.get("news", []):
            items.append(
                MemoryItem(
                    id=item["id"],
                    content=f"{item.get('title', '')}: {item.get('summary', '')}",
                    content_type="news",
                    category="current_events",
                    source_type="news_article",
                    confidence_score=item.get("relevance_score", 0.7),
                    similarity=item.get("similarity", 0.7),
                    created_at=item["fetched_at"],
                )
            )

        # Add research results
        for item in results.get("research", []):
            items.append(
                MemoryItem(
                    id=item["id"],
                    content=item.get("executive_summary", item.get("query", "")),
                    content_type="research",
                    category="research_session",
                    source_type="research",
                    confidence_score=0.85,
                    similarity=item.get("similarity", 0.75),
                    created_at=item["created_at"],
                )
            )

        # Sort by similarity
        items.sort(key=lambda x: x.similarity, reverse=True)

        # Apply limit
        items = items[: request.limit]

        search_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Memory search complete",
            knowledge=len(results.get("knowledge", [])),
            news=len(results.get("news", [])),
            research=len(results.get("research", [])),
            search_time_ms=search_time_ms,
        )

        return MemorySearchResponse(
            query=request.query,
            results=items,
            total_found=len(items),
            search_time_ms=search_time_ms,
        )

    except Exception as e:
        logger.error("Memory search error", error=str(e))
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/add")
async def add_memory_json(
    payload: dict,
    auth: dict = Depends(verify_auth),
):
    """JSON alias for manually adding a memory from UI clients."""
    content = (payload.get("content") or payload.get("text") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    return await store_memory(
        content=content,
        content_type=payload.get("content_type") or "fact",
        category=payload.get("category"),
        auth=auth,
    )


@router.post("/store")
async def store_memory(
    content: str,
    content_type: str = "fact",
    category: Optional[str] = None,
    auth: dict = Depends(verify_auth),
):
    """
    Explicitly store a knowledge item.
    Generates embedding automatically (Phase 2).
    """
    user_id = auth["user_id"]

    logger.info("Storing memory", content_type=content_type, category=category)

    try:
        # PHASE 2: Store with embedding
        from app.memory.semantic_search import semantic_search

        result = await semantic_search.store_with_embedding(
            user_id=user_id,
            content=content,
            content_type=content_type,
            category=category,
            source_type="user",
            source_metadata={"api_endpoint": "/memory/store"},
        )

        if result:
            return {
                "success": True,
                "memory_id": result["id"],
                "embedding_generated": True,
                "message": "Memory stored with embedding successfully",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store memory")

    except Exception as e:
        logger.error("Memory store error", error=str(e))
        raise HTTPException(status_code=500, detail="Store failed")


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, auth: dict = Depends(verify_auth)):
    """Delete a memory item"""
    user_id = auth["user_id"]

    logger.info("Deleting memory", memory_id=memory_id)

    result = await db.delete("knowledge_base", {"id": memory_id, "user_id": user_id})

    if result:
        return {"success": True, "message": "Memory deleted"}
    else:
        raise HTTPException(status_code=404, detail="Memory not found")


# ── Internal endpoints for workflow automation ─────────────────────────────────


@router.get("/internal/weekly-summary")
async def get_weekly_summary(
    weeks_back: int = 1, x_internal_auth: Optional[str] = Header(None)
):
    """
    Get weekly interaction summary for personality evolution.
    Internal endpoint used by n8n workflows.

    Returns:
        - interactions: List of interactions from the past week
        - summary_stats: Aggregated quality scores
        - current_personality: Current personality parameters
    """
    # Allow internal calls from n8n/engine without full auth
    internal = await require_internal_secret(x_internal_auth)

    user_id = internal["user_id"]

    try:
        import datetime

        # Calculate cutoff time (weeks_back weeks ago)
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks_back)

        # Fetch interactions from the past week
        all_interactions = await db.fetch_many(
            "interactions",
            filters={"user_id": user_id},
            order_by="created_at",
            ascending=False,
            limit=500,
        )

        # Filter to interactions within the date range
        recent_interactions = [
            i
            for i in all_interactions
            if i.get("created_at")
            and datetime.datetime.fromisoformat(
                str(i["created_at"]).replace("Z", "+00:00")
            )
            > cutoff_date
        ]

        # Get current user profile for personality params
        user_profile = await db.fetch_one("user_profile", {"user_id": user_id})

        current_personality = (
            user_profile.get("personality_params", {}) if user_profile else {}
        )

        # Calculate summary statistics
        summary_stats = {}
        if recent_interactions:
            # Filter interactions with quality scores
            scored = [
                i
                for i in recent_interactions
                if i.get("quality_accuracy_score") is not None
            ]

            if scored:
                summary_stats = {
                    "total_interactions": len(recent_interactions),
                    "scored_interactions": len(scored),
                    "avg_accuracy": sum(
                        i.get("quality_accuracy_score", 0) for i in scored
                    )
                    / len(scored),
                    "avg_helpfulness": sum(
                        i.get("quality_helpfulness_score", 0) for i in scored
                    )
                    / len(scored),
                    "avg_personality_fit": sum(
                        i.get("quality_personality_fit_score", 0) for i in scored
                    )
                    / len(scored),
                }
            else:
                summary_stats = {
                    "total_interactions": len(recent_interactions),
                    "scored_interactions": 0,
                    "message": "No scored interactions in period",
                }

        logger.info(
            "Weekly summary retrieved",
            user_id=user_id,
            weeks_back=weeks_back,
            interactions=len(recent_interactions),
        )

        return {
            "week": weeks_back,
            "period_start": cutoff_date.isoformat(),
            "interactions": recent_interactions,
            "summary_stats": summary_stats,
            "current_personality": current_personality,
            "user_id": user_id,
        }

    except Exception as e:
        logger.error("Error getting weekly summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.post("/internal/update-personality")
async def update_personality(
    new_params: dict,
    evolution_notes: Optional[str] = None,
    week: Optional[int] = None,
    x_internal_auth: Optional[str] = Header(None),
):
    """
    Update user personality parameters after evolution.
    Internal endpoint used by personality-evolution workflow.

    Args:
        new_params: New personality parameters (dict with temperature, sarcasm, warmth, etc.)
        evolution_notes: Optional notes about the evolution
        week: Week number for audit trail
    """
    internal = await require_internal_secret(x_internal_auth)

    user_id = internal["user_id"]

    try:
        import time

        # Fetch current profile
        profile = await db.fetch_one("user_profile", {"user_id": user_id})

        if not profile:
            logger.warning(f"User profile not found for {user_id}")
            profile = {"user_id": user_id, "personality_params": {}}

        # Update personality params
        existing_personality = profile.get("personality_params", {})
        existing_personality["base"] = new_params
        existing_personality["meta"] = {
            "last_evolved": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evolution_count": existing_personality.get("meta", {}).get(
                "evolution_count", 0
            )
            + 1,
            "week": week,
            "notes": evolution_notes,
        }

        # Update in database
        await db.update(
            "user_profile",
            {"personality_params": existing_personality},
            {"user_id": user_id},
        )

        # Invalidate cache
        await cache.delete(f"user_profile:{user_id}")

        logger.info(
            "Personality updated",
            user_id=user_id,
            week=week,
            params=list(new_params.keys()) if new_params else [],
        )

        return {
            "success": True,
            "message": "Personality parameters updated",
            "user_id": user_id,
            "week": week,
            "new_params": new_params,
            "updated_at": existing_personality["meta"]["last_evolved"],
        }

    except Exception as e:
        logger.error("Error updating personality", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to update personality: {str(e)}"
        )
