"""
System Setting model
Stores system-wide configuration settings
"""

from sqlalchemy import Column, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SystemSetting(BaseModel):
    """System setting model"""
    
    __tablename__ = "system_settings"
    
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    __table_args__ = (
        UniqueConstraint('key', name='uq_system_settings_key'),
    )
    
    def __repr__(self):
        return f"<SystemSetting {self.key} = {self.value}>"

