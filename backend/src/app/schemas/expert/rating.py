"""
Expert rating schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class RatingResponse(BaseModel):
    """Rating response"""
    rating_id: UUID
    question_id: UUID
    question_text: str
    answer_text: str
    score: int  # 1-5
    comment: Optional[str] = None
    client_name: Optional[str] = None
    created_at: datetime


class RatingStatsResponse(BaseModel):
    """Rating statistics response"""
    expert_id: UUID
    average_rating: float
    total_ratings: int
    rating_distribution: Dict[int, int]  # {1: count, 2: count, ...}
    recent_ratings: List[RatingResponse]
    rating_trend: List[Dict[str, Any]]  # Time series data

