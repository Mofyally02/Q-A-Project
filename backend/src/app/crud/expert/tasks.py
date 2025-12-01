"""
Expert task CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime


async def get_expert_tasks(
    db: asyncpg.Connection,
    expert_id: UUID,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get expert tasks"""
    offset = (page - 1) * page_size
    conditions = ["expert_id = $1"]
    params = [expert_id]
    param_count = 1
    
    if status:
        param_count += 1
        conditions.append(f"status = ${param_count}")
        params.append(status)
    else:
        # Default to pending and in_progress
        param_count += 1
        conditions.append(f"status IN ('pending', 'in_progress', 'reviewed')")
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM questions WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get pending and in_progress counts
    pending_count = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE expert_id = $1 AND status = 'pending'
    """, expert_id) or 0
    
    in_progress_count = await db.fetchval("""
        SELECT COUNT(*)
        FROM questions
        WHERE expert_id = $1 AND status = 'in_progress'
    """, expert_id) or 0
    
    # Get tasks
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            q.id as task_id,
            q.id as question_id,
            q.question_text,
            a.answer_text,
            q.status,
            q.priority,
            q.created_at as assigned_at,
            q.metadata,
            c.first_name as client_first_name,
            c.last_name as client_last_name,
            q.subject
        FROM questions q
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users c ON q.client_id = c.id
        WHERE {where_clause}
        ORDER BY 
            CASE q.priority
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'normal' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
            END,
            q.created_at ASC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    tasks = []
    
    for row in rows:
        client_name = None
        if row["client_first_name"] or row["client_last_name"]:
            client_name = f"{row['client_first_name'] or ''} {row['client_last_name'] or ''}".strip()
        
        # Calculate deadline (simplified: 24 hours from assignment)
        deadline = row["assigned_at"]
        if deadline:
            from datetime import timedelta
            deadline = deadline + timedelta(hours=24)
        
        tasks.append({
            "task_id": row["task_id"],
            "question_id": row["question_id"],
            "question_text": row["question_text"][:200],  # Truncate
            "answer_text": row["answer_text"][:500] if row["answer_text"] else None,  # Truncate
            "status": row["status"],
            "priority": row["priority"],
            "assigned_at": row["assigned_at"],
            "deadline": deadline,
            "client_name": client_name,
            "subject": row["subject"]
        })
    
    return {
        "tasks": tasks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count
    }


async def get_task_detail(
    db: asyncpg.Connection,
    task_id: UUID,
    expert_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get task detail"""
    row = await db.fetchrow("""
        SELECT 
            q.id as task_id,
            q.id as question_id,
            q.question_text,
            a.answer_text,
            a.ai_confidence,
            a.originality_score,
            q.status,
            q.priority,
            q.created_at as assigned_at,
            q.metadata,
            q.client_id,
            c.first_name as client_first_name,
            c.last_name as client_last_name,
            c.email as client_email,
            q.subject
        FROM questions q
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users c ON q.client_id = c.id
        WHERE q.id = $1 AND q.expert_id = $2
    """, task_id, expert_id)
    
    if not row:
        return None
    
    client_name = None
    if row["client_first_name"] or row["client_last_name"]:
        client_name = f"{row['client_first_name'] or ''} {row['client_last_name'] or ''}".strip()
    
    # Calculate deadline
    deadline = row["assigned_at"]
    if deadline:
        from datetime import timedelta
        deadline = deadline + timedelta(hours=24)
    
    metadata = row["metadata"] if isinstance(row["metadata"], dict) else {}
    
    return {
        "task_id": row["task_id"],
        "question_id": row["question_id"],
        "question_text": row["question_text"],
        "answer_text": row["answer_text"],
        "ai_confidence": float(row["ai_confidence"]) if row["ai_confidence"] else None,
        "originality_score": float(row["originality_score"]) if row["originality_score"] else None,
        "status": row["status"],
        "priority": row["priority"],
        "assigned_at": row["assigned_at"],
        "deadline": deadline,
        "client_id": row["client_id"],
        "client_name": client_name,
        "client_email": row["client_email"],
        "subject": row["subject"],
        "metadata": metadata
    }


async def start_task(
    db: asyncpg.Connection,
    task_id: UUID,
    expert_id: UUID
) -> bool:
    """Start working on a task"""
    result = await db.execute("""
        UPDATE questions
        SET status = 'in_progress', updated_at = NOW()
        WHERE id = $1 AND expert_id = $2 AND status = 'pending'
    """, task_id, expert_id)
    return result == "UPDATE 1"

