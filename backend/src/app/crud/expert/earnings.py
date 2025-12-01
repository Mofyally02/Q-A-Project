"""
Expert earnings CRUD operations
"""

from typing import Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime, timedelta


async def get_expert_earnings(
    db: asyncpg.Connection,
    expert_id: UUID
) -> Dict[str, Any]:
    """Get expert earnings"""
    # Total earnings
    total_earnings = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = $1 AND transaction_type = 'expert_earnings' AND status = 'completed'
    """, expert_id) or 0.0
    
    # This month
    earnings_this_month = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = $1 
        AND transaction_type = 'expert_earnings' 
        AND status = 'completed'
        AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
    """, expert_id) or 0.0
    
    # This week
    earnings_this_week = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = $1 
        AND transaction_type = 'expert_earnings' 
        AND status = 'completed'
        AND created_at >= DATE_TRUNC('week', CURRENT_DATE)
    """, expert_id) or 0.0
    
    # Today
    earnings_today = await db.fetchval("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = $1 
        AND transaction_type = 'expert_earnings' 
        AND status = 'completed'
        AND DATE(created_at) = CURRENT_DATE
    """, expert_id) or 0.0
    
    # Review counts
    total_reviews = await db.fetchval("""
        SELECT COUNT(*)
        FROM expert_reviews
        WHERE expert_id = $1 AND is_approved = TRUE
    """, expert_id) or 0
    
    reviews_this_month = await db.fetchval("""
        SELECT COUNT(*)
        FROM expert_reviews
        WHERE expert_id = $1 
        AND is_approved = TRUE
        AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
    """, expert_id) or 0
    
    reviews_this_week = await db.fetchval("""
        SELECT COUNT(*)
        FROM expert_reviews
        WHERE expert_id = $1 
        AND is_approved = TRUE
        AND created_at >= DATE_TRUNC('week', CURRENT_DATE)
    """, expert_id) or 0
    
    reviews_today = await db.fetchval("""
        SELECT COUNT(*)
        FROM expert_reviews
        WHERE expert_id = $1 
        AND is_approved = TRUE
        AND DATE(created_at) = CURRENT_DATE
    """, expert_id) or 0
    
    # Average earnings per review
    avg_earnings_per_review = total_earnings / total_reviews if total_reviews > 0 else 0.0
    
    # Pending payout (simplified: all completed earnings)
    pending_payout = total_earnings  # Would be filtered by payout status
    
    # Last payout
    last_payout = await db.fetchval("""
        SELECT MAX(created_at)
        FROM transactions
        WHERE user_id = $1 AND transaction_type = 'payout'
    """, expert_id)
    
    # Earnings breakdown (by month)
    earnings_breakdown = await db.fetch("""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            SUM(amount) as earnings,
            COUNT(*) as reviews
        FROM transactions
        WHERE user_id = $1 
        AND transaction_type = 'expert_earnings' 
        AND status = 'completed'
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month DESC
        LIMIT 12
    """, expert_id)
    
    return {
        "expert_id": expert_id,
        "total_earnings": float(total_earnings),
        "earnings_this_month": float(earnings_this_month),
        "earnings_this_week": float(earnings_this_week),
        "earnings_today": float(earnings_today),
        "total_reviews": total_reviews,
        "reviews_this_month": reviews_this_month,
        "reviews_this_week": reviews_this_week,
        "reviews_today": reviews_today,
        "average_earnings_per_review": float(avg_earnings_per_review),
        "pending_payout": float(pending_payout),
        "last_payout_at": last_payout,
        "earnings_breakdown": [dict(row) for row in earnings_breakdown]
    }

