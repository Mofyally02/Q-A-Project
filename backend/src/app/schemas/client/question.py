"""
Client question schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class QuestionSubmissionRequest(BaseModel):
    """Question submission request"""
    question_text: str = Field(..., min_length=1, max_length=5000, description="Question text")
    subject: Optional[str] = Field(None, max_length=100, description="Subject/category")
    priority: Optional[str] = Field("normal", description="Priority: low, normal, high, urgent")
    image_urls: Optional[List[str]] = Field(None, description="Image URLs if any")


class QuestionSubmissionResponse(BaseModel):
    """Question submission response"""
    question_id: UUID
    status: str
    estimated_completion: Optional[datetime] = None
    credits_charged: int
    message: str


class QuestionStatusResponse(BaseModel):
    """Question status response"""
    question_id: UUID
    status: str  # pending, processing, reviewed, delivered, cancelled
    question_text: str
    answer_text: Optional[str] = None
    expert_id: Optional[UUID] = None
    expert_name: Optional[str] = None
    submitted_at: datetime
    delivered_at: Optional[datetime] = None
    rating: Optional[int] = None
    credits_used: int


class QuestionHistoryResponse(BaseModel):
    """Question history response"""
    questions: List[QuestionStatusResponse]
    total: int
    page: int
    page_size: int


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    message_id: UUID
    question_id: UUID
    sender_type: str  # client, expert, system
    message_text: str
    created_at: datetime
    attachments: Optional[List[str]] = None


class ChatThreadResponse(BaseModel):
    """Chat thread response"""
    question_id: UUID
    question_text: str
    status: str
    messages: List[ChatMessageResponse]
    expert_id: Optional[UUID] = None
    expert_name: Optional[str] = None

