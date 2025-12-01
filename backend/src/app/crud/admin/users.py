"""
User management CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime


async def get_users(
    db: asyncpg.Connection,
    role: Optional[str] = None,
    is_banned: Optional[bool] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get users with filters"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_count = 0
    
    if role:
        param_count += 1
        conditions.append(f"role = ${param_count}")
        params.append(role)
    
    if is_banned is not None:
        param_count += 1
        conditions.append(f"is_banned = ${param_count}")
        params.append(is_banned)
    
    if is_active is not None:
        param_count += 1
        conditions.append(f"is_active = ${param_count}")
        params.append(is_active)
    
    if search:
        param_count += 1
        conditions.append(f"(email ILIKE ${param_count} OR first_name ILIKE ${param_count} OR last_name ILIKE ${param_count})")
        params.append(f"%{search}%")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM users WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get users
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT * FROM users 
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    users = [dict(row) for row in rows]
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_user_by_id(db: asyncpg.Connection, user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    row = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return dict(row) if row else None


async def update_user_role(
    db: asyncpg.Connection,
    user_id: UUID,
    new_role: str,
    updated_by: UUID
) -> bool:
    """Update user role"""
    result = await db.execute(
        "UPDATE users SET role = $1, updated_at = NOW() WHERE id = $2",
        new_role, user_id
    )
    return result == "UPDATE 1"


async def ban_user(
    db: asyncpg.Connection,
    user_id: UUID,
    banned: bool,
    banned_by: UUID,
    reason: Optional[str] = None
) -> bool:
    """Ban or unban user"""
    if banned:
        result = await db.execute(
            """
            UPDATE users 
            SET is_banned = TRUE, banned_at = NOW(), banned_by_id = $1, updated_at = NOW()
            WHERE id = $2
            """,
            banned_by, user_id
        )
    else:
        result = await db.execute(
            """
            UPDATE users 
            SET is_banned = FALSE, banned_at = NULL, banned_by_id = NULL, updated_at = NOW()
            WHERE id = $1
            """,
            user_id
        )
    return result == "UPDATE 1"


async def reset_user_password(
    db: asyncpg.Connection,
    user_id: UUID,
    new_password_hash: str
) -> bool:
    """Reset user password"""
    result = await db.execute(
        "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
        new_password_hash, user_id
    )
    return result == "UPDATE 1"


async def promote_to_expert(
    db: asyncpg.Connection,
    user_id: UUID,
    specialization: Optional[str] = None
) -> bool:
    """Promote user to expert"""
    result = await db.execute(
        "UPDATE users SET role = 'expert', updated_at = NOW() WHERE id = $1",
        user_id
    )
    return result == "UPDATE 1"


async def get_user_stats(db: asyncpg.Connection) -> Dict[str, Any]:
    """Get user statistics"""
    stats = await db.fetchrow("""
        SELECT 
            COUNT(*) as total_users,
            COUNT(*) FILTER (WHERE is_active = TRUE) as active_users,
            COUNT(*) FILTER (WHERE is_banned = TRUE) as banned_users,
            COUNT(*) FILTER (WHERE is_verified = TRUE) as verified_users,
            COUNT(*) FILTER (WHERE role = 'client') as clients,
            COUNT(*) FILTER (WHERE role = 'expert') as experts,
            COUNT(*) FILTER (WHERE role = 'admin_editor') as admin_editors,
            COUNT(*) FILTER (WHERE role = 'super_admin') as super_admins,
            COUNT(*) FILTER (WHERE created_at::date = CURRENT_DATE) as new_today,
            COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as new_this_week,
            COUNT(*) FILTER (WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)) as new_this_month
        FROM users
    """)
    
    return dict(stats) if stats else {}

