"""
Client question endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import Optional, List
import asyncpg
from uuid import UUID
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.question_service import QuestionService
from app.schemas.client.question import (
    QuestionSubmissionRequest,
    QuestionSubmissionResponse,
    QuestionStatusResponse,
    QuestionHistoryResponse,
    ChatThreadResponse
)
from app.models.user import User

router = APIRouter()
question_service = QuestionService()


@router.post("/ask", response_model=QuestionSubmissionResponse, summary="Submit question")
async def submit_question(
    question_text: str = Form(...),
    subject: Optional[str] = Form(None),
    priority: Optional[str] = Form("normal"),
    images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit a new question"""
    # TODO: Handle image uploads
    image_urls = []
    if images:
        # Process and upload images
        # For now, just collect filenames
        image_urls = [img.filename for img in images if img.filename]
    
    try:
        result = await question_service.submit_question(
            db, current_user.id, question_text, subject, priority, image_urls
        )
        return QuestionSubmissionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{question_id}", response_model=QuestionStatusResponse, summary="Get question status")
async def get_question_status(
    question_id: UUID,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question status"""
    question = await question_service.get_question_status(db, question_id, current_user.id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionStatusResponse(**question)


@router.get("/history/list", response_model=QuestionHistoryResponse, summary="Get question history")
@router.get("/history", response_model=QuestionHistoryResponse, summary="Get question history (alias)")
async def get_question_history(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question history"""
    result = await question_service.get_question_history(
        db, current_user.id, status, page, page_size
    )
    return QuestionHistoryResponse(**result)


@router.get("/chat/{question_id}", response_model=ChatThreadResponse, summary="Get chat thread")
async def get_chat_thread(
    question_id: UUID,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get chat thread for question"""
    thread = await question_service.get_chat_thread(db, question_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Question not found")
    return ChatThreadResponse(**thread)

