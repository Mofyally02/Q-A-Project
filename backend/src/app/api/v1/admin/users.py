"""
User management admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import (
    require_admin_or_super,
    get_current_admin,
    log_admin_action
)
from app.db.session import get_db
from app.services.admin.user_service import UserService
from app.schemas.admin.user import (
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
    UserBanRequest,
    UserPasswordReset,
    UserPasswordResetResponse,
    UserStatsResponse
)
from app.models.user import User

router = APIRouter()
user_service = UserService()


@router.get("", response_model=UserListResponse)
async def list_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    is_banned: Optional[bool] = Query(None, description="Filter by ban status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by email/name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """List all users with filters"""
    result = await user_service.get_users(
        db, role, is_banned, is_active, search, page, page_size
    )
    return UserListResponse(**result)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user details"""
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@router.post("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_update: UserRoleUpdate,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update user role (super_admin only for role changes to admin roles)"""
    # Check if trying to change to admin role
    if role_update.role in ["admin_editor", "super_admin"]:
        if not current_admin.is_super_admin():
            raise HTTPException(
                status_code=403,
                detail="Only super admin can assign admin roles"
            )
    
    result = await user_service.update_user_role(
        db, user_id, role_update.role, current_admin.id,
        role_update.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{user_id}/ban")
async def ban_user(
    user_id: UUID,
    ban_request: UserBanRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Ban or unban user"""
    result = await user_service.ban_user(
        db, user_id, ban_request.banned, current_admin.id,
        ban_request.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{user_id}/reset-password", response_model=UserPasswordResetResponse)
async def reset_password(
    user_id: UUID,
    reset_request: UserPasswordReset,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Reset user password"""
    result = await user_service.reset_password(
        db, user_id, current_admin.id,
        reset_request.send_email,
        reset_request.temporary_password,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return UserPasswordResetResponse(
        temporary_password=result["temporary_password"],
        expires_at=None  # TODO: Implement expiration
    )


@router.post("/{user_id}/promote-to-expert")
async def promote_to_expert(
    user_id: UUID,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Promote user to expert"""
    result = await user_service.promote_to_expert(
        db, user_id, current_admin.id,
        None,  # specialization
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user statistics"""
    stats = await user_service.get_user_stats(db)
    return UserStatsResponse(**stats)

