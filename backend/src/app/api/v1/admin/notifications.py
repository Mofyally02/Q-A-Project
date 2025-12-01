"""
Notification broadcast admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_admin_or_super
from app.db.session import get_db
from app.services.admin.notification_service import NotificationService
from app.schemas.admin.notification import (
    NotificationBroadcastRequest,
    NotificationBroadcastResponse,
    NotificationSegmentRequest,
    NotificationHistoryResponse,
    NotificationTemplateResponse,
    NotificationTemplateCreate
)
from app.models.user import User

router = APIRouter()
notification_service = NotificationService()


@router.post("/broadcast", response_model=NotificationBroadcastResponse, summary="Broadcast notification")
async def broadcast_notification(
    broadcast_request: NotificationBroadcastRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Broadcast notification to users"""
    result = await notification_service.broadcast_notification(
        db, broadcast_request.title, broadcast_request.message,
        broadcast_request.notification_type, current_admin.id,
        broadcast_request.target_roles, broadcast_request.target_status,
        broadcast_request.send_email, broadcast_request.send_sms,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return NotificationBroadcastResponse(**result)


@router.post("/broadcast/segment", response_model=NotificationBroadcastResponse, summary="Broadcast to segment")
async def broadcast_to_segment(
    segment_request: NotificationSegmentRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Broadcast notification to custom segment"""
    result = await notification_service.broadcast_to_segment(
        db, segment_request.title, segment_request.message,
        segment_request.notification_type, segment_request.segment_query,
        current_admin.id, segment_request.send_email, segment_request.send_sms,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return NotificationBroadcastResponse(**result)


@router.get("/history", response_model=NotificationHistoryResponse, summary="Get notification history")
async def get_notification_history(
    sent_by: Optional[UUID] = Query(None, description="Filter by sender"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get notification broadcast history"""
    result = await notification_service.get_notification_history(
        db, sent_by, page, page_size
    )
    return NotificationHistoryResponse(**result)


@router.get("/templates", response_model=list[NotificationTemplateResponse], summary="Get notification templates")
async def get_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get notification templates"""
    templates = await notification_service.get_templates(db, template_type)
    return [NotificationTemplateResponse(**t) for t in templates]


@router.post("/templates", summary="Create notification template")
async def create_template(
    template_request: NotificationTemplateCreate,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Create notification template"""
    result = await notification_service.create_template(
        db, template_request.name, template_request.subject,
        template_request.body, template_request.template_type,
        template_request.variables, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.put("/templates/{template_id}", summary="Update notification template")
async def update_template(
    template_id: UUID,
    template_request: NotificationTemplateCreate,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update notification template"""
    result = await notification_service.update_template(
        db, template_id, template_request.name,
        template_request.subject, template_request.body,
        template_request.variables, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.delete("/templates/{template_id}", summary="Delete notification template")
async def delete_template(
    template_id: UUID,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete notification template"""
    result = await notification_service.delete_template(
        db, template_id, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result

