"""
Client notification service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.client import notifications as notification_crud


class NotificationService:
    """Client notification service"""
    
    @staticmethod
    async def get_notifications(
        db: asyncpg.Connection,
        user_id: UUID,
        read: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get notifications"""
        return await notification_crud.get_notifications(db, user_id, read, page, page_size)
    
    @staticmethod
    async def mark_notification_read(
        db: asyncpg.Connection,
        notification_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Mark notification as read"""
        success = await notification_crud.mark_notification_read(db, notification_id, user_id)
        return {"success": success}
    
    @staticmethod
    async def mark_all_notifications_read(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Mark all notifications as read"""
        count = await notification_crud.mark_all_notifications_read(db, user_id)
        return {"success": True, "count": count}

