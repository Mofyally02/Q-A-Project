"""
Expert earnings service
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from app.crud.expert import earnings as earnings_crud


class EarningsService:
    """Expert earnings service"""
    
    @staticmethod
    async def get_earnings(
        db: asyncpg.Connection,
        expert_id: UUID
    ) -> Dict[str, Any]:
        """Get expert earnings"""
        return await earnings_crud.get_expert_earnings(db, expert_id)

