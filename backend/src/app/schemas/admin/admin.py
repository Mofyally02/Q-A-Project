"""
Admin management schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AdminInviteRequest(BaseModel):
    """Invite admin request"""
    email: EmailStr
    role: str = Field(..., description="admin_editor or super_admin")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    expires_in_hours: int = Field(24, description="Invitation expiration in hours")


class AdminInviteResponse(BaseModel):
    """Admin invite response"""
    invitation_id: UUID
    magic_link: str
    expires_at: datetime
    email: EmailStr


class AdminResponse(BaseModel):
    """Admin response schema"""
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    last_active: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminListResponse(BaseModel):
    """Admin list response"""
    admins: List[AdminResponse]
    total: int


class AdminSuspendRequest(BaseModel):
    """Suspend admin request"""
    suspended: bool = Field(..., description="True to suspend, False to activate")
    reason: Optional[str] = Field(None, description="Reason for suspension")

