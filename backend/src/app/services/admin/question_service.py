"""
Question oversight service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from app.crud.admin import questions as question_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """Question oversight service"""
    
    @staticmethod
    async def get_questions(
        db: asyncpg.Connection,
        status: Optional[str] = None,
        subject: Optional[str] = None,
        client_id: Optional[UUID] = None,
        expert_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get questions with filters"""
        return await question_crud.get_questions(
            db, status, subject, client_id, expert_id,
            date_from, date_to, search, page, page_size
        )
    
    @staticmethod
    async def get_question_by_id(
        db: asyncpg.Connection,
        question_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get question details with full pipeline"""
        return await question_crud.get_question_by_id(db, question_id)
    
    @staticmethod
    async def reassign_expert(
        db: asyncpg.Connection,
        question_id: UUID,
        new_expert_id: UUID,
        admin_id: UUID,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reassign question to different expert"""
        success = await question_crud.reassign_expert(db, question_id, new_expert_id)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "reassign_expert",
                target_type="question", target_id=question_id,
                details={"new_expert_id": str(new_expert_id), "reason": reason},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "question_id": question_id, "expert_id": new_expert_id}
    
    @staticmethod
    async def force_deliver(
        db: asyncpg.Connection,
        question_id: UUID,
        admin_id: UUID,
        answer: Optional[str] = None,
        reason: str = "Admin force delivery",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Force deliver question (bypass review)"""
        success = await question_crud.force_deliver_question(db, question_id, answer)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "force_deliver",
                target_type="question", target_id=question_id,
                details={"answer_provided": answer is not None, "reason": reason},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "question_id": question_id}
    
    @staticmethod
    async def reject_and_correct(
        db: asyncpg.Connection,
        question_id: UUID,
        correction: str,
        admin_id: UUID,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reject question and add admin correction"""
        success = await question_crud.reject_and_correct_question(
            db, question_id, correction, reason
        )
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "reject_and_correct",
                target_type="question", target_id=question_id,
                details={"reason": reason, "correction_length": len(correction)},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "question_id": question_id}
    
    @staticmethod
    async def flag_plagiarism(
        db: asyncpg.Connection,
        question_id: UUID,
        admin_id: UUID,
        fine_amount: Optional[float] = None,
        reason: str = "Plagiarism detected",
        notify_client: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Flag question as plagiarism"""
        success = await question_crud.flag_plagiarism(db, question_id, fine_amount)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "flag_plagiarism",
                target_type="question", target_id=question_id,
                details={"fine_amount": fine_amount, "reason": reason, "notify_client": notify_client},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "question_id": question_id, "fine_amount": fine_amount}
    
    @staticmethod
    async def escalate(
        db: asyncpg.Connection,
        question_id: UUID,
        admin_id: UUID,
        reason: str,
        priority: str = "normal",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Escalate question to super admin"""
        success = await question_crud.escalate_question(db, question_id, priority)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "escalate_question",
                target_type="question", target_id=question_id,
                details={"reason": reason, "priority": priority},
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "question_id": question_id, "priority": priority}
    
    @staticmethod
    async def get_question_stats(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get question statistics"""
        return await question_crud.get_question_stats(db)

