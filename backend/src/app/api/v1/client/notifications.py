"""
Client notification endpoints
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.notification_service import NotificationService
from app.schemas.client.notification import NotificationListResponse
from app.models.user import User

router = APIRouter()
notification_service = NotificationService()


@router.get("", response_model=NotificationListResponse, summary="Get notifications")
async def get_notifications(
    read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get notifications"""
    result = await notification_service.get_notifications(
        db, current_user.id, read, page, page_size
    )
    return NotificationListResponse(**result)


@router.post("/{notification_id}/read", summary="Mark notification as read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Mark notification as read"""
    result = await notification_service.mark_notification_read(
        db, notification_id, current_user.id
    )
    return result


@router.post("/read-all", summary="Mark all notifications as read")
async def mark_all_notifications_read(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Mark all notifications as read"""
    result = await notification_service.mark_all_notifications_read(db, current_user.id)
    return result

