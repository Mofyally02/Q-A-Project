"""
Admin authentication dependencies
Role-based access control for admin endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from typing import Optional
import asyncpg
from app.db.session import get_auth_db
from app.models.user import User, UserRole
from app.core.security import security
import logging

logger = logging.getLogger(__name__)


# Super admin email that has access to all routes
SUPER_ADMIN_EMAIL = "allansaiti02@gmail.com"

async def get_current_user(
    request: Request,
    db: asyncpg.Connection = Depends(get_auth_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    # Extract token from Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Verify JWT token
    payload = security.verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user_row = await db.fetchrow(
        "SELECT * FROM users WHERE user_id = $1",
        user_id
    )
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Convert to User object (simplified - in production use ORM)
    # Create a simple object with user data
    class UserObj:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
        
        def is_super_admin(self) -> bool:
            """Check if user is super admin"""
            return self.role == UserRole.SUPER_ADMIN or self.email == SUPER_ADMIN_EMAIL
        
        def is_admin_or_super(self) -> bool:
            """Check if user is admin or super admin"""
            return self.role in UserRole.admin_roles() or self.email == SUPER_ADMIN_EMAIL
    
    user = UserObj(dict(user_row))
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    if hasattr(user, 'is_banned') and user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    return user


async def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires super admin role
    Super admin email has access regardless of role check
    """
    # Check if user is the super admin by email
    if hasattr(current_user, 'email') and current_user.email == SUPER_ADMIN_EMAIL:
        return current_user
    
    if not current_user.is_super_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def require_admin_or_super(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires admin_editor or super_admin role
    Super admin email has access regardless of role check
    """
    # Check if user is the super admin by email
    if hasattr(current_user, 'email') and current_user.email == SUPER_ADMIN_EMAIL:
        return current_user
    
    if not current_user.is_admin_or_super():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(require_admin_or_super)
) -> User:
    """
    Get current admin user (alias for require_admin_or_super)
    """
    return current_user


def log_admin_action(
    admin_id: str,
    action_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> dict:
    """
    Helper function to create admin action log entry
    Returns dict ready for database insertion
    """
    return {
        "admin_id": admin_id,
        "action_type": action_type,
        "target_type": target_type,
        "target_id": target_id,
        "details": details or {},
        "ip_address": ip_address,
        "user_agent": user_agent
    }

