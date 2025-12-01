"""
Expert review endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.expert import require_expert
from app.db.session import get_db
from app.services.expert.review_service import ReviewService
from app.schemas.expert.review import (
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
    ReviewListResponse
)
from app.models.user import User

router = APIRouter()
review_service = ReviewService()


@router.post("/submit", response_model=ReviewSubmissionResponse, summary="Submit review")
async def submit_review(
    review_request: ReviewSubmissionRequest,
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit expert review"""
    from datetime import datetime
    
    result = await review_service.submit_review(
        db, current_user.id,
        review_request.answer_id,
        review_request.question_id,
        review_request.is_approved,
        review_request.rejection_reason,
        review_request.corrections,
        review_request.review_notes,
        review_request.review_time_seconds
    )
    
    return ReviewSubmissionResponse(
        review_id=result["review_id"],
        answer_id=result["answer_id"],
        question_id=result["question_id"],
        status=result["status"],
        is_approved=result["is_approved"],
        submitted_at=datetime.utcnow(),
        message=result["message"]
    )


@router.get("", response_model=ReviewListResponse, summary="Get expert reviews")
async def get_reviews(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert reviews"""
    result = await review_service.get_reviews(
        db, current_user.id, status, page, page_size
    )
    return ReviewListResponse(**result)

