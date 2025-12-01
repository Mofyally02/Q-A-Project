"""
Backup and recovery schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class BackupRequest(BaseModel):
    """Backup request"""
    backup_type: str = Field(..., description="full, incremental, or data_only")
    include_files: bool = Field(True, description="Include file uploads")
    description: Optional[str] = Field(None, description="Backup description")


class BackupResponse(BaseModel):
    """Backup response"""
    backup_id: UUID
    backup_type: str
    status: str
    size_bytes: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    download_url: Optional[str] = None


class BackupListResponse(BaseModel):
    """Backup list response"""
    backups: List[BackupResponse]
    total: int
    page: int
    page_size: int


class RestoreRequest(BaseModel):
    """Restore request"""
    backup_id: UUID
    confirm: bool = Field(..., description="Confirmation required")
    restore_type: str = Field("full", description="full or partial")


class RestoreResponse(BaseModel):
    """Restore response"""
    restore_id: UUID
    backup_id: UUID
    status: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None

