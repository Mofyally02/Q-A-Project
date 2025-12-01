"""
User management service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import users as user_crud
from app.crud.admin import admin_actions as action_crud
from app.core.security import security
import secrets
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""
    
    @staticmethod
    async def get_users(
        db: asyncpg.Connection,
        role: Optional[str] = None,
        is_banned: Optional[bool] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get users with filters"""
        return await user_crud.get_users(
            db, role, is_banned, is_active, search, page, page_size
        )
    
    @staticmethod
    async def get_user_by_id(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await user_crud.get_user_by_id(db, user_id)
    
    @staticmethod
    async def update_user_role(
        db: asyncpg.Connection,
        user_id: UUID,
        new_role: str,
        admin_id: UUID,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user role with logging"""
        # Validate role
        valid_roles = ["client", "expert", "admin_editor", "super_admin"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")
        
        # Update role
        success = await user_crud.update_user_role(db, user_id, new_role, admin_id)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "change_user_role",
                target_type="user", target_id=user_id,
                details={"new_role": new_role, "reason": reason},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "user_id": user_id, "new_role": new_role}
    
    @staticmethod
    async def ban_user(
        db: asyncpg.Connection,
        user_id: UUID,
        banned: bool,
        admin_id: UUID,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ban or unban user with logging"""
        success = await user_crud.ban_user(db, user_id, banned, admin_id, reason)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "ban_user" if banned else "unban_user",
                target_type="user", target_id=user_id,
                details={"reason": reason},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "user_id": user_id, "banned": banned}
    
    @staticmethod
    async def reset_password(
        db: asyncpg.Connection,
        user_id: UUID,
        admin_id: UUID,
        send_email: bool = True,
        temporary_password: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reset user password"""
        # Generate temporary password if not provided
        if not temporary_password:
            temporary_password = secrets.token_urlsafe(12)
        
        # Hash password
        password_hash = security.hash_password(temporary_password)
        
        # Update password
        success = await user_crud.reset_user_password(db, user_id, password_hash)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "reset_password",
                target_type="user", target_id=user_id,
                details={"send_email": send_email},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {
            "success": success,
            "user_id": user_id,
            "temporary_password": temporary_password,
            "send_email": send_email
        }
    
    @staticmethod
    async def promote_to_expert(
        db: asyncpg.Connection,
        user_id: UUID,
        admin_id: UUID,
        specialization: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Promote user to expert"""
        success = await user_crud.promote_to_expert(db, user_id, specialization)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "promote_to_expert",
                target_type="user", target_id=user_id,
                details={"specialization": specialization},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "user_id": user_id}
    
    @staticmethod
    async def get_user_stats(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get user statistics"""
        return await user_crud.get_user_stats(db)

