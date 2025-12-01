"""
Expert review service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.expert import reviews as review_crud


class ReviewService:
    """Expert review service"""
    
    @staticmethod
    async def submit_review(
        db: asyncpg.Connection,
        expert_id: UUID,
        answer_id: UUID,
        question_id: UUID,
        is_approved: bool,
        rejection_reason: Optional[str] = None,
        corrections: Optional[Dict[str, Any]] = None,
        review_notes: Optional[str] = None,
        review_time_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Submit expert review"""
        result = await review_crud.submit_review(
            db, expert_id, answer_id, question_id, is_approved,
            rejection_reason, corrections, review_notes, review_time_seconds
        )
        
        return {
            "review_id": result["review_id"],
            "answer_id": result["answer_id"],
            "question_id": result["question_id"],
            "status": result["status"],
            "is_approved": result["is_approved"],
            "submitted_at": result.get("submitted_at"),
            "message": "Review submitted successfully"
        }
    
    @staticmethod
    async def get_reviews(
        db: asyncpg.Connection,
        expert_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get expert reviews"""
        return await review_crud.get_expert_reviews(db, expert_id, status, page, page_size)

