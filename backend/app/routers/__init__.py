"""
API Routers
"""

from .gail import router as gail_router
from .health import router as health_router

__all__ = ["gail_router", "health_router"]