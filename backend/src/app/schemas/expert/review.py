"""
Expert review schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ReviewSubmissionRequest(BaseModel):
    """Review submission request"""
    answer_id: UUID = Field(..., description="Answer ID to review")
    question_id: UUID = Field(..., description="Question ID")
    is_approved: bool = Field(..., description="Whether answer is approved")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")
    corrections: Optional[Dict[str, Any]] = Field(None, description="Corrections made")
    review_notes: Optional[str] = Field(None, description="Review notes")
    review_time_seconds: Optional[int] = Field(None, description="Time taken to review")


class ReviewSubmissionResponse(BaseModel):
    """Review submission response"""
    review_id: UUID
    answer_id: UUID
    question_id: UUID
    status: str
    is_approved: bool
    submitted_at: datetime
    message: str


class ReviewResponse(BaseModel):
    """Review response"""
    review_id: UUID
    answer_id: UUID
    question_id: UUID
    question_text: str
    answer_text: str
    is_approved: bool
    rejection_reason: Optional[str] = None
    corrections: Optional[Dict[str, Any]] = None
    review_notes: Optional[str] = None
    review_time_seconds: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ReviewListResponse(BaseModel):
    """Review list response"""
    reviews: List[ReviewResponse]
    total: int
    page: int
    page_size: int

