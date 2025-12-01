"""
Client settings endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
import asyncpg
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.profile_service import ProfileService
from app.schemas.client.profile import ProfileResponse, ProfileUpdateRequest
from app.models.user import User

router = APIRouter()
profile_service = ProfileService()


@router.get("/profile", response_model=ProfileResponse, summary="Get user profile")
async def get_profile(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user profile"""
    profile = await profile_service.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(**profile)


@router.put("/profile", response_model=ProfileResponse, summary="Update user profile")
async def update_profile(
    profile_request: ProfileUpdateRequest,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update user profile"""
    try:
        result = await profile_service.update_profile(
            db, current_user.id,
            profile_request.first_name,
            profile_request.last_name,
            profile_request.phone,
            profile_request.avatar_url,
            profile_request.bio,
            profile_request.preferences
        )
        return ProfileResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

