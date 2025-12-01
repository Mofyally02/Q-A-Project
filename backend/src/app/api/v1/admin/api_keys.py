"""
API Key management admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_super_admin, require_admin_or_super
from app.db.session import get_db
from app.services.admin.api_key_service import APIKeyService
from app.schemas.admin.api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyListResponse,
    APIKeyTestResponse
)
from app.models.user import User

router = APIRouter()
api_key_service = APIKeyService()


@router.get("", response_model=APIKeyListResponse)
async def list_api_keys(
    key_type: Optional[str] = Query(None, description="Filter by key type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """List all API keys"""
    result = await api_key_service.get_api_keys(db, key_type, is_active)
    return APIKeyListResponse(**result)


@router.post("", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Create new API key (super_admin only)"""
    result = await api_key_service.create_api_key(
        db, api_key_data.name, api_key_data.key_type,
        api_key_data.api_key, current_admin.id,
        api_key_data.is_active,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    
    # Get created key
    from app.crud.admin.api_keys import get_api_key_by_id
    key = await get_api_key_by_id(db, result["id"])
    return APIKeyResponse(**key)


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: UUID,
    api_key_update: APIKeyUpdate,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update API key (super_admin only)"""
    result = await api_key_service.update_api_key(
        db, key_id, current_admin.id,
        api_key_update.name,
        api_key_update.api_key,
        api_key_update.is_active,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Get updated key
    from app.crud.admin.api_keys import get_api_key_by_id
    key = await get_api_key_by_id(db, key_id)
    return APIKeyResponse(**key)


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: UUID,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete API key (super_admin only)"""
    result = await api_key_service.delete_api_key(
        db, key_id, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {"success": True, "message": "API key deleted"}


@router.post("/{key_id}/test", response_model=APIKeyTestResponse)
async def test_api_key(
    key_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Test API key connection"""
    result = await api_key_service.test_api_key(db, key_id)
    return APIKeyTestResponse(**result)

