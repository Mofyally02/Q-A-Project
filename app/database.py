import asyncpg
import redis
from typing import AsyncGenerator
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        self.redis_client = None
    
    async def connect(self):
        """Initialize database connection pool and Redis client"""
        try:
            # PostgreSQL connection pool
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Redis client
            self.redis_client = redis.from_url(settings.redis_url)
            
            logger.info("Database connections established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.redis_client:
            self.redis_client.close()
        logger.info("Database connections closed")
    
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool"""
        async with self.pool.acquire() as connection:
            yield connection
    
    def get_redis(self) -> redis.Redis:
        """Get Redis client"""
        return self.redis_client

# Global database instance
db = Database()

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency for FastAPI to get database connection"""
    async for connection in db.get_connection():
        yield connection

def get_redis() -> redis.Redis:
    """Dependency for FastAPI to get Redis client"""
    return db.get_redis()
