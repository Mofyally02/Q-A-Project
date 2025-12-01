"""
Client question CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def submit_question(
    db: asyncpg.Connection,
    user_id: UUID,
    question_text: str,
    subject: Optional[str] = None,
    priority: str = "normal",
    image_urls: Optional[List[str]] = None,
    credits_required: int = 1
) -> Dict[str, Any]:
    """Submit a new question"""
    # Check user has enough credits
    user_credits = await db.fetchval("SELECT credits FROM users WHERE id = $1", user_id)
    if user_credits is None:
        raise ValueError("User not found")
    
    if user_credits < credits_required:
        raise ValueError(f"Insufficient credits. Required: {credits_required}, Available: {user_credits}")
    
    # Deduct credits
    new_balance = user_credits - credits_required
    await db.execute("UPDATE users SET credits = $1 WHERE id = $2", new_balance, user_id)
    
    # Create question
    question_id = await db.fetchval("""
        INSERT INTO questions 
        (client_id, question_text, subject, priority, status, credits_used, metadata)
        VALUES ($1, $2, $3, $4, 'pending', $5, $6::jsonb)
        RETURNING id
    """, user_id, question_text, subject, priority, credits_required,
        json.dumps({"image_urls": image_urls or []}))
    
    # Create transaction record
    await db.execute("""
        INSERT INTO transactions 
        (user_id, transaction_type, amount, credits, status, details)
        VALUES ($1, 'question_submission', 0, $2, 'completed', $3::jsonb)
    """, user_id, -credits_required, json.dumps({
        "question_id": str(question_id),
        "question_text": question_text[:100]  # Truncate for transaction record
    }))
    
    # TODO: Queue question for AI processing
    
    return {
        "question_id": question_id,
        "status": "pending",
        "credits_charged": credits_required,
        "new_balance": new_balance
    }


async def get_question_status(
    db: asyncpg.Connection,
    question_id: UUID,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get question status"""
    row = await db.fetchrow("""
        SELECT 
            q.id, q.question_text, q.status, q.subject, q.priority,
            q.credits_used, q.created_at, q.delivered_at,
            q.expert_id, q.answer_id,
            a.answer_text,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name,
            r.rating
        FROM questions q
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users e ON q.expert_id = e.id
        LEFT JOIN ratings r ON q.id = r.question_id AND r.client_id = $2
        WHERE q.id = $1 AND q.client_id = $2
    """, question_id, user_id)
    
    if not row:
        return None
    
    expert_name = None
    if row["expert_first_name"] or row["expert_last_name"]:
        expert_name = f"{row['expert_first_name'] or ''} {row['expert_last_name'] or ''}".strip()
    
    return {
        "question_id": row["id"],
        "status": row["status"],
        "question_text": row["question_text"],
        "answer_text": row["answer_text"],
        "expert_id": row["expert_id"],
        "expert_name": expert_name,
        "submitted_at": row["created_at"],
        "delivered_at": row["delivered_at"],
        "rating": row["rating"],
        "credits_used": row["credits_used"]
    }


async def get_question_history(
    db: asyncpg.Connection,
    user_id: UUID,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get question history"""
    offset = (page - 1) * page_size
    conditions = ["client_id = $1"]
    params = [user_id]
    param_count = 1
    
    if status:
        param_count += 1
        conditions.append(f"status = ${param_count}")
        params.append(status)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM questions WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get questions
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            q.id, q.question_text, q.status, q.credits_used,
            q.created_at, q.delivered_at, q.expert_id, q.answer_id,
            a.answer_text,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name,
            r.rating
        FROM questions q
        LEFT JOIN answers a ON q.answer_id = a.id
        LEFT JOIN users e ON q.expert_id = e.id
        LEFT JOIN ratings r ON q.id = r.question_id AND r.client_id = $1
        WHERE {where_clause}
        ORDER BY q.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    questions = []
    
    for row in rows:
        expert_name = None
        if row["expert_first_name"] or row["expert_last_name"]:
            expert_name = f"{row['expert_first_name'] or ''} {row['expert_last_name'] or ''}".strip()
        
        questions.append({
            "question_id": row["id"],
            "status": row["status"],
            "question_text": row["question_text"],
            "answer_text": row["answer_text"],
            "expert_id": row["expert_id"],
            "expert_name": expert_name,
            "submitted_at": row["created_at"],
            "delivered_at": row["delivered_at"],
            "rating": row["rating"],
            "credits_used": row["credits_used"]
        })
    
    return {
        "questions": questions,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_chat_thread(
    db: asyncpg.Connection,
    question_id: UUID,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get chat thread for question"""
    # Get question details
    question = await db.fetchrow("""
        SELECT 
            q.id, q.question_text, q.status, q.expert_id,
            e.first_name as expert_first_name,
            e.last_name as expert_last_name
        FROM questions q
        LEFT JOIN users e ON q.expert_id = e.id
        WHERE q.id = $1 AND q.client_id = $2
    """, question_id, user_id)
    
    if not question:
        return None
    
    expert_name = None
    if question["expert_first_name"] or question["expert_last_name"]:
        expert_name = f"{question['expert_first_name'] or ''} {question['expert_last_name'] or ''}".strip()
    
    # Get chat messages (if chat table exists, otherwise use question/answer)
    # For now, we'll create messages from question and answer
    messages = []
    
    # Add question as first message
    messages.append({
        "message_id": question_id,  # Using question_id as message_id
        "question_id": question_id,
        "sender_type": "client",
        "message_text": question["question_text"],
        "created_at": dt.utcnow(),  # Would get from question.created_at
        "attachments": None
    })
    
    # Get answer if exists
    answer = await db.fetchrow("""
        SELECT id, answer_text, created_at
        FROM answers
        WHERE question_id = $1
        ORDER BY created_at DESC
        LIMIT 1
    """, question_id)
    
    if answer:
        messages.append({
            "message_id": answer["id"],
            "question_id": question_id,
            "sender_type": "expert",
            "message_text": answer["answer_text"],
            "created_at": answer["created_at"],
            "attachments": None
        })
    
    return {
        "question_id": question_id,
        "question_text": question["question_text"],
        "status": question["status"],
        "messages": messages,
        "expert_id": question["expert_id"],
        "expert_name": expert_name
    }

