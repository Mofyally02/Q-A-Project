"""
User management schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_banned: bool
    banned_at: Optional[datetime] = None
    last_login: Optional[str] = None
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserRoleUpdate(BaseModel):
    """Update user role request"""
    role: str = Field(..., description="New role: client, expert, admin_editor, super_admin")
    reason: Optional[str] = Field(None, description="Reason for role change")


class UserBanRequest(BaseModel):
    """Ban/unban user request"""
    banned: bool = Field(..., description="True to ban, False to unban")
    reason: Optional[str] = Field(None, description="Reason for ban/unban")


class UserPasswordReset(BaseModel):
    """Password reset request"""
    send_email: bool = Field(True, description="Send reset email to user")
    temporary_password: Optional[str] = Field(None, description="Custom temporary password")


class UserPasswordResetResponse(BaseModel):
    """Password reset response"""
    temporary_password: str
    expires_at: datetime


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_users: int
    active_users: int
    banned_users: int
    by_role: Dict[str, int]
    verified_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int

