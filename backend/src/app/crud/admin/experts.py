"""
Expert management CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime


async def get_experts(
    db: asyncpg.Connection,
    is_active: Optional[bool] = None,
    is_suspended: Optional[bool] = None,
    min_rating: Optional[float] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get experts with filters"""
    offset = (page - 1) * page_size
    conditions = ["u.role = 'expert'"]
    params = []
    param_count = 0
    
    if is_active is not None:
        param_count += 1
        conditions.append(f"u.is_active = ${param_count}")
        params.append(is_active)
    
    if is_suspended is not None:
        param_count += 1
        conditions.append(f"u.is_banned = ${param_count}")
        params.append(is_suspended)
    
    if min_rating is not None:
        param_count += 1
        conditions.append(f"COALESCE(e.rating, 0) >= ${param_count}")
        params.append(min_rating)
    
    if search:
        param_count += 1
        conditions.append(f"(u.email ILIKE ${param_count} OR u.first_name ILIKE ${param_count} OR u.last_name ILIKE ${param_count})")
        params.append(f"%{search}%")
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*) 
        FROM users u
        LEFT JOIN experts e ON u.id = e.user_id
        WHERE {where_clause}
    """
    total = await db.fetchval(count_query, *params)
    
    # Get experts
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            u.id,
            u.email,
            u.first_name,
            u.last_name,
            u.is_active,
            u.is_banned as is_suspended,
            COALESCE(e.total_questions_answered, 0) as total_questions_answered,
            COALESCE(e.rating, 0) as average_rating,
            u.last_active,
            u.created_at
        FROM users u
        LEFT JOIN experts e ON u.id = e.user_id
        WHERE {where_clause}
        ORDER BY COALESCE(e.rating, 0) DESC, u.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    experts = [dict(row) for row in rows]
    
    return {
        "experts": experts,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_expert_by_id(db: asyncpg.Connection, expert_id: UUID) -> Optional[Dict[str, Any]]:
    """Get expert by ID with full details"""
    row = await db.fetchrow("""
        SELECT 
            u.id,
            u.email,
            u.first_name,
            u.last_name,
            u.is_active,
            u.is_banned as is_suspended,
            COALESCE(e.total_questions_answered, 0) as total_questions_answered,
            COALESCE(e.rating, 0) as average_rating,
            COALESCE(e.total_earnings, 0) as total_earnings,
            COALESCE(e.response_time_avg_hours, 0) as response_time_avg_hours,
            COALESCE(e.rejection_rate, 0) as rejection_rate,
            COALESCE(e.on_time_delivery_rate, 0) as on_time_delivery_rate,
            COALESCE(e.compliance_score, 100) as compliance_score,
            u.last_active,
            u.created_at
        FROM users u
        LEFT JOIN experts e ON u.id = e.user_id
        WHERE u.id = $1 AND u.role = 'expert'
    """, expert_id)
    
    if not row:
        return None
    
    expert = dict(row)
    
    # Get active questions count
    active_count = await db.fetchval("""
        SELECT COUNT(*) FROM questions 
        WHERE expert_id = $1 AND status IN ('assigned', 'review', 'processing')
    """, expert_id)
    expert["active_questions"] = active_count
    
    return expert


async def suspend_expert(
    db: asyncpg.Connection,
    expert_id: UUID,
    suspended: bool
) -> bool:
    """Suspend or activate expert"""
    result = await db.execute("""
        UPDATE users 
        SET is_banned = $1, updated_at = NOW()
        WHERE id = $2 AND role = 'expert'
    """, suspended, expert_id)
    return result == "UPDATE 1"


async def get_expert_performance(
    db: asyncpg.Connection,
    expert_id: UUID,
    period: str = "all_time"
) -> Dict[str, Any]:
    """Get expert performance metrics for period"""
    date_filter = ""
    if period == "today":
        date_filter = "AND q.created_at::date = CURRENT_DATE"
    elif period == "week":
        date_filter = "AND q.created_at >= CURRENT_DATE - INTERVAL '7 days'"
    elif period == "month":
        date_filter = "AND q.created_at >= DATE_TRUNC('month', CURRENT_DATE)"
    
    row = await db.fetchrow(f"""
        SELECT 
            COUNT(*) as questions_answered,
            AVG(r.rating) as average_rating,
            SUM(e.earnings) as total_earnings,
            AVG(EXTRACT(EPOCH FROM (q.delivered_at - q.created_at))/3600) as response_time_avg_hours,
            COUNT(*) FILTER (WHERE q.status = 'rejected')::float / NULLIF(COUNT(*), 0) * 100 as rejection_rate,
            COUNT(*) FILTER (WHERE q.delivered_at <= q.due_date)::float / NULLIF(COUNT(*), 0) * 100 as on_time_delivery_rate
        FROM questions q
        LEFT JOIN ratings r ON q.id = r.question_id
        LEFT JOIN expert_earnings e ON q.expert_id = e.expert_id AND q.id = e.question_id
        WHERE q.expert_id = $1 AND q.status = 'delivered'
        {date_filter}
    """, expert_id)
    
    return dict(row) if row else {}


async def get_expert_leaderboard(
    db: asyncpg.Connection,
    period: str = "all_time",
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get expert leaderboard"""
    date_filter = ""
    if period == "week":
        date_filter = "AND q.created_at >= CURRENT_DATE - INTERVAL '7 days'"
    elif period == "month":
        date_filter = "AND q.created_at >= DATE_TRUNC('month', CURRENT_DATE)"
    
    rows = await db.fetch(f"""
        SELECT 
            u.id as expert_id,
            CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, '')) as expert_name,
            COUNT(q.id) as questions_answered,
            AVG(r.rating) as average_rating,
            SUM(e.earnings) as total_earnings,
            COALESCE(exp.compliance_score, 100) as compliance_score
        FROM users u
        LEFT JOIN questions q ON u.id = q.expert_id AND q.status = 'delivered' {date_filter}
        LEFT JOIN ratings r ON q.id = r.question_id
        LEFT JOIN expert_earnings e ON q.expert_id = e.expert_id AND q.id = e.question_id
        LEFT JOIN experts exp ON u.id = exp.user_id
        WHERE u.role = 'expert' AND u.is_active = TRUE
        GROUP BY u.id, u.first_name, u.last_name, exp.compliance_score
        ORDER BY questions_answered DESC, average_rating DESC
        LIMIT $1
    """, limit)
    
    leaderboard = []
    for idx, row in enumerate(rows, 1):
        entry = dict(row)
        entry["rank"] = idx
        leaderboard.append(entry)
    
    return leaderboard


async def get_expert_stats(db: asyncpg.Connection) -> Dict[str, Any]:
    """Get expert statistics"""
    stats = await db.fetchrow("""
        SELECT 
            COUNT(*) FILTER (WHERE u.role = 'expert') as total_experts,
            COUNT(*) FILTER (WHERE u.role = 'expert' AND u.is_active = TRUE) as active_experts,
            COUNT(*) FILTER (WHERE u.role = 'expert' AND u.is_banned = TRUE) as suspended_experts,
            AVG(e.rating) as average_rating_all,
            SUM(e.total_questions_answered) as total_questions_answered,
            SUM(e.total_earnings) as total_earnings
        FROM users u
        LEFT JOIN experts e ON u.id = e.user_id
        WHERE u.role = 'expert'
    """)
    
    return dict(stats) if stats else {}

