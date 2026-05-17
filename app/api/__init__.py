"""
TILLU API Routes
"""

from .auth import router as auth_router
from .chains import router as chains_router
from .conversation import router as conversation_router
from .events import router as events_router
from .gateway import router as gateway_router
from .health import router as health_router
from .memory import router as memory_router
from .notifications import router as notifications_router
from .os_bridge import router as os_bridge_router
from .proactive import router as proactive_router

__all__ = [
    "gateway_router",
    "conversation_router",
    "memory_router",
    "health_router",
    "events_router",
    "chains_router",
    "auth_router",
    "proactive_router",
    "os_bridge_router",
    "notifications_router",
]
