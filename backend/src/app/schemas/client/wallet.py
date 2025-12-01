"""
Client wallet schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class WalletInfoResponse(BaseModel):
    """Wallet information response"""
    user_id: UUID
    credits_balance: int
    credits_used_total: int
    credits_purchased_total: int
    last_transaction_at: Optional[datetime] = None
    transaction_history: List[Dict[str, Any]]


class TopupRequest(BaseModel):
    """Topup request"""
    amount: float = Field(..., gt=0, description="Topup amount")
    payment_method: Optional[str] = Field("credit_card", description="Payment method")


class TopupResponse(BaseModel):
    """Topup response"""
    transaction_id: UUID
    amount: float
    credits_added: int
    new_balance: int
    payment_url: Optional[str] = None
    status: str

