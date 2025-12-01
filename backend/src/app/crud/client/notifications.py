"""
Client notification CRUD operations
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
from typing import List


async def get_notifications(
    db: asyncpg.Connection,
    user_id: UUID,
    read: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get notifications for user"""
    offset = (page - 1) * page_size
    conditions = ["user_id = $1"]
    params = [user_id]
    param_count = 1
    
    if read is not None:
        param_count += 1
        conditions.append(f"read = ${param_count}")
        params.append(read)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM notifications WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get unread count
    unread_count = await db.fetchval("""
        SELECT COUNT(*)
        FROM notifications
        WHERE user_id = $1 AND read = FALSE
    """, user_id) or 0
    
    # Get notifications
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            id, title, message, notification_type, read,
            created_at, action_url
        FROM notifications
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    notifications = [dict(row) for row in rows] if rows else []
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def mark_notification_read(
    db: asyncpg.Connection,
    notification_id: UUID,
    user_id: UUID
) -> bool:
    """Mark notification as read"""
    result = await db.execute("""
        UPDATE notifications
        SET read = TRUE, read_at = NOW()
        WHERE id = $1 AND user_id = $2
    """, notification_id, user_id)
    return result == "UPDATE 1"


async def mark_all_notifications_read(
    db: asyncpg.Connection,
    user_id: UUID
) -> int:
    """Mark all notifications as read"""
    result = await db.execute("""
        UPDATE notifications
        SET read = TRUE, read_at = NOW()
        WHERE user_id = $1 AND read = FALSE
    """, user_id)
    # Extract count from result
    return int(result.split()[-1]) if result else 0

