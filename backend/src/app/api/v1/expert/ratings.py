"""
Expert rating endpoints
"""

from fastapi import APIRouter, Depends, Query
import asyncpg
from app.dependencies.expert import require_expert
from app.db.session import get_db
from app.services.expert.rating_service import RatingService
from app.schemas.expert.rating import RatingStatsResponse
from app.models.user import User

router = APIRouter()
rating_service = RatingService()


@router.get("", response_model=RatingStatsResponse, summary="Get expert ratings")
async def get_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert ratings and statistics"""
    result = await rating_service.get_rating_stats(db, current_user.id)
    return RatingStatsResponse(**result)

