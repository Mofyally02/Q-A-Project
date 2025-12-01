"""
Client wallet endpoints
"""

from fastapi import APIRouter, Depends
import asyncpg
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.wallet_service import WalletService
from app.schemas.client.wallet import WalletInfoResponse, TopupRequest, TopupResponse
from app.models.user import User

router = APIRouter()
wallet_service = WalletService()


@router.get("", response_model=WalletInfoResponse, summary="Get wallet info")
async def get_wallet_info(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get wallet information"""
    info = await wallet_service.get_wallet_info(db, current_user.id)
    return WalletInfoResponse(**info)


@router.post("/topup", response_model=TopupResponse, summary="Initiate topup")
async def initiate_topup(
    topup_request: TopupRequest,
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Initiate topup"""
    result = await wallet_service.initiate_topup(
        db, current_user.id, topup_request.amount, topup_request.payment_method
    )
    return TopupResponse(**result)

