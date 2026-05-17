"""
Startup validation for production readiness.

Fails fast in production when dangerous development defaults or missing secrets
would make the backend unsafe to expose.
"""

from __future__ import annotations

import os

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("startup_validation")


def validate_production_config() -> None:
    """Validate critical settings. Raises RuntimeError only in production."""
    warnings: list[str] = []
    errors: list[str] = []

    if os.getenv("TILLU_PIN", "123456") == "123456":
        warnings.append("TILLU_PIN is using the default development PIN")
    if settings.secret_key in {"dev-secret-key", "tillu-dev-secret-key-change-in-prod"}:
        warnings.append("SECRET_KEY is using a development default")
    if not settings.internal_secret:
        warnings.append("INTERNAL_SECRET is not configured")
    if settings.enable_jwt_verification and not settings.secret_key:
        errors.append("ENABLE_JWT_VERIFICATION=true but SECRET_KEY is empty")
    if settings.os_bridge_enabled and not settings.os_daemon_key:
        errors.append("OS_BRIDGE_ENABLED=true but OS_DAEMON_KEY is missing")
    if settings.os_bridge_enabled and settings.os_daemon_url.startswith(
        "http://0.0.0.0"
    ):
        errors.append("OS_DAEMON_URL must not point to 0.0.0.0")
    if settings.is_production and not settings.supabase_url:
        errors.append("SUPABASE_URL is not configured")
    if settings.is_production and not settings.supabase_key:
        errors.append("SUPABASE_KEY is not configured")
    if settings.is_production and not settings.supabase_service_key:
        warnings.append(
            "SUPABASE_SERVICE_KEY is not configured; some server operations may fail"
        )

    for item in warnings:
        logger.warning("Production config warning", warning=item)

    if settings.is_production:
        errors.extend(warnings)

    if errors:
        for item in errors:
            logger.error("Production config error", error=item)
        raise RuntimeError("Invalid production configuration: " + "; ".join(errors))
