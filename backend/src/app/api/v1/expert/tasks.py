"""
Expert task endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import asyncpg
from uuid import UUID
from app.dependencies.expert import require_expert
from app.db.session import get_db
from app.services.expert.task_service import TaskService
from app.schemas.expert.task import TaskListResponse, TaskDetailResponse
from app.models.user import User

router = APIRouter()
task_service = TaskService()


@router.get("", response_model=TaskListResponse, summary="Get expert tasks")
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert tasks"""
    result = await task_service.get_tasks(
        db, current_user.id, status, page, page_size
    )
    return TaskListResponse(**result)


@router.get("/{task_id}", response_model=TaskDetailResponse, summary="Get task detail")
async def get_task_detail(
    task_id: UUID,
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get task detail"""
    task = await task_service.get_task_detail(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskDetailResponse(**task)


@router.post("/{task_id}/start", summary="Start working on task")
async def start_task(
    task_id: UUID,
    current_user: User = Depends(require_expert),
    db: asyncpg.Connection = Depends(get_db)
):
    """Start working on a task"""
    try:
        result = await task_service.start_task(db, task_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

