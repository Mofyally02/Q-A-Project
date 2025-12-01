"""
Admin Dashboard endpoint
Provides overview statistics and data for admin dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.admin import require_admin_or_super
from app.db.session import get_db
from app.models.user import User
from app.services.admin.admin_service import AdminService
import asyncpg

router = APIRouter()
admin_service = AdminService()


@router.get("/dashboard", summary="Get admin dashboard overview")
async def get_admin_dashboard(
    current_admin: User = Depends(require_admin_or_super),
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Get dashboard overview with statistics, charts, and recent activity
    """
    try:
        # Get statistics from various services
        stats = await admin_service.get_dashboard_stats(db)
        
        # Get chart data
        charts = await admin_service.get_dashboard_charts(db)
        
        # Get recent activity
        recent_activity = await admin_service.get_recent_activity(db, limit=10)
        
        return {
            "success": True,
            "data": {
                "stats": stats,
                "charts": charts,
                "recent_activity": recent_activity
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

