"""
FastAPI dependencies
Reusable dependencies for database, cache, authentication, etc.
"""

from typing import AsyncGenerator
import asyncpg
from fastapi import Depends, HTTPException, status
from app.db.session import get_db, get_redis
from app.utils.cache import cache

# Database dependency (already defined in db/session.py, re-exported here)
async def get_database() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection dependency"""
    async for connection in get_db():
        yield connection


# Cache dependency
async def get_cache():
    """Get cache service dependency"""
    return cache


# Redis dependency (already defined in db/session.py, re-exported here)
def get_redis_client():
    """Get Redis client dependency"""
    return get_redis()

