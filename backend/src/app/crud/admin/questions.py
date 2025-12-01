"""
Question oversight CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def get_questions(
    db: asyncpg.Connection,
    status: Optional[str] = None,
    subject: Optional[str] = None,
    client_id: Optional[UUID] = None,
    expert_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get questions with filters"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_count = 0
    
    if status:
        param_count += 1
        conditions.append(f"q.status = ${param_count}")
        params.append(status)
    
    if subject:
        param_count += 1
        conditions.append(f"q.subject ILIKE ${param_count}")
        params.append(f"%{subject}%")
    
    if client_id:
        param_count += 1
        conditions.append(f"q.client_id = ${param_count}")
        params.append(client_id)
    
    if expert_id:
        param_count += 1
        conditions.append(f"q.expert_id = ${param_count}")
        params.append(expert_id)
    
    if date_from:
        param_count += 1
        conditions.append(f"q.created_at >= ${param_count}")
        params.append(date_from)
    
    if date_to:
        param_count += 1
        conditions.append(f"q.created_at <= ${param_count}")
        params.append(date_to)
    
    if search:
        param_count += 1
        conditions.append(f"q.question_text ILIKE ${param_count}")
        params.append(f"%{search}%")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM questions q WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get questions with related data
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            q.*,
            u.email as client_email,
            u.first_name as client_first_name,
            u.last_name as client_last_name,
            e.email as expert_email,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name
        FROM questions q
        LEFT JOIN users u ON q.client_id = u.id
        LEFT JOIN users e ON q.expert_id = e.id
        WHERE {where_clause}
        ORDER BY q.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    questions = [dict(row) for row in rows]
    
    return {
        "questions": questions,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_question_by_id(db: asyncpg.Connection, question_id: UUID) -> Optional[Dict[str, Any]]:
    """Get question by ID with full pipeline data"""
    row = await db.fetchrow("""
        SELECT 
            q.*,
            u.email as client_email,
            u.first_name as client_first_name,
            u.last_name as client_last_name,
            e.email as expert_email,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name
        FROM questions q
        LEFT JOIN users u ON q.client_id = u.id
        LEFT JOIN users e ON q.expert_id = e.id
        WHERE q.id = $1
    """, question_id)
    
    if not row:
        return None
    
    question = dict(row)
    
    # Get answer data if exists
    answer_row = await db.fetchrow("""
        SELECT * FROM answers WHERE question_id = $1 ORDER BY created_at DESC LIMIT 1
    """, question_id)
    
    if answer_row:
        question["answer_data"] = dict(answer_row)
    
    # Get admin actions related to this question
    actions = await db.fetch("""
        SELECT * FROM admin_actions 
        WHERE target_type = 'question' AND target_id = $1
        ORDER BY created_at DESC
    """, question_id)
    question["admin_actions"] = [dict(a) for a in actions]
    
    return question


async def reassign_expert(
    db: asyncpg.Connection,
    question_id: UUID,
    new_expert_id: UUID
) -> bool:
    """Reassign question to different expert"""
    result = await db.execute("""
        UPDATE questions 
        SET expert_id = $1, status = 'assigned', updated_at = NOW()
        WHERE id = $2
    """, new_expert_id, question_id)
    return result == "UPDATE 1"


async def force_deliver_question(
    db: asyncpg.Connection,
    question_id: UUID,
    answer_text: Optional[str] = None
) -> bool:
    """Force deliver question (bypass review)"""
    if answer_text:
        # Update or create answer
        await db.execute("""
            INSERT INTO answers (question_id, answer_text, is_delivered, created_at)
            VALUES ($1, $2, TRUE, NOW())
            ON CONFLICT (question_id) 
            DO UPDATE SET answer_text = EXCLUDED.answer_text, is_delivered = TRUE, updated_at = NOW()
        """, question_id, answer_text)
    
    result = await db.execute("""
        UPDATE questions 
        SET status = 'delivered', updated_at = NOW()
        WHERE id = $1
    """, question_id)
    return result == "UPDATE 1"


async def reject_and_correct_question(
    db: asyncpg.Connection,
    question_id: UUID,
    correction: str,
    reason: str
) -> bool:
    """Reject question and add admin correction"""
    # Update answer with correction
    await db.execute("""
        INSERT INTO answers (question_id, answer_text, is_admin_corrected, created_at)
        VALUES ($1, $2, TRUE, NOW())
        ON CONFLICT (question_id)
        DO UPDATE SET answer_text = EXCLUDED.answer_text, is_admin_corrected = TRUE, updated_at = NOW()
    """, question_id, correction)
    
    result = await db.execute("""
        UPDATE questions 
        SET status = 'delivered', updated_at = NOW()
        WHERE id = $1
    """, question_id)
    return result == "UPDATE 1"


async def flag_plagiarism(
    db: asyncpg.Connection,
    question_id: UUID,
    fine_amount: Optional[float] = None
) -> bool:
    """Flag question as plagiarism"""
    result = await db.execute("""
        UPDATE questions 
        SET is_flagged = TRUE, plagiarism_fine = $1, updated_at = NOW()
        WHERE id = $2
    """, fine_amount, question_id)
    return result == "UPDATE 1"


async def escalate_question(
    db: asyncpg.Connection,
    question_id: UUID,
    priority: str = "normal"
) -> bool:
    """Escalate question to super admin"""
    result = await db.execute("""
        UPDATE questions 
        SET is_escalated = TRUE, escalation_priority = $1, updated_at = NOW()
        WHERE id = $2
    """, priority, question_id)
    return result == "UPDATE 1"


async def get_question_stats(db: asyncpg.Connection) -> Dict[str, Any]:
    """Get question statistics"""
    stats = await db.fetchrow("""
        SELECT 
            COUNT(*) as total_questions,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'processing') as processing,
            COUNT(*) FILTER (WHERE status = 'review') as in_review,
            COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
            COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
            COUNT(*) FILTER (WHERE created_at::date = CURRENT_DATE) as delivered_today,
            AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/3600) as avg_response_time_hours,
            COUNT(*) FILTER (WHERE status = 'rejected')::float / NULLIF(COUNT(*), 0) * 100 as rejection_rate
        FROM questions
    """)
    
    # Get by subject
    by_subject = await db.fetch("""
        SELECT subject, COUNT(*) as count
        FROM questions
        GROUP BY subject
        ORDER BY count DESC
    """)
    
    result = dict(stats) if stats else {}
    result["by_subject"] = {row["subject"]: row["count"] for row in by_subject}
    
    return result

