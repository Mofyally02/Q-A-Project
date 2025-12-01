"""
Notification broadcast CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def create_notification_broadcast(
    db: asyncpg.Connection,
    title: str,
    message: str,
    notification_type: str,
    sent_by: UUID,
    target_roles: Optional[List[str]] = None,
    target_status: Optional[List[str]] = None,
    send_email: bool = False,
    send_sms: bool = False
) -> Dict[str, Any]:
    """Create notification broadcast"""
    # Calculate target count
    conditions = []
    params = []
    param_count = 0
    
    if target_roles:
        param_count += 1
        conditions.append(f"role = ANY(${param_count})")
        params.append(target_roles)
    
    if target_status:
        # Assuming status is in metadata or is_active
        # This is simplified - adjust based on your schema
        pass
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    target_count_query = f"SELECT COUNT(*) FROM users WHERE {where_clause}"
    target_count = await db.fetchval(target_count_query, *params)
    
    # Create broadcast record (using a notifications table or admin_actions)
    # For now, we'll use admin_actions with a specific action type
    broadcast_id = await db.fetchval("""
        INSERT INTO admin_actions (admin_id, action_type, target_type, details)
        VALUES ($1, 'broadcast_notification', 'system', $2::jsonb)
        RETURNING id
    """, sent_by, {
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "target_roles": target_roles,
        "target_status": target_status,
        "send_email": send_email,
        "send_sms": send_sms,
        "target_count": target_count,
        "queued_at": datetime.utcnow().isoformat()
    })
    
    return {
        "broadcast_id": broadcast_id,
        "target_count": target_count,
        "queued_at": datetime.utcnow(),
        "estimated_completion": datetime.utcnow()  # Simplified
    }


async def get_notification_history(
    db: asyncpg.Connection,
    sent_by: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get notification broadcast history"""
    offset = (page - 1) * page_size
    conditions = ["action_type = 'broadcast_notification'"]
    params = []
    param_count = 0
    
    if sent_by:
        param_count += 1
        conditions.append(f"admin_id = ${param_count}")
        params.append(sent_by)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM admin_actions WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get broadcasts
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            id, admin_id as sent_by, created_at as sent_at, details
        FROM admin_actions
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    broadcasts = []
    for row in rows:
        details = row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {}
        broadcasts.append({
            "id": row["id"],
            "title": details.get("title", ""),
            "message": details.get("message", ""),
            "notification_type": details.get("notification_type", "info"),
            "target_count": details.get("target_count", 0),
            "sent_count": details.get("sent_count", 0),  # Would be updated by worker
            "failed_count": details.get("failed_count", 0),
            "sent_by": row["sent_by"],
            "sent_at": row["sent_at"]
        })
    
    return {
        "broadcasts": broadcasts,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def get_notification_templates(
    db: asyncpg.Connection,
    template_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get notification templates"""
    conditions = []
    params = []
    
    if template_type:
        params.append(template_type)
        conditions.append("template_type = $1")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT 
            id, name, subject, body, template_type, variables,
            created_at, updated_at
        FROM notification_templates
        WHERE {where_clause}
        ORDER BY name
    """
    
    rows = await db.fetch(query, *params)
    return [dict(row) for row in rows]


async def create_notification_template(
    db: asyncpg.Connection,
    name: str,
    subject: Optional[str],
    body: str,
    template_type: str,
    variables: Optional[Dict[str, Any]] = None,
    created_by: UUID = None
) -> UUID:
    """Create notification template"""
    template_id = await db.fetchval("""
        INSERT INTO notification_templates 
        (name, subject, body, template_type, variables, created_by_id)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
    """, name, subject, body, template_type,
        json.dumps(variables) if variables else None, created_by)
    return template_id


async def update_notification_template(
    db: asyncpg.Connection,
    template_id: UUID,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    variables: Optional[Dict[str, Any]] = None
) -> bool:
    """Update notification template"""
    updates = []
    params = []
    param_count = 0
    
    if name:
        param_count += 1
        updates.append(f"name = ${param_count}")
        params.append(name)
    
    if subject is not None:
        param_count += 1
        updates.append(f"subject = ${param_count}")
        params.append(subject)
    
    if body:
        param_count += 1
        updates.append(f"body = ${param_count}")
        params.append(body)
    
    if variables is not None:
        param_count += 1
        updates.append(f"variables = ${param_count}")
        params.append(json.dumps(variables))
    
    if not updates:
        return False
    
    param_count += 1
    updates.append(f"updated_at = NOW()")
    param_count += 1
    params.append(template_id)
    
    query = f"""
        UPDATE notification_templates
        SET {', '.join(updates)}
        WHERE id = ${param_count}
    """
    
    result = await db.execute(query, *params)
    return result == "UPDATE 1"


async def delete_notification_template(
    db: asyncpg.Connection,
    template_id: UUID
) -> bool:
    """Delete notification template"""
    result = await db.execute("""
        DELETE FROM notification_templates WHERE id = $1
    """, template_id)
    return result == "DELETE 1"

