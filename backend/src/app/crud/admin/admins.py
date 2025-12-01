"""
Admin management CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime, timedelta
import secrets
import hashlib


async def get_admins(
    db: asyncpg.Connection,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get all admins with filters"""
    offset = (page - 1) * page_size
    conditions = ["role IN ('super_admin', 'admin_editor')"]
    params = []
    param_count = 0
    
    if role:
        param_count += 1
        conditions.append(f"role = ${param_count}")
        params.append(role)
    
    if is_active is not None:
        param_count += 1
        conditions.append(f"is_active = ${param_count}")
        params.append(is_active)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM users WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get admins
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT 
            id, email, first_name, last_name, role, is_active, 
            last_active, created_at, invited_by_id
        FROM users
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    admins = [dict(row) for row in rows]
    
    return {
        "admins": admins,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def create_admin_invitation(
    db: asyncpg.Connection,
    email: str,
    role: str,
    invited_by: UUID,
    expires_in_hours: int = 24
) -> Dict[str, Any]:
    """Create admin invitation with magic link"""
    # Check if user already exists
    existing = await db.fetchrow("SELECT id, role FROM users WHERE email = $1", email)
    
    if existing:
        if existing["role"] in ("super_admin", "admin_editor"):
            raise ValueError("User is already an admin")
        # User exists but is not admin - we'll update their role
        user_id = existing["id"]
    else:
        # Create new user with pending status
        user_id = await db.fetchval("""
            INSERT INTO users (email, role, is_active, invited_by_id)
            VALUES ($1, $2, FALSE, $3)
            RETURNING id
        """, email, role, invited_by)
    
    # Generate invitation token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    # Store invitation (using admin_actions table or create invitations table)
    # For now, we'll use a simple approach with admin_actions
    await db.execute("""
        INSERT INTO admin_actions (admin_id, action_type, target_type, target_id, details)
        VALUES ($1, 'invite_admin', 'user', $2, $3::jsonb)
    """, invited_by, user_id, {
        "email": email,
        "role": role,
        "token_hash": token_hash,
        "expires_at": expires_at.isoformat()
    })
    
    # Generate magic link
    magic_link = f"/admin/accept-invite?token={token}&email={email}"
    
    return {
        "invitation_id": user_id,
        "magic_link": magic_link,
        "token": token,  # Only returned for initial creation
        "expires_at": expires_at,
        "email": email
    }


async def suspend_admin(
    db: asyncpg.Connection,
    admin_id: UUID,
    suspended: bool,
    reason: Optional[str] = None,
    suspended_by: UUID = None
) -> bool:
    """Suspend or activate admin"""
    result = await db.execute("""
        UPDATE users 
        SET is_active = $1, 
            metadata = jsonb_set(
                COALESCE(metadata, '{}'::jsonb),
                '{suspension_reason}',
                to_jsonb($2)
            )
        WHERE id = $3 AND role IN ('super_admin', 'admin_editor')
    """, not suspended, reason, admin_id)
    
    # Log suspension action
    if suspended_by:
        await db.execute("""
            INSERT INTO admin_actions (admin_id, action_type, target_type, target_id, details)
            VALUES ($1, 'suspend_admin', 'user', $2, $3::jsonb)
        """, suspended_by, admin_id, {
            "suspended": suspended,
            "reason": reason
        })
    
    return result == "UPDATE 1"


async def revoke_admin_access(
    db: asyncpg.Connection,
    admin_id: UUID,
    revoked_by: UUID
) -> bool:
    """Revoke admin access (demote to client)"""
    # Check if trying to revoke self
    if admin_id == revoked_by:
        raise ValueError("Cannot revoke your own admin access")
    
    # Get current role
    current = await db.fetchrow("SELECT role FROM users WHERE id = $1", admin_id)
    if not current or current["role"] not in ("super_admin", "admin_editor"):
        raise ValueError("User is not an admin")
    
    # Demote to client
    result = await db.execute("""
        UPDATE users 
        SET role = 'client',
            is_active = FALSE,
            metadata = jsonb_set(
                COALESCE(metadata, '{}'::jsonb),
                '{revoked_at}',
                to_jsonb(NOW()::text)
            )
        WHERE id = $1
    """, admin_id)
    
    # Log revocation
    await db.execute("""
        INSERT INTO admin_actions (admin_id, action_type, target_type, target_id, details)
        VALUES ($1, 'revoke_admin', 'user', $2, $3::jsonb)
    """, revoked_by, admin_id, {
        "previous_role": current["role"]
    })
    
    return result == "UPDATE 1"


async def get_admin_by_id(
    db: asyncpg.Connection,
    admin_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get admin by ID"""
    row = await db.fetchrow("""
        SELECT 
            id, email, first_name, last_name, role, is_active,
            last_active, created_at, invited_by_id, metadata
        FROM users
        WHERE id = $1 AND role IN ('super_admin', 'admin_editor')
    """, admin_id)
    
    return dict(row) if row else None

