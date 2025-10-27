#!/usr/bin/env python3
"""
Database migration runner for AL-Tech Academy Q&A System
"""
import asyncio
import asyncpg
import os
import hashlib
import secrets
from dotenv import load_dotenv
from app.config import settings

load_dotenv()

async def run_migration():
    """Run database migration to create users table"""
    try:
        # Connect to auth database
        conn = await asyncpg.connect(settings.auth_database_url)
        
        print("Connected to PostgreSQL database")
        
        # Ensure required extension and types exist before creating tables
        # Needed for gen_random_uuid()
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
        """)

        # Create userrole enum if it doesn't exist
        await conn.execute("""
            DO $$ BEGIN
                CREATE TYPE userrole AS ENUM ('client', 'expert', 'admin');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)

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

        # Role-specific tables
        print("Creating role-specific tables...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                approved BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)
        
        # Create indexes
        print("Creating indexes...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at)")
        
        # Remove any legacy demo users if present
        await conn.execute(
            "DELETE FROM users WHERE email = ANY($1)",
            [
                'client@demo.com',
                'expert@demo.com',
                'admin@demo.com'
            ]
        )

        # Seed requested admin account if missing
        admin_email = "allansaiti02@gmail.com"
        admin_password = "MofyAlly.21"
        existing_admin = await conn.fetchval("SELECT user_id FROM users WHERE email = $1", admin_email)
        if not existing_admin:
            # Hash password with same scheme as SecurityUtils
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((admin_password + salt).encode()).hexdigest()
            full_hash = f"{salt}:{password_hash}"
            user_id = await conn.fetchval(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
                VALUES ($1, $2, $3, $4, 'admin', TRUE)
                RETURNING user_id
                """,
                admin_email,
                full_hash,
                "Admin",
                "User"
            )
            await conn.execute("INSERT INTO admins (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", user_id)
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
