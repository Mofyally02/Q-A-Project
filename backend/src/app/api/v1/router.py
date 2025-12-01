"""
Main API router for v1
Aggregates all v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, root
from app.api.v1.admin import admin_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(root.router, tags=["root"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Admin routes
api_router.include_router(admin_router)

# Client routes
from app.api.v1.client import client_router
api_router.include_router(client_router)

# Expert routes
from app.api.v1.expert import expert_router
api_router.include_router(expert_router)

# Auth routes
from app.api.v1 import auth
api_router.include_router(auth.router)

