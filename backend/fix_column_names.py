#!/usr/bin/env python3
"""
Fix column names to match code expectations
Renames user_id -> id and question_id -> id where needed
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.db.session import db


async def fix_column_names():
    """Rename columns to match code expectations"""
    print("=" * 60)
    print("Fixing Column Names")
    print("=" * 60)
    print()
    
    async for conn in db.get_connection():
        # Check if users table has user_id but not id
        has_user_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'user_id'
            )
        """)
        
        has_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'id'
            )
        """)
        
        if has_user_id and not has_id:
            print("Renaming users.user_id to users.id...")
            # First, drop foreign key constraints that reference user_id
            await conn.execute("""
                DO $$ 
                BEGIN
                    -- Drop foreign keys that reference user_id
                    ALTER TABLE IF EXISTS questions DROP CONSTRAINT IF EXISTS questions_client_id_fkey;
                    ALTER TABLE IF EXISTS answers DROP CONSTRAINT IF EXISTS answers_expert_id_fkey;
                    ALTER TABLE IF EXISTS ratings DROP CONSTRAINT IF EXISTS ratings_expert_id_fkey;
                    ALTER TABLE IF EXISTS ratings DROP CONSTRAINT IF EXISTS ratings_client_id_fkey;
                    ALTER TABLE IF EXISTS expert_reviews DROP CONSTRAINT IF EXISTS expert_reviews_expert_id_fkey;
                    ALTER TABLE IF EXISTS transactions DROP CONSTRAINT IF EXISTS transactions_user_id_fkey;
                    ALTER TABLE IF EXISTS notifications DROP CONSTRAINT IF EXISTS notifications_user_id_fkey;
                    ALTER TABLE IF EXISTS admin_actions DROP CONSTRAINT IF EXISTS admin_actions_admin_id_fkey;
                    ALTER TABLE IF EXISTS api_keys DROP CONSTRAINT IF EXISTS api_keys_created_by_id_fkey;
                    ALTER TABLE IF EXISTS system_settings DROP CONSTRAINT IF EXISTS system_settings_updated_by_id_fkey;
                    ALTER TABLE IF EXISTS notification_templates DROP CONSTRAINT IF EXISTS notification_templates_created_by_id_fkey;
                    ALTER TABLE IF EXISTS compliance_flags DROP CONSTRAINT IF EXISTS compliance_flags_user_id_fkey;
                    ALTER TABLE IF EXISTS compliance_flags DROP CONSTRAINT IF EXISTS compliance_flags_resolved_by_fkey;
                    ALTER TABLE IF EXISTS expert_metrics DROP CONSTRAINT IF EXISTS expert_metrics_expert_id_fkey;
                    ALTER TABLE IF EXISTS client_wallet DROP CONSTRAINT IF EXISTS client_wallet_client_id_fkey;
                END $$;
            """)
            
            # Rename the column
            await conn.execute("ALTER TABLE users RENAME COLUMN user_id TO id;")
            
            # Recreate foreign keys with new column name
            await conn.execute("""
                ALTER TABLE questions ADD CONSTRAINT questions_client_id_fkey 
                    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE answers ADD CONSTRAINT answers_expert_id_fkey 
                    FOREIGN KEY (expert_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE ratings ADD CONSTRAINT ratings_expert_id_fkey 
                    FOREIGN KEY (expert_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE ratings ADD CONSTRAINT ratings_client_id_fkey 
                    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE expert_reviews ADD CONSTRAINT expert_reviews_expert_id_fkey 
                    FOREIGN KEY (expert_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE transactions ADD CONSTRAINT transactions_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE notifications ADD CONSTRAINT notifications_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE admin_actions ADD CONSTRAINT admin_actions_admin_id_fkey 
                    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE api_keys ADD CONSTRAINT api_keys_created_by_id_fkey 
                    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE system_settings ADD CONSTRAINT system_settings_updated_by_id_fkey 
                    FOREIGN KEY (updated_by_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE notification_templates ADD CONSTRAINT notification_templates_created_by_id_fkey 
                    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE compliance_flags ADD CONSTRAINT compliance_flags_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE compliance_flags ADD CONSTRAINT compliance_flags_resolved_by_fkey 
                    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL;
                ALTER TABLE expert_metrics ADD CONSTRAINT expert_metrics_expert_id_fkey 
                    FOREIGN KEY (expert_id) REFERENCES users(id) ON DELETE CASCADE;
                ALTER TABLE client_wallet ADD CONSTRAINT client_wallet_client_id_fkey 
                    FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE;
            """)
            print("✅ users.user_id renamed to users.id")
        
        # Check if questions table has question_id but not id
        has_question_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'questions' 
                AND column_name = 'question_id'
            )
        """)
        
        has_q_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'questions' 
                AND column_name = 'id'
            )
        """)
        
        if has_question_id and not has_q_id:
            print("Renaming questions.question_id to questions.id...")
            # Drop foreign keys
            await conn.execute("""
                ALTER TABLE IF EXISTS answers DROP CONSTRAINT IF EXISTS answers_question_id_fkey;
                ALTER TABLE IF EXISTS ratings DROP CONSTRAINT IF EXISTS ratings_question_id_fkey;
                ALTER TABLE IF EXISTS expert_reviews DROP CONSTRAINT IF EXISTS expert_reviews_question_id_fkey;
            """)
            
            # Rename column
            await conn.execute("ALTER TABLE questions RENAME COLUMN question_id TO id;")
            
            # Recreate foreign keys
            await conn.execute("""
                ALTER TABLE answers ADD CONSTRAINT answers_question_id_fkey 
                    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE;
                ALTER TABLE ratings ADD CONSTRAINT ratings_question_id_fkey 
                    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE;
                ALTER TABLE expert_reviews ADD CONSTRAINT expert_reviews_question_id_fkey 
                    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE;
            """)
            print("✅ questions.question_id renamed to questions.id")
        
        # Check if answers table has answer_id but not id
        has_answer_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'answers' 
                AND column_name = 'answer_id'
            )
        """)
        
        has_a_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'answers' 
                AND column_name = 'id'
            )
        """)
        
        if has_answer_id and not has_a_id:
            print("Renaming answers.answer_id to answers.id...")
            await conn.execute("""
                ALTER TABLE IF EXISTS expert_reviews DROP CONSTRAINT IF EXISTS expert_reviews_answer_id_fkey;
            """)
            await conn.execute("ALTER TABLE answers RENAME COLUMN answer_id TO id;")
            await conn.execute("""
                ALTER TABLE expert_reviews ADD CONSTRAINT expert_reviews_answer_id_fkey 
                    FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE;
            """)
            print("✅ answers.answer_id renamed to answers.id")
        
        # Check if ratings table has rating_id but not id
        has_rating_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'ratings' 
                AND column_name = 'rating_id'
            )
        """)
        
        has_r_id = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'ratings' 
                AND column_name = 'id'
            )
        """)
        
        if has_rating_id and not has_r_id:
            print("Renaming ratings.rating_id to ratings.id...")
            await conn.execute("ALTER TABLE ratings RENAME COLUMN rating_id TO id;")
            print("✅ ratings.rating_id renamed to ratings.id")
        
        print()
        print("✅ Column names fixed!")
        break


async def main():
    try:
        await db.connect()
        await fix_column_names()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

