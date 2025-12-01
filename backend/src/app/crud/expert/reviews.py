"""
Expert review CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def submit_review(
    db: asyncpg.Connection,
    expert_id: UUID,
    answer_id: UUID,
    question_id: UUID,
    is_approved: bool,
    rejection_reason: Optional[str] = None,
    corrections: Optional[Dict[str, Any]] = None,
    review_notes: Optional[str] = None,
    review_time_seconds: Optional[int] = None
) -> Dict[str, Any]:
    """Submit expert review"""
    # Create review record
    review_id = await db.fetchval("""
        INSERT INTO expert_reviews 
        (answer_id, question_id, expert_id, review_status, is_approved,
         rejection_reason, corrections, review_notes, review_time_seconds, completed_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, NOW())
        RETURNING id
    """, answer_id, question_id, expert_id,
        "approved" if is_approved else "rejected",
        is_approved, rejection_reason,
        json.dumps(corrections) if corrections else None,
        review_notes, review_time_seconds)
    
    # Update question status
    if is_approved:
        await db.execute("""
            UPDATE questions
            SET status = 'delivered', updated_at = NOW()
            WHERE id = $1
        """, question_id)
    else:
        await db.execute("""
            UPDATE questions
            SET status = 'needs_revision', updated_at = NOW()
            WHERE id = $1
        """, question_id)
    
    # Update answer status
    await db.execute("""
        UPDATE answers
        SET status = $1, updated_at = NOW()
        WHERE id = $2
    """, "approved" if is_approved else "rejected", answer_id)
    
    # Calculate earnings (simplified: $5 per approved review)
    if is_approved:
        earnings_amount = 5.0
        await db.execute("""
            INSERT INTO transactions 
            (user_id, transaction_type, amount, credits, status, details)
            VALUES ($1, 'expert_earnings', $2, 0, 'completed', $3::jsonb)
        """, expert_id, earnings_amount, json.dumps({
            "review_id": str(review_id),
            "question_id": str(question_id),
            "type": "review_approval"
        }))
    
    return {
        "review_id": review_id,
        "answer_id": answer_id,
        "question_id": question_id,
        "status": "approved" if is_approved else "rejected",
        "is_approved": is_approved
    }


async def get_expert_reviews(
    db: asyncpg.Connection,
    expert_id: UUID,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get expert reviews"""
    offset = (page - 1) * page_size
    conditions = ["er.expert_id = $1"]
    params = [expert_id]
    param_count = 1
    
    if status:
        param_count += 1
        conditions.append(f"er.review_status = ${param_count}")
        params.append(status)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM expert_reviews er WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get reviews
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            er.id as review_id,
            er.answer_id,
            er.question_id,
            q.question_text,
            a.answer_text,
            er.is_approved,
            er.rejection_reason,
            er.corrections,
            er.review_notes,
            er.review_time_seconds,
            er.created_at,
            er.completed_at
        FROM expert_reviews er
        JOIN questions q ON er.question_id = q.id
        LEFT JOIN answers a ON er.answer_id = a.id
        WHERE {where_clause}
        ORDER BY er.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    reviews = []
    
    for row in rows:
        corrections = row["corrections"]
        if corrections and not isinstance(corrections, dict):
            try:
                corrections = json.loads(corrections) if corrections else None
            except:
                corrections = None
        
        reviews.append({
            "review_id": row["review_id"],
            "answer_id": row["answer_id"],
            "question_id": row["question_id"],
            "question_text": row["question_text"],
            "answer_text": row["answer_text"],
            "is_approved": row["is_approved"],
            "rejection_reason": row["rejection_reason"],
            "corrections": corrections,
            "review_notes": row["review_notes"],
            "review_time_seconds": row["review_time_seconds"],
            "created_at": row["created_at"],
            "completed_at": row["completed_at"]
        })
    
    return {
        "reviews": reviews,
        "total": total,
        "page": page,
        "page_size": page_size
    }

