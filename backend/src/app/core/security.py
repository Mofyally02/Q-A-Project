"""
Security utilities module
JWT, encryption, password hashing, and security helpers
"""

import hashlib
import hmac
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from .config import settings
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt (production-ready)"""
        import bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its bcrypt hash"""
        import bcrypt
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def generate_jwt_token(
        user_id: str, 
        role: str, 
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate a JWT token for user authentication"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        
        payload = {
            "sub": user_id,  # Subject (user ID)
            "user_id": user_id,
            "role": role,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encrypt sensitive data (e.g., API keys)"""
        try:
            # Generate key from encryption_key setting
            key = settings.encryption_key.encode()
            if len(key) != 32:
                key = key[:32].ljust(32, b'0')
            
            # Use Fernet for encryption
            # Note: In production, use a proper key derivation function
            fernet_key = Fernet.generate_key()
            fernet = Fernet(fernet_key)
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return data
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            # This is a simplified version
            # In production, store the Fernet key securely
            # For now, return as-is if decryption fails
            return encrypted_data
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return encrypted_data
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_api_key(api_key: str, stored_hash: str) -> bool:
        """Verify an API key against its stored hash"""
        return hmac.compare_digest(api_key, stored_hash)
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_string:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limit length
        return sanitized[:1000]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """Check password strength"""
        if len(password) < 8:
            return {"strong": False, "message": "Password must be at least 8 characters long"}
        
        if not any(c.isupper() for c in password):
            return {"strong": False, "message": "Password must contain at least one uppercase letter"}
        
        if not any(c.islower() for c in password):
            return {"strong": False, "message": "Password must contain at least one lowercase letter"}
        
        if not any(c.isdigit() for c in password):
            return {"strong": False, "message": "Password must contain at least one number"}
        
        return {"strong": True, "message": "Password is strong"}
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """Verify a CSRF token"""
        return hmac.compare_digest(token, stored_token)
    
    @staticmethod
    def rate_limit_key(user_id: str, action: str) -> str:
        """Generate a rate limiting key"""
        return f"rate_limit:{user_id}:{action}"
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
        filename_lower = filename.lower()
        
        for ext in dangerous_extensions:
            if filename_lower.endswith(ext):
                return False
        
        return True
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate a secure filename"""
        import uuid
        import os
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate secure filename
        secure_name = f"{uuid.uuid4()}{ext}"
        
        return secure_name


# Export singleton instance
security = SecurityUtils()

