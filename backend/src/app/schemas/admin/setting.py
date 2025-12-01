"""
System settings schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class SystemSettingResponse(BaseModel):
    """System setting response schema"""
    id: UUID
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemSettingListResponse(BaseModel):
    """System settings list response"""
    settings: List[SystemSettingResponse]
    total: int


class SystemSettingUpdate(BaseModel):
    """Update system setting request"""
    value: Dict[str, Any] = Field(..., description="New setting value")
    description: Optional[str] = None


class SystemSettingBulkUpdate(BaseModel):
    """Bulk update system settings"""
    settings: Dict[str, Dict[str, Any]] = Field(..., description="Key-value pairs of settings to update")


class MaintenanceModeResponse(BaseModel):
    """Maintenance mode response"""
    enabled: bool
    message: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None


class MaintenanceModeRequest(BaseModel):
    """Maintenance mode request"""
    enabled: bool = Field(..., description="True to enable, False to disable")
    message: Optional[str] = Field(None, description="Message to show to users")

