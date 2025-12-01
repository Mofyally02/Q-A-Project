"""
Notification Template model
Stores reusable notification templates
"""

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class NotificationTemplateType:
    """Notification template type constants"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    
    @classmethod
    def all(cls):
        return [cls.EMAIL, cls.SMS, cls.PUSH, cls.IN_APP]


class NotificationTemplate(BaseModel):
    """Notification template model"""
    
    __tablename__ = "notification_templates"
    
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    template_type = Column(String(20), nullable=False, index=True)
    variables = Column(JSON, nullable=True)  # Available template variables
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<NotificationTemplate {self.name} ({self.template_type})>"

