"""
Compliance and audit schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AuditLogResponse(BaseModel):
    """Audit log response schema"""
    id: UUID
    admin_id: UUID
    admin_email: Optional[str] = None
    action_type: str
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Audit log list response"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class ComplianceFlaggedItem(BaseModel):
    """Flagged content item"""
    id: UUID
    type: str  # "question", "answer", "user"
    content_id: UUID
    reason: str  # "ai_content", "plagiarism", "vpn", "suspicious"
    severity: str  # "low", "medium", "high", "critical"
    details: Dict[str, Any]
    flagged_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None


class ComplianceFlaggedResponse(BaseModel):
    """Flagged content response"""
    items: List[ComplianceFlaggedItem]
    total: int
    by_reason: Dict[str, int]
    by_severity: Dict[str, int]


class ComplianceUserHistory(BaseModel):
    """User compliance history"""
    user_id: UUID
    total_violations: int
    violations_by_type: Dict[str, int]
    last_violation: Optional[datetime] = None
    compliance_score: float
    status: str  # "clean", "warning", "flagged", "banned"


class ComplianceStatsResponse(BaseModel):
    """Compliance statistics response"""
    total_flagged: int
    resolved: int
    pending: int
    by_reason: Dict[str, int]
    by_severity: Dict[str, int]
    ai_content_detections: int
    plagiarism_detections: int
    vpn_detections: int
    suspicious_activity: int


class ComplianceFlagRequest(BaseModel):
    """Manual flag request"""
    content_id: UUID
    content_type: str  # "question", "answer", "user"
    reason: str
    severity: str = Field("medium", description="low, medium, high, critical")
    details: Optional[Dict[str, Any]] = None

