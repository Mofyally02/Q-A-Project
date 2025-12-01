-- Add missing columns to users table
-- This migration adds columns that are used by the application but missing from the schema

-- Add is_banned column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_banned BOOLEAN NOT NULL DEFAULT FALSE;

-- Add invited_by column (for tracking who invited the user)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS invited_by UUID REFERENCES users(user_id) ON DELETE SET NULL;

-- Add user_metadata column (alternative name for profile_data, for compatibility)
-- Note: profile_data already exists, so we'll just ensure it's there
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS user_metadata JSONB;
-- We'll use profile_data instead

-- Create index on is_banned for faster queries
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users(is_banned) WHERE is_banned = TRUE;

-- Create index on invited_by
CREATE INDEX IF NOT EXISTS idx_users_invited_by ON users(invited_by) WHERE invited_by IS NOT NULL;

-- Update the enum to include super_admin and admin_editor if not already present
DO $$ 
BEGIN
    -- Add super_admin if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'super_admin' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole')) THEN
        ALTER TYPE userrole ADD VALUE 'super_admin';
    END IF;
    
    -- Add admin_editor if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'admin_editor' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole')) THEN
        ALTER TYPE userrole ADD VALUE 'admin_editor';
    END IF;
END $$;

-- Update the role_check constraint to include new roles
ALTER TABLE users DROP CONSTRAINT IF EXISTS role_check;
ALTER TABLE users ADD CONSTRAINT role_check CHECK (
    role IN ('client', 'expert', 'admin', 'super_admin', 'admin_editor')
);

