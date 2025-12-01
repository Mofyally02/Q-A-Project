"""
Override triggers admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID
from datetime import datetime
import asyncpg
from app.dependencies.admin import require_super_admin
from app.db.session import get_db
from app.services.admin.override_service import OverrideService
from app.schemas.admin.override import (
    OverrideResponse,
    AIBypassRequest,
    OriginalityPassRequest,
    ConfidenceOverrideRequest,
    HumanizationSkipRequest,
    ExpertBypassRequest
)
from app.models.user import User

router = APIRouter()
override_service = OverrideService()


@router.post("/ai-bypass/{question_id}", response_model=OverrideResponse, summary="Bypass AI content check")
async def bypass_ai_check(
    question_id: UUID,
    request_body: AIBypassRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Bypass AI content check (super_admin only)"""
    result = await override_service.bypass_ai_check(
        db, question_id, current_admin.id, request_body.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return OverrideResponse(
        success=result["success"],
        override_id=result["override_id"],
        action=result["action"],
        target_id=result["target_id"],
        reason=request_body.reason,
        overridden_at=datetime.utcnow(),
        overridden_by=current_admin.id
    )


@router.post("/originality-pass/{answer_id}", response_model=OverrideResponse, summary="Pass originality check")
async def pass_originality_check(
    answer_id: UUID,
    request_body: OriginalityPassRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Pass originality check override (super_admin only)"""
    result = await override_service.pass_originality_check(
        db, answer_id, current_admin.id, request_body.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return OverrideResponse(
        success=result["success"],
        override_id=result["override_id"],
        action=result["action"],
        target_id=result["target_id"],
        reason=request_body.reason,
        overridden_at=datetime.utcnow(),
        overridden_by=current_admin.id
    )


@router.post("/confidence-override/{question_id}", response_model=OverrideResponse, summary="Override confidence threshold")
async def override_confidence(
    question_id: UUID,
    request_body: ConfidenceOverrideRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Override confidence threshold (super_admin only)"""
    result = await override_service.override_confidence_threshold(
        db, question_id, request_body.min_confidence,
        current_admin.id, request_body.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return OverrideResponse(
        success=result["success"],
        override_id=result["override_id"],
        action=result["action"],
        target_id=result["target_id"],
        reason=request_body.reason,
        overridden_at=datetime.utcnow(),
        overridden_by=current_admin.id
    )


@router.post("/humanization-skip/{answer_id}", response_model=OverrideResponse, summary="Skip humanization")
async def skip_humanization(
    answer_id: UUID,
    request_body: HumanizationSkipRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Skip humanization step (super_admin only)"""
    result = await override_service.skip_humanization(
        db, answer_id, current_admin.id, request_body.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return OverrideResponse(
        success=result["success"],
        override_id=result["override_id"],
        action=result["action"],
        target_id=result["target_id"],
        reason=request_body.reason,
        overridden_at=datetime.utcnow(),
        overridden_by=current_admin.id
    )


@router.post("/expert-bypass/{answer_id}", response_model=OverrideResponse, summary="Bypass expert review")
async def bypass_expert_review(
    answer_id: UUID,
    request_body: ExpertBypassRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Bypass expert review (super_admin only)"""
    result = await override_service.bypass_expert_review(
        db, answer_id, current_admin.id, request_body.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return OverrideResponse(
        success=result["success"],
        override_id=result["override_id"],
        action=result["action"],
        target_id=result["target_id"],
        reason=request_body.reason,
        overridden_at=datetime.utcnow(),
        overridden_by=current_admin.id
    )

