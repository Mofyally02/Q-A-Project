"""Add admin tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend users table with admin fields
    op.add_column('users', sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('banned_at', postgresql.TIMESTAMPTZ(), nullable=True))
    op.add_column('users', sa.Column('banned_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('invited_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('last_active', postgresql.TIMESTAMPTZ(), nullable=True))
    op.add_column('users', sa.Column('metadata', postgresql.JSON(), nullable=False, server_default='{}'))
    
    # Update role column to support new roles
    op.execute("""
        ALTER TABLE users 
        DROP CONSTRAINT IF EXISTS users_role_check;
    """)
    op.execute("""
        ALTER TABLE users 
        ADD CONSTRAINT users_role_check 
        CHECK (role IN ('client', 'expert', 'admin_editor', 'super_admin'));
    """)
    
    # Add foreign keys
    op.create_foreign_key(
        'fk_users_banned_by',
        'users', 'users',
        ['banned_by_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_users_invited_by',
        'users', 'users',
        ['invited_by_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create admin_actions table
    op.create_table(
        'admin_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_admin_actions_admin_id', 'admin_actions', ['admin_id'])
    op.create_index('idx_admin_actions_action_type', 'admin_actions', ['action_type'])
    op.create_index('idx_admin_actions_target', 'admin_actions', ['target_type', 'target_id'])
    op.create_index('idx_admin_actions_created_at', 'admin_actions', ['created_at'])
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_type', sa.String(50), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_tested_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('last_tested_status', sa.String(20), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_api_keys_key_type', 'api_keys', ['key_type'])
    op.create_index('idx_api_keys_is_active', 'api_keys', ['is_active'])
    
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', postgresql.JSON(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_system_settings_key', 'system_settings', ['key'])
    
    # Create notification_templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('template_type', sa.String(20), nullable=False),
        sa.Column('variables', postgresql.JSON(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_notification_templates_type', 'notification_templates', ['template_type'])
    
    # Create compliance_flags table
    op.create_table(
        'compliance_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),  # 'question', 'answer', 'user'
        sa.Column('reason', sa.String(50), nullable=False),  # 'ai_content', 'plagiarism', 'vpn', 'suspicious_activity'
        sa.Column('severity', sa.String(20), nullable=False, server_default='medium'),  # 'low', 'medium', 'high', 'critical'
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', postgresql.TIMESTAMPTZ(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('flagged_at', postgresql.TIMESTAMPTZ(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_compliance_flags_content', 'compliance_flags', ['content_type', 'content_id'])
    op.create_index('idx_compliance_flags_reason', 'compliance_flags', ['reason'])
    op.create_index('idx_compliance_flags_severity', 'compliance_flags', ['severity'])
    op.create_index('idx_compliance_flags_resolved', 'compliance_flags', ['resolved'])


def downgrade() -> None:
    # Drop compliance_flags table
    op.drop_index('idx_compliance_flags_resolved', table_name='compliance_flags')
    op.drop_index('idx_compliance_flags_severity', table_name='compliance_flags')
    op.drop_index('idx_compliance_flags_reason', table_name='compliance_flags')
    op.drop_index('idx_compliance_flags_content', table_name='compliance_flags')
    op.drop_table('compliance_flags')
    
    # Drop notification_templates table
    op.drop_index('idx_notification_templates_type', table_name='notification_templates')
    op.drop_table('notification_templates')
    
    # Drop system_settings table
    op.drop_index('idx_system_settings_key', table_name='system_settings')
    op.drop_table('system_settings')
    
    # Drop api_keys table
    op.drop_index('idx_api_keys_is_active', table_name='api_keys')
    op.drop_index('idx_api_keys_key_type', table_name='api_keys')
    op.drop_table('api_keys')
    
    # Drop admin_actions table
    op.drop_index('idx_admin_actions_created_at', table_name='admin_actions')
    op.drop_index('idx_admin_actions_target', table_name='admin_actions')
    op.drop_index('idx_admin_actions_action_type', table_name='admin_actions')
    op.drop_index('idx_admin_actions_admin_id', table_name='admin_actions')
    op.drop_table('admin_actions')
    
    # Remove foreign keys from users
    op.drop_constraint('fk_users_invited_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_banned_by', 'users', type_='foreignkey')
    
    # Remove columns from users table
    op.drop_column('users', 'metadata')
    op.drop_column('users', 'last_active')
    op.drop_column('users', 'invited_by_id')
    op.drop_column('users', 'banned_by_id')
    op.drop_column('users', 'banned_at')
    op.drop_column('users', 'is_banned')
    
    # Restore original role constraint
    op.execute("""
        ALTER TABLE users 
        DROP CONSTRAINT IF EXISTS users_role_check;
    """)

