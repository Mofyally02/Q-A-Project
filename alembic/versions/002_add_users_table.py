"""Add users table

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
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', sa.Enum('client', 'expert', 'admin', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('api_key', sa.String(255), nullable=True, unique=True),
        sa.Column('profile_data', postgresql.JSONB, nullable=True),
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Insert default users for each role
    op.execute("""
        INSERT INTO users (email, password_hash, first_name, last_name, role, is_active) VALUES
        ('client@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Client', 'client', true),
        ('expert@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Expert', 'expert', true),
        ('admin@demo.com', 'demo123:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'Demo', 'Admin', 'admin', true)
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_users_created_at', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_role', 'users')
    op.drop_index('idx_users_email', 'users')
    
    # Drop users table
    op.drop_table('users')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS userrole')
