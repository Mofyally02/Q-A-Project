#!/usr/bin/env python3
"""
Database initialization script for AI Q&A System
This script ensures the database is properly set up with all required tables and data.
"""

import asyncio
import asyncpg
import logging
from app.config import settings
from app.utils.security import SecurityUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """Initialize the database with all required tables and default data"""
    try:
        # Connect to auth database (where users are stored)
        conn = await asyncpg.connect(settings.auth_database_url)
        logger.info("Connected to database")
        
        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        existing_tables = [row['table_name'] for row in tables]
        logger.info(f"Existing tables: {existing_tables}")
        
        # Create default users if they don't exist
        await create_default_users(conn)
        
        # Create default role-specific records
        await create_default_role_records(conn)
        
        # Verify database integrity
        await verify_database_integrity(conn)
        
        await conn.close()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def create_default_users(conn):
    """Create default users for testing"""
    security_utils = SecurityUtils()
    
    # Check if default users exist
    existing_users = await conn.fetch("SELECT email FROM users")
    existing_emails = [row['email'] for row in existing_users]
    
    default_users = [
        {
            'email': 'client@demo.com',
            'password': 'demo123',
            'first_name': 'Demo',
            'last_name': 'Client',
            'role': 'client'
        },
        {
            'email': 'expert@demo.com',
            'password': 'demo123',
            'first_name': 'Demo',
            'last_name': 'Expert',
            'role': 'expert'
        },
        {
            'email': 'admin@demo.com',
            'password': 'demo123',
            'first_name': 'Demo',
            'last_name': 'Admin',
            'role': 'admin'
        }
    ]
    
    for user_data in default_users:
        if user_data['email'] not in existing_emails:
            password_hash = security_utils.hash_password(user_data['password'])
            api_key = security_utils.generate_api_key()
            
            user_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, first_name, last_name, role, api_key, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, true)
                RETURNING user_id
            """, user_data['email'], password_hash, user_data['first_name'], 
                user_data['last_name'], user_data['role'], api_key)
            
            logger.info(f"Created default user: {user_data['email']} (ID: {user_id})")
        else:
            logger.info(f"User {user_data['email']} already exists")

async def create_default_role_records(conn):
    """Create default role-specific records"""
    # Get all users
    users = await conn.fetch("SELECT user_id, role FROM users")
    
    for user in users:
        user_id = user['user_id']
        role = user['role']
        
        if role == 'client':
            # Check if client record exists
            client_exists = await conn.fetchval(
                "SELECT user_id FROM clients WHERE user_id = $1", user_id
            )
            if not client_exists:
                await conn.execute("""
                    INSERT INTO clients (user_id, subscription_type, credits_remaining)
                    VALUES ($1, 'premium', 1000)
                """, user_id)
                logger.info(f"Created client record for user {user_id}")
        
        elif role == 'expert':
            # Check if expert record exists
            expert_exists = await conn.fetchval(
                "SELECT user_id FROM experts WHERE user_id = $1", user_id
            )
            if not expert_exists:
                await conn.execute("""
                    INSERT INTO experts (user_id, approved, specialization, experience_years)
                    VALUES ($1, true, 'General', 5)
                """, user_id)
                logger.info(f"Created expert record for user {user_id}")
        
        elif role == 'admin':
            # Check if admin record exists
            admin_exists = await conn.fetchval(
                "SELECT user_id FROM admins WHERE user_id = $1", user_id
            )
            if not admin_exists:
                await conn.execute("""
                    INSERT INTO admins (user_id, permissions)
                    VALUES ($1, '{"all": true}')
                """, user_id)
                logger.info(f"Created admin record for user {user_id}")

async def verify_database_integrity(conn):
    """Verify database integrity and report any issues"""
    logger.info("Verifying database integrity...")
    
    # Check table counts (auth database tables only)
    tables_to_check = [
        'users', 'clients', 'experts', 'admins', 'role_change_history'
    ]
    
    for table in tables_to_check:
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        logger.info(f"Table {table}: {count} records")
    
    # Check foreign key constraints
    fk_constraints = await conn.fetch("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name
    """)
    
    logger.info(f"Found {len(fk_constraints)} foreign key constraints")
    for fk in fk_constraints:
        logger.info(f"FK: {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
    
    # Check indexes
    indexes = await conn.fetch("""
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
    """)
    
    logger.info(f"Found {len(indexes)} indexes")
    for idx in indexes:
        logger.info(f"Index: {idx['tablename']}.{idx['indexname']}")

async def test_database_operations():
    """Test basic database operations"""
    try:
        conn = await asyncpg.connect(settings.database_url)
        logger.info("Testing database operations...")
        
        # Test user creation
        test_user_id = await conn.fetchval("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
            VALUES ($1, $2, $3, $4, $5, true)
            RETURNING user_id
        """, 'test@example.com', 'hashed_password', 'Test', 'User', 'client')
        
        logger.info(f"Test user created with ID: {test_user_id}")
        
        # Test question creation
        test_question_id = await conn.fetchval("""
            INSERT INTO questions (question_id, client_id, type, content, subject, status)
            VALUES (gen_random_uuid(), $1, $2, $3, $4, 'submitted')
            RETURNING question_id
        """, test_user_id, 'text', '{"data": "Test question"}', 'Test Subject')
        
        logger.info(f"Test question created with ID: {test_question_id}")
        
        # Test answer creation
        test_answer_id = await conn.fetchval("""
            INSERT INTO answers (answer_id, question_id, ai_response, confidence_score)
            VALUES (gen_random_uuid(), $1, $2, $3)
            RETURNING answer_id
        """, test_question_id, '{"response": "Test answer"}', 0.95)
        
        logger.info(f"Test answer created with ID: {test_answer_id}")
        
        # Clean up test data
        await conn.execute("DELETE FROM answers WHERE answer_id = $1", test_answer_id)
        await conn.execute("DELETE FROM questions WHERE question_id = $1", test_question_id)
        await conn.execute("DELETE FROM users WHERE user_id = $1", test_user_id)
        
        logger.info("Test data cleaned up")
        
        await conn.close()
        logger.info("Database operations test completed successfully")
        
    except Exception as e:
        logger.error(f"Database operations test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
    # test_database_operations() removed - it was testing qa_system tables in qa_auth database
