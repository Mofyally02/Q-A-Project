"""
Authentication endpoints
Login and registration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime

from app.db.session import get_auth_db, get_db
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg
from app.core.security import SecurityUtils
from app.core.config import settings
from pydantic import BaseModel, EmailStr
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "client"  # Always default to client for public signup


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    auth_db: asyncpg.Connection = Depends(get_auth_db),
    main_db: asyncpg.Connection = Depends(get_db)
):
    """
    Register a new user
    Only allows client role registration. Experts and admins must be added manually.
    Creates user in both auth database and main database.
    """
    try:
        # Force client role for public registration
        if request.role and request.role != "client":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only client registration is allowed. Experts and admins must be added by administrators."
            )
        
        # Check if user already exists in auth database
        existing_user = await auth_db.fetchrow(
            "SELECT user_id FROM users WHERE email = $1",
            request.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = SecurityUtils.hash_password(request.password)
        
        # Generate user_id
        user_id = uuid4()
        
        # Create user in auth database
        user_data = await auth_db.fetchrow("""
            INSERT INTO users (
                user_id,
                email,
                password_hash,
                first_name,
                last_name,
                role,
                is_active,
                email_verified,
                created_at,
                updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW()
            )
            RETURNING user_id, email, first_name, last_name, role, is_active, email_verified as is_verified
        """,
            user_id,
            request.email,
            password_hash,
            request.first_name,
            request.last_name,
            "client",  # Always client
            True,
            True  # Auto-verify clients
        )
        
        # Create user in main database (for application data)
        try:
            await main_db.execute("""
                INSERT INTO users (
                    id,
                    email,
                    first_name,
                    last_name,
                    role,
                    is_active,
                    credits,
                    created_at,
                    updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, NOW(), NOW()
                )
                ON CONFLICT (id) DO NOTHING
            """,
                user_id,
                request.email,
                request.first_name,
                request.last_name,
                "client",
                True,
                0  # Start with 0 credits
            )
        except Exception as main_db_error:
            logger.warning(f"Failed to create user in main database: {main_db_error}. User created in auth DB only.")
            # Continue - user can still login, main DB entry can be created later
        
        # Generate JWT token
        token = SecurityUtils.generate_jwt_token(
            user_id=str(user_data['user_id']),
            role=user_data['role'],
            email=user_data['email']
        )
        
        return LoginResponse(
            success=True,
            message="Registration successful",
            access_token=token,
            user=UserResponse(
                user_id=str(user_data['user_id']),
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_active=user_data['is_active'],
                is_verified=user_data['is_verified']
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: asyncpg.Connection = Depends(get_auth_db)
):
    """
    Login endpoint
    Supports all user roles: client, expert, admin_editor, super_admin
    """
    try:
        # Find user by email
        user = await db.fetchrow("""
            SELECT user_id, email, password_hash, first_name, last_name, role, is_active, email_verified as is_verified, is_banned
            FROM users
            WHERE email = $1
        """, request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is banned
        if user['is_banned']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is banned"
            )
        
        # Check if user is active
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Verify password
        if not SecurityUtils.verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        await db.execute("""
            UPDATE users
            SET last_login = NOW(),
                updated_at = NOW()
            WHERE user_id = $1
        """, user['user_id'])
        
        # Generate JWT token
        token = SecurityUtils.generate_jwt_token(
            user_id=str(user['user_id']),
            role=user['role'],
            email=user['email']
        )
        
        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=token,
            user=UserResponse(
                user_id=str(user['user_id']),
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                role=user['role'],
                is_active=user['is_active'],
                is_verified=user['is_verified']
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

