"""
Expert rating CRUD operations
"""

from typing import Dict, Any, List
import asyncpg
from uuid import UUID
from datetime import datetime, timedelta


async def get_expert_ratings(
    db: asyncpg.Connection,
    expert_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get expert ratings"""
    offset = (page - 1) * page_size
    
    # Get total count
    total = await db.fetchval("""
        SELECT COUNT(*)
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        WHERE q.expert_id = $1
    """, expert_id) or 0
    
    # Get ratings
    rows = await db.fetch("""
        SELECT 
            r.id as rating_id,
            r.question_id,
            q.question_text,
            a.answer_text,
            r.score,
            r.comment,
            c.first_name as client_first_name,
            c.last_name as client_last_name,
            r.created_at
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users c ON r.client_id = c.id
        WHERE q.expert_id = $1
        ORDER BY r.created_at DESC
        LIMIT $2 OFFSET $3
    """, expert_id, page_size, offset)
    
    ratings = []
    for row in rows:
        client_name = None
        if row["client_first_name"] or row["client_last_name"]:
            client_name = f"{row['client_first_name'] or ''} {row['client_last_name'] or ''}".strip()
        
        ratings.append({
            "rating_id": row["rating_id"],
            "question_id": row["question_id"],
            "question_text": row["question_text"][:200],  # Truncate
            "answer_text": row["answer_text"][:500] if row["answer_text"] else None,  # Truncate
            "score": row["score"],
            "comment": row["comment"],
            "client_name": client_name,
            "created_at": row["created_at"]
        })
    
    return {
        "ratings": ratings,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_expert_rating_stats(
    db: asyncpg.Connection,
    expert_id: UUID
) -> Dict[str, Any]:
    """Get expert rating statistics"""
    # Average rating
    avg_rating = await db.fetchval("""
        SELECT AVG(r.score)
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        WHERE q.expert_id = $1
    """, expert_id)
    
    # Total ratings
    total_ratings = await db.fetchval("""
        SELECT COUNT(*)
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        WHERE q.expert_id = $1
    """, expert_id) or 0
    
    # Rating distribution
    distribution = await db.fetch("""
        SELECT 
            r.score,
            COUNT(*) as count
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        WHERE q.expert_id = $1
        GROUP BY r.score
        ORDER BY r.score DESC
    """, expert_id)
    
    rating_distribution = {row["score"]: row["count"] for row in distribution}
    
    # Recent ratings (last 10)
    recent_ratings = await db.fetch("""
        SELECT 
            r.id as rating_id,
            r.question_id,
            q.question_text,
            a.answer_text,
            r.score,
            r.comment,
            c.first_name as client_first_name,
            c.last_name as client_last_name,
            r.created_at
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users c ON r.client_id = c.id
        WHERE q.expert_id = $1
        ORDER BY r.created_at DESC
        LIMIT 10
    """, expert_id)
    
    recent_list = []
    for row in recent_ratings:
        client_name = None
        if row["client_first_name"] or row["client_last_name"]:
            client_name = f"{row['client_first_name'] or ''} {row['client_last_name'] or ''}".strip()
        
        recent_list.append({
            "rating_id": row["rating_id"],
            "question_id": row["question_id"],
            "question_text": row["question_text"][:200],
            "answer_text": row["answer_text"][:500] if row["answer_text"] else None,
            "score": row["score"],
            "comment": row["comment"],
            "client_name": client_name,
            "created_at": row["created_at"]
        })
    
    # Rating trend (last 30 days)
    rating_trend = await db.fetch("""
        SELECT 
            DATE(r.created_at) as date,
            AVG(r.score) as avg_score,
            COUNT(*) as count
        FROM ratings r
        JOIN questions q ON r.question_id = q.id
        WHERE q.expert_id = $1
        AND r.created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(r.created_at)
        ORDER BY date ASC
    """, expert_id)
    
    return {
        "expert_id": expert_id,
        "average_rating": float(avg_rating) if avg_rating else 0.0,
        "total_ratings": total_ratings,
        "rating_distribution": rating_distribution,
        "recent_ratings": recent_list,
        "rating_trend": [dict(row) for row in rating_trend]
    }

