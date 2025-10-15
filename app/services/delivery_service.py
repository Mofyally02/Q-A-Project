import asyncio
import logging
from typing import Dict, Any, Optional
import asyncpg
from app.models import APIResponse
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class DeliveryService:
    """Service for delivering answers to clients"""
    
    def __init__(self):
        self.audit_service = AuditService()
        self.notification_service = NotificationService()
    
    async def deliver_answer(
        self,
        question_id: str,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Deliver answer to client"""
        try:
            # Get question and answer data
            question_data = await self._get_question_data(db, question_id)
            if not question_data:
                return APIResponse(
                    success=False,
                    message="Question not found"
                )
            
            # Get answer data
            answer_data = await self._get_answer_data(db, question_id)
            if not answer_data:
                return APIResponse(
                    success=False,
                    message="Answer not found"
                )
            
            # Check if answer is approved
            if not answer_data.get("is_approved"):
                return APIResponse(
                    success=False,
                    message="Answer not approved for delivery"
                )
            
            # Format answer for delivery
            formatted_answer = await self._format_answer_for_delivery(
                question_data,
                answer_data
            )
            
            # Update question status to delivered
            await self._update_question_status(db, question_id, "delivered")
            
            # Send notification to client
            await self._notify_client(
                question_data["client_id"],
                question_id,
                formatted_answer
            )
            
            # Log delivery
            await self.audit_service.log_action(
                db=db,
                action="answer_delivered",
                user_id=question_data["client_id"],
                question_id=question_id,
                details={
                    "answer_id": answer_data["answer_id"],
                    "delivery_method": "websocket",
                    "formatted": True
                }
            )
            
            logger.info(f"Answer delivered for question {question_id}")
            
            return APIResponse(
                success=True,
                message="Answer delivered successfully",
                data={
                    "question_id": question_id,
                    "answer": formatted_answer,
                    "delivery_method": "websocket"
                }
            )
            
        except Exception as e:
            logger.error(f"Error delivering answer: {e}")
            return APIResponse(
                success=False,
                message="Failed to deliver answer",
                data={"error": str(e)}
            )
    
    async def _get_question_data(
        self,
        db: asyncpg.Connection,
        question_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get question data from database"""
        try:
            row = await db.fetchrow(
                """
                SELECT question_id, client_id, type, content, subject, status, created_at
                FROM questions
                WHERE question_id = $1
                """,
                question_id
            )
            
            if not row:
                return None
            
            return {
                "question_id": str(row["question_id"]),
                "client_id": str(row["client_id"]),
                "type": row["type"],
                "content": row["content"],
                "subject": row["subject"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error getting question data: {e}")
            return None
    
    async def _get_answer_data(
        self,
        db: asyncpg.Connection,
        question_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get answer data from database"""
        try:
            row = await db.fetchrow(
                """
                SELECT answer_id, ai_response, humanized_response, expert_response, 
                       confidence_score, is_approved, rejection_reason, created_at
                FROM answers
                WHERE question_id = $1
                ORDER BY created_at DESC
                LIMIT 1
                """,
                question_id
            )
            
            if not row:
                return None
            
            return {
                "answer_id": str(row["answer_id"]),
                "ai_response": row["ai_response"],
                "humanized_response": row["humanized_response"],
                "expert_response": row["expert_response"],
                "confidence_score": row["confidence_score"],
                "is_approved": row["is_approved"],
                "rejection_reason": row["rejection_reason"],
                "created_at": row["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error getting answer data: {e}")
            return None
    
    async def _format_answer_for_delivery(
        self,
        question_data: Dict[str, Any],
        answer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format answer for delivery to client"""
        try:
            # Determine which response to use
            if answer_data.get("expert_response"):
                # Use expert response if available
                response = answer_data["expert_response"]
                response_type = "expert"
            elif answer_data.get("humanized_response"):
                # Use humanized response if available
                response = answer_data["humanized_response"]
                response_type = "humanized"
            else:
                # Use AI response as fallback
                response = answer_data.get("ai_response", {})
                response_type = "ai"
            
            # Format based on question type
            if question_data["type"] == "text":
                formatted_answer = await self._format_text_answer(response, response_type)
            else:
                formatted_answer = await self._format_image_answer(response, response_type)
            
            # Add metadata
            formatted_answer["metadata"] = {
                "response_type": response_type,
                "confidence_score": answer_data.get("confidence_score"),
                "created_at": answer_data["created_at"].isoformat(),
                "question_subject": question_data["subject"]
            }
            
            return formatted_answer
            
        except Exception as e:
            logger.error(f"Error formatting answer: {e}")
            return {
                "content": "Error formatting answer",
                "type": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _format_text_answer(
        self,
        response: Dict[str, Any],
        response_type: str
    ) -> Dict[str, Any]:
        """Format text answer for delivery"""
        try:
            if response_type == "expert":
                # Expert response might have corrections
                content = response.get("text", "")
                corrections = response.get("corrections", [])
                
                formatted_content = {
                    "text": content,
                    "corrections": corrections,
                    "type": "expert_text"
                }
                
            elif response_type == "humanized":
                # Humanized response
                content = response.get("text", "")
                sources = response.get("sources", [])
                
                formatted_content = {
                    "text": content,
                    "sources": sources,
                    "type": "humanized_text"
                }
                
            else:
                # AI response
                content = response.get("response", "")
                sources = response.get("sources", [])
                
                formatted_content = {
                    "text": content,
                    "sources": sources,
                    "type": "ai_text"
                }
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error formatting text answer: {e}")
            return {
                "text": "Error formatting text answer",
                "type": "error"
            }
    
    async def _format_image_answer(
        self,
        response: Dict[str, Any],
        response_type: str
    ) -> Dict[str, Any]:
        """Format image answer for delivery"""
        try:
            if response_type == "expert":
                # Expert response might have image corrections
                content = response.get("image", "")
                corrections = response.get("corrections", [])
                
                formatted_content = {
                    "image": content,
                    "corrections": corrections,
                    "type": "expert_image"
                }
                
            elif response_type == "humanized":
                # Humanized response
                content = response.get("image", "")
                sources = response.get("sources", [])
                
                formatted_content = {
                    "image": content,
                    "sources": sources,
                    "type": "humanized_image"
                }
                
            else:
                # AI response
                content = response.get("response", "")
                sources = response.get("sources", [])
                
                formatted_content = {
                    "image": content,
                    "sources": sources,
                    "type": "ai_image"
                }
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error formatting image answer: {e}")
            return {
                "image": "Error formatting image answer",
                "type": "error"
            }
    
    async def _update_question_status(
        self,
        db: asyncpg.Connection,
        question_id: str,
        status: str
    ) -> None:
        """Update question status"""
        try:
            await db.execute(
                "UPDATE questions SET status = $1 WHERE question_id = $2",
                status,
                question_id
            )
            
        except Exception as e:
            logger.error(f"Error updating question status: {e}")
            raise
    
    async def _notify_client(
        self,
        client_id: str,
        question_id: str,
        formatted_answer: Dict[str, Any]
    ) -> None:
        """Send notification to client about answer delivery"""
        try:
            # Send WebSocket notification
            await self.notification_service.send_websocket_notification(
                user_id=client_id,
                message={
                    "type": "answer_delivered",
                    "question_id": question_id,
                    "answer": formatted_answer
                }
            )
            
            # Send email notification (optional)
            await self.notification_service.send_email_notification(
                user_id=client_id,
                subject="Your Answer is Ready",
                message=f"Your answer for question {question_id} has been delivered and is ready for review."
            )
            
        except Exception as e:
            logger.error(f"Error notifying client: {e}")
    
    async def get_delivery_status(
        self,
        question_id: str,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Get delivery status for a question"""
        try:
            row = await db.fetchrow(
                """
                SELECT q.status, q.created_at, a.created_at as answer_created_at
                FROM questions q
                LEFT JOIN answers a ON q.question_id = a.question_id
                WHERE q.question_id = $1
                """,
                question_id
            )
            
            if not row:
                return APIResponse(
                    success=False,
                    message="Question not found"
                )
            
            return APIResponse(
                success=True,
                message="Delivery status retrieved",
                data={
                    "question_id": question_id,
                    "status": row["status"],
                    "question_created_at": row["created_at"].isoformat(),
                    "answer_created_at": row["answer_created_at"].isoformat() if row["answer_created_at"] else None,
                    "is_delivered": row["status"] == "delivered"
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting delivery status: {e}")
            return APIResponse(
                success=False,
                message="Failed to get delivery status",
                data={"error": str(e)}
            )
    
    async def redeliver_answer(
        self,
        question_id: str,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Redeliver answer to client"""
        try:
            # Check if answer exists and is approved
            answer_data = await self._get_answer_data(db, question_id)
            if not answer_data or not answer_data.get("is_approved"):
                return APIResponse(
                    success=False,
                    message="Answer not available for redelivery"
                )
            
            # Get question data
            question_data = await self._get_question_data(db, question_id)
            if not question_data:
                return APIResponse(
                    success=False,
                    message="Question not found"
                )
            
            # Format answer
            formatted_answer = await self._format_answer_for_delivery(
                question_data,
                answer_data
            )
            
            # Send notification
            await self._notify_client(
                question_data["client_id"],
                question_id,
                formatted_answer
            )
            
            # Log redelivery
            await self.audit_service.log_action(
                db=db,
                action="answer_redelivered",
                user_id=question_data["client_id"],
                question_id=question_id,
                details={"redelivery": True}
            )
            
            return APIResponse(
                success=True,
                message="Answer redelivered successfully",
                data={
                    "question_id": question_id,
                    "answer": formatted_answer
                }
            )
            
        except Exception as e:
            logger.error(f"Error redelivering answer: {e}")
            return APIResponse(
                success=False,
                message="Failed to redeliver answer",
                data={"error": str(e)}
            )

