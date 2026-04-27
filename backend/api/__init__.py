from .documents import router as documents_router
from .chat import router as chat_router
from .memory import router as memory_router
from .search import router as search_router
from .settings import router as settings_router

__all__ = ["documents_router", "chat_router", "memory_router", "search_router", "settings_router"]