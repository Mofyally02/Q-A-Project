"""
Expert dependencies
"""

from fastapi import Depends, HTTPException, status
from app.dependencies.admin import get_current_user
from app.models.user import User, UserRole


from app.dependencies.admin import SUPER_ADMIN_EMAIL

async def require_expert(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require expert role - super admin has access to all routes"""
    # Super admin can access all routes
    if hasattr(current_user, 'email') and current_user.email == SUPER_ADMIN_EMAIL:
        return current_user
    
    if current_user.role != UserRole.EXPERT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Expert access only"
        )
    return current_user

