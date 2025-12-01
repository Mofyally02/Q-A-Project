"""
Expert earnings schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class EarningsResponse(BaseModel):
    """Earnings response"""
    expert_id: UUID
    total_earnings: float
    earnings_this_month: float
    earnings_this_week: float
    earnings_today: float
    total_reviews: int
    reviews_this_month: int
    reviews_this_week: int
    reviews_today: int
    average_earnings_per_review: float
    pending_payout: float
    last_payout_at: Optional[datetime] = None
    earnings_breakdown: List[Dict[str, Any]]


class EarningsTransactionResponse(BaseModel):
    """Earnings transaction response"""
    transaction_id: UUID
    review_id: UUID
    question_id: UUID
    amount: float
    status: str  # pending, completed, paid
    created_at: datetime
    paid_at: Optional[datetime] = None

