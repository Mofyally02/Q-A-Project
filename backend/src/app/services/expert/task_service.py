"""
Expert task service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.expert import tasks as task_crud


class TaskService:
    """Expert task service"""
    
    @staticmethod
    async def get_tasks(
        db: asyncpg.Connection,
        expert_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get expert tasks"""
        return await task_crud.get_expert_tasks(db, expert_id, status, page, page_size)
    
    @staticmethod
    async def get_task_detail(
        db: asyncpg.Connection,
        task_id: UUID,
        expert_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get task detail"""
        return await task_crud.get_task_detail(db, task_id, expert_id)
    
    @staticmethod
    async def start_task(
        db: asyncpg.Connection,
        task_id: UUID,
        expert_id: UUID
    ) -> Dict[str, Any]:
        """Start working on a task"""
        success = await task_crud.start_task(db, task_id, expert_id)
        if not success:
            raise ValueError("Task not found or already started")
        return {"success": True, "task_id": task_id, "status": "in_progress"}

