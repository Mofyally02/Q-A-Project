"""
Question oversight admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from app.dependencies.admin import require_admin_or_super, require_super_admin
from app.db.session import get_db
from app.services.admin.question_service import QuestionService
from app.schemas.admin.question import (
    QuestionListResponse,
    QuestionDetailResponse,
    QuestionReassignRequest,
    QuestionForceDeliverRequest,
    QuestionRejectRequest,
    QuestionPlagiarismFlag,
    QuestionEscalateRequest,
    QuestionStatsResponse
)
from app.models.user import User

router = APIRouter()
question_service = QuestionService()


@router.get("", response_model=QuestionListResponse)
async def list_questions(
    status: Optional[str] = Query(None, description="Filter by status"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    expert_id: Optional[UUID] = Query(None, description="Filter by expert ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    search: Optional[str] = Query(None, description="Search in question text"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """List all questions with filters"""
    result = await question_service.get_questions(
        db, status, subject, client_id, expert_id,
        date_from, date_to, search, page, page_size
    )
    return QuestionListResponse(**result)


@router.get("/{question_id}", response_model=QuestionDetailResponse)
async def get_question(
    question_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question details with full pipeline"""
    question = await question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionDetailResponse(**question)


@router.post("/{question_id}/reassign-expert")
async def reassign_expert(
    question_id: UUID,
    reassign_request: QuestionReassignRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Reassign question to different expert"""
    result = await question_service.reassign_expert(
        db, question_id, reassign_request.expert_id, current_admin.id,
        reassign_request.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{question_id}/force-deliver")
async def force_deliver(
    question_id: UUID,
    deliver_request: QuestionForceDeliverRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Force deliver question (bypass review)"""
    result = await question_service.force_deliver(
        db, question_id, current_admin.id,
        deliver_request.answer, deliver_request.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{question_id}/reject-and-correct")
async def reject_and_correct(
    question_id: UUID,
    reject_request: QuestionRejectRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Reject question and upload admin correction"""
    result = await question_service.reject_and_correct(
        db, question_id, reject_request.correction, current_admin.id,
        reject_request.reason,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{question_id}/flag-plagiarism")
async def flag_plagiarism(
    question_id: UUID,
    flag_request: QuestionPlagiarismFlag,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Flag question as plagiarism"""
    result = await question_service.flag_plagiarism(
        db, question_id, current_admin.id,
        flag_request.fine_amount, flag_request.reason, flag_request.notify_client,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{question_id}/escalate")
async def escalate_question(
    question_id: UUID,
    escalate_request: QuestionEscalateRequest,
    request: Request,
    current_admin: User = Depends(require_super_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Escalate question to super admin (super_admin only)"""
    result = await question_service.escalate(
        db, question_id, current_admin.id,
        escalate_request.reason, escalate_request.priority,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.get("/stats", response_model=QuestionStatsResponse)
async def get_question_stats(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question statistics"""
    stats = await question_service.get_question_stats(db)
    return QuestionStatsResponse(**stats)

