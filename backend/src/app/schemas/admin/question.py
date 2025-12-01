"""
Question oversight schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class QuestionListResponse(BaseModel):
    """Question list response"""
    questions: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int


class QuestionDetailResponse(BaseModel):
    """Question detail response with full pipeline"""
    id: UUID
    question_text: str
    subject: str
    status: str
    client_id: UUID
    expert_id: Optional[UUID] = None
    ai_response: Optional[Dict[str, Any]] = None
    humanized_response: Optional[Dict[str, Any]] = None
    originality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    final_answer: Optional[str] = None
    pipeline_stage: str
    created_at: datetime
    updated_at: datetime
    full_history: List[Dict[str, Any]] = Field(default_factory=list)


class QuestionReassignRequest(BaseModel):
    """Reassign question to different expert"""
    expert_id: UUID = Field(..., description="New expert ID")
    reason: Optional[str] = Field(None, description="Reason for reassignment")


class QuestionForceDeliverRequest(BaseModel):
    """Force deliver question request"""
    answer: Optional[str] = Field(None, description="Optional admin-provided answer")
    reason: str = Field(..., description="Reason for force delivery")


class QuestionRejectRequest(BaseModel):
    """Reject and correct question request"""
    correction: str = Field(..., description="Admin correction/answer")
    reason: str = Field(..., description="Reason for rejection")


class QuestionPlagiarismFlag(BaseModel):
    """Flag question as plagiarism"""
    fine_amount: Optional[float] = Field(None, description="Fine amount in credits")
    reason: str = Field(..., description="Reason for flagging")
    notify_client: bool = Field(True, description="Notify client of violation")


class QuestionEscalateRequest(BaseModel):
    """Escalate question to super admin"""
    reason: str = Field(..., description="Reason for escalation")
    priority: str = Field("normal", description="Priority: low, normal, high, urgent")


class QuestionStatsResponse(BaseModel):
    """Question statistics response"""
    total_questions: int
    by_status: Dict[str, int]
    by_subject: Dict[str, int]
    pending_review: int
    in_progress: int
    delivered_today: int
    average_response_time_hours: float
    rejection_rate: float

