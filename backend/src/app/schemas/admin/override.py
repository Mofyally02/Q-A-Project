"""
Backend override trigger schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class OverrideRequest(BaseModel):
    """Override request base"""
    reason: str = Field(..., description="Reason for override")
    notify_admins: bool = Field(True, description="Notify other admins")


class OverrideResponse(BaseModel):
    """Override response"""
    success: bool
    override_id: UUID
    action: str
    target_id: UUID
    reason: str
    overridden_at: datetime
    overridden_by: UUID


class AIBypassRequest(OverrideRequest):
    """AI bypass override request"""
    pass


class OriginalityPassRequest(OverrideRequest):
    """Originality pass override request"""
    pass


class ConfidenceOverrideRequest(OverrideRequest):
    """Confidence override request"""
    min_confidence: Optional[float] = Field(None, description="Minimum confidence to accept")


class HumanizationSkipRequest(OverrideRequest):
    """Humanization skip override request"""
    pass


class ExpertBypassRequest(OverrideRequest):
    """Expert bypass override request"""
    pass

