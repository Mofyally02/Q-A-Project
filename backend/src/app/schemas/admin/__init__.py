"""
Admin schemas
Pydantic models for admin API request/response validation
"""

from app.schemas.admin.user import *
from app.schemas.admin.admin import *
from app.schemas.admin.api_key import *
from app.schemas.admin.setting import *
from app.schemas.admin.question import *
from app.schemas.admin.expert import *
from app.schemas.admin.compliance import *
from app.schemas.admin.notification import *
from app.schemas.admin.revenue import *
from app.schemas.admin.override import *

__all__ = [
    # User schemas
    "UserResponse",
    "UserListResponse",
    "UserRoleUpdate",
    "UserBanRequest",
    "UserPasswordReset",
    "UserStatsResponse",
    # Admin schemas
    "AdminInviteRequest",
    "AdminInviteResponse",
    "AdminListResponse",
    "AdminSuspendRequest",
    # API Key schemas
    "APIKeyCreate",
    "APIKeyUpdate",
    "APIKeyResponse",
    "APIKeyListResponse",
    "APIKeyTestResponse",
    # Setting schemas
    "SystemSettingResponse",
    "SystemSettingUpdate",
    "MaintenanceModeResponse",
    # Question schemas
    "QuestionListResponse",
    "QuestionDetailResponse",
    "QuestionReassignRequest",
    "QuestionForceDeliverRequest",
    "QuestionRejectRequest",
    "QuestionPlagiarismFlag",
    "QuestionStatsResponse",
    # Expert schemas
    "ExpertListResponse",
    "ExpertDetailResponse",
    "ExpertPerformanceResponse",
    "ExpertLeaderboardResponse",
    "ExpertStatsResponse",
    # Compliance schemas
    "AuditLogResponse",
    "AuditLogListResponse",
    "ComplianceFlaggedResponse",
    "ComplianceStatsResponse",
    # Notification schemas
    "NotificationBroadcastRequest",
    "NotificationTemplateResponse",
    "NotificationHistoryResponse",
    # Revenue schemas
    "RevenueDashboardResponse",
    "CreditGrantRequest",
    "TransactionResponse",
    # Override schemas
    "OverrideRequest",
    "OverrideResponse",
]

