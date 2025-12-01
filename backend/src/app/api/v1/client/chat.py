"""
Client chat alias endpoint
"""

from fastapi import APIRouter, Depends, HTTPException
import asyncpg
from uuid import UUID
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.question_service import QuestionService
from app.schemas.client.question import ChatThreadResponse
from app.models.user import User

router = APIRouter()
question_service = QuestionService()


@router.get("/{question_id}", response_model=ChatThreadResponse, summary="Get chat thread")
async def get_chat(
    question_id: UUID,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get chat thread for question (alias for /client/questions/chat/{id})"""
    thread = await question_service.get_chat_thread(db, question_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Question not found")
    return ChatThreadResponse(**thread)

