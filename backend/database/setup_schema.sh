#!/bin/bash

# Database Setup Script for AL-Tech Academy Q&A System
# This script creates the databases and runs the complete schema

set -e

echo "🗄️  Setting up PostgreSQL Databases for AL-Tech Academy"
echo "========================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL client (psql) is not installed${NC}"
    echo "Please install PostgreSQL first"
    exit 1
fi

# Get database credentials from environment or use defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-${USER:-postgres}}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Try to detect PostgreSQL installation
echo "🔍 Checking PostgreSQL installation..."

# Check if databases exist
echo "📋 Checking if databases exist..."

# Try to connect and create databases
if [ -n "$DB_PASSWORD" ]; then
    export PGPASSWORD="$DB_PASSWORD"
fi

# Create qa_auth database if it doesn't exist
echo "🔨 Creating qa_auth database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "SELECT 1" postgres 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Cannot connect to PostgreSQL server${NC}"
    echo ""
    echo "Please ensure PostgreSQL is running and accessible."
    echo ""
    echo "To start PostgreSQL:"
    echo "  macOS:   brew services start postgresql@14"
    echo "  Linux:   sudo systemctl start postgresql"
    echo "  Docker:  docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15"
    echo ""
    echo "Then run this script again."
    exit 1
}

# Create databases (will fail gracefully if they exist)
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<EOF
-- Create databases if they don't exist
SELECT 'CREATE DATABASE qa_auth' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'qa_auth')\gexec
SELECT 'CREATE DATABASE qa_system' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'qa_system')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE qa_auth TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE qa_system TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Databases created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Note: Databases may already exist${NC}"
fi

# Run schema for qa_auth
echo ""
echo "📝 Creating schema for qa_auth database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d qa_auth -f "$(dirname "$0")/complete_schema.sql" 2>&1 | grep -v "already exists" || true

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ qa_auth schema created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some items may already exist in qa_auth${NC}"
fi

# Run schema for qa_system
echo ""
echo "📝 Creating schema for qa_system database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d qa_system -f "$(dirname "$0")/complete_schema.sql" 2>&1 | grep -v "already exists" || true

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ qa_system schema created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some items may already exist in qa_system${NC}"
fi

# Create default admin user (optional)
echo ""
echo "👤 Creating default users..."
python3 "$(dirname "$0")/../init_database.py" 2>&1 || echo -e "${YELLOW}⚠️  Could not create default users${NC}"

echo ""
echo -e "${GREEN}✅ Database setup completed!${NC}"
echo ""
echo "📊 Database Information:"
echo "  - qa_auth:    Authentication and user management"
echo "  - qa_system:  Main application database"
echo ""
echo "📚 Next steps:"
echo "  1. Update your .env file with database credentials"
echo "  2. Run migrations: cd backend && alembic upgrade head"
echo "  3. Start the application: python backend/start_backend.py"
echo ""
