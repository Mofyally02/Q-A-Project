"""
Revenue management service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from app.crud.admin import revenue as revenue_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class RevenueService:
    """Revenue management service"""
    
    @staticmethod
    async def get_revenue_dashboard(
        db: asyncpg.Connection
    ) -> Dict[str, Any]:
        """Get revenue dashboard statistics"""
        return await revenue_crud.get_revenue_dashboard(db)
    
    @staticmethod
    async def get_transactions(
        db: asyncpg.Connection,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        transaction_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get transactions with filters"""
        return await revenue_crud.get_transactions(
            db, user_id, status, transaction_type,
            date_from, date_to, page, page_size
        )
    
    @staticmethod
    async def grant_credits(
        db: asyncpg.Connection,
        user_id: UUID,
        credits: int,
        reason: str,
        granted_by: UUID,
        expires_at: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Grant credits to user"""
        result = await revenue_crud.grant_credits(
            db, user_id, credits, reason, granted_by, expires_at
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, granted_by, "grant_credits",
            target_type="user", target_id=user_id,
            details={
                "credits": credits,
                "reason": reason,
                "new_balance": result["new_balance"]
            },
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def revoke_credits(
        db: asyncpg.Connection,
        user_id: UUID,
        credits: int,
        reason: str,
        revoked_by: UUID,
        refund: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Revoke credits from user"""
        try:
            result = await revenue_crud.revoke_credits(
                db, user_id, credits, reason, revoked_by, refund
            )
            
            # Log admin action
            await action_crud.log_admin_action(
                db, revoked_by, "revoke_credits",
                target_type="user", target_id=user_id,
                details={
                    "credits": credits,
                    "reason": reason,
                    "refund": refund,
                    "new_balance": result["new_balance"]
                },
                ip_address=ip_address, user_agent=user_agent
            )
            
            return result
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    async def get_credits_stats(
        db: asyncpg.Connection
    ) -> Dict[str, Any]:
        """Get credits statistics"""
        return await revenue_crud.get_credits_stats(db)

