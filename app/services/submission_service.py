import asyncio
import base64
import logging
from typing import Dict, Any
from uuid import uuid4
import asyncpg
from app.models import QuestionCreate, QuestionResponse, APIResponse
from app.config import settings
from app.services.queue_service import QueueService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class SubmissionService:
    def __init__(self):
        self.queue_service = QueueService()
        self.audit_service = AuditService()
    
    async def submit_question(self, question_data: QuestionCreate, db: asyncpg.Connection) -> APIResponse:
        """Submit a new question for processing"""
        try:
            # Validate question data
            validation_result = await self._validate_question(question_data)
            if not validation_result["valid"]:
                return APIResponse(
                    success=False,
                    message=validation_result["message"],
                    data={"errors": validation_result["errors"]}
                )
            
            # Generate question ID
            question_id = uuid4()
            
            # Prepare content based on type
            content = await self._prepare_content(question_data)
            
            # Store question in database
            await db.execute(
                """
                INSERT INTO questions (question_id, client_id, type, content, subject, status)
                VALUES ($1, $2, $3, $4, $5, 'submitted')
                """,
                question_id,
                question_data.client_id,
                question_data.type.value,
                content,
                question_data.subject
            )
            
            # Queue for AI processing
            await self.queue_service.enqueue_ai_processing(str(question_id))
            
            # Log submission
            await self.audit_service.log_action(
                db=db,
                action="submit_question",
                user_id=question_data.client_id,
                question_id=question_id,
                details={"status": "queued", "type": question_data.type.value}
            )
            
            logger.info(f"Question {question_id} submitted successfully")
            
            return APIResponse(
                success=True,
                message="Question submitted successfully",
                data={
                    "question_id": str(question_id),
                    "status": "submitted"
                }
            )
            
        except Exception as e:
            logger.error(f"Error submitting question: {e}")
            return APIResponse(
                success=False,
                message="Failed to submit question",
                data={"error": str(e)}
            )
    
    async def _validate_question(self, question_data: QuestionCreate) -> Dict[str, Any]:
        """Validate question data before submission"""
        errors = []
        
        # Check question type
        if question_data.type not in ["text", "image"]:
            errors.append("Invalid question type. Must be 'text' or 'image'")
        
        # Check content length
        if question_data.type == "text":
            content_text = question_data.content.get("data", "")
            if len(content_text) > settings.max_question_length:
                errors.append(f"Text content too long. Maximum {settings.max_question_length} characters allowed")
            if len(content_text.strip()) == 0:
                errors.append("Text content cannot be empty")
        
        # Check file size for images
        if question_data.type == "image":
            content_data = question_data.content.get("data", "")
            if content_data:
                try:
                    # Decode base64 to check file size
                    file_data = base64.b64decode(content_data)
                    file_size_mb = len(file_data) / (1024 * 1024)
                    if file_size_mb > settings.max_file_size_mb:
                        errors.append(f"File too large. Maximum {settings.max_file_size_mb}MB allowed")
                except Exception:
                    errors.append("Invalid base64 image data")
        
        # Check subject
        if not question_data.subject or len(question_data.subject.strip()) == 0:
            errors.append("Subject is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Validation failed" if errors else "Validation passed"
        }
    
    async def _prepare_content(self, question_data: QuestionCreate) -> Dict[str, Any]:
        """Prepare content for storage based on question type"""
        if question_data.type == "text":
            return {
                "data": question_data.content.get("data", ""),
                "format": "text"
            }
        elif question_data.type == "image":
            return {
                "data": question_data.content.get("data", ""),
                "format": question_data.content.get("format", "jpeg"),
                "size": len(base64.b64decode(question_data.content.get("data", ""))) if question_data.content.get("data") else 0
            }
        
        return question_data.content
    
    async def get_question_status(self, question_id: str, db: asyncpg.Connection) -> APIResponse:
        """Get the current status of a question"""
        try:
            row = await db.fetchrow(
                "SELECT question_id, status, created_at FROM questions WHERE question_id = $1",
                uuid4() if isinstance(question_id, str) else question_id
            )
            
            if not row:
                return APIResponse(
                    success=False,
                    message="Question not found"
                )
            
            return APIResponse(
                success=True,
                message="Question status retrieved",
                data={
                    "question_id": str(row["question_id"]),
                    "status": row["status"],
                    "created_at": row["created_at"].isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting question status: {e}")
            return APIResponse(
                success=False,
                message="Failed to get question status",
                data={"error": str(e)}
            )
    
    async def get_user_questions(self, client_id: str, db: asyncpg.Connection, limit: int = 50, offset: int = 0) -> APIResponse:
        """Get all questions for a specific client"""
        try:
            rows = await db.fetch(
                """
                SELECT question_id, type, subject, status, created_at
                FROM questions 
                WHERE client_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                uuid4() if isinstance(client_id, str) else client_id,
                limit,
                offset
            )
            
            questions = []
            for row in rows:
                questions.append({
                    "question_id": str(row["question_id"]),
                    "type": row["type"],
                    "subject": row["subject"],
                    "status": row["status"],
                    "created_at": row["created_at"].isoformat()
                })
            
            return APIResponse(
                success=True,
                message="Questions retrieved successfully",
                data={"questions": questions, "count": len(questions)}
            )
            
        except Exception as e:
            logger.error(f"Error getting user questions: {e}")
            return APIResponse(
                success=False,
                message="Failed to get user questions",
                data={"error": str(e)}
            )
