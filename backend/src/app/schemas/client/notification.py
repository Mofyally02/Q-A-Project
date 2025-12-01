"""
Client notification schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID
    title: str
    message: str
    notification_type: str  # info, success, warning, error
    read: bool
    created_at: datetime
    action_url: Optional[str] = None


class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int
    page: int
    page_size: int

