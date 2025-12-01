"""
Revenue management admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from app.dependencies.admin import require_admin_or_super
from app.db.session import get_db
from app.services.admin.revenue_service import RevenueService
from app.schemas.admin.revenue import (
    RevenueDashboardResponse,
    TransactionListResponse,
    CreditsStatsResponse,
    CreditGrantRequest,
    CreditGrantResponse,
    CreditRevokeRequest
)
from app.models.user import User

router = APIRouter()
revenue_service = RevenueService()


@router.get("/dashboard", response_model=RevenueDashboardResponse, summary="Get revenue dashboard")
async def get_revenue_dashboard(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get revenue dashboard statistics"""
    result = await revenue_service.get_revenue_dashboard(db)
    return RevenueDashboardResponse(**result)


@router.get("/transactions", response_model=TransactionListResponse, summary="Get transactions")
async def get_transactions(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get transactions with filters"""
    result = await revenue_service.get_transactions(
        db, user_id, status, transaction_type,
        date_from, date_to, page, page_size
    )
    return TransactionListResponse(**result)


@router.post("/credits/grant", response_model=CreditGrantResponse, summary="Grant credits to user")
async def grant_credits(
    grant_request: CreditGrantRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Grant credits to user"""
    result = await revenue_service.grant_credits(
        db, grant_request.user_id, grant_request.credits,
        grant_request.reason, current_admin.id, grant_request.expires_at,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return CreditGrantResponse(**result)


@router.post("/credits/revoke", summary="Revoke credits from user")
async def revoke_credits(
    revoke_request: CreditRevokeRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Revoke credits from user"""
    try:
        result = await revenue_service.revoke_credits(
            db, revoke_request.user_id, revoke_request.credits,
            revoke_request.reason, current_admin.id, revoke_request.refund,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/credits/stats", response_model=CreditsStatsResponse, summary="Get credits statistics")
async def get_credits_stats(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get credits statistics"""
    result = await revenue_service.get_credits_stats(db)
    return CreditsStatsResponse(**result)

