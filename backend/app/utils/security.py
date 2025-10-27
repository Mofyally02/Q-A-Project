import hashlib
import hmac
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, password_hash = hashed_password.split(":")
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except ValueError:
            return False
    
    @staticmethod
    def generate_jwt_token(user_id: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """Generate a JWT token for user authentication"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encrypt sensitive data"""
        try:
            key = settings.encryption_key.encode()
            if len(key) != 32:
                key = key[:32].ljust(32, b'0')
            
            fernet = Fernet(Fernet.generate_key())
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return data
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            key = settings.encryption_key.encode()
            if len(key) != 32:
                key = key[:32].ljust(32, b'0')
            
            fernet = Fernet(Fernet.generate_key())
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
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
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return {"strong": False, "message": "Password must contain at least one special character"}
        
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
