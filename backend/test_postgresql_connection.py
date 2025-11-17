"""
Comprehensive PostgreSQL Connection Test
Tests all database connections and services including login functionality
"""
import asyncio
import asyncpg
import sys
from app.config import settings
from app.database import db
from app.services.auth_service import auth_service
from app.models import LoginRequest, RegisterRequest, UserRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection(url: str, name: str) -> bool:
    """Test a database connection"""
    try:
        conn = await asyncpg.connect(url)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        logger.info(f"✅ {name} connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ {name} connection failed: {e}")
        return False

async def test_database_pool(pool, name: str) -> bool:
    """Test database connection pool"""
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
        logger.info(f"✅ {name} pool connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ {name} pool connection failed: {e}")
        return False

async def test_table_exists(conn, table_name: str) -> bool:
    """Check if a table exists"""
    try:
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            )
        """, table_name)
        return result
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {e}")
        return False

async def test_users_table(conn) -> bool:
    """Test users table structure and data"""
    try:
        # Check if table exists
        exists = await test_table_exists(conn, "users")
        if not exists:
            logger.error("❌ Users table does not exist")
            return False
        
        # Check table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        required_columns = ['user_id', 'email', 'password_hash', 'first_name', 'last_name', 'role', 'is_active']
        existing_columns = [col['column_name'] for col in columns]
        
        missing_columns = [col for col in required_columns if col not in existing_columns]
        if missing_columns:
            logger.error(f"❌ Users table missing columns: {missing_columns}")
            return False
        
        logger.info(f"✅ Users table structure is correct")
        
        # Check if there are any users
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        logger.info(f"   Found {user_count} users in database")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing users table: {e}")
        return False

async def test_login_functionality(conn) -> bool:
    """Test login functionality with database"""
    try:
        # Check if we can query users
        users = await conn.fetch("SELECT email, role FROM users LIMIT 5")
        
        if not users:
            logger.warning("⚠️  No users found in database. Creating test user...")
            # Create a test user
            from app.utils.security import SecurityUtils
            security_utils = SecurityUtils()
            
            test_email = "test@example.com"
            test_password = "test123"
            password_hash = security_utils.hash_password(test_password)
            
            user_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, first_name, last_name, role, api_key)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (email) DO NOTHING
                RETURNING user_id
            """, test_email, password_hash, "Test", "User", UserRole.CLIENT.value, security_utils.generate_api_key())
            
            if user_id:
                logger.info(f"✅ Created test user: {test_email}")
            else:
                logger.info(f"✅ Test user already exists: {test_email}")
        
        # Test authentication
        test_user = await conn.fetchrow("""
            SELECT user_id, email, password_hash, first_name, last_name, role, is_active
            FROM users WHERE email = $1
        """, "test@example.com")
        
        if test_user:
            logger.info(f"✅ Can query user for login: {test_user['email']}")
            
            # Test password verification
            from app.utils.security import SecurityUtils
            security_utils = SecurityUtils()
            
            if security_utils.verify_password("test123", test_user['password_hash']):
                logger.info("✅ Password verification works correctly")
                return True
            else:
                logger.error("❌ Password verification failed")
                return False
        else:
            logger.warning("⚠️  No test user found for login test")
            return True  # Not a failure, just no test data
            
    except Exception as e:
        logger.error(f"❌ Error testing login functionality: {e}")
        return False

async def test_all_tables(conn) -> bool:
    """Test all required tables exist"""
    required_tables = [
        'users', 'clients', 'experts', 'admins',
        'questions', 'answers', 'ratings', 
        'expert_reviews', 'expert_metrics', 'audit_logs'
    ]
    
    all_exist = True
    for table in required_tables:
        exists = await test_table_exists(conn, table)
        if exists:
            logger.info(f"✅ Table '{table}' exists")
        else:
            logger.error(f"❌ Table '{table}' does not exist")
            all_exist = False
    
    return all_exist

async def test_auth_service(conn) -> bool:
    """Test auth service with database connection"""
    try:
        # Test user creation
        test_register = RegisterRequest(
            email="auth_test@example.com",
            password="test123",
            first_name="Auth",
            last_name="Test",
            role=UserRole.CLIENT
        )
        
        user = await auth_service.create_user(test_register, conn)
        if user:
            logger.info(f"✅ Auth service can create users: {user.email}")
        else:
            logger.warning("⚠️  Could not create test user (may already exist)")
        
        # Test authentication
        test_login = LoginRequest(
            email="auth_test@example.com",
            password="test123"
        )
        
        authenticated_user = await auth_service.authenticate_user(test_login, conn)
        if authenticated_user:
            logger.info(f"✅ Auth service can authenticate users: {authenticated_user.email}")
            return True
        else:
            logger.error("❌ Auth service authentication failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing auth service: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("PostgreSQL Connection and Service Test")
    logger.info("=" * 60)
    
    results = {
        "database_url": False,
        "auth_database_url": False,
        "database_pool": False,
        "auth_pool": False,
        "users_table": False,
        "all_tables": False,
        "login_functionality": False,
        "auth_service": False
    }
    
    # Test 1: Direct connection to main database
    logger.info("\n1. Testing direct connection to main database...")
    results["database_url"] = await test_database_connection(
        settings.database_url, 
        "Main Database"
    )
    
    # Test 2: Direct connection to auth database
    logger.info("\n2. Testing direct connection to auth database...")
    results["auth_database_url"] = await test_database_connection(
        settings.auth_database_url,
        "Auth Database"
    )
    
    # Test 3: Initialize database pools
    logger.info("\n3. Testing database connection pools...")
    try:
        await db.connect()
        logger.info("✅ Database pools initialized")
        
        # Test main pool
        results["database_pool"] = await test_database_pool(
            db.pool, 
            "Main Database Pool"
        )
        
        # Test auth pool
        results["auth_pool"] = await test_database_pool(
            db.auth_pool,
            "Auth Database Pool"
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pools: {e}")
    
    # Test 4: Test users table
    logger.info("\n4. Testing users table...")
    try:
        async with db.pool.acquire() as conn:
            results["users_table"] = await test_users_table(conn)
    except Exception as e:
        logger.error(f"❌ Error accessing users table: {e}")
    
    # Test 5: Test all tables
    logger.info("\n5. Testing all required tables...")
    try:
        async with db.pool.acquire() as conn:
            results["all_tables"] = await test_all_tables(conn)
    except Exception as e:
        logger.error(f"❌ Error checking tables: {e}")
    
    # Test 6: Test login functionality
    logger.info("\n6. Testing login functionality...")
    try:
        async with db.auth_pool.acquire() as conn:
            results["login_functionality"] = await test_login_functionality(conn)
    except Exception as e:
        logger.error(f"❌ Error testing login: {e}")
    
    # Test 7: Test auth service
    logger.info("\n7. Testing auth service...")
    try:
        async with db.auth_pool.acquire() as conn:
            results["auth_service"] = await test_auth_service(conn)
    except Exception as e:
        logger.error(f"❌ Error testing auth service: {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n🎉 All tests passed! PostgreSQL is properly configured.")
        return 0
    else:
        logger.error("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

