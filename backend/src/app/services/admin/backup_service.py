"""
Backup and recovery service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import backup as backup_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class BackupService:
    """Backup and recovery service"""
    
    @staticmethod
    async def create_backup(
        db: asyncpg.Connection,
        backup_type: str,
        created_by: UUID,
        include_files: bool = True,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create backup"""
        result = await backup_crud.create_backup(
            db, backup_type, created_by, include_files, description
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, created_by, "create_backup",
            target_type="backup", target_id=result["backup_id"],
            details={
                "backup_type": backup_type,
                "include_files": include_files
            },
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def get_backups(
        db: asyncpg.Connection,
        backup_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get backups"""
        return await backup_crud.get_backups(db, backup_type, status, page, page_size)
    
    @staticmethod
    async def get_backup_by_id(
        db: asyncpg.Connection,
        backup_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get backup by ID"""
        return await backup_crud.get_backup_by_id(db, backup_id)
    
    @staticmethod
    async def delete_backup(
        db: asyncpg.Connection,
        backup_id: UUID,
        deleted_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete backup"""
        success = await backup_crud.delete_backup(db, backup_id, deleted_by)
        
        if success:
            await action_crud.log_admin_action(
                db, deleted_by, "delete_backup",
                target_type="backup", target_id=backup_id,
                details={},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success}
    
    @staticmethod
    async def create_restore(
        db: asyncpg.Connection,
        backup_id: UUID,
        restore_type: str,
        restored_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create restore operation"""
        try:
            result = await backup_crud.create_restore(
                db, backup_id, restore_type, restored_by
            )
            
            # Log admin action
            await action_crud.log_admin_action(
                db, restored_by, "create_restore",
                target_type="backup", target_id=backup_id,
                details={"restore_type": restore_type},
                ip_address=ip_address, user_agent=user_agent
            )
            
            return result
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    async def get_restore_status(
        db: asyncpg.Connection,
        restore_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get restore status"""
        return await backup_crud.get_restore_status(db, restore_id)

