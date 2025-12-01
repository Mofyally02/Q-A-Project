"""
Client dashboard schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics"""
    total_credits: int
    credits_used: int
    credits_remaining: int
    total_questions: int
    pending_questions: int
    answered_questions: int
    average_rating: Optional[float] = None


class RecentAnswerResponse(BaseModel):
    """Recent answer response"""
    question_id: UUID
    question_text: str
    answer_text: str
    expert_name: Optional[str] = None
    delivered_at: datetime
    rating: Optional[int] = None


class LiveQuestionResponse(BaseModel):
    """Live question response"""
    question_id: UUID
    question_text: str
    status: str
    submitted_at: datetime
    estimated_completion: Optional[datetime] = None


class DashboardResponse(BaseModel):
    """Client dashboard response"""
    stats: DashboardStatsResponse
    recent_answers: List[RecentAnswerResponse]
    live_questions: List[LiveQuestionResponse]
    recommended_actions: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]

