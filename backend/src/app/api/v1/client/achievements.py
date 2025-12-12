"""
Client achievements endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from datetime import date
from app.dependencies.client import require_client
from app.db.session import get_db
from app.services.client.achievements_service import AchievementsService
from app.models.user import User

router = APIRouter()
achievements_service = AchievementsService()


@router.get("", summary="Get client achievements and streaks")
async def get_achievements(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get all achievements, progress, and streaks for the current client"""
    try:
        data = await achievements_service.get_achievements_data(db, current_user.id)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch achievements: {str(e)}"
        )


@router.post("/record-question", summary="Record question activity")
async def record_question_activity(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Record a question activity and update streaks"""
    try:
        activity_date = date.today()
        result = await achievements_service.record_question_activity(
            db,
            current_user.id,
            activity_date
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record activity: {str(e)}"
        )


@router.post("/record-login", summary="Record login activity")
async def record_login_activity(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Record a login activity and update streaks"""
    try:
        activity_date = date.today()
        result = await achievements_service.record_login_activity(
            db,
            current_user.id,
            activity_date
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record login: {str(e)}"
        )


@router.post("/sync", summary="Sync achievements based on current stats")
async def sync_achievements(
    current_user: User = Depends(require_client),
    db: asyncpg.Connection = Depends(get_db)
):
    """Check and unlock achievements based on current user stats"""
    try:
        # Get current stats from dashboard
        from app.services.client.dashboard_service import DashboardService
        dashboard_service = DashboardService()
        dashboard_data = await dashboard_service.get_dashboard_data(db, current_user.id)
        
        total_questions = dashboard_data.get("stats", {}).get("total_questions", 0)
        avg_rating = dashboard_data.get("stats", {}).get("average_rating")
        
        # Get current streak
        streaks_data = await achievements_service.get_achievements_data(db, current_user.id)
        current_streak = 0
        for streak in streaks_data.get("streaks", []):
            if streak.get("streak_type") == "daily_question":
                current_streak = streak.get("current_streak", 0)
                break
        
        # Sync achievements
        unlocked = await achievements_service.sync_achievements(
            db,
            current_user.id,
            total_questions,
            avg_rating,
            current_streak
        )
        
        return {
            "success": True,
            "data": {
                "unlocked_count": len(unlocked),
                "unlocked_achievements": unlocked
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync achievements: {str(e)}"
        )

