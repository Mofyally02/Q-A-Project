#!/usr/bin/env python3
"""
Create missing tables in the main database (qa_system)
This script ensures questions, answers, ratings, and expert_reviews tables exist
"""
import asyncio
import asyncpg
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_questions_table(conn):
    """Create questions table in main database"""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_id UUID NOT NULL,
            question_type VARCHAR(20) NOT NULL DEFAULT 'text',
            content JSONB NOT NULL,
            subject VARCHAR(100),
            status VARCHAR(50) NOT NULL DEFAULT 'submitted',
            priority VARCHAR(20) NOT NULL DEFAULT 'normal',
            word_count INTEGER,
            estimated_time INTEGER,
            assigned_expert_id UUID,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            submitted_at TIMESTAMP WITH TIME ZONE,
            processed_at TIMESTAMP WITH TIME ZONE,
            delivered_at TIMESTAMP WITH TIME ZONE,
            metadata JSONB,
            CONSTRAINT question_type_check CHECK (question_type IN ('text', 'image', 'mixed')),
            CONSTRAINT status_check CHECK (status IN ('submitted', 'processing', 'ai_generated', 'humanized', 'expert_review', 'approved', 'delivered', 'rated', 'rejected', 'cancelled')),
            CONSTRAINT priority_check CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
        )
    """)
    
    # Create indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_client_id ON questions(client_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_content ON questions USING GIN(content)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_questions_metadata ON questions USING GIN(metadata)")
    
    logger.info("✓ Created questions table")

async def create_answers_table(conn):
    """Create answers table in main database"""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            question_id UUID NOT NULL,
            ai_response JSONB,
            ai_model VARCHAR(100),
            ai_confidence_score DECIMAL(5,4),
            humanized_response JSONB,
            humanization_service VARCHAR(50),
            humanization_confidence DECIMAL(5,4),
            expert_response JSONB,
            expert_id UUID,
            final_response JSONB,
            response_type VARCHAR(50) NOT NULL DEFAULT 'ai',
            word_count INTEGER,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            approved_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT response_type_check CHECK (response_type IN ('ai', 'humanized', 'expert', 'hybrid'))
        )
    """)
    
    # Create indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_answers_expert_id ON answers(expert_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_answers_created_at ON answers(created_at)")
    
    logger.info("✓ Created answers table")

async def create_ratings_table(conn):
    """Create ratings table in main database"""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            question_id UUID NOT NULL,
            client_id UUID NOT NULL,
            expert_id UUID,
            answer_id UUID,
            overall_score DECIMAL(2,1) NOT NULL CHECK (overall_score >= 1.0 AND overall_score <= 5.0),
            accuracy_score DECIMAL(2,1) CHECK (accuracy_score >= 1.0 AND accuracy_score <= 5.0),
            clarity_score DECIMAL(2,1) CHECK (clarity_score >= 1.0 AND clarity_score <= 5.0),
            completeness_score DECIMAL(2,1) CHECK (completeness_score >= 1.0 AND completeness_score <= 5.0),
            relevance_score DECIMAL(2,1) CHECK (relevance_score >= 1.0 AND relevance_score <= 5.0),
            comment TEXT,
            is_helpful BOOLEAN,
            would_recommend BOOLEAN,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    """)
    
    # Create indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_question_id ON ratings(question_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_client_id ON ratings(client_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_expert_id ON ratings(expert_id)")
    
    logger.info("✓ Created ratings table")

async def create_expert_reviews_table(conn):
    """Create expert_reviews table in main database"""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS expert_reviews (
            review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            answer_id UUID NOT NULL,
            question_id UUID NOT NULL,
            expert_id UUID NOT NULL,
            review_status VARCHAR(50) NOT NULL DEFAULT 'pending',
            is_approved BOOLEAN,
            rejection_reason TEXT,
            corrections JSONB,
            review_notes TEXT,
            review_time_seconds INTEGER,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT review_status_check CHECK (review_status IN ('pending', 'in_progress', 'approved', 'rejected', 'needs_revision'))
        )
    """)
    
    # Create indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_expert_reviews_answer_id ON expert_reviews(answer_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_expert_reviews_question_id ON expert_reviews(question_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_expert_reviews_expert_id ON expert_reviews(expert_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_expert_reviews_status ON expert_reviews(review_status)")
    
    logger.info("✓ Created expert_reviews table")

async def check_table_exists(conn, table_name):
    """Check if a table exists"""
    exists = await conn.fetchval("""
        SELECT EXISTS(
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = $1
        )
    """, table_name)
    return exists

async def main():
    """Create missing tables in main database"""
    logger.info("Creating missing tables in main database (qa_system)...")
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        
        # Check and create each table
        tables_to_create = {
            "questions": create_questions_table,
            "answers": create_answers_table,
            "ratings": create_ratings_table,
            "expert_reviews": create_expert_reviews_table,
        }
        
        for table_name, create_func in tables_to_create.items():
            exists = await check_table_exists(conn, table_name)
            if not exists:
                logger.info(f"Creating {table_name} table...")
                await create_func(conn)
            else:
                logger.info(f"✓ {table_name} table already exists")
        
        await conn.close()
        logger.info("\n✅ All required tables verified/created successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Start Redis: redis-server or docker-compose up redis")
        logger.info("  2. Start RabbitMQ: rabbitmq-server or docker-compose up rabbitmq")
        logger.info("  3. Run verification: python verify_setup.py")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())

