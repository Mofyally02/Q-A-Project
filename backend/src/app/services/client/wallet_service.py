"""
Client wallet service
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from app.crud.client import wallet as wallet_crud


class WalletService:
    """Client wallet service"""
    
    @staticmethod
    async def get_wallet_info(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get wallet information"""
        return await wallet_crud.get_wallet_info(db, user_id)
    
    @staticmethod
    async def initiate_topup(
        db: asyncpg.Connection,
        user_id: UUID,
        amount: float,
        payment_method: str = "credit_card"
    ) -> Dict[str, Any]:
        """Initiate topup"""
        return await wallet_crud.initiate_topup(db, user_id, amount, payment_method)

