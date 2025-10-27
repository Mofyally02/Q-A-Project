import asyncio
import logging
from typing import Dict, Any, Optional, List
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications via WebSocket and email"""
    
    def __init__(self):
        self.websocket_connections = {}  # Store active WebSocket connections
        self.email_config = {
            "smtp_server": "smtp.gmail.com",  # Example SMTP server
            "smtp_port": 587,
            "username": "noreply@altechacademy.com",  # Example email
            "password": "your_email_password"  # Should be in environment variables
        }
    
    async def send_websocket_notification(
        self,
        user_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """Send WebSocket notification to user"""
        try:
            if user_id in self.websocket_connections:
                connection = self.websocket_connections[user_id]
                await connection.send(json.dumps(message))
                logger.info(f"WebSocket notification sent to user {user_id}")
                return True
            else:
                logger.warning(f"No WebSocket connection found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
            return False
    
    async def send_email_notification(
        self,
        user_id: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None
    ) -> bool:
        """Send email notification to user"""
        try:
            # Get user email from database (you'd need to implement this)
            user_email = await self._get_user_email(user_id)
            if not user_email:
                logger.warning(f"No email found for user {user_id}")
                return False
            
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_config["username"]
            msg["To"] = user_email
            msg["Subject"] = subject
            
            # Add text part
            text_part = MIMEText(message, "plain")
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, "html")
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["username"], self.email_config["password"])
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def send_bulk_notification(
        self,
        user_ids: List[str],
        message: Dict[str, Any],
        notification_type: str = "info"
    ) -> Dict[str, Any]:
        """Send notification to multiple users"""
        try:
            results = {
                "websocket_success": 0,
                "websocket_failed": 0,
                "email_success": 0,
                "email_failed": 0
            }
            
            for user_id in user_ids:
                # Send WebSocket notification
                websocket_success = await self.send_websocket_notification(user_id, message)
                if websocket_success:
                    results["websocket_success"] += 1
                else:
                    results["websocket_failed"] += 1
                
                # Send email notification
                email_success = await self.send_email_notification(
                    user_id,
                    message.get("subject", "Notification"),
                    message.get("message", "")
                )
                if email_success:
                    results["email_success"] += 1
                else:
                    results["email_failed"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending bulk notification: {e}")
            return {"error": str(e)}
    
    async def send_question_status_update(
        self,
        user_id: str,
        question_id: str,
        status: str
    ) -> bool:
        """Send question status update notification"""
        try:
            message = {
                "type": "question_status_update",
                "question_id": question_id,
                "status": status,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return await self.send_websocket_notification(user_id, message)
            
        except Exception as e:
            logger.error(f"Error sending question status update: {e}")
            return False
    
    async def send_answer_ready_notification(
        self,
        user_id: str,
        question_id: str,
        answer_preview: str
    ) -> bool:
        """Send answer ready notification"""
        try:
            message = {
                "type": "answer_ready",
                "question_id": question_id,
                "answer_preview": answer_preview[:200] + "..." if len(answer_preview) > 200 else answer_preview,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send WebSocket notification
            websocket_success = await self.send_websocket_notification(user_id, message)
            
            # Send email notification
            email_subject = "Your Answer is Ready"
            email_message = f"Your answer for question {question_id} is ready for review.\n\nPreview: {answer_preview[:200]}..."
            
            email_success = await self.send_email_notification(
                user_id,
                email_subject,
                email_message
            )
            
            return websocket_success or email_success
            
        except Exception as e:
            logger.error(f"Error sending answer ready notification: {e}")
            return False
    
    async def send_expert_assignment_notification(
        self,
        expert_id: str,
        question_id: str,
        subject: str
    ) -> bool:
        """Send expert assignment notification"""
        try:
            message = {
                "type": "expert_assignment",
                "question_id": question_id,
                "subject": subject,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send WebSocket notification
            websocket_success = await self.send_websocket_notification(expert_id, message)
            
            # Send email notification
            email_subject = "New Question Assigned for Review"
            email_message = f"You have been assigned a new question for review.\n\nQuestion ID: {question_id}\nSubject: {subject}"
            
            email_success = await self.send_email_notification(
                expert_id,
                email_subject,
                email_message
            )
            
            return websocket_success or email_success
            
        except Exception as e:
            logger.error(f"Error sending expert assignment notification: {e}")
            return False
    
    async def send_rating_reminder(
        self,
        user_id: str,
        question_id: str
    ) -> bool:
        """Send rating reminder notification"""
        try:
            message = {
                "type": "rating_reminder",
                "question_id": question_id,
                "message": "Please rate your answer to help us improve our service.",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send WebSocket notification
            websocket_success = await self.send_websocket_notification(user_id, message)
            
            # Send email notification
            email_subject = "Please Rate Your Answer"
            email_message = f"Your answer for question {question_id} has been delivered. Please take a moment to rate our service."
            
            email_success = await self.send_email_notification(
                user_id,
                email_subject,
                email_message
            )
            
            return websocket_success or email_success
            
        except Exception as e:
            logger.error(f"Error sending rating reminder: {e}")
            return False
    
    async def send_system_announcement(
        self,
        announcement: str,
        user_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send system announcement to users"""
        try:
            message = {
                "type": "system_announcement",
                "announcement": announcement,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            if user_ids:
                # Send to specific users
                return await self.send_bulk_notification(user_ids, message)
            else:
                # Send to all users (you'd need to implement this)
                logger.warning("Sending to all users not implemented yet")
                return {"error": "Not implemented"}
            
        except Exception as e:
            logger.error(f"Error sending system announcement: {e}")
            return {"error": str(e)}
    
    async def register_websocket_connection(
        self,
        user_id: str,
        connection
    ) -> None:
        """Register WebSocket connection for user"""
        try:
            self.websocket_connections[user_id] = connection
            logger.info(f"WebSocket connection registered for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error registering WebSocket connection: {e}")
    
    async def unregister_websocket_connection(
        self,
        user_id: str
    ) -> None:
        """Unregister WebSocket connection for user"""
        try:
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
                logger.info(f"WebSocket connection unregistered for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error unregistering WebSocket connection: {e}")
    
    async def get_active_connections(self) -> List[str]:
        """Get list of users with active WebSocket connections"""
        return list(self.websocket_connections.keys())
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from database (placeholder implementation)"""
        # This would typically query the database
        # For now, return a placeholder
        return f"user{user_id}@example.com"
    
    async def send_rating_notification(
        self,
        expert_id: str,
        question_id: str,
        rating: int,
        comment: str
    ) -> bool:
        """Send rating notification to expert"""
        try:
            message = {
                "type": "rating_received",
                "question_id": question_id,
                "rating": rating,
                "comment": comment,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send WebSocket notification
            websocket_success = await self.send_websocket_notification(expert_id, message)
            
            # Send email notification
            email_subject = "New Rating Received"
            email_message = f"You received a {rating}-star rating for question {question_id}.\n\nComment: {comment}"
            
            email_success = await self.send_email_notification(
                expert_id,
                email_subject,
                email_message
            )
            
            return websocket_success or email_success
            
        except Exception as e:
            logger.error(f"Error sending rating notification: {e}")
            return False

