"""Add achievements and streaks tables

Revision ID: 005
Revises: 004
Create Date: 2024-12-09 13:00:00.000000

This migration creates tables for:
- Achievements tracking
- Achievement progress tracking
- Streaks tracking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Achievements Table
    op.create_table(
        'achievements',
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_type', sa.String(50), nullable=False),
        sa.Column('achievement_key', sa.String(100), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('target', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('client_id', 'achievement_key', name='unique_client_achievement')
    )
    
    op.create_index('idx_achievements_client_id', 'achievements', ['client_id'])
    op.create_index('idx_achievements_type', 'achievements', ['achievement_type'])
    op.create_index('idx_achievements_key', 'achievements', ['achievement_key'])
    op.create_index('idx_achievements_unlocked_at', 'achievements', ['unlocked_at'], postgresql_where=sa.text('unlocked_at IS NOT NULL'))
    
    # Achievement Progress Table
    op.create_table(
        'achievement_progress',
        sa.Column('progress_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_key', sa.String(100), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('target_value', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('progress_percentage', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('client_id', 'achievement_key', name='unique_client_progress')
    )
    
    op.create_index('idx_achievement_progress_client_id', 'achievement_progress', ['client_id'])
    op.create_index('idx_achievement_progress_key', 'achievement_progress', ['achievement_key'])
    
    # Streaks Table
    op.create_table(
        'streaks',
        sa.Column('streak_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('streak_type', sa.String(50), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=False),
        sa.Column('streak_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('client_id', 'streak_type', name='unique_client_streak_type')
    )
    
    op.create_index('idx_streaks_client_id', 'streaks', ['client_id'])
    op.create_index('idx_streaks_type', 'streaks', ['streak_type'])
    op.create_index('idx_streaks_last_activity', 'streaks', ['last_activity_date'])


def downgrade() -> None:
    op.drop_index('idx_streaks_last_activity', table_name='streaks')
    op.drop_index('idx_streaks_type', table_name='streaks')
    op.drop_index('idx_streaks_client_id', table_name='streaks')
    op.drop_table('streaks')
    
    op.drop_index('idx_achievement_progress_key', table_name='achievement_progress')
    op.drop_index('idx_achievement_progress_client_id', table_name='achievement_progress')
    op.drop_table('achievement_progress')
    
    op.drop_index('idx_achievements_unlocked_at', table_name='achievements')
    op.drop_index('idx_achievements_key', table_name='achievements')
    op.drop_index('idx_achievements_type', table_name='achievements')
    op.drop_index('idx_achievements_client_id', table_name='achievements')
    op.drop_table('achievements')

