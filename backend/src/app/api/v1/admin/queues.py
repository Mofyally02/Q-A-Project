"""
Queue control admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional, List
import asyncpg
from uuid import UUID
from app.dependencies.admin import require_admin_or_super
from app.db.session import get_db
from app.services.admin.queue_service import QueueService
from app.models.user import User

router = APIRouter()
queue_service = QueueService()


@router.get("/status", summary="Get queue status")
async def get_queue_status(
    queue_name: Optional[str] = Query(None, description="Filter by queue name"),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get queue status"""
    result = await queue_service.get_queue_status(db, queue_name)
    return result


@router.get("/workers", summary="Get worker status")
async def get_worker_status(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get worker status"""
    workers = await queue_service.get_worker_status(db)
    return {"workers": workers}


@router.post("/{queue_name}/pause", summary="Pause queue")
async def pause_queue(
    queue_name: str,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Pause queue processing"""
    result = await queue_service.pause_queue(
        db, queue_name, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{queue_name}/resume", summary="Resume queue")
async def resume_queue(
    queue_name: str,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Resume queue processing"""
    result = await queue_service.resume_queue(
        db, queue_name, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{queue_name}/purge", summary="Purge queue")
async def purge_queue(
    queue_name: str,
    request: Request,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Purge queue (remove all pending tasks)"""
    result = await queue_service.purge_queue(
        db, queue_name, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )
    return result


@router.post("/{queue_name}/retry", summary="Retry failed tasks")
async def retry_failed_tasks(
    queue_name: str,
    task_ids: Optional[List[UUID]] = Query(None, description="Specific task IDs to retry"),
    request: Request = None,
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Retry failed tasks"""
    result = await queue_service.retry_failed_tasks(
        db, queue_name, task_ids, current_admin.id,
        request.client.host if request.client else None,
        request.headers.get("user-agent") if request else None
    )
    return result


@router.get("/tasks", summary="Get queue tasks")
async def get_queue_tasks(
    queue_name: Optional[str] = Query(None, description="Filter by queue name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get queue tasks"""
    result = await queue_service.get_queue_tasks(
        db, queue_name, status, page, page_size
    )
    return result

