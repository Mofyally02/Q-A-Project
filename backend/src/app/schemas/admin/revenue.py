"""
Revenue and financial schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class RevenueDashboardResponse(BaseModel):
    """Revenue dashboard response"""
    total_revenue: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    revenue_this_year: float
    credits_sold: int
    credits_sold_today: int
    credits_sold_this_week: int
    credits_sold_this_month: int
    average_transaction_value: float
    total_transactions: int
    refund_rate: float
    top_spending_users: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]  # Daily/weekly trend


class CreditsStatsResponse(BaseModel):
    """Credits statistics response"""
    total_credits_sold: int
    credits_by_package: Dict[str, int]
    total_revenue_from_credits: float
    average_credits_per_user: float
    top_packages: List[Dict[str, Any]]


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: UUID
    user_id: UUID
    user_email: Optional[str] = None
    transaction_type: str  # "purchase", "grant", "revoke", "refund"
    amount: float
    credits: int
    status: str  # "completed", "pending", "failed", "refunded"
    payment_method: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list response"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_revenue: float


class CreditGrantRequest(BaseModel):
    """Grant credits request"""
    user_id: UUID = Field(..., description="User to grant credits to")
    credits: int = Field(..., gt=0, description="Number of credits to grant")
    reason: str = Field(..., description="Reason for granting credits")
    expires_at: Optional[datetime] = Field(None, description="Credit expiration date")


class CreditRevokeRequest(BaseModel):
    """Revoke credits request"""
    user_id: UUID = Field(..., description="User to revoke credits from")
    credits: int = Field(..., gt=0, description="Number of credits to revoke")
    reason: str = Field(..., description="Reason for revoking credits")
    refund: bool = Field(False, description="Whether to refund payment")


class CreditGrantResponse(BaseModel):
    """Credit grant response"""
    user_id: UUID
    credits_granted: int
    new_balance: int
    granted_at: datetime
    expires_at: Optional[datetime] = None

