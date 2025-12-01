"""
Notification broadcast service
"""

from typing import Dict, Any, Optional, List
import asyncpg
from uuid import UUID
from app.crud.admin import notifications as notification_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification broadcast service"""
    
    @staticmethod
    async def broadcast_notification(
        db: asyncpg.Connection,
        title: str,
        message: str,
        notification_type: str,
        sent_by: UUID,
        target_roles: Optional[List[str]] = None,
        target_status: Optional[List[str]] = None,
        send_email: bool = False,
        send_sms: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Broadcast notification to users"""
        result = await notification_crud.create_notification_broadcast(
            db, title, message, notification_type, sent_by,
            target_roles, target_status, send_email, send_sms
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, sent_by, "broadcast_notification",
            target_type="system", target_id=None,
            details={
                "title": title,
                "target_count": result["target_count"],
                "target_roles": target_roles
            },
            ip_address=ip_address, user_agent=user_agent
        )
        
        # TODO: Queue notification sending to background worker
        # This would use RabbitMQ to send notifications asynchronously
        
        return result
    
    @staticmethod
    async def broadcast_to_segment(
        db: asyncpg.Connection,
        title: str,
        message: str,
        notification_type: str,
        segment_query: Dict[str, Any],
        sent_by: UUID,
        send_email: bool = False,
        send_sms: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Broadcast to custom segment"""
        # Parse segment query to build user filter
        # This is simplified - in production, you'd have a more robust query builder
        target_roles = segment_query.get("roles")
        target_status = segment_query.get("status")
        
        return await NotificationService.broadcast_notification(
            db, title, message, notification_type, sent_by,
            target_roles, target_status, send_email, send_sms,
            ip_address, user_agent
        )
    
    @staticmethod
    async def get_notification_history(
        db: asyncpg.Connection,
        sent_by: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get notification broadcast history"""
        return await notification_crud.get_notification_history(
            db, sent_by, page, page_size
        )
    
    @staticmethod
    async def get_templates(
        db: asyncpg.Connection,
        template_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get notification templates"""
        return await notification_crud.get_notification_templates(db, template_type)
    
    @staticmethod
    async def create_template(
        db: asyncpg.Connection,
        name: str,
        subject: Optional[str],
        body: str,
        template_type: str,
        variables: Optional[Dict[str, Any]] = None,
        created_by: UUID = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create notification template"""
        template_id = await notification_crud.create_notification_template(
            db, name, subject, body, template_type, variables, created_by
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, created_by, "create_notification_template",
            target_type="template", target_id=template_id,
            details={"name": name, "template_type": template_type},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return {"success": True, "template_id": template_id}
    
    @staticmethod
    async def update_template(
        db: asyncpg.Connection,
        template_id: UUID,
        name: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        updated_by: UUID = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update notification template"""
        success = await notification_crud.update_notification_template(
            db, template_id, name, subject, body, variables
        )
        
        if success and updated_by:
            await action_crud.log_admin_action(
                db, updated_by, "update_notification_template",
                target_type="template", target_id=template_id,
                details={"updated_fields": [k for k in [name, subject, body, variables] if k is not None]},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success}
    
    @staticmethod
    async def delete_template(
        db: asyncpg.Connection,
        template_id: UUID,
        deleted_by: UUID = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete notification template"""
        success = await notification_crud.delete_notification_template(db, template_id)
        
        if success and deleted_by:
            await action_crud.log_admin_action(
                db, deleted_by, "delete_notification_template",
                target_type="template", target_id=template_id,
                details={},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success}

