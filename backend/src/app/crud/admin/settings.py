"""
System settings CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
import json


async def get_system_settings(
    db: asyncpg.Connection,
    key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get system settings"""
    if key:
        row = await db.fetchrow("SELECT * FROM system_settings WHERE key = $1", key)
        return [dict(row)] if row else []
    
    rows = await db.fetch("SELECT * FROM system_settings ORDER BY key")
    return [dict(row) for row in rows]


async def get_system_setting_by_key(
    db: asyncpg.Connection,
    key: str
) -> Optional[Dict[str, Any]]:
    """Get system setting by key"""
    row = await db.fetchrow("SELECT * FROM system_settings WHERE key = $1", key)
    return dict(row) if row else None


async def create_system_setting(
    db: asyncpg.Connection,
    key: str,
    value: Dict[str, Any],
    description: Optional[str] = None,
    updated_by: Optional[UUID] = None
) -> UUID:
    """Create system setting"""
    row = await db.fetchrow("""
        INSERT INTO system_settings (key, value, description, updated_by_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """, key, json.dumps(value), description, updated_by)
    return row['id']


async def update_system_setting(
    db: asyncpg.Connection,
    key: str,
    value: Dict[str, Any],
    description: Optional[str] = None,
    updated_by: Optional[UUID] = None
) -> bool:
    """Update system setting"""
    result = await db.execute("""
        UPDATE system_settings 
        SET value = $1, description = COALESCE($2, description), 
            updated_by_id = $3, updated_at = NOW()
        WHERE key = $4
    """, json.dumps(value), description, updated_by, key)
    return result == "UPDATE 1"


async def upsert_system_setting(
    db: asyncpg.Connection,
    key: str,
    value: Dict[str, Any],
    description: Optional[str] = None,
    updated_by: Optional[UUID] = None
) -> UUID:
    """Create or update system setting"""
    row = await db.fetchrow("""
        INSERT INTO system_settings (key, value, description, updated_by_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (key) 
        DO UPDATE SET 
            value = EXCLUDED.value,
            description = COALESCE(EXCLUDED.description, system_settings.description),
            updated_by_id = EXCLUDED.updated_by_id,
            updated_at = NOW()
        RETURNING id
    """, key, json.dumps(value), description, updated_by)
    return row['id']


async def delete_system_setting(db: asyncpg.Connection, key: str) -> bool:
    """Delete system setting"""
    result = await db.execute("DELETE FROM system_settings WHERE key = $1", key)
    return result == "DELETE 1"

