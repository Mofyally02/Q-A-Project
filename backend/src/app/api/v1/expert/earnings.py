"""
Expert earnings endpoints
"""

from fastapi import APIRouter, Depends
import asyncpg
from app.dependencies.expert import require_expert
from app.db.session import get_db
from app.services.expert.earnings_service import EarningsService
from app.schemas.expert.earnings import EarningsResponse
from app.models.user import User

router = APIRouter()
earnings_service = EarningsService()


@router.get("", response_model=EarningsResponse, summary="Get expert earnings")
async def get_earnings(
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert earnings"""
    result = await earnings_service.get_earnings(db, current_user.id)
    return EarningsResponse(**result)

