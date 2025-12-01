"""
Expert management service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import experts as expert_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class ExpertService:
    """Expert management service"""
    
    @staticmethod
    async def get_experts(
        db: asyncpg.Connection,
        is_active: Optional[bool] = None,
        is_suspended: Optional[bool] = None,
        min_rating: Optional[float] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get experts with filters"""
        return await expert_crud.get_experts(
            db, is_active, is_suspended, min_rating, search, page, page_size
        )
    
    @staticmethod
    async def get_expert_by_id(
        db: asyncpg.Connection,
        expert_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get expert details"""
        return await expert_crud.get_expert_by_id(db, expert_id)
    
    @staticmethod
    async def suspend_expert(
        db: asyncpg.Connection,
        expert_id: UUID,
        suspended: bool,
        admin_id: UUID,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suspend or activate expert"""
        success = await expert_crud.suspend_expert(db, expert_id, suspended)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "suspend_expert" if suspended else "activate_expert",
                target_type="expert", target_id=expert_id,
                details={"reason": reason},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "expert_id": expert_id, "suspended": suspended}
    
    @staticmethod
    async def get_expert_performance(
        db: asyncpg.Connection,
        expert_id: UUID,
        period: str = "all_time"
    ) -> Dict[str, Any]:
        """Get expert performance metrics"""
        return await expert_crud.get_expert_performance(db, expert_id, period)
    
    @staticmethod
    async def get_expert_leaderboard(
        db: asyncpg.Connection,
        period: str = "all_time",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get expert leaderboard"""
        leaderboard = await expert_crud.get_expert_leaderboard(db, period, limit)
        return {
            "period": period,
            "leaderboard": leaderboard,
            "updated_at": None  # TODO: Add cache timestamp
        }
    
    @staticmethod
    async def get_expert_stats(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get expert statistics"""
        stats = await expert_crud.get_expert_stats(db)
        
        # Get top performers
        top_performers = await expert_crud.get_expert_leaderboard(db, "all_time", 10)
        stats["top_performers"] = top_performers
        
        return stats

