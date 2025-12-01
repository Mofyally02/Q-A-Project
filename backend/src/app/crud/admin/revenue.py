"""
Revenue management CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime, timedelta
import json


async def get_revenue_dashboard(
    db: asyncpg.Connection
) -> Dict[str, Any]:
    """Get revenue dashboard statistics"""
    # Total revenue (all time)
    total_revenue = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0) 
        FROM transactions 
        WHERE status = 'completed' AND transaction_type = 'purchase'
    """) or 0.0
    
    # Today's revenue
    revenue_today = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'completed' 
        AND transaction_type = 'purchase'
        AND DATE(created_at) = CURRENT_DATE
    """) or 0.0
    
    # This week's revenue
    revenue_this_week = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= DATE_TRUNC('week', CURRENT_DATE)
    """) or 0.0
    
    # This month's revenue
    revenue_this_month = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
    """) or 0.0
    
    # This year's revenue
    revenue_this_year = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= DATE_TRUNC('year', CURRENT_DATE)
    """) or 0.0
    
    # Credits sold
    credits_sold = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
    """) or 0
    
    credits_sold_today = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND DATE(created_at) = CURRENT_DATE
    """) or 0
    
    credits_sold_this_week = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= DATE_TRUNC('week', CURRENT_DATE)
    """) or 0
    
    credits_sold_this_month = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
    """) or 0
    
    # Average transaction value
    total_transactions = await db.fetchval("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
    """) or 0
    
    average_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0.0
    
    # Refund rate
    refunded_count = await db.fetchval("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'refunded'
    """) or 0
    
    refund_rate = (refunded_count / total_transactions * 100) if total_transactions > 0 else 0.0
    
    # Top spending users
    top_spenders = await db.fetch("""
        SELECT 
            u.id, u.email, u.first_name, u.last_name,
            SUM(t.amount) as total_spent,
            COUNT(t.id) as transaction_count
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE t.status = 'completed' AND t.transaction_type = 'purchase'
        GROUP BY u.id, u.email, u.first_name, u.last_name
        ORDER BY total_spent DESC
        LIMIT 10
    """)
    
    # Revenue trend (last 30 days)
    revenue_trend = await db.fetch("""
        SELECT 
            DATE(created_at) as date,
            SUM(amount) as revenue,
            COUNT(*) as transactions
        FROM transactions
        WHERE status = 'completed'
        AND transaction_type = 'purchase'
        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """)
    
    return {
        "total_revenue": float(total_revenue),
        "revenue_today": float(revenue_today),
        "revenue_this_week": float(revenue_this_week),
        "revenue_this_month": float(revenue_this_month),
        "revenue_this_year": float(revenue_this_year),
        "credits_sold": int(credits_sold),
        "credits_sold_today": int(credits_sold_today),
        "credits_sold_this_week": int(credits_sold_this_week),
        "credits_sold_this_month": int(credits_sold_this_month),
        "average_transaction_value": float(average_transaction_value),
        "total_transactions": int(total_transactions),
        "refund_rate": float(refund_rate),
        "top_spending_users": [dict(row) for row in top_spenders],
        "revenue_trend": [dict(row) for row in revenue_trend]
    }


async def get_transactions(
    db: asyncpg.Connection,
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    transaction_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get transactions with filters"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_count = 0
    
    if user_id:
        param_count += 1
        conditions.append(f"t.user_id = ${param_count}")
        params.append(user_id)
    
    if status:
        param_count += 1
        conditions.append(f"t.status = ${param_count}")
        params.append(status)
    
    if transaction_type:
        param_count += 1
        conditions.append(f"t.transaction_type = ${param_count}")
        params.append(transaction_type)
    
    if date_from:
        param_count += 1
        conditions.append(f"t.created_at >= ${param_count}")
        params.append(date_from)
    
    if date_to:
        param_count += 1
        conditions.append(f"t.created_at <= ${param_count}")
        params.append(date_to)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM transactions t WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get total revenue for filtered transactions
    revenue_query = f"""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions t
        WHERE {where_clause} AND status = 'completed'
    """
    total_revenue = await db.fetchval(revenue_query, *params) or 0.0
    
    # Get transactions
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            t.id, t.user_id, u.email as user_email,
            t.transaction_type, t.amount, t.credits, t.status,
            t.payment_method, t.created_at
        FROM transactions t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE {where_clause}
        ORDER BY t.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    transactions = [dict(row) for row in rows]
    
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_revenue": float(total_revenue)
    }


