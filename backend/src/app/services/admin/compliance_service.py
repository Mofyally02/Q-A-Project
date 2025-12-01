"""
Compliance and audit service
"""

from typing import Dict, Any, Optional, List
import asyncpg
from uuid import UUID
from datetime import datetime
from app.crud.admin import compliance as compliance_crud
from app.crud.admin import admin_actions as action_crud
import csv
import io
import json
import logging

logger = logging.getLogger(__name__)


class ComplianceService:
    """Compliance and audit service"""
    
    @staticmethod
    async def get_audit_logs(
        db: asyncpg.Connection,
        admin_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get audit logs with filters"""
        from app.crud.admin.admin_actions import get_admin_actions
        return await get_admin_actions(
            db, admin_id, action_type, target_type, target_id, page, page_size
        )
    
    @staticmethod
    async def get_audit_log_by_id(
        db: asyncpg.Connection,
        log_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get specific audit log"""
        from app.crud.admin.admin_actions import get_admin_action_by_id
        return await get_admin_action_by_id(db, log_id)
    
    @staticmethod
    async def get_flagged_content(
        db: asyncpg.Connection,
        reason: Optional[str] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get flagged content"""
        return await compliance_crud.get_flagged_content(
            db, reason, severity, resolved, page, page_size
        )
    
    @staticmethod
    async def get_user_compliance_history(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get user compliance history"""
        return await compliance_crud.get_user_compliance_history(db, user_id)
    
    @staticmethod
    async def flag_content(
        db: asyncpg.Connection,
        content_id: UUID,
        content_type: str,
        reason: str,
        admin_id: UUID,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manually flag content"""
        flag_id = await compliance_crud.create_compliance_flag(
            db, content_id, content_type, reason, severity, details, user_id
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, admin_id, "flag_content",
            target_type=content_type, target_id=content_id,
            details={"reason": reason, "severity": severity},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return {"success": True, "flag_id": flag_id, "content_id": content_id}
    
    @staticmethod
    async def get_compliance_stats(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get compliance statistics"""
        return await compliance_crud.get_compliance_stats(db)
    
    @staticmethod
    async def export_audit_logs(
        db: asyncpg.Connection,
        format: str = "json",
        admin_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export audit logs"""
        logs = await compliance_crud.export_audit_logs(
            db, format, admin_id, action_type, date_from, date_to
        )
        
        if format == "csv":
            # Convert to CSV
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            return {
                "format": "csv",
                "data": output.getvalue(),
                "filename": f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        else:
            # JSON format
            return {
                "format": "json",
                "data": logs,
                "filename": f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            }

