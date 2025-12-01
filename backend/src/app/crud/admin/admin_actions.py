"""
Admin actions CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def log_admin_action(
    db: asyncpg.Connection,
    admin_id: UUID,
    action_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UUID:
    """Log admin action"""
    row = await db.fetchrow("""
        INSERT INTO admin_actions 
        (admin_id, action_type, target_type, target_id, details, ip_address, user_agent)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
    """, admin_id, action_type, target_type, target_id, 
        json.dumps(details) if details else None, ip_address, user_agent)
    return row['id']


async def get_admin_actions(
    db: asyncpg.Connection,
    admin_id: Optional[UUID] = None,
    action_type: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get admin actions with filters"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_count = 0
    
    if admin_id:
        param_count += 1
        conditions.append(f"aa.admin_id = ${param_count}")
        params.append(admin_id)
    
    if action_type:
        param_count += 1
        conditions.append(f"aa.action_type = ${param_count}")
        params.append(action_type)
    
    if target_type:
        param_count += 1
        conditions.append(f"aa.target_type = ${param_count}")
        params.append(target_type)
    
    if target_id:
        param_count += 1
        conditions.append(f"aa.target_id = ${param_count}")
        params.append(target_id)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM admin_actions aa WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get actions with admin email
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            aa.*,
            u.email as admin_email
        FROM admin_actions aa
        LEFT JOIN users u ON aa.admin_id = u.id
        WHERE {where_clause}
        ORDER BY aa.created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    actions = [dict(row) for row in rows]
    
    return {
        "logs": actions,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_admin_action_by_id(
    db: asyncpg.Connection,
    action_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get admin action by ID"""
    row = await db.fetchrow("""
        SELECT 
            aa.*,
            u.email as admin_email
        FROM admin_actions aa
        LEFT JOIN users u ON aa.admin_id = u.id
        WHERE aa.id = $1
    """, action_id)
    return dict(row) if row else None

