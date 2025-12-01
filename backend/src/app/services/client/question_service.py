"""
Client question service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.client import questions as question_crud
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """Client question service"""
    
    @staticmethod
    async def submit_question(
        db: asyncpg.Connection,
        user_id: UUID,
        question_text: str,
        subject: Optional[str] = None,
        priority: str = "normal",
        image_urls: Optional[list] = None,
        credits_required: int = 1
    ) -> Dict[str, Any]:
        """Submit a new question"""
        try:
            result = await question_crud.submit_question(
                db, user_id, question_text, subject, priority, image_urls, credits_required
            )
            
            # TODO: Queue question for AI processing via RabbitMQ
            
            return {
                "question_id": result["question_id"],
                "status": result["status"],
                "estimated_completion": None,  # Would be calculated
                "credits_charged": result["credits_charged"],
                "message": "Question submitted successfully"
            }
        except ValueError as e:
            raise ValueError(str(e))
    
    @staticmethod
    async def get_question_status(
        db: asyncpg.Connection,
        question_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get question status"""
        return await question_crud.get_question_status(db, question_id, user_id)
    
    @staticmethod
    async def get_question_history(
        db: asyncpg.Connection,
        user_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get question history"""
        return await question_crud.get_question_history(db, user_id, status, page, page_size)
    
    @staticmethod
    async def get_chat_thread(
        db: asyncpg.Connection,
        question_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get chat thread"""
        return await question_crud.get_chat_thread(db, question_id, user_id)

