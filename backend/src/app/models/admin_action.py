"""
Admin Action model
Tracks all admin actions for audit and compliance
"""

from sqlalchemy import Column, String, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy import DateTime
from datetime import timezone
TIMESTAMPTZ = DateTime(timezone=True)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AdminAction(BaseModel):
    """Admin action audit log"""
    
    __tablename__ = "admin_actions"
    
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50), nullable=True)  # 'question', 'user', 'expert', 'system'
    target_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_admin_actions_target', 'target_type', 'target_id'),
        Index('idx_admin_actions_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AdminAction {self.action_type} by {self.admin_id}>"

