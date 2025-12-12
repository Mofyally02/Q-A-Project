"""
Client dashboard CRUD operations
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime, timedelta


async def get_dashboard_data(
    db: asyncpg.Connection,
    user_id: UUID
) -> Dict[str, Any]:
    """Get client dashboard data"""
    # Get user credits from clients table
    # If client record doesn't exist, create it with default values
    client_data = await db.fetchrow("""
        SELECT 
            credits_remaining,
            credits_total,
            created_at
        FROM clients
        WHERE user_id = $1
    """, user_id)
    
    if not client_data:
        # Create client record if it doesn't exist
        try:
            await db.execute("""
                INSERT INTO clients (user_id, credits_remaining, credits_total, subscription_type, subscription_status)
                VALUES ($1, 100, 100, 'free', 'active')
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)
            
            # Fetch the newly created record
            client_data = await db.fetchrow("""
                SELECT 
                    credits_remaining,
                    credits_total,
                    created_at
                FROM clients
                WHERE user_id = $1
            """, user_id)
        except Exception as e:
            # If insert fails, use default values
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to create client record for user {user_id}: {e}")
            client_data = None
    
    # Use client data or defaults
    if client_data:
        credits_balance = client_data["credits_remaining"] or 0
        credits_total = client_data["credits_total"] or 0
        # Calculate credits used: total - remaining
        credits_used = max(0, credits_total - credits_balance)
    else:
        # Fallback to default values if client record still doesn't exist
        credits_balance = 100
        credits_total = 100
        credits_used = 0
    
    # Get question statistics
    total_questions = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE client_id = $1
    """, user_id) or 0
    
    pending_questions = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE client_id = $1 AND status IN ('submitted', 'processing', 'ai_generated', 'humanized', 'expert_review')
    """, user_id) or 0
    
    answered_questions = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE client_id = $1 AND status = 'delivered'
    """, user_id) or 0
    
    # Get average rating
    avg_rating = await db.fetchval("""
        SELECT AVG(rating)
        FROM ratings
        WHERE client_id = $1
    """, user_id)
    
    # Get recent answers (last 5)
    # Note: Expert info removed since users table is in different database (qa_auth)
    recent_answers = await db.fetch("""
        SELECT 
            q.question_id,
            COALESCE(q.subject, 'Question') as question_text,
            COALESCE(a.humanized_response->>'text', a.ai_response->>'text', 'Answer') as answer_text,
            q.delivered_at,
            r.rating
        FROM questions q
        JOIN answers a ON q.question_id = a.question_id
        LEFT JOIN ratings r ON q.question_id = r.question_id AND r.client_id = $1
        WHERE q.client_id = $1 AND q.status = 'delivered'
        ORDER BY q.delivered_at DESC
        LIMIT 5
    """, user_id)
    
    recent_answers_list = []
    for row in recent_answers:
        recent_answers_list.append({
            "question_id": row["question_id"],
            "question_text": row["question_text"][:100],  # Truncate
            "answer_text": row["answer_text"][:200],  # Truncate
            "expert_name": "Expert",  # Placeholder - expert info requires cross-database query
            "delivered_at": row["delivered_at"],
            "rating": row["rating"]
        })
    
    # Get live questions (pending/processing)
    live_questions = await db.fetch("""
        SELECT 
            question_id,
            COALESCE(subject, content->>'text', 'Question') as question_text,
            status,
            created_at
        FROM questions
        WHERE client_id = $1 AND status IN ('submitted', 'processing', 'ai_generated', 'humanized', 'expert_review')
        ORDER BY created_at DESC
        LIMIT 10
    """, user_id)
    
    live_questions_list = []
    for row in live_questions:
        # Estimate completion (simplified - would be calculated based on queue)
        estimated_completion = row["created_at"] + timedelta(hours=2)
        
        live_questions_list.append({
            "question_id": row["question_id"],
            "question_text": row["question_text"][:100],  # Truncate
            "status": row["status"],
            "submitted_at": row["created_at"],
            "estimated_completion": estimated_completion
        })
    
    # Recommended actions (simplified)
    recommended_actions = []
    if credits_balance < 10:
        recommended_actions.append({
            "type": "topup",
            "title": "Low Credits",
            "message": "You're running low on credits. Top up now!",
            "action_url": "/client/wallet"
        })
    
    if pending_questions == 0 and total_questions == 0:
        recommended_actions.append({
            "type": "ask_question",
            "title": "Get Started",
            "message": "Ask your first question!",
            "action_url": "/client/ask"
        })
    
    # Achievements (simplified)
    achievements = []
    if total_questions >= 10:
        achievements.append({
            "id": "10_questions",
            "title": "Curious Mind",
            "description": "Asked 10 questions",
            "unlocked_at": datetime.utcnow()
        })
    
    # Get actual achievements from database
    from app.crud.client import achievements as achievements_crud
    
    # Get unlocked achievements
    unlocked_achievements = await achievements_crud.get_user_achievements(db, user_id)
    
    # Get streaks
    streaks = await achievements_crud.get_user_streaks(db, user_id)
    
    # Get current streak for achievement checking
    current_streak = 0
    for streak in streaks:
        if streak.get("streak_type") == "daily_question":
            current_streak = streak.get("current_streak", 0)
            break
    
    # Sync and check for new achievements
    newly_unlocked = await achievements_crud.check_and_unlock_achievements(
        db,
        user_id,
        total_questions,
        float(avg_rating) if avg_rating else None,
        current_streak
    )
    
    # Refresh achievements list if new ones were unlocked
    if newly_unlocked:
        unlocked_achievements = await achievements_crud.get_user_achievements(db, user_id)
    
    return {
        "stats": {
            "total_credits": credits_balance + credits_used,  # Total ever had
            "credits_used": credits_used,
            "credits_remaining": credits_balance,
            "total_questions": total_questions,
            "pending_questions": pending_questions,
            "answered_questions": answered_questions,
            "average_rating": float(avg_rating) if avg_rating else None
        },
        "recent_answers": recent_answers_list,
        "live_questions": live_questions_list,
        "recommended_actions": recommended_actions,
        "achievements": [dict(a) for a in unlocked_achievements],
        "streaks": [dict(s) for s in streaks],
        "newly_unlocked": [dict(a) for a in newly_unlocked]
    }

