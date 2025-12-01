"""
Expert API routes
All expert endpoints with proper permissions
"""

from fastapi import APIRouter
from app.api.v1.expert import tasks, reviews, earnings, ratings

# Create expert router
expert_router = APIRouter(prefix="/expert", tags=["expert"])

# Include sub-routers
expert_router.include_router(tasks.router, prefix="/tasks", tags=["expert-tasks"])
expert_router.include_router(reviews.router, prefix="/reviews", tags=["expert-reviews"])
expert_router.include_router(earnings.router, prefix="/earnings", tags=["expert-earnings"])
expert_router.include_router(ratings.router, prefix="/ratings", tags=["expert-ratings"])

