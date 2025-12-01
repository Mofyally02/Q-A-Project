"""
Client history alias endpoint
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import asyncpg
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.question_service import QuestionService
from app.schemas.client.question import QuestionHistoryResponse
from app.models.user import User

router = APIRouter()
question_service = QuestionService()


@router.get("/history", response_model=QuestionHistoryResponse, summary="Get question history")
async def get_history(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question history (alias for /client/questions/history/list)"""
    result = await question_service.get_question_history(
        db, current_user.id, status, page, page_size
    )
    return QuestionHistoryResponse(**result)

