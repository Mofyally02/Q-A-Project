"""
Expert management admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_admin_or_super, require_super_admin
from app.db.session import get_db
from app.services.admin.expert_service import ExpertService
from app.schemas.admin.expert import (
    ExpertListResponse,
    ExpertDetailResponse,
    ExpertPerformanceResponse,
    ExpertLeaderboardResponse,
    ExpertStatsResponse,
    ExpertSuspendRequest
)
from app.models.user import User

router = APIRouter()
expert_service = ExpertService()


@router.get("", response_model=ExpertListResponse)
async def list_experts(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_suspended: Optional[bool] = Query(None, description="Filter by suspended status"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    search: Optional[str] = Query(None, description="Search by email/name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """List all experts with filters"""
    result = await expert_service.get_experts(
        db, is_active, is_suspended, min_rating, search, page, page_size
    )
    return ExpertListResponse(**result)


@router.get("/{expert_id}", response_model=ExpertDetailResponse)
async def get_expert(
    expert_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert details"""
    expert = await expert_service.get_expert_by_id(db, expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return ExpertDetailResponse(**expert)


@router.get("/stats", response_model=ExpertStatsResponse)
async def get_expert_stats(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert statistics"""
    stats = await expert_service.get_expert_stats(db)
    return ExpertStatsResponse(**stats)


@router.get("/{expert_id}/performance", response_model=ExpertPerformanceResponse)
async def get_expert_performance(
    expert_id: UUID,
    period: str = Query("all_time", description="Period: today, week, month, all_time"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert performance metrics"""
    performance = await expert_service.get_expert_performance(db, expert_id, period)
    return ExpertPerformanceResponse(expert_id=expert_id, period=period, **performance)


@router.post("/{expert_id}/suspend")
async def suspend_expert(
    expert_id: UUID,
    suspend_request: ExpertSuspendRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Suspend expert (super_admin only)"""
    result = await expert_service.suspend_expert(
        db, expert_id, suspend_request.suspended, current_admin.id,
        suspend_request.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{expert_id}/activate")
async def activate_expert(
    expert_id: UUID,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Activate expert"""
    result = await expert_service.suspend_expert(
        db, expert_id, False, current_admin.id,
        "Admin activation",
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.get("/{expert_id}/reviews")
async def get_expert_reviews(
    expert_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert review history"""
    # TODO: Implement review history
    reviews = await db.fetch("""
        SELECT r.*, q.question_text, u.email as client_email
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        JOIN users u ON q.client_id = u.id
        WHERE q.expert_id = $1
        ORDER BY r.created_at DESC
        LIMIT $2 OFFSET $3
    """, expert_id, page_size, (page - 1) * page_size)
    
    return {"reviews": [dict(r) for r in reviews]}


@router.get("/leaderboard", response_model=ExpertLeaderboardResponse)
async def get_expert_leaderboard(
    period: str = Query("all_time", description="Period: week, month, all_time"),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert leaderboard"""
    result = await expert_service.get_expert_leaderboard(db, period, limit)
    return ExpertLeaderboardResponse(**result)

