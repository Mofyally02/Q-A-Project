"""
Backup and recovery admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_super_admin
from app.db.session import get_db
from app.services.admin.backup_service import BackupService
from app.schemas.admin.backup import (
    BackupRequest,
    BackupResponse,
    BackupListResponse,
    RestoreRequest,
    RestoreResponse
)
from app.models.user import User

router = APIRouter()
backup_service = BackupService()


@router.post("/create", response_model=BackupResponse, summary="Create backup")
async def create_backup(
    backup_request: BackupRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Create backup (super_admin only)"""
    result = await backup_service.create_backup(
        db, backup_request.backup_type, current_admin.id,
        backup_request.include_files, backup_request.description,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return BackupResponse(**result)


@router.get("", response_model=BackupListResponse, summary="List backups")
async def get_backups(
    backup_type: Optional[str] = Query(None, description="Filter by backup type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get backups"""
    result = await backup_service.get_backups(
        db, backup_type, status, page, page_size
    )
    return BackupListResponse(**result)


@router.get("/{backup_id}", response_model=BackupResponse, summary="Get backup by ID")
async def get_backup(
    backup_id: UUID,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get backup by ID"""
    backup = await backup_service.get_backup_by_id(db, backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    return BackupResponse(**backup)


@router.delete("/{backup_id}", summary="Delete backup")
async def delete_backup(
    backup_id: UUID,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete backup (super_admin only)"""
    result = await backup_service.delete_backup(
        db, backup_id, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/restore", response_model=RestoreResponse, summary="Restore from backup")
async def restore_backup(
    restore_request: RestoreRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Restore from backup (super_admin only)"""
    if not restore_request.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")
    
    try:
        result = await backup_service.create_restore(
            db, restore_request.backup_id, restore_request.restore_type,
            current_admin.id,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        return RestoreResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/restore/{restore_id}", summary="Get restore status")
async def get_restore_status(
    restore_id: UUID,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get restore status"""
    status = await backup_service.get_restore_status(db, restore_id)
    if not status:
        raise HTTPException(status_code=404, detail="Restore not found")
    return status

