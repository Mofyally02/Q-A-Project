"""
Compliance Flag model
Tracks flagged content for compliance monitoring
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import DateTime
from datetime import timezone
TIMESTAMPTZ = DateTime(timezone=True)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ComplianceFlag(BaseModel):
    """Compliance flag model"""
    
    __tablename__ = "compliance_flags"
    
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # 'question', 'answer', 'user'
    reason = Column(String(50), nullable=False, index=True)  # 'ai_content', 'plagiarism', 'vpn', 'suspicious_activity'
    severity = Column(String(20), default="medium", nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    details = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(TIMESTAMPTZ, nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    flagged_at = Column(TIMESTAMPTZ, nullable=False, server_default="CURRENT_TIMESTAMP")
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    
    def __repr__(self):
        return f"<ComplianceFlag {self.reason} on {self.content_type} {self.content_id}>"

