"""
Client dashboard service
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from app.crud.client import dashboard as dashboard_crud


class DashboardService:
    """Client dashboard service"""
    
    @staticmethod
    async def get_dashboard_data(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get dashboard data"""
        return await dashboard_crud.get_dashboard_data(db, user_id)

