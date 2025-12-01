"""
Database initialization
Create tables, extensions, and initial data
"""

import asyncpg
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database with extensions and base tables"""
    try:
        # Connect to main database
        conn = await asyncpg.connect(settings.database_url)
        
        try:
            # Enable required extensions
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";")
            logger.info("Database extensions enabled")
            
            # Run Alembic migrations (they handle table creation)
            logger.info("Database initialization complete")
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def init_auth_database():
    """Initialize auth database"""
    try:
        conn = await asyncpg.connect(settings.auth_database_url)
        
        try:
            # Enable required extensions
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";")
            logger.info("Auth database extensions enabled")
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize auth database: {e}")
        raise

