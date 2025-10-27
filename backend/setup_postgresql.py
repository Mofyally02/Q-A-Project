#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
This script sets up PostgreSQL databases and runs migrations
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import asyncpg

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLSetup:
    """PostgreSQL database setup and management"""
    
    def __init__(self):
        self.main_db_url = "postgresql://postgres:password@localhost:5432/qa_system"
        self.auth_db_url = "postgresql://postgres:password@localhost:5432/qa_auth"
        self.postgres_url = "postgresql://postgres:password@localhost:5432/postgres"
    
    async def test_postgres_connection(self):
        """Test if PostgreSQL is running and accessible"""
        logger.info("🔍 Testing PostgreSQL connection...")
        
        # Try different common passwords
        passwords = ["password", "postgres", "admin", "", "123456"]
        
        for password in passwords:
            test_url = f"postgresql://postgres:{password}@localhost:5432/postgres"
            try:
                logger.info(f"  Trying password: {'(empty)' if not password else password}")
                conn = await asyncpg.connect(test_url)
                await conn.close()
                logger.info(f"  ✅ SUCCESS! Password: {'(empty)' if not password else password}")
                
                # Update URLs with working password
                self.main_db_url = f"postgresql://postgres:{password}@localhost:5432/qa_system"
                self.auth_db_url = f"postgresql://postgres:{password}@localhost:5432/qa_auth"
                self.postgres_url = test_url
                return True
                
            except Exception as e:
                logger.info(f"  ❌ Failed: {str(e)[:50]}...")
        
        logger.error("❌ Could not connect to PostgreSQL")
        return False
    
    async def create_databases(self):
        """Create the required databases"""
        logger.info("🏗️  Creating databases...")
        
        try:
            conn = await asyncpg.connect(self.postgres_url)
            
            # Create qa_system database
            try:
                await conn.execute("CREATE DATABASE qa_system;")
                logger.info("  ✅ Created qa_system database")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("  ℹ️  qa_system database already exists")
                else:
                    raise
            
            # Create qa_auth database
            try:
                await conn.execute("CREATE DATABASE qa_auth;")
                logger.info("  ✅ Created qa_auth database")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("  ℹ️  qa_auth database already exists")
                else:
                    raise
            
            await conn.close()
            logger.info("✅ Database creation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database creation failed: {e}")
            return False
    
    async def run_migrations(self):
        """Run Alembic migrations"""
        logger.info("🔄 Running database migrations...")
        
        try:
            # Test connection to both databases
            main_conn = await asyncpg.connect(self.main_db_url)
            auth_conn = await asyncpg.connect(self.auth_db_url)
            
            # Run migration 001 - Initial schema
            await self._run_migration_001(main_conn)
            
            # Run migration 002 - Additional tables
            await self._run_migration_002(main_conn)
            
            await main_conn.close()
            await auth_conn.close()
            
            logger.info("✅ Migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    async def _run_migration_001(self, conn):
        """Run migration 001 - Initial schema"""
        logger.info("  Running migration 001 - Initial schema...")
        
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'expert', 'admin')),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create questions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_id UUID NOT NULL REFERENCES users(user_id),
                type VARCHAR(10) NOT NULL CHECK (type IN ('text', 'image')),
                content JSONB NOT NULL,
                subject VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('submitted', 'processing', 'humanized', 'review', 'delivered', 'rated')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create answers table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                question_id UUID NOT NULL REFERENCES questions(question_id),
                ai_response JSONB,
                humanized_response JSONB,
                expert_response JSONB,
                confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
                is_approved BOOLEAN,
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create ratings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                question_id UUID NOT NULL REFERENCES questions(question_id),
                expert_id UUID REFERENCES users(user_id),
                score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create expert_reviews table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expert_reviews (
                review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                answer_id UUID NOT NULL REFERENCES answers(answer_id),
                expert_id UUID NOT NULL REFERENCES users(user_id),
                is_approved BOOLEAN NOT NULL,
                rejection_reason TEXT,
                correction JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit_logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                action VARCHAR(50) NOT NULL,
                user_id UUID NOT NULL REFERENCES users(user_id),
                question_id UUID REFERENCES questions(question_id),
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_questions_client_id ON questions (client_id)",
            "CREATE INDEX IF NOT EXISTS idx_questions_status ON questions (status)",
            "CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers (question_id)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_question_id ON ratings (question_id)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_expert_id ON ratings (expert_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_question_id ON audit_logs (question_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at)"
        ]
        
        for index_sql in indexes:
            await conn.execute(index_sql)
        
        logger.info("  ✅ Migration 001 completed")
    
    async def _run_migration_002(self, conn):
        """Run migration 002 - Additional tables and columns"""
        logger.info("  Running migration 002 - Additional tables and columns...")
        
        # Add missing columns to users table
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key VARCHAR(255) UNIQUE")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_data JSONB")
        
        # Add missing columns to answers table
        await conn.execute("ALTER TABLE answers ADD COLUMN IF NOT EXISTS expert_id UUID REFERENCES users(user_id)")
        
        # Create role-specific tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                subscription_type VARCHAR(50) DEFAULT 'basic',
                credits_remaining INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                approved BOOLEAN DEFAULT false,
                specialization VARCHAR(100),
                experience_years INTEGER,
                rating FLOAT DEFAULT 0.0,
                total_reviews INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                permissions JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expert_metrics (
                expert_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                avg_rating FLOAT NOT NULL DEFAULT 0.0,
                total_ratings INTEGER NOT NULL DEFAULT 0,
                total_score INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create additional indexes
        additional_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_first_name ON users (first_name)",
            "CREATE INDEX IF NOT EXISTS idx_users_last_name ON users (last_name)",
            "CREATE INDEX IF NOT EXISTS idx_users_api_key ON users (api_key)",
            "CREATE INDEX IF NOT EXISTS idx_answers_expert_id ON answers (expert_id)",
            "CREATE INDEX IF NOT EXISTS idx_experts_approved ON experts (approved)",
            "CREATE INDEX IF NOT EXISTS idx_experts_rating ON experts (rating)",
            "CREATE INDEX IF NOT EXISTS idx_clients_subscription ON clients (subscription_type)"
        ]
        
        for index_sql in additional_indexes:
            await conn.execute(index_sql)
        
        logger.info("  ✅ Migration 002 completed")
    
    async def create_default_users(self):
        """Create default users for testing"""
        logger.info("👥 Creating default users...")
        
        try:
            conn = await asyncpg.connect(self.main_db_url)
            
            # Simple password hashing for development
            import hashlib
            def hash_password(password):
                return hashlib.sha256(password.encode()).hexdigest()
            
            def generate_api_key():
                import secrets
                return secrets.token_urlsafe(32)
            
            users = [
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
            
            for user_data in users:
                # Check if user exists
                existing = await conn.fetchrow(
                    "SELECT user_id FROM users WHERE email = $1", 
                    user_data['email']
                )
                
                if not existing:
                    # Insert user
                    user_id = await conn.fetchval("""
                        INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, api_key)
                        VALUES ($1, $2, $3, $4, $5, true, $6)
                        RETURNING user_id
                    """, 
                        user_data['email'],
                        hash_password(user_data['password']),
                        user_data['first_name'],
                        user_data['last_name'],
                        user_data['role'],
                        generate_api_key()
                    )
                    
                    # Insert role-specific record
                    if user_data['role'] == 'client':
                        await conn.execute("""
                            INSERT INTO clients (user_id, subscription_type, credits_remaining)
                            VALUES ($1, 'premium', 1000)
                        """, user_id)
                    elif user_data['role'] == 'expert':
                        await conn.execute("""
                            INSERT INTO experts (user_id, approved, specialization, experience_years)
                            VALUES ($1, true, 'General', 5)
                        """, user_id)
                    elif user_data['role'] == 'admin':
                        await conn.execute("""
                            INSERT INTO admins (user_id, permissions)
                            VALUES ($1, '{"all": true}')
                        """, user_id)
                    
                    logger.info(f"  ✅ Created user: {user_data['email']}")
                else:
                    logger.info(f"  ℹ️  User already exists: {user_data['email']}")
            
            await conn.close()
            logger.info("✅ Default users created")
            return True
            
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            return False
    
    async def verify_setup(self):
        """Verify database setup"""
        logger.info("🔍 Verifying database setup...")
        
        try:
            conn = await asyncpg.connect(self.main_db_url)
            
            # Check tables
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            logger.info("  📋 Tables created:")
            for table in tables:
                logger.info(f"    ✅ {table['table_name']}")
            
            # Check users
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            logger.info(f"  👥 Users: {user_count}")
            
            # Check indexes
            indexes = await conn.fetch("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY indexname
            """)
            
            logger.info(f"  📊 Indexes: {len(indexes)} created")
            
            await conn.close()
            logger.info("✅ Database verification completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def create_env_file(self):
        """Create .env file with correct database URLs"""
        logger.info("📝 Creating .env file...")
        
        env_content = f"""# Database Configuration
DATABASE_URL={self.main_db_url}
AUTH_DATABASE_URL={self.auth_db_url}
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_change_this_in_production
ENCRYPTION_KEY=your_encryption_key_here_change_this_in_production

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# API Keys (Add your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
POE_API_KEY_CHATGPT=wcX2fQ9s2D-6DrQN85NTbsC0lyhaIlwcs6p7CDslPeI
POE_API_KEY_CLAUDE=dReWOKrYBCRB3BiXHKfIcjSbyr-7Vq_vrw9a7PHQwyc
"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            logger.info("✅ .env file created")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create .env file: {e}")
            return False

async def main():
    """Main setup function"""
    logger.info("🚀 PostgreSQL Database Setup")
    logger.info("=" * 50)
    
    setup = PostgreSQLSetup()
    
    try:
        # Test PostgreSQL connection
        if not await setup.test_postgres_connection():
            logger.error("\n❌ PostgreSQL setup failed!")
            logger.error("\n📋 To install PostgreSQL:")
            logger.error("   1. Download from: https://www.postgresql.org/download/windows/")
            logger.error("   2. Install with default settings")
            logger.error("   3. Remember the password you set for 'postgres' user")
            logger.error("   4. Run this script again")
            logger.error("\n🐳 Or use Docker:")
            logger.error("   docker run -d --name qa-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15")
            return False
        
        # Create databases
        if not await setup.create_databases():
            return False
        
        # Run migrations
        if not await setup.run_migrations():
            return False
        
        # Create default users
        if not await setup.create_default_users():
            return False
        
        # Verify setup
        if not await setup.verify_setup():
            return False
        
        # Create .env file
        setup.create_env_file()
        
        logger.info("\n🎉 PostgreSQL setup completed successfully!")
        logger.info("\n🔑 Default login credentials:")
        logger.info("   Client: client@demo.com / demo123")
        logger.info("   Expert: expert@demo.com / demo123")
        logger.info("   Admin:  admin@demo.com / demo123")
        logger.info("\n🚀 Next steps:")
        logger.info("   1. Run tests: python run_tests.py")
        logger.info("   2. Start backend: python app/main.py")
        logger.info("   3. Test API endpoints")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

