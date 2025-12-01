"""
Database session management
PostgreSQL connection pools and Redis client
"""

import asyncpg
import redis
from typing import AsyncGenerator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.pool = None
        self.auth_pool = None
        self.redis_client = None
    
    async def connect(self):
        """Initialize database connection pool and Redis client"""
        try:
            # Main PostgreSQL connection pool
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Main database connection pool created")
            
            # Auth database connection pool
            self.auth_pool = await asyncpg.create_pool(
                settings.auth_database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Auth database connection pool created")
            
            # Redis client (optional - server can run without it)
            try:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True
                )
                # Test Redis connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as redis_error:
                logger.warning(f"Redis connection failed: {redis_error}. Continuing without Redis.")
                self.redis_client = None
            
            logger.info("All database connections established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Main database pool closed")
        if self.auth_pool:
            await self.auth_pool.close()
            logger.info("Auth database pool closed")
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")
        logger.info("All database connections closed")
    
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the main pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        async with self.pool.acquire() as connection:
            yield connection
    
    async def get_auth_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the auth pool"""
        if not self.auth_pool:
            raise RuntimeError("Auth database pool not initialized. Call connect() first.")
        async with self.auth_pool.acquire() as connection:
            yield connection
    
    def get_redis(self) -> redis.Redis:
        """Get Redis client (returns None if Redis is not available)"""
        return self.redis_client  # Can be None if Redis is not available
    
    async def health_check(self) -> dict:
        """Check health of all database connections"""
        health_status = {
            "postgresql": "unknown",
            "auth_postgresql": "unknown",
            "redis": "unknown"
        }
        
        # Check main PostgreSQL
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["postgresql"] = "healthy"
        except Exception as e:
            health_status["postgresql"] = f"unhealthy: {str(e)}"
        
        # Check auth PostgreSQL
        try:
            async with self.auth_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["auth_postgresql"] = "healthy"
        except Exception as e:
            health_status["auth_postgresql"] = f"unhealthy: {str(e)}"
        
        # Check Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                health_status["redis"] = "healthy"
            except Exception as e:
                health_status["redis"] = f"unhealthy: {str(e)}"
        else:
            health_status["redis"] = "not_configured"
        
        return health_status


# Global database instance
db = Database()


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency for FastAPI to get main database connection"""
    async for connection in db.get_connection():
        yield connection


async def get_auth_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency for FastAPI to get auth database connection"""
    async for connection in db.get_auth_connection():
        yield connection


def get_redis() -> redis.Redis:
    """Dependency for FastAPI to get Redis client"""
    return db.get_redis()

