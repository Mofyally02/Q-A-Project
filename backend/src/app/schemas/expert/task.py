"""
Expert task schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class TaskResponse(BaseModel):
    """Task response"""
    task_id: UUID
    question_id: UUID
    question_text: str
    answer_text: Optional[str] = None
    status: str  # pending, in_progress, reviewed, approved, rejected
    priority: Optional[str] = None
    assigned_at: datetime
    deadline: Optional[datetime] = None
    client_name: Optional[str] = None
    subject: Optional[str] = None


class TaskListResponse(BaseModel):
    """Task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    pending_count: int
    in_progress_count: int


class TaskDetailResponse(BaseModel):
    """Task detail response"""
    task_id: UUID
    question_id: UUID
    question_text: str
    answer_text: Optional[str] = None
    ai_confidence: Optional[float] = None
    originality_score: Optional[float] = None
    status: str
    priority: Optional[str] = None
    assigned_at: datetime
    deadline: Optional[datetime] = None
    client_id: UUID
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    subject: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

