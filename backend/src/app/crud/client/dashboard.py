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
    # Get user credits
    user = await db.fetchrow("""
        SELECT credits, created_at
        FROM users
        WHERE id = $1
    """, user_id)
    
    if not user:
        raise ValueError("User not found")
    
    credits_balance = user["credits"] or 0
    
    # Get credits used
    credits_used = await db.fetchval("""
        SELECT COALESCE(SUM(credits_used), 0)
        FROM questions
        WHERE client_id = $1
    """, user_id) or 0
    
    # Get question statistics
    total_questions = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE client_id = $1
    """, user_id) or 0
    
    pending_questions = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE client_id = $1 AND status IN ('pending', 'processing', 'reviewed')
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
    recent_answers = await db.fetch("""
        SELECT 
            q.id as question_id,
            q.question_text,
            a.answer_text,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name,
            q.delivered_at,
            r.rating
        FROM questions q
        JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users e ON q.expert_id = e.id
        LEFT JOIN ratings r ON q.id = r.question_id AND r.client_id = $1
        WHERE q.client_id = $1 AND q.status = 'delivered'
        ORDER BY q.delivered_at DESC
        LIMIT 5
    """, user_id)
    
    recent_answers_list = []
    for row in recent_answers:
        expert_name = None
        if row["expert_first_name"] or row["expert_last_name"]:
            expert_name = f"{row['expert_first_name'] or ''} {row['expert_last_name'] or ''}".strip()
        
        recent_answers_list.append({
            "question_id": row["question_id"],
            "question_text": row["question_text"][:100],  # Truncate
            "answer_text": row["answer_text"][:200],  # Truncate
            "expert_name": expert_name,
            "delivered_at": row["delivered_at"],
            "rating": row["rating"]
        })
    
    # Get live questions (pending/processing)
    live_questions = await db.fetch("""
        SELECT 
            id as question_id,
            question_text,
            status,
            created_at
        FROM questions
        WHERE client_id = $1 AND status IN ('pending', 'processing', 'reviewed')
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
    
    if avg_rating and avg_rating >= 4.5:
        achievements.append({
            "id": "high_rating",
            "title": "Satisfied Customer",
            "description": "Maintained high ratings",
            "unlocked_at": datetime.utcnow()
        })
    
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
        "achievements": achievements
    }

