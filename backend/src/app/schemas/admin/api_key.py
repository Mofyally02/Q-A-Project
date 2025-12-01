"""
API Key management schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class APIKeyCreate(BaseModel):
    """Create API key request"""
    name: str = Field(..., min_length=1, max_length=255)
    key_type: str = Field(..., description="openai, anthropic, turnitin, etc.")
    api_key: str = Field(..., description="The actual API key to encrypt and store")
    is_active: bool = Field(True, description="Whether key is active")


class APIKeyUpdate(BaseModel):
    """Update API key request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = Field(None, description="New API key value")
    is_active: Optional[bool] = None


class APIKeyResponse(BaseModel):
    """API key response schema"""
    id: UUID
    name: str
    key_type: str
    is_active: bool
    last_tested_at: Optional[datetime] = None
    last_tested_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """API key list response"""
    api_keys: List[APIKeyResponse]
    total: int


class APIKeyTestResponse(BaseModel):
    """API key test response"""
    success: bool
    message: str
    tested_at: datetime
    response_time_ms: Optional[float] = None


class APIKeyRotateResponse(BaseModel):
    """API key rotation response"""
    old_key_id: UUID
    new_key_id: UUID
    rotated_at: datetime