async def grant_credits(
    db: asyncpg.Connection,
    user_id: UUID,
    credits: int,
    reason: str,
    granted_by: UUID,
    expires_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Grant credits to user"""
    # Get current balance
    current_balance = await db.fetchval("""
        SELECT COALESCE(credits, 0) FROM users WHERE id = $1
    """, user_id) or 0
    
    # Update user credits
    new_balance = current_balance + credits
    await db.execute("""
        UPDATE users SET credits = $1 WHERE id = $2
    """, new_balance, user_id)
    
    # Create transaction record
    transaction_id = await db.fetchval("""
        INSERT INTO transactions 
        (user_id, transaction_type, amount, credits, status, details)
        VALUES ($1, 'grant', 0, $2, 'completed', $3::jsonb)
        RETURNING id
    """, user_id, credits, json.dumps({
        "reason": reason,
        "granted_by": str(granted_by),
        "expires_at": expires_at.isoformat() if expires_at else None
    }))
    
    return {
        "user_id": user_id,
        "credits_granted": credits,
        "new_balance": new_balance,
        "granted_at": datetime.utcnow(),
        "expires_at": expires_at
    }


async def revoke_credits(
    db: asyncpg.Connection,
    user_id: UUID,
    credits: int,
    reason: str,
    revoked_by: UUID,
    refund: bool = False
) -> Dict[str, Any]:
    """Revoke credits from user"""
    # Get current balance
    current_balance = await db.fetchval("""
        SELECT COALESCE(credits, 0) FROM users WHERE id = $1
    """, user_id) or 0
    
    if current_balance < credits:
        raise ValueError(f"Insufficient credits. User has {current_balance}, trying to revoke {credits}")
    
    # Update user credits
    new_balance = max(0, current_balance - credits)
    await db.execute("""
        UPDATE users SET credits = $1 WHERE id = $2
    """, new_balance, user_id)
    
    # Create transaction record
    transaction_id = await db.fetchval("""
        INSERT INTO transactions 
        (user_id, transaction_type, amount, credits, status, details)
        VALUES ($1, 'revoke', 0, $2, 'completed', $3::jsonb)
        RETURNING id
    """, user_id, -credits, json.dumps({
        "reason": reason,
        "revoked_by": str(revoked_by),
        "refund": refund
    }))
    
    # If refund requested, create refund transaction
    if refund:
        # Find original purchase transaction to refund
        # This is simplified - in production, you'd track which transaction to refund
        pass
    
    return {
        "user_id": user_id,
        "credits_revoked": credits,
        "new_balance": new_balance,
        "revoked_at": datetime.utcnow(),
        "refunded": refund
    }


async def get_credits_stats(db: asyncpg.Connection) -> Dict[str, Any]:
    """Get credits statistics"""
    # Total credits sold
    total_credits_sold = await db.fetchval("""
        SELECT COALESCE(SUM(credits), 0)
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
    """) or 0
    
    # Credits by package (assuming package info in details)
    credits_by_package = await db.fetch("""
        SELECT 
            details->>'package' as package,
            SUM(credits) as credits
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
        AND details->>'package' IS NOT NULL
        GROUP BY details->>'package'
    """)
    
    # Total revenue from credits
    total_revenue_from_credits = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
    """) or 0.0
    
    # Average credits per user
    users_with_credits = await db.fetchval("""
        SELECT COUNT(DISTINCT user_id)
        FROM transactions
        WHERE transaction_type = 'purchase'
    """) or 0
    
    average_credits_per_user = total_credits_sold / users_with_credits if users_with_credits > 0 else 0.0
    
    # Top packages
    top_packages = await db.fetch("""
        SELECT 
            details->>'package' as package,
            SUM(credits) as credits_sold,
            SUM(amount) as revenue,
            COUNT(*) as transactions
        FROM transactions
        WHERE status = 'completed' AND transaction_type = 'purchase'
        AND details->>'package' IS NOT NULL
        GROUP BY details->>'package'
        ORDER BY credits_sold DESC
        LIMIT 10
    """)
    
    return {
        "total_credits_sold": int(total_credits_sold),
        "credits_by_package": {row["package"]: row["credits"] for row in credits_by_package},
        "total_revenue_from_credits": float(total_revenue_from_credits),
        "average_credits_per_user": float(average_credits_per_user),
        "top_packages": [dict(row) for row in top_packages]
    }

