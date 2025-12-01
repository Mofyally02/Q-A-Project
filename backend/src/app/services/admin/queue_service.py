"""
Queue control service
"""

from typing import Dict, Any, Optional, List
import asyncpg
from uuid import UUID
from app.crud.admin import queues as queue_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class QueueService:
    """Queue control service"""
    
    @staticmethod
    async def get_queue_status(
        db: asyncpg.Connection,
        queue_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get queue status"""
        return await queue_crud.get_queue_status(db, queue_name)
    
    @staticmethod
    async def get_worker_status(
        db: asyncpg.Connection
    ) -> List[Dict[str, Any]]:
        """Get worker status"""
        return await queue_crud.get_worker_status(db)
    
    @staticmethod
    async def pause_queue(
        db: asyncpg.Connection,
        queue_name: str,
        paused_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pause queue processing"""
        result = await queue_crud.pause_queue(db, queue_name, paused_by)
        
        # Log admin action
        await action_crud.log_admin_action(
            db, paused_by, "pause_queue",
            target_type="queue", target_id=None,
            details={"queue_name": queue_name},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def resume_queue(
        db: asyncpg.Connection,
        queue_name: str,
        resumed_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Resume queue processing"""
        result = await queue_crud.resume_queue(db, queue_name, resumed_by)
        
        await action_crud.log_admin_action(
            db, resumed_by, "resume_queue",
            target_type="queue", target_id=None,
            details={"queue_name": queue_name},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def purge_queue(
        db: asyncpg.Connection,
        queue_name: str,
        purged_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Purge queue"""
        result = await queue_crud.purge_queue(db, queue_name, purged_by)
        
        await action_crud.log_admin_action(
            db, purged_by, "purge_queue",
            target_type="queue", target_id=None,
            details={"queue_name": queue_name},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def retry_failed_tasks(
        db: asyncpg.Connection,
        queue_name: str,
        task_ids: Optional[List[UUID]] = None,
        retried_by: UUID = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retry failed tasks"""
        result = await queue_crud.retry_failed_tasks(
            db, queue_name, task_ids, retried_by
        )
        
        if retried_by:
            await action_crud.log_admin_action(
                db, retried_by, "retry_failed_tasks",
                target_type="queue", target_id=None,
                details={
                    "queue_name": queue_name,
                    "task_count": result["tasks_retried"]
                },
                ip_address=ip_address, user_agent=user_agent
            )
        
        return result
    
    @staticmethod
    async def get_queue_tasks(
        db: asyncpg.Connection,
        queue_name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get queue tasks"""
        return await queue_crud.get_queue_tasks(
            db, queue_name, status, page, page_size
        )

