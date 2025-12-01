"""
Compliance and audit admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from typing import Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from app.dependencies.admin import require_admin_or_super
from app.db.session import get_db
from app.services.admin.compliance_service import ComplianceService
from app.schemas.admin.compliance import (
    AuditLogResponse,
    AuditLogListResponse,
    ComplianceFlaggedResponse,
    ComplianceUserHistory,
    ComplianceStatsResponse,
    ComplianceFlagRequest
)
from app.models.user import User

router = APIRouter()
compliance_service = ComplianceService()


@router.get("/audit-logs", response_model=AuditLogListResponse, summary="Get audit logs")
async def get_audit_logs(
    admin_id: Optional[UUID] = Query(None, description="Filter by admin ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    target_id: Optional[UUID] = Query(None, description="Filter by target ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get audit logs with filters"""
    result = await compliance_service.get_audit_logs(
        db, admin_id, action_type, target_type, target_id, page, page_size
    )
    return AuditLogListResponse(**result)


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse, summary="Get audit log by ID")
async def get_audit_log(
    log_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get specific audit log"""
    log = await compliance_service.get_audit_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return AuditLogResponse(**log)


@router.get("/compliance/flagged", response_model=ComplianceFlaggedResponse, summary="Get flagged content")
async def get_flagged_content(
    reason: Optional[str] = Query(None, description="Filter by reason"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get flagged content (AI >10%, plagiarism, VPN, etc.)"""
    result = await compliance_service.get_flagged_content(
        db, reason, severity, resolved, page, page_size
    )
    return ComplianceFlaggedResponse(**result)


@router.get("/compliance/users/{user_id}", response_model=ComplianceUserHistory, summary="Get user compliance history")
async def get_user_compliance(
    user_id: UUID,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user compliance history"""
    history = await compliance_service.get_user_compliance_history(db, user_id)
    return ComplianceUserHistory(**history)


@router.post("/compliance/flag/{content_id}", summary="Manually flag content")
async def flag_content(
    content_id: UUID,
    flag_request: ComplianceFlagRequest,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Manually flag content"""
    result = await compliance_service.flag_content(
        db, content_id, flag_request.content_type,
        flag_request.reason, current_admin.id,
        flag_request.severity, flag_request.details,
        None,  # user_id - could be extracted from content
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.get("/compliance/stats", response_model=ComplianceStatsResponse, summary="Get compliance statistics")
async def get_compliance_stats(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get compliance statistics"""
    stats = await compliance_service.get_compliance_stats(db)
    return ComplianceStatsResponse(**stats)


@router.post("/audit-logs/export", summary="Export audit logs")
async def export_audit_logs(
    format: str = Query("json", description="Export format: json or csv"),
    admin_id: Optional[UUID] = Query(None, description="Filter by admin ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Export audit logs"""
    result = await compliance_service.export_audit_logs(
        db, format, admin_id, action_type, date_from, date_to
    )
    
    if format == "csv":
        return Response(
            content=result["data"],
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"'
            }
        )
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=result["data"],
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"'
            }
        )

