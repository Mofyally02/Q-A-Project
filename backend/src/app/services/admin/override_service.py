"""
Override triggers service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import override as override_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class OverrideService:
    """Override triggers service"""
    
    @staticmethod
    async def bypass_ai_check(
        db: asyncpg.Connection,
        question_id: UUID,
        overridden_by: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bypass AI content check"""
        result = await override_crud.bypass_ai_check(
            db, question_id, overridden_by, reason
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, overridden_by, "override_ai_bypass",
            target_type="question", target_id=question_id,
            details={"reason": reason},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def pass_originality_check(
        db: asyncpg.Connection,
        answer_id: UUID,
        overridden_by: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pass originality check override"""
        result = await override_crud.pass_originality_check(
            db, answer_id, overridden_by, reason
        )
        
        await action_crud.log_admin_action(
            db, overridden_by, "override_originality_pass",
            target_type="answer", target_id=answer_id,
            details={"reason": reason},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def override_confidence_threshold(
        db: asyncpg.Connection,
        question_id: UUID,
        min_confidence: Optional[float],
        overridden_by: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Override confidence threshold"""
        result = await override_crud.override_confidence_threshold(
            db, question_id, min_confidence, overridden_by, reason
        )
        
        await action_crud.log_admin_action(
            db, overridden_by, "override_confidence",
            target_type="question", target_id=question_id,
            details={"min_confidence": min_confidence, "reason": reason},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def skip_humanization(
        db: asyncpg.Connection,
        answer_id: UUID,
        overridden_by: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Skip humanization step"""
        result = await override_crud.skip_humanization(
            db, answer_id, overridden_by, reason
        )
        
        await action_crud.log_admin_action(
            db, overridden_by, "override_humanization_skip",
            target_type="answer", target_id=answer_id,
            details={"reason": reason},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def bypass_expert_review(
        db: asyncpg.Connection,
        answer_id: UUID,
        overridden_by: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bypass expert review"""
        result = await override_crud.bypass_expert_review(
            db, answer_id, overridden_by, reason
        )
        
        await action_crud.log_admin_action(
            db, overridden_by, "override_expert_bypass",
            target_type="answer", target_id=answer_id,
            details={"reason": reason},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result

