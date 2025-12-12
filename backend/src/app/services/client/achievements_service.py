"""
Client achievements and streaks service
Business logic for achievements and streaks
"""

from typing import Dict, Any, List, Optional
import asyncpg
from uuid import UUID
from datetime import date
from app.crud.client import achievements as achievements_crud


class AchievementsService:
    """Service for managing client achievements and streaks"""
    
    @staticmethod
    async def get_achievements_data(
        db: asyncpg.Connection,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get all achievements data for a client"""
        # Get unlocked achievements
        unlocked_achievements = await achievements_crud.get_user_achievements(db, user_id)
        
        # Get progress for locked achievements
        progress_data = await achievements_crud.get_achievement_progress(db, user_id)
        
        # Get streaks
        streaks = await achievements_crud.get_user_streaks(db, user_id)
        
        return {
            "achievements": unlocked_achievements,
            "progress": progress_data,
            "streaks": streaks
        }
    
    @staticmethod
    async def record_question_activity(
        db: asyncpg.Connection,
        user_id: UUID,
        activity_date: date
    ) -> Dict[str, Any]:
        """Record a question activity and update streaks"""
        # Update daily question streak
        streak = await achievements_crud.update_streak(
            db,
            user_id,
            "daily_question",
            activity_date
        )
        
        return {"streak": streak}
    
    @staticmethod
    async def record_login_activity(
        db: asyncpg.Connection,
        user_id: UUID,
        activity_date: date
    ) -> Dict[str, Any]:
        """Record a login activity and update streaks"""
        # Update daily login streak
        streak = await achievements_crud.update_streak(
            db,
            user_id,
            "daily_login",
            activity_date
        )
        
        return {"streak": streak}
    
    @staticmethod
    async def sync_achievements(
        db: asyncpg.Connection,
        user_id: UUID,
        total_questions: int,
        avg_rating: Optional[float],
        current_streak: int
    ) -> List[Dict[str, Any]]:
        """Check and unlock achievements based on current stats"""
        unlocked = await achievements_crud.check_and_unlock_achievements(
            db,
            user_id,
            total_questions,
            avg_rating,
            current_streak
        )
        
        return unlocked

