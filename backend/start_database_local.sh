#!/bin/bash

# Start Database Services Script (Local PostgreSQL - No Docker)
# This script starts PostgreSQL locally without Docker

set -e

echo "=========================================="
echo "Starting Database Services (Local)"
echo "=========================================="

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    echo ""
    echo "Install PostgreSQL:"
    echo "  brew install postgresql@15"
    echo ""
    echo "Or use Docker:"
    echo "  ./start_database.sh"
    exit 1
fi

# Detect PostgreSQL version and installation method
PG_VERSION=""
PG_DATA_DIR=""
PG_USER=""

# Check for Homebrew PostgreSQL
if brew list postgresql@15 &> /dev/null 2>&1; then
    PG_VERSION="15"
    PG_DATA_DIR="/opt/homebrew/var/postgresql@15"  # Apple Silicon
    if [ ! -d "$PG_DATA_DIR" ]; then
        PG_DATA_DIR="/usr/local/var/postgresql@15"  # Intel Mac
    fi
    PG_USER=$(whoami)
    echo "✅ Found PostgreSQL 15 via Homebrew"
elif brew list postgresql@14 &> /dev/null 2>&1; then
    PG_VERSION="14"
    PG_DATA_DIR="/opt/homebrew/var/postgresql@14"
    if [ ! -d "$PG_DATA_DIR" ]; then
        PG_DATA_DIR="/usr/local/var/postgresql@14"
    fi
    PG_USER=$(whoami)
    echo "✅ Found PostgreSQL 14 via Homebrew"
elif brew list postgresql &> /dev/null 2>&1; then
    PG_VERSION=$(psql --version | grep -oE '[0-9]+' | head -1)
    PG_DATA_DIR="/opt/homebrew/var/postgres"
    if [ ! -d "$PG_DATA_DIR" ]; then
        PG_DATA_DIR="/usr/local/var/postgres"
    fi
    PG_USER=$(whoami)
    echo "✅ Found PostgreSQL $PG_VERSION via Homebrew"
else
    # Try to detect from psql
    PG_VERSION=$(psql --version | grep -oE '[0-9]+' | head -1)
    PG_USER=$(whoami)
    echo "✅ Found PostgreSQL $PG_VERSION (system installation)"
fi

# Start PostgreSQL service
echo ""
echo "Starting PostgreSQL..."

if command -v brew &> /dev/null; then
    # Try to start via brew services
    if brew services list | grep -q "postgresql"; then
        echo "Starting PostgreSQL via Homebrew services..."
        if brew services list | grep -q "postgresql.*started"; then
            echo "✅ PostgreSQL is already running"
        else
            if [ -n "$PG_VERSION" ] && [ "$PG_VERSION" != "" ]; then
                brew services start postgresql@$PG_VERSION 2>/dev/null || brew services start postgresql 2>/dev/null || true
            else
                brew services start postgresql 2>/dev/null || true
            fi
            sleep 3
        fi
    else
        echo "⚠️  PostgreSQL service not managed by Homebrew"
        echo "   Attempting to start manually..."
    fi
fi

# Wait a moment for PostgreSQL to start
sleep 2

# Check PostgreSQL connection
echo ""
echo "Checking PostgreSQL connection..."
if psql -h localhost -U "$PG_USER" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️  Cannot connect to PostgreSQL"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if PostgreSQL is running:"
    echo "     brew services list | grep postgresql"
    echo ""
    echo "  2. Start PostgreSQL manually:"
    if [ -n "$PG_VERSION" ]; then
        echo "     brew services start postgresql@$PG_VERSION"
    else
        echo "     brew services start postgresql"
    fi
    echo ""
    echo "  3. Or start with pg_ctl:"
    if [ -n "$PG_DATA_DIR" ] && [ -d "$PG_DATA_DIR" ]; then
        echo "     pg_ctl -D $PG_DATA_DIR start"
    fi
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if databases exist
echo ""
echo "Checking databases..."

# Check main database
if psql -h localhost -U "$PG_USER" -d qa_system -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database 'qa_system' exists"
else
    echo "⚠️  Database 'qa_system' does not exist"
    echo "   Creating database..."
    createdb -h localhost -U "$PG_USER" qa_system 2>/dev/null || {
        echo "❌ Failed to create database 'qa_system'"
        echo "   You may need to create it manually:"
        echo "   createdb -h localhost -U $PG_USER qa_system"
    }
fi

# Check auth database
if psql -h localhost -U "$PG_USER" -d qa_auth -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database 'qa_auth' exists"
else
    echo "⚠️  Database 'qa_auth' does not exist"
    echo "   Creating database..."
    createdb -h localhost -U "$PG_USER" qa_auth 2>/dev/null || {
        echo "❌ Failed to create database 'qa_auth'"
        echo "   You may need to create it manually:"
        echo "   createdb -h localhost -U $PG_USER qa_auth"
    }
fi

# Check Redis (optional)
echo ""
echo "Checking Redis (optional)..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running (optional service)"
        echo "   Start with: brew services start redis"
    fi
else
    echo "⚠️  Redis is not installed (optional service)"
    echo "   Install with: brew install redis"
fi

# Summary
echo ""
echo "=========================================="
echo "Database Services Status:"
echo "=========================================="
echo "PostgreSQL:"
if psql -h localhost -U "$PG_USER" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "  ✅ Running on localhost:5432"
    echo "  ✅ User: $PG_USER"
    echo "  ✅ Databases: qa_system, qa_auth"
else
    echo "  ❌ Not running"
fi

echo ""
echo "Redis:"
if command -v redis-cli &> /dev/null && redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Running on localhost:6379"
else
    echo "  ⚠️  Not running (optional)"
fi

echo ""
echo "✅ Database setup complete!"
echo ""
echo "To stop PostgreSQL:"
if [ -n "$PG_VERSION" ]; then
    echo "  brew services stop postgresql@$PG_VERSION"
else
    echo "  brew services stop postgresql"
fi

