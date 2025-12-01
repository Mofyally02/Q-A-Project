#!/bin/bash

# Complete Database Setup Script for All 90 Endpoints
# This script sets up the PostgreSQL database with all required tables

set -e

echo "=========================================="
echo "Database Setup for AL-Tech Academy Q&A"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_auth

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# RabbitMQ (Optional)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-change-in-production

# App
APP_NAME=AL-Tech Academy Q&A Platform
APP_VERSION=1.0.0
ENVIRONMENT=development
EOF
    echo "✓ Created .env file. Please update with your database credentials."
    echo ""
fi

# Load environment variables (handle special characters properly)
# Use python-dotenv approach or load only what we need
if [ -f .env ]; then
    # Extract only the variables we need for database setup (safer approach)
    # This avoids issues with special characters like &, spaces, etc.
    DATABASE_URL=$(grep "^DATABASE_URL=" .env | cut -d '=' -f2- | sed 's/^["'\'']//;s/["'\'']$//')
    AUTH_DATABASE_URL=$(grep "^AUTH_DATABASE_URL=" .env | cut -d '=' -f2- | sed 's/^["'\'']//;s/["'\'']$//' || echo "$DATABASE_URL")
    
    # Export only the variables we need
    export DATABASE_URL
    [ -n "$AUTH_DATABASE_URL" ] && export AUTH_DATABASE_URL
fi

# Extract database name from DATABASE_URL
# Handle both formats: postgresql://user:pass@host:port/db and postgresql://user@host:port/db
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
# Check if password is present (has : before @)
if echo $DATABASE_URL | grep -q "://[^:]*:[^@]*@"; then
    # Format: user:pass@host
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
else
    # Format: user@host (no password)
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^@]*\)@.*/\1/p')
    DB_PASS=""
fi
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."

# Try to connect (handle case where password might be empty)
if [ -z "$DB_PASS" ]; then
    # Try without password (local connection)
    if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1" > /dev/null 2>&1; then
        echo "❌ Cannot connect to PostgreSQL."
        echo ""
        echo "PostgreSQL Setup Options:"
        echo "  1. Docker (Recommended): docker-compose up -d postgres"
        echo "  2. Homebrew: brew services start postgresql@15"
        echo "  3. See POSTGRESQL_SETUP.md for detailed instructions"
        echo ""
        echo "Current connection attempt:"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT"
        echo "  User: $DB_USER"
        echo "  Database: $DB_NAME"
        exit 1
    fi
else
    # Try with password
    if ! PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1" > /dev/null 2>&1; then
        echo "❌ Cannot connect to PostgreSQL."
        echo ""
        echo "PostgreSQL Setup Options:"
        echo "  1. Docker (Recommended): docker-compose up -d postgres"
        echo "  2. Homebrew: brew services start postgresql@15"
        echo "  3. See POSTGRESQL_SETUP.md for detailed instructions"
        echo ""
        echo "Current connection attempt:"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT"
        echo "  User: $DB_USER"
        echo "  Database: $DB_NAME"
        exit 1
    fi
fi
echo "✓ PostgreSQL connection successful"
echo ""

# Create database if it doesn't exist
echo "Creating database if it doesn't exist..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"
echo "✓ Database ready"
echo ""

# Install Python dependencies if needed
if ! python -c "import alembic" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Run migrations
echo "Running database migrations..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
alembic upgrade head

echo ""
echo "=========================================="
echo "✅ Database setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the server: ./start_server.sh"
echo "2. Visit API docs: http://localhost:8000/docs"
echo "3. Test endpoints interactively"
echo ""

