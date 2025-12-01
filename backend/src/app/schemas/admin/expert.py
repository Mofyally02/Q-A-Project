"""
Expert management schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ExpertResponse(BaseModel):
    """Expert response schema"""
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_suspended: bool
    total_questions_answered: int
    average_rating: Optional[float] = None
    last_active: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExpertListResponse(BaseModel):
    """Expert list response"""
    experts: List[ExpertResponse]
    total: int
    page: int
    page_size: int


class ExpertDetailResponse(BaseModel):
    """Expert detail response"""
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_suspended: bool
    total_questions_answered: int
    average_rating: Optional[float] = None
    total_earnings: float
    response_time_avg_hours: Optional[float] = None
    rejection_rate: Optional[float] = None
    on_time_delivery_rate: Optional[float] = None
    active_questions: int
    compliance_score: Optional[float] = None
    last_active: Optional[datetime] = None
    created_at: datetime


class ExpertPerformanceResponse(BaseModel):
    """Expert performance metrics"""
    expert_id: UUID
    period: str  # "today", "week", "month", "all_time"
    questions_answered: int
    average_rating: Optional[float] = None
    total_earnings: float
    response_time_avg_hours: Optional[float] = None
    rejection_rate: Optional[float] = None
    on_time_delivery_rate: Optional[float] = None
    compliance_score: Optional[float] = None


class ExpertLeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    expert_id: UUID
    expert_name: str
    questions_answered: int
    average_rating: Optional[float] = None
    total_earnings: float
    compliance_score: Optional[float] = None


class ExpertLeaderboardResponse(BaseModel):
    """Expert leaderboard response"""
    period: str
    leaderboard: List[ExpertLeaderboardEntry]
    updated_at: datetime


class ExpertStatsResponse(BaseModel):
    """Expert statistics response"""
    total_experts: int
    active_experts: int
    suspended_experts: int
    average_rating_all: Optional[float] = None
    total_questions_answered: int
    total_earnings: float
    top_performers: List[ExpertLeaderboardEntry]


class ExpertSuspendRequest(BaseModel):
    """Suspend expert request"""
    suspended: bool = Field(..., description="True to suspend, False to activate")
    reason: Optional[str] = Field(None, description="Reason for suspension")

