"""Add missing tables and columns

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean, nullable=True, default=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('api_key', sa.String(255), nullable=True, unique=True))
    op.add_column('users', sa.Column('profile_data', postgresql.JSONB, nullable=True))
    
    # Add missing columns to answers table
    op.add_column('answers', sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create role-specific tables
    op.create_table('clients',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_type', sa.String(50), nullable=True, default='basic'),
        sa.Column('credits_remaining', sa.Integer, nullable=True, default=100),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    op.create_table('experts',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved', sa.Boolean, nullable=False, default=False),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('experience_years', sa.Integer, nullable=True),
        sa.Column('rating', sa.Float, nullable=True, default=0.0),
        sa.Column('total_reviews', sa.Integer, nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    op.create_table('admins',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permissions', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create expert metrics table
    op.create_table('expert_metrics',
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avg_rating', sa.Float, nullable=False, default=0.0),
        sa.Column('total_ratings', sa.Integer, nullable=False, default=0),
        sa.Column('total_score', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['expert_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('expert_id')
    )
    
    # Create additional indexes
    op.create_index('idx_users_first_name', 'users', ['first_name'])
    op.create_index('idx_users_last_name', 'users', ['last_name'])
    op.create_index('idx_users_api_key', 'users', ['api_key'])
    op.create_index('idx_answers_expert_id', 'answers', ['expert_id'])
    op.create_index('idx_experts_approved', 'experts', ['approved'])
    op.create_index('idx_experts_rating', 'experts', ['rating'])
    op.create_index('idx_clients_subscription', 'clients', ['subscription_type'])
    
    # Update existing users with default values
    op.execute("""
        UPDATE users SET 
            first_name = 'Demo',
            last_name = 'User',
            is_active = true,
            updated_at = NOW()
        WHERE first_name IS NULL
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_clients_subscription', 'clients')
    op.drop_index('idx_experts_rating', 'experts')
    op.drop_index('idx_experts_approved', 'experts')
    op.drop_index('idx_answers_expert_id', 'answers')
    op.drop_index('idx_users_api_key', 'users')
    op.drop_index('idx_users_last_name', 'users')
    op.drop_index('idx_users_first_name', 'users')
    
    # Drop tables
    op.drop_table('expert_metrics')
    op.drop_table('admins')
    op.drop_table('experts')
    op.drop_table('clients')
    
    # Drop columns
    op.drop_column('answers', 'expert_id')
    op.drop_column('users', 'profile_data')
    op.drop_column('users', 'api_key')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
