"""
Internal chains API endpoints
Used by n8n workflows and internal processes to invoke chains
"""

import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException

from app.chains.base import ChainRegistry, ChainType
from app.config import settings
from app.security.dependencies import require_internal_secret
from app.utils.logging import get_logger

logger = get_logger("chains_api")
router = APIRouter(prefix="/internal/chains", tags=["chains"])


async def verify_internal_auth(x_internal_auth: Optional[str] = Header(None)):
    """Verify internal request (from n8n, engine, etc)."""
    return await require_internal_secret(x_internal_auth)


@router.post("/personality-evolution")
async def run_personality_evolution(
    weekly_data: Dict[str, Any],
    current_params: Optional[Dict[str, Any]] = None,
    x_internal_auth: Optional[str] = Header(None),
):
    """
    Run personality evolution chain.
    Called by n8n personality-evolution workflow.

    Args:
        weekly_data: Weekly interaction summary from /internal/memory/weekly-summary
        current_params: Current personality parameters
        x_internal_auth: Internal authentication header

    Returns:
        Evolved personality parameters and analysis
    """
    await verify_internal_auth(x_internal_auth)

    try:
        start_time = time.time()

        logger.info(
            "Running personality evolution chain",
            interactions=len(weekly_data.get("interactions", [])),
        )

        # Get the personality evolution chain
        chain = ChainRegistry.get(ChainType.PERSONALITY_EVOLUTION)
        if not chain:
            logger.error("Personality evolution chain not found in registry")
            raise HTTPException(status_code=500, detail="Chain not available")

        # Prepare input for the chain
        user_id = weekly_data.get("user_id", settings.single_user_id)
        input_data = {
            "user_id": user_id,
            "weekly_data": weekly_data,
            "current_params": current_params,
        }

        # Execute the chain
        result = await chain.execute(input_data, context=None)

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Personality evolution chain completed",
            user_id=user_id,
            elapsed_ms=elapsed_ms,
            evolved=result.get("evolved", False),
        )

        # Extract evolved parameters from the chain result
        evolved_params = (
            result.get("response", {}).get("structured_data", {}).get("new_params", {})
        )

        return {
            "evolved_params": evolved_params,
            "notes": f"Evolution based on {len(weekly_data.get('interactions', []))} interactions",
            "week": weekly_data.get("week", 1),
            "analysis": result.get("response", {}).get("structured_data", {}),
            "latency_ms": elapsed_ms,
            "success": result.get("evolved", False),
        }

    except Exception as e:
        logger.error("Personality evolution error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")


@router.post("/conversational")
async def run_conversational_chain(
    input_text: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    x_internal_auth: Optional[str] = Header(None),
):
    """
    Run conversational chain.
    Internal endpoint for direct chain invocation.

    Args:
        input_text: User input text
        context: Optional context
        user_id: User ID
        x_internal_auth: Internal authentication header

    Returns:
        Chain result with response
    """
    await verify_internal_auth(x_internal_auth)

    try:
        start_time = time.time()

        user_id = user_id or settings.single_user_id
        logger.info("Running conversational chain", user_id=user_id)

        # Get the conversational chain
        chain = ChainRegistry.get(ChainType.CONVERSATIONAL)
        if not chain:
            logger.error("Conversational chain not found in registry")
            raise HTTPException(status_code=500, detail="Chain not available")

        # Prepare input
        input_data = {"text": input_text, "user_id": user_id}

        # Execute the chain
        result = await chain.execute(input_data, context=context)

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Conversational chain completed", user_id=user_id, elapsed_ms=elapsed_ms
        )

        return {
            "response": result.get("response", {}),
            "personality_mode": result.get("personality_mode", "normal"),
            "chain": result.get("chain", "conversational"),
            "model": result.get("model", "groq-llama-3.1-8b"),
            "latency_ms": elapsed_ms,
            "tokens_used": result.get("tokens_used", 0),
        }

    except Exception as e:
        logger.error("Conversational chain error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {str(e)}")


@router.post("/research")
async def run_research_chain(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    x_internal_auth: Optional[str] = Header(None),
):
    """
    Run research chain.
    Internal endpoint for research queries.

    Args:
        query: Research query
        context: Optional context
        user_id: User ID
        x_internal_auth: Internal authentication header

    Returns:
        Research results
    """
    await verify_internal_auth(x_internal_auth)

    try:
        start_time = time.time()

        user_id = user_id or settings.single_user_id
        logger.info("Running research chain", user_id=user_id, query=query[:100])

        # Get the research chain
        chain = ChainRegistry.get(ChainType.RESEARCH)
        if not chain:
            logger.error("Research chain not found in registry")
            raise HTTPException(status_code=500, detail="Chain not available")

        # Prepare input
        input_data = {"query": query, "user_id": user_id}

        # Execute the chain
        result = await chain.execute(input_data, context=context)

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info("Research chain completed", user_id=user_id, elapsed_ms=elapsed_ms)

        return {
            "response": result.get("response", {}),
            "sources": result.get("sources", []),
            "chain": result.get("chain", "research"),
            "model": result.get("model", "groq-llama-3.3-70b"),
            "latency_ms": elapsed_ms,
            "tokens_used": result.get("tokens_used", 0),
        }

    except Exception as e:
        logger.error("Research chain error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {str(e)}")


@router.post("/analysis")
async def run_analysis_chain(
    input_text: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    x_internal_auth: Optional[str] = Header(None),
):
    """
    Run analysis chain.
    Internal endpoint for data analysis.

    Args:
        input_text: Text to analyze
        context: Optional context
        user_id: User ID
        x_internal_auth: Internal authentication header

    Returns:
        Analysis results
    """
    await verify_internal_auth(x_internal_auth)

    try:
        start_time = time.time()

        user_id = user_id or settings.single_user_id
        logger.info("Running analysis chain", user_id=user_id)

        # Get the analysis chain
        chain = ChainRegistry.get(ChainType.ANALYSIS)
        if not chain:
            logger.error("Analysis chain not found in registry")
            raise HTTPException(status_code=500, detail="Chain not available")

        # Prepare input
        input_data = {"text": input_text, "user_id": user_id}

        # Execute the chain
        result = await chain.execute(input_data, context=context)

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info("Analysis chain completed", user_id=user_id, elapsed_ms=elapsed_ms)

        return {
            "response": result.get("response", {}),
            "chain": result.get("chain", "analysis"),
            "model": result.get("model", "groq-llama-3.3-70b"),
            "latency_ms": elapsed_ms,
            "tokens_used": result.get("tokens_used", 0),
        }

    except Exception as e:
        logger.error("Analysis chain error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {str(e)}")


@router.get("/available")
async def list_available_chains(x_internal_auth: Optional[str] = Header(None)):
    """
    List all available chains.
    Internal endpoint for discovery.
    """
    await verify_internal_auth(x_internal_auth)

    return {
        "available_chains": [
            {
                "name": "conversational",
                "endpoint": "/internal/chains/conversational",
                "method": "POST",
                "description": "Conversational chain for natural dialogue",
            },
            {
                "name": "research",
                "endpoint": "/internal/chains/research",
                "method": "POST",
                "description": "Research chain for information gathering",
            },
            {
                "name": "analysis",
                "endpoint": "/internal/chains/analysis",
                "method": "POST",
                "description": "Analysis chain for data analysis",
            },
            {
                "name": "personality-evolution",
                "endpoint": "/internal/chains/personality-evolution",
                "method": "POST",
                "description": "Personality evolution chain for weekly evolution",
            },
        ]
    }
