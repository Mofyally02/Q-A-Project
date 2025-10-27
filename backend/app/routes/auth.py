from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
import asyncpg
from typing import Dict, Any, List
from app.database import get_auth_db
from app.services.auth_service import auth_service
from app.models import (
    LoginRequest, LoginResponse, RegisterRequest, UserResponse, 
    UserRole, APIResponse, RoleUpdateRequest, RoleUpdateResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Login endpoint for all user types"""
    try:
        result = await auth_service.login_user(login_data, db)
        return result
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/register", response_model=LoginResponse)
async def register(user_data: RegisterRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Register new user"""
    try:
        result = await auth_service.register_user(user_data, db)
        return result
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(auth_service.get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout", response_model=APIResponse)
async def logout():
    """Logout endpoint (client-side token removal)"""
    return APIResponse(
        success=True,
        message="Logout successful"
    )

# Role-specific login endpoints
@router.post("/login/client", response_model=LoginResponse)
async def login_client(login_data: LoginRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Login endpoint specifically for clients"""
    try:
        result = await auth_service.login_user(login_data, db)
        if result.success and result.user and result.user.role != UserRole.CLIENT:
            return LoginResponse(
                success=False,
                message="Access denied. This endpoint is for clients only."
            )
        return result
    except Exception as e:
        logger.error(f"Client login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Client login failed"
        )

@router.post("/login/expert", response_model=LoginResponse)
async def login_expert(login_data: LoginRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Login endpoint specifically for experts"""
    try:
        result = await auth_service.login_user(login_data, db)
        if result.success and result.user and result.user.role != UserRole.EXPERT:
            return LoginResponse(
                success=False,
                message="Access denied. This endpoint is for experts only."
            )
        return result
    except Exception as e:
        logger.error(f"Expert login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Expert login failed"
        )

@router.post("/login/admin", response_model=LoginResponse)
async def login_admin(login_data: LoginRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Login endpoint specifically for admins"""
    try:
        result = await auth_service.login_user(login_data, db)
        if result.success and result.user and result.user.role != UserRole.ADMIN:
            return LoginResponse(
                success=False,
                message="Access denied. This endpoint is for admins only."
            )
        return result
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin login failed"
        )

# Role-specific registration endpoints
@router.post("/register/client", response_model=LoginResponse)
async def register_client(user_data: RegisterRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Register new client (default registration)"""
    # Force client role for this endpoint
    user_data.role = UserRole.CLIENT
    
    try:
        result = await auth_service.register_user(user_data, db)
        return result
    except Exception as e:
        logger.error(f"Client registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Client registration failed"
        )

@router.post("/register/expert", response_model=LoginResponse)
async def register_expert(user_data: RegisterRequest, db: asyncpg.Connection = Depends(get_auth_db)):
    """Register new expert (will be created as client, admin must promote to expert)"""
    # Force client role - admin must promote to expert
    user_data.role = UserRole.CLIENT
    
    try:
        result = await auth_service.register_user(user_data, db)
        if result.success:
            result.message = "Registration successful. Contact admin to become an expert."
        return result
    except Exception as e:
        logger.error(f"Expert registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Expert registration failed"
        )

@router.post("/register/admin", response_model=LoginResponse)
async def register_admin(
    user_data: RegisterRequest, 
    db: asyncpg.Connection = Depends(get_auth_db),
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.ADMIN]))
):
    """Register new admin (requires existing admin privileges)"""
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is for admin registration only"
        )
    
    try:
        result = await auth_service.register_user(user_data, db)
        return result
    except Exception as e:
        logger.error(f"Admin registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin registration failed"
        )

# Admin role management endpoints
@router.post("/admin/assign-role", response_model=RoleUpdateResponse)
async def assign_user_role(
    role_update: RoleUpdateRequest,
    db: asyncpg.Connection = Depends(get_auth_db),
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.ADMIN]))
):
    """Admin endpoint to assign roles to users (Admin controls all role assignments)"""
    try:
        result = await auth_service.update_user_role(role_update, current_user, db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Role assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role"
        )

@router.get("/admin/users", response_model=List[UserResponse])
async def list_all_users(
    db: asyncpg.Connection = Depends(get_auth_db),
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.ADMIN]))
):
    """Admin endpoint to list all users"""
    try:
        users = await db.fetch("""
            SELECT user_id, email, first_name, last_name, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        return [UserResponse(
            user_id=user['user_id'],
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            role=UserRole(user['role']),
            is_active=user['is_active'],
            created_at=user['created_at']
        ) for user in users]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )
