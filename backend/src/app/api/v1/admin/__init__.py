"""
Admin API routes
All admin endpoints with proper permissions
"""

from fastapi import APIRouter
from app.api.v1.admin import users, api_keys, settings, questions, experts, compliance, admins, notifications, revenue, override, queues, backup, dashboard

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Include sub-routers
admin_router.include_router(dashboard.router, tags=["admin-dashboard"])
admin_router.include_router(users.router, prefix="/users", tags=["admin-users"])
admin_router.include_router(api_keys.router, prefix="/api-keys", tags=["admin-api-keys"])
admin_router.include_router(settings.router, prefix="/settings", tags=["admin-settings"])
admin_router.include_router(questions.router, prefix="/questions", tags=["admin-questions"])
admin_router.include_router(experts.router, prefix="/experts", tags=["admin-experts"])
admin_router.include_router(compliance.router, tags=["admin-compliance"])
admin_router.include_router(admins.router, prefix="/admins", tags=["admin-admins"])
admin_router.include_router(notifications.router, prefix="/notifications", tags=["admin-notifications"])
admin_router.include_router(revenue.router, prefix="/revenue", tags=["admin-revenue"])
admin_router.include_router(override.router, prefix="/override", tags=["admin-override"])
admin_router.include_router(queues.router, prefix="/queues", tags=["admin-queues"])
admin_router.include_router(backup.router, prefix="/backup", tags=["admin-backup"])

