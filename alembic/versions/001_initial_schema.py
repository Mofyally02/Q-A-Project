"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.VARCHAR(20), nullable=False),
        sa.Column('email', sa.VARCHAR(255), nullable=False),
        sa.Column('hashed_password', sa.VARCHAR(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("role IN ('client', 'expert', 'admin')", name='users_role_check'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    
    # Create questions table
    op.create_table('questions',
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.VARCHAR(10), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('subject', sa.VARCHAR(100), nullable=False),
        sa.Column('status', sa.VARCHAR(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("type IN ('text', 'image')", name='questions_type_check'),
        sa.CheckConstraint("status IN ('submitted', 'processing', 'humanized', 'review', 'delivered', 'rated')", name='questions_status_check'),
        sa.ForeignKeyConstraint(['client_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('question_id')
    )
    
    # Create answers table
    op.create_table('answers',
        sa.Column('answer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('humanized_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expert_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.FLOAT(), nullable=True),
        sa.Column('is_approved', sa.BOOLEAN(), nullable=True),
        sa.Column('rejection_reason', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ),
        sa.PrimaryKeyConstraint('answer_id')
    )
    
    # Create ratings table
    op.create_table('ratings',
        sa.Column('rating_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('score', sa.INTEGER(), nullable=False),
        sa.Column('comment', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('score >= 1 AND score <= 5', name='ratings_score_check'),
        sa.ForeignKeyConstraint(['expert_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ),
        sa.PrimaryKeyConstraint('rating_id')
    )
    
    # Create expert_reviews table
    op.create_table('expert_reviews',
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('answer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_approved', sa.BOOLEAN(), nullable=False),
        sa.Column('rejection_reason', sa.TEXT(), nullable=True),
        sa.Column('correction', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.answer_id'], ),
        sa.ForeignKeyConstraint(['expert_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('review_id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.VARCHAR(50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_questions_client_id', 'questions', ['client_id'])
    op.create_index('idx_questions_status', 'questions', ['status'])
    op.create_index('idx_questions_created_at', 'questions', ['created_at'])
    op.create_index('idx_answers_question_id', 'answers', ['question_id'])
    op.create_index('idx_ratings_question_id', 'ratings', ['question_id'])
    op.create_index('idx_ratings_expert_id', 'ratings', ['expert_id'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_question_id', 'audit_logs', ['question_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_question_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('idx_ratings_expert_id', table_name='ratings')
    op.drop_index('idx_ratings_question_id', table_name='ratings')
    op.drop_index('idx_answers_question_id', table_name='answers')
    op.drop_index('idx_questions_created_at', table_name='questions')
    op.drop_index('idx_questions_status', table_name='questions')
    op.drop_index('idx_questions_client_id', table_name='questions')
    
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('expert_reviews')
    op.drop_table('ratings')
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('users')
