"""
Notification broadcast schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class NotificationBroadcastRequest(BaseModel):
    """Broadcast notification request"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    notification_type: str = Field("info", description="info, warning, success, error")
    target_roles: Optional[List[str]] = Field(None, description="Filter by roles")
    target_status: Optional[List[str]] = Field(None, description="Filter by status")
    send_email: bool = Field(False, description="Also send email")
    send_sms: bool = Field(False, description="Also send SMS")


class NotificationSegmentRequest(BaseModel):
    """Broadcast to segment request"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    notification_type: str = Field("info")
    segment_query: Dict[str, Any] = Field(..., description="Custom segment query")
    send_email: bool = Field(False)
    send_sms: bool = Field(False)


class NotificationTemplateResponse(BaseModel):
    """Notification template response"""
    id: UUID
    name: str
    subject: Optional[str] = None
    body: str
    template_type: str
    variables: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationTemplateCreate(BaseModel):
    """Create notification template"""
    name: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    template_type: str = Field(..., description="email, sms, push, in_app")
    variables: Optional[Dict[str, Any]] = None


class NotificationHistoryEntry(BaseModel):
    """Broadcast history entry"""
    id: UUID
    title: str
    message: str
    notification_type: str
    target_count: int
    sent_count: int
    failed_count: int
    sent_by: UUID
    sent_at: datetime


class NotificationHistoryResponse(BaseModel):
    """Broadcast history response"""
    broadcasts: List[NotificationHistoryEntry]
    total: int
    page: int
    page_size: int


class NotificationBroadcastResponse(BaseModel):
    """Broadcast response"""
    broadcast_id: UUID
    target_count: int
    queued_at: datetime
    estimated_completion: datetime

