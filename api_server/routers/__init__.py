"""
Router package for API endpoints
"""

from api_server.routers.auth import router as auth_router

__all__ = ['auth_router']