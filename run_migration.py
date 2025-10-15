#!/usr/bin/env python3
"""
Database migration runner for AL-Tech Academy Q&A System
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from app.config import settings

load_dotenv()

async def run_migration():
    """Run database migration to create users table"""
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.database_url)
        
        print("Connected to PostgreSQL database")
        
        # Check if users table already exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        
        if table_exists:
            print("Users table already exists. Skipping migration.")
            return
        
        # Create users table
        print("Creating users table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                role userrole NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE,
                api_key VARCHAR(255) UNIQUE,
                profile_data JSONB
            )
        """)
        
        # Create userrole enum if it doesn't exist
        await conn.execute("""
            DO $$ BEGIN
                CREATE TYPE userrole AS ENUM ('client', 'expert', 'admin');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Create indexes
        print("Creating indexes...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at)")
        
        # Insert default users
        print("Inserting default users...")
        await conn.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active) VALUES
            ('client@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Client', 'client', true),
            ('expert@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Expert', 'expert', true),
            ('admin@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Admin', 'admin', true)
            ON CONFLICT (email) DO NOTHING
        """)
        
        print("Migration completed successfully!")
        print("\nDefault users created:")
        print("- client@demo.com (password: demo123)")
        print("- expert@demo.com (password: demo123)")
        print("- admin@demo.com (password: demo123)")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
