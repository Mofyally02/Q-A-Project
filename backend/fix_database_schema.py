#!/usr/bin/env python3
"""
Fix database schema to match code expectations
This script:
1. Creates missing tables from migration 004
2. Adds missing columns to existing tables
3. Ensures all endpoints can work with the database
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.db.session import db
import asyncpg


async def create_missing_tables():
    """Create missing tables from migration 004"""
    print("Creating missing tables...")
    
    async for conn in db.get_connection():
        # Check and create transactions table
        transactions_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'transactions'
            )
        """)
        
        if not transactions_exists:
            print("  Creating transactions table...")
            await conn.execute("""
                CREATE TABLE transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    amount INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    description TEXT,
                    reference_id UUID,
                    reference_type VARCHAR(50),
                    metadata JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT transactions_type_check CHECK (type IN ('credit', 'debit', 'refund', 'topup', 'purchase', 'reward'))
                );
                CREATE INDEX idx_transactions_user_id ON transactions(user_id);
                CREATE INDEX idx_transactions_type ON transactions(type);
                CREATE INDEX idx_transactions_created_at ON transactions(created_at);
            """)
            print("  ✅ transactions table created")
        
        # Check and create admin_actions table
        admin_actions_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'admin_actions'
            )
        """)
        
        if not admin_actions_exists:
            print("  Creating admin_actions table...")
            await conn.execute("""
                CREATE TABLE admin_actions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    admin_id UUID NOT NULL,
                    action_type VARCHAR(100) NOT NULL,
                    target_type VARCHAR(50),
                    target_id UUID,
                    details JSONB,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
                CREATE INDEX idx_admin_actions_action_type ON admin_actions(action_type);
            """)
            print("  ✅ admin_actions table created")
        
        # Check and create api_keys table
        api_keys_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_keys'
            )
        """)
        
        if not api_keys_exists:
            print("  Creating api_keys table...")
            await conn.execute("""
                CREATE TABLE api_keys (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    key_type VARCHAR(50) NOT NULL,
                    encrypted_key TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    last_tested_at TIMESTAMPTZ,
                    last_tested_status VARCHAR(20),
                    created_by_id UUID,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_api_keys_key_type ON api_keys(key_type);
            """)
            print("  ✅ api_keys table created")
        
        # Check and create system_settings table
        system_settings_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'system_settings'
            )
        """)
        
        if not system_settings_exists:
            print("  Creating system_settings table...")
            await conn.execute("""
                CREATE TABLE system_settings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    key VARCHAR(100) NOT NULL UNIQUE,
                    value JSONB NOT NULL,
                    description TEXT,
                    updated_by_id UUID,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_system_settings_key ON system_settings(key);
            """)
            print("  ✅ system_settings table created")
        
        # Check and create notification_templates table
        notification_templates_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'notification_templates'
            )
        """)
        
        if not notification_templates_exists:
            print("  Creating notification_templates table...")
            await conn.execute("""
                CREATE TABLE notification_templates (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    subject VARCHAR(500),
                    body TEXT NOT NULL,
                    template_type VARCHAR(20) NOT NULL,
                    variables JSONB,
                    created_by_id UUID,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_notification_templates_type ON notification_templates(template_type);
            """)
            print("  ✅ notification_templates table created")
        
        # Check and create compliance_flags table
        compliance_flags_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'compliance_flags'
            )
        """)
        
        if not compliance_flags_exists:
            print("  Creating compliance_flags table...")
            await conn.execute("""
                CREATE TABLE compliance_flags (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content_id UUID NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    reason VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
                    details JSONB,
                    user_id UUID,
                    resolved BOOLEAN NOT NULL DEFAULT false,
                    resolved_at TIMESTAMPTZ,
                    resolved_by UUID,
                    resolution_notes TEXT,
                    flagged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_compliance_flags_content ON compliance_flags(content_type, content_id);
            """)
            print("  ✅ compliance_flags table created")
        
        # Check and create expert_metrics table
        expert_metrics_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'expert_metrics'
            )
        """)
        
        if not expert_metrics_exists:
            print("  Creating expert_metrics table...")
            await conn.execute("""
                CREATE TABLE expert_metrics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    expert_id UUID NOT NULL UNIQUE,
                    total_earnings NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                    total_reviews INTEGER NOT NULL DEFAULT 0,
                    total_ratings INTEGER NOT NULL DEFAULT 0,
                    average_rating NUMERIC(3, 2) NOT NULL DEFAULT 0.00,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    completed_tasks INTEGER NOT NULL DEFAULT 0,
                    pending_tasks INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_expert_metrics_expert_id ON expert_metrics(expert_id);
            """)
            print("  ✅ expert_metrics table created")
        
        # Check and create client_wallet table
        client_wallet_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'client_wallet'
            )
        """)
        
        if not client_wallet_exists:
            print("  Creating client_wallet table...")
            await conn.execute("""
                CREATE TABLE client_wallet (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    client_id UUID NOT NULL UNIQUE,
                    credits_balance INTEGER NOT NULL DEFAULT 0,
                    credits_total INTEGER NOT NULL DEFAULT 0,
                    credits_used INTEGER NOT NULL DEFAULT 0,
                    subscription_type VARCHAR(50),
                    subscription_status VARCHAR(20),
                    subscription_expires_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX idx_client_wallet_client_id ON client_wallet(client_id);
            """)
            print("  ✅ client_wallet table created")
        
        print()
        print("✅ All missing tables created")
        break


async def add_missing_columns():
    """Add missing columns to existing tables"""
    print("Adding missing columns to existing tables...")
    
    async for conn in db.get_connection():
        # Add missing columns to users table
        # Check if is_verified exists
        is_verified_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'is_verified'
            )
        """)
        
        if not is_verified_exists:
            print("  Adding is_verified to users...")
            await conn.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT false;")
            print("  ✅ is_verified added")
        
        # Check if is_banned exists
        is_banned_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'is_banned'
            )
        """)
        
        if not is_banned_exists:
            print("  Adding is_banned to users...")
            await conn.execute("ALTER TABLE users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT false;")
            print("  ✅ is_banned added")
        
        # Add missing columns to questions table
        # Check if expert_id exists
        expert_id_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'questions' 
                AND column_name = 'expert_id'
            )
        """)
        
        if not expert_id_exists:
            print("  Adding expert_id to questions...")
            await conn.execute("ALTER TABLE questions ADD COLUMN expert_id UUID;")
            print("  ✅ expert_id added")
        
        # Add missing columns to answers table
        is_approved_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'answers' 
                AND column_name = 'is_approved'
            )
        """)
        
        if not is_approved_exists:
            print("  Adding is_approved to answers...")
            await conn.execute("ALTER TABLE answers ADD COLUMN is_approved BOOLEAN NOT NULL DEFAULT false;")
            print("  ✅ is_approved added")
        
        # Add missing columns to ratings table
        score_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'ratings' 
                AND column_name = 'score'
            )
        """)
        
        if not score_exists:
            print("  Adding score to ratings...")
            await conn.execute("ALTER TABLE ratings ADD COLUMN score INTEGER CHECK (score >= 1 AND score <= 5);")
            print("  ✅ score added")
        
        # Add missing columns to notifications table
        type_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'notifications' 
                AND column_name = 'type'
            )
        """)
        
        if not type_exists:
            print("  Adding type to notifications...")
            await conn.execute("ALTER TABLE notifications ADD COLUMN type VARCHAR(50);")
            print("  ✅ type added")
        
        print()
        print("✅ All missing columns added")
        break


async def main():
    """Run database schema fixes"""
    print("=" * 60)
    print("Fixing Database Schema")
    print("=" * 60)
    print()
    
    try:
        await db.connect()
        print("✅ Connected to database")
        print()
        
        await create_missing_tables()
        await add_missing_columns()
        
        print()
        print("=" * 60)
        print("✅ Database schema fixed!")
        print("=" * 60)
        print()
        print("Next: Run verify_database_connections.py to verify")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

