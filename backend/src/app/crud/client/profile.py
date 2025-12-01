"""
Client profile CRUD operations
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def get_user_profile(
    db: asyncpg.Connection,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """Get user profile"""
    row = await db.fetchrow("""
        SELECT 
            id, email, first_name, last_name, phone,
            avatar_url, bio, profile_data, created_at, last_active
        FROM users
        WHERE id = $1
    """, user_id)
    
    if not row:
        return None
    
    profile_data = row["profile_data"] if isinstance(row["profile_data"], dict) else json.loads(row["profile_data"]) if row["profile_data"] else {}
    
    return {
        "id": row["id"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "phone": row["phone"],
        "avatar_url": row["avatar_url"],
        "bio": row["bio"],
        "preferences": profile_data.get("preferences"),
        "created_at": row["created_at"],
        "last_active": row["last_active"]
    }


async def update_user_profile(
    db: asyncpg.Connection,
    user_id: UUID,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    avatar_url: Optional[str] = None,
    bio: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Update user profile"""
    updates = []
    params = []
    param_count = 0
    
    if first_name is not None:
        param_count += 1
        updates.append(f"first_name = ${param_count}")
        params.append(first_name)
    
    if last_name is not None:
        param_count += 1
        updates.append(f"last_name = ${param_count}")
        params.append(last_name)
    
    if phone is not None:
        param_count += 1
        updates.append(f"phone = ${param_count}")
        params.append(phone)
    
    if avatar_url is not None:
        param_count += 1
        updates.append(f"avatar_url = ${param_count}")
        params.append(avatar_url)
    
    if bio is not None:
        param_count += 1
        updates.append(f"bio = ${param_count}")
        params.append(bio)
    
    if preferences is not None:
        # Get current profile_data
        current_profile = await db.fetchval("SELECT profile_data FROM users WHERE id = $1", user_id)
        current_data = current_profile if isinstance(current_profile, dict) else json.loads(current_profile) if current_profile else {}
        current_data["preferences"] = preferences
        
        param_count += 1
        updates.append(f"profile_data = ${param_count}")
        params.append(json.dumps(current_data))
    
    if not updates:
        raise ValueError("No fields to update")
    
    param_count += 1
    params.append(user_id)
    
    query = f"""
        UPDATE users
        SET {', '.join(updates)}, last_active = NOW()
        WHERE id = ${param_count}
    """
    
    result = await db.execute(query, *params)
    
    if result != "UPDATE 1":
        raise ValueError("Failed to update profile")
    
    # Return updated profile
    return await get_user_profile(db, user_id)

