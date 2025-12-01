"""
Client profile service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.client import profile as profile_crud


class ProfileService:
    """Client profile service"""
    
    @staticmethod
    async def get_profile(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        return await profile_crud.get_user_profile(db, user_id)
    
    @staticmethod
    async def update_profile(
        db: asyncpg.Connection,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user profile"""
        return await profile_crud.update_user_profile(
            db, user_id, first_name, last_name, phone, avatar_url, bio, preferences
        )

