"""
System settings admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_super_admin, require_admin_or_super
from app.db.session import get_db
from app.crud.admin.settings import (
    get_system_settings,
    get_system_setting_by_key,
    upsert_system_setting
)
from app.crud.admin.admin_actions import log_admin_action
from app.schemas.admin.setting import (
    SystemSettingResponse,
    SystemSettingListResponse,
    SystemSettingUpdate,
    MaintenanceModeResponse,
    MaintenanceModeRequest
)
from app.models.user import User
from datetime import datetime

router = APIRouter()


@router.get("", response_model=SystemSettingListResponse)
async def list_settings(
    key: Optional[str] = Query(None, description="Get specific setting by key"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get system settings"""
    if key:
        setting = await get_system_setting_by_key(db, key)
        settings = [setting] if setting else []
    else:
        settings = await get_system_settings(db)
    
    return SystemSettingListResponse(settings=settings, total=len(settings))


@router.patch("", response_model=SystemSettingResponse)
async def update_setting(
    key: str,
    setting_update: SystemSettingUpdate,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update system setting (super_admin only)"""
    setting_id = await upsert_system_setting(
        db, key, setting_update.value,
        setting_update.description, current_admin.id
    )
    
    # Log action
    await log_admin_action(
        db, current_admin.id, "update_system_setting",
        target_type="system", target_id=setting_id,
        details={"key": key, "value": setting_update.value},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    setting = await get_system_setting_by_key(db, key)
    return SystemSettingResponse(**setting)


@router.get("/maintenance-mode", response_model=MaintenanceModeResponse)
async def get_maintenance_mode(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get maintenance mode status"""
    setting = await get_system_setting_by_key(db, "maintenance_mode")
    if not setting:
        return MaintenanceModeResponse(enabled=False)
    
    value = setting.get("value", {})
    return MaintenanceModeResponse(
        enabled=value.get("enabled", False),
        message=value.get("message"),
        updated_at=setting.get("updated_at"),
        updated_by=setting.get("updated_by_id")
    )


@router.post("/maintenance-mode", response_model=MaintenanceModeResponse)
async def toggle_maintenance_mode(
    maintenance_request: MaintenanceModeRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Toggle maintenance mode (super_admin only)"""
    setting_id = await upsert_system_setting(
        db, "maintenance_mode",
        {"enabled": maintenance_request.enabled, "message": maintenance_request.message},
        "Platform maintenance mode", current_admin.id
    )
    
    # Log action
    await log_admin_action(
        db, current_admin.id, "toggle_maintenance_mode",
        target_type="system", target_id=setting_id,
        details={"enabled": maintenance_request.enabled},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    setting = await get_system_setting_by_key(db, "maintenance_mode")
    value = setting.get("value", {})
    return MaintenanceModeResponse(
        enabled=value.get("enabled", False),
        message=value.get("message"),
        updated_at=setting.get("updated_at"),
        updated_by=setting.get("updated_by_id")
    )

