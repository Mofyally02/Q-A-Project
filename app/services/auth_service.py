import asyncpg
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from app.database import get_db
from app.models import UserResponse, LoginRequest, LoginResponse, RegisterRequest, UserRole, TokenData
from app.utils.security import SecurityUtils
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.security_utils = SecurityUtils()
    
    async def create_user(self, user_data: RegisterRequest, db: asyncpg.Connection) -> UserResponse:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await db.fetchrow(
                "SELECT user_id FROM users WHERE email = $1",
                user_data.email
            )
            
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Hash password
            password_hash = self.security_utils.hash_password(user_data.password)
            
            # Generate API key
            api_key = self.security_utils.generate_api_key()
            
            # Insert user
            user_id = await db.fetchval("""
                INSERT INTO users (email, password_hash, first_name, last_name, role, api_key)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING user_id
            """, user_data.email, password_hash, user_data.first_name, 
                user_data.last_name, user_data.role.value, api_key)
            
            # Fetch created user
            user = await db.fetchrow("""
                SELECT user_id, email, first_name, last_name, role, is_active, created_at
                FROM users WHERE user_id = $1
            """, user_id)
            
            return UserResponse(
                user_id=user['user_id'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                role=UserRole(user['role']),
                is_active=user['is_active'],
                created_at=user['created_at']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail="Failed to create user")
    
    async def authenticate_user(self, login_data: LoginRequest, db: asyncpg.Connection) -> Optional[UserResponse]:
        """Authenticate user with email and password"""
        try:
            # Fetch user by email
            user = await db.fetchrow("""
                SELECT user_id, email, password_hash, first_name, last_name, role, is_active, created_at
                FROM users WHERE email = $1
            """, login_data.email)
            
            if not user:
                return None
            
            # Check if user is active
            if not user['is_active']:
                return None
            
            # Verify password
            if not self.security_utils.verify_password(login_data.password, user['password_hash']):
                return None
            
            # Update last login
            await db.execute("""
                UPDATE users SET last_login = $1 WHERE user_id = $2
            """, datetime.utcnow(), user['user_id'])
            
            return UserResponse(
                user_id=user['user_id'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                role=UserRole(user['role']),
                is_active=user['is_active'],
                created_at=user['created_at']
            )
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: UUID, db: asyncpg.Connection) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user = await db.fetchrow("""
                SELECT user_id, email, first_name, last_name, role, is_active, created_at
                FROM users WHERE user_id = $1
            """, user_id)
            
            if not user:
                return None
            
            return UserResponse(
                user_id=user['user_id'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                role=UserRole(user['role']),
                is_active=user['is_active'],
                created_at=user['created_at']
            )
            
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def create_access_token(self, user: UserResponse) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(hours=24)
        payload = {
            "user_id": str(user.user_id),
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return self.security_utils.generate_jwt_token(
            str(user.user_id), 
            user.role.value, 
            timedelta(hours=24)
        )
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        try:
            payload = self.security_utils.verify_jwt_token(token)
            if payload:
                return TokenData(
                    user_id=payload.get("user_id"),
                    role=payload.get("role")
                )
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: asyncpg.Connection = Depends(get_db)
    ) -> UserResponse:
        """Get current authenticated user"""
        token = credentials.credentials
        token_data = self.verify_token(token)
        
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.get_user_by_id(UUID(token_data.user_id), db)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    def require_role(self, required_roles: list[UserRole]):
        """Decorator to require specific roles"""
        def role_checker(current_user: UserResponse = Depends(self.get_current_user)):
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return current_user
        return role_checker
    
    async def login_user(self, login_data: LoginRequest, db: asyncpg.Connection) -> LoginResponse:
        """Login user and return JWT token"""
        user = await self.authenticate_user(login_data, db)
        
        if not user:
            return LoginResponse(
                success=False,
                message="Invalid email or password"
            )
        
        access_token = self.create_access_token(user)
        
        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            user=user
        )
    
    async def register_user(self, user_data: RegisterRequest, db: asyncpg.Connection) -> LoginResponse:
        """Register new user and return JWT token"""
        try:
            user = await self.create_user(user_data, db)
            access_token = self.create_access_token(user)
            
            return LoginResponse(
                success=True,
                message="Registration successful",
                access_token=access_token,
                user=user
            )
        except HTTPException as e:
            return LoginResponse(
                success=False,
                message=e.detail
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return LoginResponse(
                success=False,
                message="Registration failed"
            )

# Global auth service instance
auth_service = AuthService()
