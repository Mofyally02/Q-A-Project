"""
API Key management CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime


async def get_api_keys(
    db: asyncpg.Connection,
    key_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """Get API keys with filters"""
    conditions = []
    params = []
    param_count = 0
    
    if key_type:
        param_count += 1
        conditions.append(f"key_type = ${param_count}")
        params.append(key_type)
    
    if is_active is not None:
        param_count += 1
        conditions.append(f"is_active = ${param_count}")
        params.append(is_active)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT id, name, key_type, is_active, last_tested_at, last_tested_status, 
               created_by_id, created_at, updated_at
        FROM api_keys
        WHERE {where_clause}
        ORDER BY created_at DESC
    """
    
    rows = await db.fetch(query, *params)
    return [dict(row) for row in rows]


async def get_api_key_by_id(db: asyncpg.Connection, key_id: UUID) -> Optional[Dict[str, Any]]:
    """Get API key by ID (without encrypted key)"""
    row = await db.fetchrow("""
        SELECT id, name, key_type, is_active, last_tested_at, last_tested_status,
               created_by_id, created_at, updated_at
        FROM api_keys
        WHERE id = $1
    """, key_id)
    return dict(row) if row else None


async def create_api_key(
    db: asyncpg.Connection,
    name: str,
    key_type: str,
    encrypted_key: str,
    created_by: Optional[UUID] = None,
    is_active: bool = True
) -> UUID:
    """Create new API key"""
    row = await db.fetchrow("""
        INSERT INTO api_keys (name, key_type, encrypted_key, is_active, created_by_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """, name, key_type, encrypted_key, is_active, created_by)
    return row['id']


async def update_api_key(
    db: asyncpg.Connection,
    key_id: UUID,
    name: Optional[str] = None,
    encrypted_key: Optional[str] = None,
    is_active: Optional[bool] = None
) -> bool:
    """Update API key"""
    updates = []
    params = []
    param_count = 0
    
    if name:
        param_count += 1
        updates.append(f"name = ${param_count}")
        params.append(name)
    
    if encrypted_key:
        param_count += 1
        updates.append(f"encrypted_key = ${param_count}")
        params.append(encrypted_key)
    
    if is_active is not None:
        param_count += 1
        updates.append(f"is_active = ${param_count}")
        params.append(is_active)
    
    if not updates:
        return False
    
    param_count += 1
    params.append(key_id)
    updates.append("updated_at = NOW()")
    
    query = f"UPDATE api_keys SET {', '.join(updates)} WHERE id = ${param_count}"
    result = await db.execute(query, *params)
    return result == "UPDATE 1"


async def delete_api_key(db: asyncpg.Connection, key_id: UUID) -> bool:
    """Delete API key"""
    result = await db.execute("DELETE FROM api_keys WHERE id = $1", key_id)
    return result == "DELETE 1"


async def update_api_key_test_status(
    db: asyncpg.Connection,
    key_id: UUID,
    status: str,
    response_time_ms: Optional[float] = None
) -> bool:
    """Update API key test status"""
    result = await db.execute("""
        UPDATE api_keys 
        SET last_tested_at = NOW(), last_tested_status = $1, updated_at = NOW()
        WHERE id = $2
    """, status, key_id)
    return result == "UPDATE 1"

