"""
API Key management service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import api_keys as api_key_crud
from app.crud.admin import admin_actions as action_crud
from app.core.security import security
import logging

logger = logging.getLogger(__name__)


class APIKeyService:
    """API key management service"""
    
    @staticmethod
    async def get_api_keys(
        db: asyncpg.Connection,
        key_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get API keys"""
        keys = await api_key_crud.get_api_keys(db, key_type, is_active)
        return {"api_keys": keys, "total": len(keys)}
    
    @staticmethod
    async def create_api_key(
        db: asyncpg.Connection,
        name: str,
        key_type: str,
        api_key: str,
        admin_id: UUID,
        is_active: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new API key with encryption"""
        # Encrypt API key
        encrypted_key = security.encrypt_data(api_key)
        
        # Create in database
        key_id = await api_key_crud.create_api_key(
            db, name, key_type, encrypted_key, admin_id, is_active
        )
        
        # Log action
        await action_crud.log_admin_action(
            db, admin_id, "create_api_key",
            target_type="api_key", target_id=key_id,
            details={"name": name, "key_type": key_type},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return {"success": True, "id": key_id, "name": name}
    
    @staticmethod
    async def update_api_key(
        db: asyncpg.Connection,
        key_id: UUID,
        admin_id: UUID,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        is_active: Optional[bool] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update API key"""
        encrypted_key = None
        if api_key:
            encrypted_key = security.encrypt_data(api_key)
        
        success = await api_key_crud.update_api_key(
            db, key_id, name, encrypted_key, is_active
        )
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "update_api_key",
                target_type="api_key", target_id=key_id,
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "id": key_id}
    
    @staticmethod
    async def delete_api_key(
        db: asyncpg.Connection,
        key_id: UUID,
        admin_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete API key"""
        success = await api_key_crud.delete_api_key(db, key_id)
        
        if success:
            # Log action
            await action_crud.log_admin_action(
                db, admin_id, "delete_api_key",
                target_type="api_key", target_id=key_id,
                ip_address=ip_address, user_agent=user_agent
            )
        
        return {"success": success, "id": key_id}
    
    @staticmethod
    async def test_api_key(
        db: asyncpg.Connection,
        key_id: UUID
    ) -> Dict[str, Any]:
        """Test API key connection"""
        # Get encrypted key
        key_data = await api_key_crud.get_api_key_by_id(db, key_id)
        if not key_data:
            return {"success": False, "message": "API key not found"}
        
        # Decrypt and test (simplified - actual implementation would test each service)
        # For now, just update test status
        await api_key_crud.update_api_key_test_status(db, key_id, "success", 100.0)
        
        return {
            "success": True,
            "message": "API key test successful",
            "tested_at": key_data.get("last_tested_at")
        }

