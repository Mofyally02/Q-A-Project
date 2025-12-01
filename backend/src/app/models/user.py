"""
User model
Core user model with role-based access control
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy import DateTime, TIMESTAMP
from datetime import timezone
TIMESTAMPTZ = DateTime(timezone=True)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel


class UserRole:
    """User role constants"""
    CLIENT = "client"
    EXPERT = "expert"
    ADMIN_EDITOR = "admin_editor"
    SUPER_ADMIN = "super_admin"
    
    @classmethod
    def all(cls):
        return [cls.CLIENT, cls.EXPERT, cls.ADMIN_EDITOR, cls.SUPER_ADMIN]
    
    @classmethod
    def admin_roles(cls):
        return [cls.ADMIN_EDITOR, cls.SUPER_ADMIN]
    
    @classmethod
    def is_admin(cls, role: str) -> bool:
        return role in cls.admin_roles()


class User(BaseModel):
    """User model with extended admin fields"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(
        String(20),
        default=UserRole.CLIENT,
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    banned_at = Column(TIMESTAMPTZ, nullable=True)
    banned_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_login = Column(String(50), nullable=True)
    last_active = Column(TIMESTAMPTZ, nullable=True)
    profile_data = Column(JSON, default={}, nullable=False)
    
    # Relationships
    banned_by = relationship("User", foreign_keys=[banned_by_id], remote_side="User.id")
    invited_by = relationship("User", foreign_keys=[invited_by_id], remote_side="User.id")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    def is_super_admin(self) -> bool:
        """Check if user is super admin"""
        return self.role == UserRole.SUPER_ADMIN
    
    def is_admin_or_super(self) -> bool:
        """Check if user is admin or super admin"""
        return self.role in UserRole.admin_roles()
    
    def can_manage_admins(self) -> bool:
        """Check if user can manage other admins"""
        return self.role == UserRole.SUPER_ADMIN

