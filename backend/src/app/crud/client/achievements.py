"""
Client achievements and streaks CRUD operations
"""

from typing import Dict, Any, List, Optional
import asyncpg
from uuid import UUID
from datetime import datetime, date, timedelta


async def _get_client_id(db: asyncpg.Connection, user_id: UUID) -> Optional[UUID]:
    """Helper function to get client_id from user_id"""
    client_id = await db.fetchval("""
        SELECT client_id FROM clients WHERE user_id = $1
    """, user_id)
    return client_id


async def get_user_achievements(
    db: asyncpg.Connection,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """Get all achievements for a client"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    
    if not client_id:
        return []
    
    achievements = await db.fetch("""
        SELECT 
            achievement_id,
            achievement_type,
            achievement_key,
            title,
            description,
            icon,
            progress,
            target,
            unlocked_at,
            metadata,
            created_at
        FROM achievements
        WHERE client_id = $1
        ORDER BY 
            unlocked_at DESC NULLS LAST,
            created_at DESC
    """, client_id)
    
    return [dict(row) for row in achievements]


async def get_user_streaks(
    db: asyncpg.Connection,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """Get all streaks for a client"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    
    if not client_id:
        return []
    
    streaks = await db.fetch("""
        SELECT 
            streak_id,
            streak_type,
            current_streak,
            longest_streak,
            last_activity_date,
            streak_started_at,
            metadata,
            updated_at
        FROM streaks
        WHERE client_id = $1
        ORDER BY streak_type
    """, client_id)
    
    return [dict(row) for row in streaks]


async def get_achievement_progress(
    db: asyncpg.Connection,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """Get progress for locked achievements"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    
    if not client_id:
        return []
    
    progress = await db.fetch("""
        SELECT 
            achievement_key,
            current_value,
            target_value,
            progress_percentage,
            metadata,
            last_updated
        FROM achievement_progress
        WHERE client_id = $1
        ORDER BY progress_percentage DESC
    """, client_id)
    
    return [dict(row) for row in progress]


async def unlock_achievement(
    db: asyncpg.Connection,
    user_id: UUID,
    achievement_key: str,
    achievement_type: str,
    title: str,
    description: str,
    icon: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Unlock an achievement for a client"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    if not client_id:
        return {}
    
    achievement = await db.fetchrow("""
        INSERT INTO achievements (
            client_id,
            achievement_type,
            achievement_key,
            title,
            description,
            icon,
            progress,
            target,
            unlocked_at,
            metadata
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), $9)
        ON CONFLICT (client_id, achievement_key) 
        DO UPDATE SET
            unlocked_at = COALESCE(achievements.unlocked_at, NOW()),
            updated_at = NOW()
        RETURNING *
    """, client_id, achievement_type, achievement_key, title, description, icon, 1, 1, metadata)
    
    return dict(achievement) if achievement else {}


async def update_streak(
    db: asyncpg.Connection,
    user_id: UUID,
    streak_type: str,
    activity_date: date
) -> Dict[str, Any]:
    """Update or create a streak for a client"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    if not client_id:
        return {}
    
    # Get existing streak
    existing = await db.fetchrow("""
        SELECT * FROM streaks
        WHERE client_id = $1 AND streak_type = $2
    """, client_id, streak_type)
    
    if existing:
        last_date = existing['last_activity_date']
        current_streak = existing['current_streak']
        longest_streak = existing['longest_streak']
        
        # Check if activity is consecutive
        if activity_date == last_date:
            # Same day, no change
            return dict(existing)
        elif activity_date == last_date + timedelta(days=1):
            # Consecutive day, increment streak
            new_streak = current_streak + 1
            longest_streak = max(longest_streak, new_streak)
            streak_started_at = existing['streak_started_at'] or datetime.utcnow()
        else:
            # Streak broken, reset to 1
            new_streak = 1
            streak_started_at = datetime.utcnow()
        
        updated = await db.fetchrow("""
            UPDATE streaks
            SET 
                current_streak = $1,
                longest_streak = $2,
                last_activity_date = $3,
                streak_started_at = $4,
                updated_at = NOW()
            WHERE client_id = $5 AND streak_type = $6
            RETURNING *
        """, new_streak, longest_streak, activity_date, streak_started_at, client_id, streak_type)
        
        return dict(updated) if updated else {}
    else:
        # Create new streak
        new_streak = await db.fetchrow("""
            INSERT INTO streaks (
                client_id,
                streak_type,
                current_streak,
                longest_streak,
                last_activity_date,
                streak_started_at
            )
            VALUES ($1, $2, 1, 1, $3, NOW())
            RETURNING *
        """, client_id, streak_type, activity_date)
        
        return dict(new_streak) if new_streak else {}


async def update_achievement_progress(
    db: asyncpg.Connection,
    user_id: UUID,
    achievement_key: str,
    current_value: int,
    target_value: int,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Update progress towards an achievement"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    if not client_id:
        return {}
    
    progress_percentage = min(100.0, (current_value / target_value * 100) if target_value > 0 else 0.0)
    
    progress = await db.fetchrow("""
        INSERT INTO achievement_progress (
            client_id,
            achievement_key,
            current_value,
            target_value,
            progress_percentage,
            metadata
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (client_id, achievement_key)
        DO UPDATE SET
            current_value = $3,
            target_value = $4,
            progress_percentage = $5,
            metadata = COALESCE($6, achievement_progress.metadata),
            last_updated = NOW()
        RETURNING *
    """, client_id, achievement_key, current_value, target_value, progress_percentage, metadata)
    
    return dict(progress) if progress else {}


async def check_and_unlock_achievements(
    db: asyncpg.Connection,
    user_id: UUID,
    total_questions: int,
    avg_rating: Optional[float],
    current_streak: int
) -> List[Dict[str, Any]]:
    """Check conditions and unlock achievements if criteria are met"""
    # Get client_id from user_id
    client_id = await _get_client_id(db, user_id)
    if not client_id:
        return []
    
    unlocked = []
    
    # Achievement definitions
    achievement_definitions = [
        {
            "key": "10_questions",
            "type": "question_count",
            "title": "Curious Mind",
            "description": "Asked 10 questions",
            "icon": "🎯",
            "condition": lambda: total_questions >= 10
        },
        {
            "key": "50_questions",
            "type": "question_count",
            "title": "Knowledge Seeker",
            "description": "Asked 50 questions",
            "icon": "📚",
            "condition": lambda: total_questions >= 50
        },
        {
            "key": "100_questions",
            "type": "question_count",
            "title": "Question Master",
            "description": "Asked 100 questions",
            "icon": "👑",
            "condition": lambda: total_questions >= 100
        },
        {
            "key": "high_rating",
            "type": "rating",
            "title": "Satisfied Customer",
            "description": "Maintained high ratings (4.5+)",
            "icon": "⭐",
            "condition": lambda: avg_rating is not None and avg_rating >= 4.5
        },
        {
            "key": "7_day_streak",
            "type": "streak",
            "title": "Week Warrior",
            "description": "7-day activity streak",
            "icon": "🔥",
            "condition": lambda: current_streak >= 7
        },
        {
            "key": "30_day_streak",
            "type": "streak",
            "title": "Streak Champion",
            "description": "30-day activity streak",
            "icon": "💪",
            "condition": lambda: current_streak >= 30
        }
    ]
    
    for achievement_def in achievement_definitions:
        if achievement_def["condition"]():
            # Check if already unlocked
            existing = await db.fetchrow("""
                SELECT achievement_id FROM achievements
                WHERE client_id = $1 AND achievement_key = $2
            """, client_id, achievement_def["key"])
            
            if not existing:
                # Unlock achievement
                achievement = await unlock_achievement(
                    db,
                    user_id,
                    achievement_def["key"],
                    achievement_def["type"],
                    achievement_def["title"],
                    achievement_def["description"],
                    achievement_def.get("icon")
                )
                if achievement:
                    unlocked.append(achievement)
    
    return unlocked
