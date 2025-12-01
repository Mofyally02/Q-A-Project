"""
Expert rating service
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from app.crud.expert import ratings as rating_crud


class RatingService:
    """Expert rating service"""
    
    @staticmethod
    async def get_ratings(
        db: asyncpg.Connection,
        expert_id: UUID,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get expert ratings"""
        return await rating_crud.get_expert_ratings(db, expert_id, page, page_size)
    
    @staticmethod
    async def get_rating_stats(
        db: asyncpg.Connection,
        expert_id: UUID
    ) -> Dict[str, Any]:
        """Get expert rating statistics"""
        return await rating_crud.get_expert_rating_stats(db, expert_id)

