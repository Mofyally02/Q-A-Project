from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    CLIENT = "client"
    EXPERT = "expert"
    ADMIN = "admin"

class QuestionType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class QuestionStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    HUMANIZED = "humanized"
    REVIEW = "review"
    DELIVERED = "delivered"
    RATED = "rated"

class CorrectionType(str, Enum):
    TEXT = "text"
    DIGITAL = "digital"
    IMAGE = "image"

# User Models
class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)

class UserResponse(UserBase):
    user_id: UUID
    first_name: str
    last_name: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Authentication Models
class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    role: UserRole = UserRole.CLIENT  # Default to CLIENT - admin can promote later

# Admin role management models
class RoleUpdateRequest(BaseModel):
    user_id: UUID
    new_role: UserRole
    reason: Optional[str] = None

class RoleUpdateResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID
    previous_role: UserRole
    new_role: UserRole

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

# Question Models
class QuestionBase(BaseModel):
    type: QuestionType
    content: Dict[str, Any]
    subject: str = Field(..., max_length=100)

class QuestionCreate(QuestionBase):
    client_id: UUID

class QuestionResponse(QuestionBase):
    question_id: UUID
    client_id: UUID
    status: QuestionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Answer Models
class AnswerBase(BaseModel):
    ai_response: Optional[Dict[str, Any]] = None
    humanized_response: Optional[Dict[str, Any]] = None
    expert_response: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_approved: Optional[bool] = None
    rejection_reason: Optional[str] = None

class AnswerCreate(AnswerBase):
    question_id: UUID

class AnswerResponse(AnswerBase):
    answer_id: UUID
    question_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Rating Models
class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class RatingCreate(RatingBase):
    question_id: UUID
    expert_id: Optional[UUID] = None

class RatingResponse(RatingBase):
    rating_id: UUID
    question_id: UUID
    expert_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Expert Review Models
class ExpertReviewBase(BaseModel):
    is_approved: bool
    rejection_reason: Optional[str] = None
    correction: Optional[Dict[str, Any]] = None

class ExpertReviewCreate(ExpertReviewBase):
    answer_id: UUID
    expert_id: UUID

class ExpertReviewResponse(ExpertReviewBase):
    review_id: UUID
    answer_id: UUID
    expert_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Admin Models
class AdminAnalytics(BaseModel):
    total_questions: int
    avg_rating: float
    rejection_rate: float
    churn_risk_clients: List[UUID]
    recent_activity: List[Dict[str, Any]]

class AdminOverride(BaseModel):
    action: str = Field(..., pattern="^(reassign|approve)$")
    expert_id: Optional[UUID] = None
    reason: str

# Audit Log Models
class AuditLogBase(BaseModel):
    action: str = Field(..., max_length=50)
    user_id: UUID
    question_id: Optional[UUID] = None
    details: Dict[str, Any]

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    log_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
