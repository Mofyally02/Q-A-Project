"""Complete schema for all 90 endpoints

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

This migration creates all tables needed for:
- Admin endpoints (71)
- Client endpoints (12)
- Expert endpoints (7)
- Health endpoints (5)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix users table to match our model structure
    # Change user_id to id if it exists, or ensure id exists
    op.execute("""
        DO $$ 
        BEGIN
            -- Check if column 'id' exists, if not rename 'user_id' to 'id'
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='user_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='id'
            ) THEN
                ALTER TABLE users RENAME COLUMN user_id TO id;
            END IF;
        END $$;
    """)
    
    # Ensure profile_data column exists (migration 003 added metadata, we need profile_data)
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='metadata'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='profile_data'
            ) THEN
                ALTER TABLE users RENAME COLUMN metadata TO profile_data;
            END IF;
        END $$;
    """)
    
    # Create questions table (if not exists)
    op.create_table(
        'questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('subject', sa.String(200), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='submitted'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='normal'),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('estimated_time', sa.Integer, nullable=True),
        sa.Column('credits_cost', sa.Integer, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('submitted_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('processed_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('delivered_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint("type IN ('text', 'image', 'mixed')", name='questions_type_check'),
        sa.CheckConstraint("status IN ('submitted', 'processing', 'ai_generated', 'humanized', 'expert_review', 'approved', 'delivered', 'rated', 'rejected', 'cancelled')", name='questions_status_check'),
        sa.CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name='questions_priority_check'),
    )
    op.create_index('idx_questions_client_id', 'questions', ['client_id'])
    op.create_index('idx_questions_status', 'questions', ['status'])
    op.create_index('idx_questions_expert_id', 'questions', ['expert_id'])
    op.create_index('idx_questions_created_at', 'questions', ['created_at'])
    op.create_index('idx_questions_priority', 'questions', ['priority'])
    
    # Create answers table
    op.create_table(
        'answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ai_response', postgresql.JSONB, nullable=True),
        sa.Column('humanized_response', postgresql.JSONB, nullable=True),
        sa.Column('expert_response', postgresql.JSONB, nullable=True),
        sa.Column('final_response', postgresql.JSONB, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('is_approved', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='answers_confidence_check'),
    )
    op.create_index('idx_answers_question_id', 'answers', ['question_id'])
    op.create_index('idx_answers_expert_id', 'answers', ['expert_id'])
    op.create_index('idx_answers_is_approved', 'answers', ['is_approved'])
    
    # Create ratings table
    op.create_table(
        'ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('score >= 1 AND score <= 5', name='ratings_score_check'),
        sa.UniqueConstraint('question_id', 'client_id', name='uq_rating_question_client'),
    )
    op.create_index('idx_ratings_question_id', 'ratings', ['question_id'])
    op.create_index('idx_ratings_expert_id', 'ratings', ['expert_id'])
    op.create_index('idx_ratings_client_id', 'ratings', ['client_id'])
    
    # Create expert_reviews table
    op.create_table(
        'expert_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('answer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_approved', sa.Boolean, nullable=False),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('correction', postgresql.JSONB, nullable=True),
        sa.Column('review_time_minutes', sa.Integer, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_expert_reviews_answer_id', 'expert_reviews', ['answer_id'])
    op.create_index('idx_expert_reviews_expert_id', 'expert_reviews', ['expert_id'])
    op.create_index('idx_expert_reviews_question_id', 'expert_reviews', ['question_id'])
    
    # Create transactions table (for wallet/credits)
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('balance_after', sa.Integer, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("type IN ('credit', 'debit', 'refund', 'topup', 'purchase', 'reward')", name='transactions_type_check'),
    )
    op.create_index('idx_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('idx_transactions_type', 'transactions', ['type'])
    op.create_index('idx_transactions_created_at', 'transactions', ['created_at'])
    op.create_index('idx_transactions_reference', 'transactions', ['reference_type', 'reference_id'])
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('read_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("type IN ('info', 'success', 'warning', 'error', 'question', 'answer', 'rating', 'system')", name='notifications_type_check'),
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    
    # Create expert_metrics table (for earnings tracking)
    op.create_table(
        'expert_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('total_earnings', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total_reviews', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_ratings', sa.Integer, nullable=False, server_default='0'),
        sa.Column('average_rating', sa.Numeric(3, 2), nullable=False, server_default='0.00'),
        sa.Column('total_score', sa.Integer, nullable=False, server_default='0'),
        sa.Column('completed_tasks', sa.Integer, nullable=False, server_default='0'),
        sa.Column('pending_tasks', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['expert_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('average_rating >= 0.0 AND average_rating <= 5.0', name='expert_metrics_rating_check'),
    )
    op.create_index('idx_expert_metrics_expert_id', 'expert_metrics', ['expert_id'])
    
    # Create client_wallet table (for client credits)
    op.create_table(
        'client_wallet',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('credits_balance', sa.Integer, nullable=False, server_default='0'),
        sa.Column('credits_total', sa.Integer, nullable=False, server_default='0'),
        sa.Column('credits_used', sa.Integer, nullable=False, server_default='0'),
        sa.Column('subscription_type', sa.String(50), nullable=True),
        sa.Column('subscription_status', sa.String(20), nullable=True),
        sa.Column('subscription_expires_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("subscription_status IN ('active', 'suspended', 'cancelled', 'expired')", name='client_wallet_status_check'),
    )
    op.create_index('idx_client_wallet_client_id', 'client_wallet', ['client_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('client_wallet')
    op.drop_table('expert_metrics')
    op.drop_table('notifications')
    op.drop_table('transactions')
    op.drop_table('expert_reviews')
    op.drop_table('ratings')
    op.drop_table('answers')
    op.drop_table('questions')
    
    # Revert users table changes if needed
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='user_id'
            ) THEN
                ALTER TABLE users RENAME COLUMN id TO user_id;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='profile_data'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='metadata'
            ) THEN
                ALTER TABLE users RENAME COLUMN profile_data TO metadata;
            END IF;
        END $$;
    """)

