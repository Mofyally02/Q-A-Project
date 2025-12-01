"""
Admin management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_super_admin, require_admin_or_super
from app.db.session import get_db
from app.services.admin.admin_service import AdminService
from app.schemas.admin.admin import (
    AdminInviteRequest,
    AdminInviteResponse,
    AdminResponse,
    AdminListResponse,
    AdminSuspendRequest
)
from app.models.user import User

router = APIRouter()
admin_service = AdminService()


@router.get("", response_model=AdminListResponse, summary="List all admins")
async def get_admins(
    role: Optional[str] = Query(None, description="Filter by role (super_admin or admin_editor)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get all admins with filters"""
    result = await admin_service.get_admins(db, role, is_active, page, page_size)
    return AdminListResponse(**result)


@router.post("/invite", response_model=AdminInviteResponse, summary="Invite new admin")
async def invite_admin(
    invite_request: AdminInviteRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Invite new admin (super_admin only)"""
    try:
        result = await admin_service.invite_admin(
            db, invite_request.email, invite_request.role,
            current_admin.id, invite_request.expires_in_hours,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        return AdminInviteResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{admin_id}/suspend", summary="Suspend or activate admin")
async def suspend_admin(
    admin_id: UUID,
    suspend_request: AdminSuspendRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Suspend or activate admin (super_admin only)"""
    try:
        result = await admin_service.suspend_admin(
            db, admin_id, suspend_request.suspended,
            suspend_request.reason, current_admin.id,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{admin_id}", summary="Revoke admin access")
async def revoke_admin(
    admin_id: UUID,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Revoke admin access - demote to client (super_admin only)"""
    try:
        result = await admin_service.revoke_admin_access(
            db, admin_id, current_admin.id,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{admin_id}", response_model=AdminResponse, summary="Get admin by ID")
async def get_admin(
    admin_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get admin details by ID"""
    admin = await admin_service.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return AdminResponse(**admin)

