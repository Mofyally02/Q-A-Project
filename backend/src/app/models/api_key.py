"""
API Key model
Stores encrypted API keys for external services
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime
from datetime import timezone
TIMESTAMPTZ = DateTime(timezone=True)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class APIKeyType:
    """API key type constants"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"
    TURNITIN = "turnitin"
    STEALTH = "stealth"
    POE_CHATGPT = "poe_chatgpt"
    POE_CLAUDE = "poe_claude"
    POE_GEMINI = "poe_gemini"
    POE_GROK = "poe_grok"
    AWS = "aws"
    
    @classmethod
    def all(cls):
        return [
            cls.OPENAI, cls.ANTHROPIC, cls.GOOGLE, cls.XAI,
            cls.TURNITIN, cls.STEALTH,
            cls.POE_CHATGPT, cls.POE_CLAUDE, cls.POE_GEMINI, cls.POE_GROK,
            cls.AWS
        ]


class APIKey(BaseModel):
    """API key model for external services"""
    
    __tablename__ = "api_keys"
    
    name = Column(String(255), nullable=False)
    key_type = Column(String(50), nullable=False, index=True)
    encrypted_key = Column(Text, nullable=False)  # Encrypted with Fernet
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_tested_at = Column(TIMESTAMPTZ, nullable=True)
    last_tested_status = Column(String(20), nullable=True)  # 'success', 'failed', 'unknown'
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<APIKey {self.name} ({self.key_type})>"

