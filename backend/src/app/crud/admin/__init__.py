"""
Admin CRUD operations
Database operations for admin features
"""

from app.crud.admin.users import *
from app.crud.admin.api_keys import *
from app.crud.admin.settings import *
from app.crud.admin.admin_actions import *
from app.crud.admin.questions import *
from app.crud.admin.experts import *
from app.crud.admin.compliance import *
from app.crud.admin.admins import *
from app.crud.admin.notifications import *
from app.crud.admin.revenue import *
from app.crud.admin.override import *
from app.crud.admin.queues import *
from app.crud.admin.backup import *

__all__ = [
    # Users
    "get_users",
    "get_user_by_id",
    "update_user_role",
    "ban_user",
    # API Keys
    "get_api_keys",
    "create_api_key",
    "update_api_key",
    "delete_api_key",
    # Settings
    "get_system_settings",
    "update_system_setting",
    # Admin Actions
    "log_admin_action",
    "get_admin_actions",
    # Questions
    "get_questions",
    "get_question_by_id",
    "reassign_expert",
    "force_deliver_question",
    "reject_and_correct_question",
    "flag_plagiarism",
    "escalate_question",
    "get_question_stats",
    # Experts
    "get_experts",
    "get_expert_by_id",
    "suspend_expert",
    "get_expert_performance",
    "get_expert_leaderboard",
    "get_expert_stats",
    # Compliance
    "get_flagged_content",
    "get_user_compliance_history",
    "create_compliance_flag",
    "resolve_compliance_flag",
    "get_compliance_stats",
    "export_audit_logs",
]

