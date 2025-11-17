"""
Quick verification script to check backend setup and PostgreSQL connectivity
"""
import asyncio
import sys
from app.config import settings
from app.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_check():
    """Quick check of backend configuration"""
    logger.info("=" * 60)
    logger.info("Backend Configuration Check")
    logger.info("=" * 60)
    
    # Check configuration
    logger.info("\n📋 Configuration:")
    logger.info(f"   Database URL: {settings.database_url[:50]}...")
    logger.info(f"   Auth Database URL: {settings.auth_database_url[:50]}...")
    logger.info(f"   Redis URL: {settings.redis_url}")
    logger.info(f"   JWT Secret: {'✅ Set' if settings.jwt_secret_key != 'your-secret-key-here' else '⚠️  Using default'}")
    logger.info(f"   CORS Origins: {settings.cors_origins}")
    
    # Test database connections
    logger.info("\n🔌 Testing Database Connections:")
    try:
        await db.connect()
        logger.info("✅ Database pools initialized successfully")
        
        # Test main database
        async with db.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            logger.info("✅ Main database connection working")
            
            # Check users table
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            logger.info(f"   Found {user_count} users in database")
        
        # Test auth database
        async with db.auth_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            logger.info("✅ Auth database connection working")
            
            # Check users table
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            logger.info(f"   Found {user_count} users in auth database")
        
        await db.disconnect()
        logger.info("\n✅ All database connections verified!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Database connection failed: {e}")
        logger.error("\n💡 Troubleshooting:")
        logger.error("   1. Make sure PostgreSQL is running")
        logger.error("   2. Check your .env file has correct DATABASE_URL and AUTH_DATABASE_URL")
        logger.error("   3. Verify database credentials are correct")
        logger.error("   4. Ensure databases 'qa_system' and 'qa_auth' exist")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_check())
    sys.exit(0 if success else 1)

