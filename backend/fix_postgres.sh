#!/bin/bash

echo "=========================================="
echo "PostgreSQL Startup & Database Setup"
echo "=========================================="
echo ""

# Remove any lock files
echo "Cleaning up lock files..."
rm -f /usr/local/var/postgresql@14/postmaster.pid 2>/dev/null
rm -f /opt/homebrew/var/postgresql@14/postmaster.pid 2>/dev/null

# Stop any existing services
echo "Stopping existing PostgreSQL services..."
brew services stop postgresql@14 2>/dev/null || true
sleep 2

# Start fresh
echo "Starting PostgreSQL..."
if brew services start postgresql@14; then
    echo "✅ PostgreSQL service started"
else
    echo "❌ Failed to start PostgreSQL service"
    exit 1
fi

echo ""
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Test connection
echo "Testing PostgreSQL connection..."
if psql -h localhost -U $(whoami) -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running and accessible!"
    echo ""
    echo "Checking databases..."
    
    # Function to check if database exists
    check_and_create_db() {
        local db_name=$1
        if psql -h localhost -U $(whoami) -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1; then
            echo "✅ Database '$db_name' already exists"
            return 0
        else
            if createdb -h localhost -U $(whoami) "$db_name" 2>/dev/null; then
                echo "✅ Database '$db_name' created successfully"
                return 0
            else
                echo "❌ Failed to create database '$db_name'"
                return 1
            fi
        fi
    }
    
    # Check and create databases
    check_and_create_db "qa_system"
    check_and_create_db "qa_auth"
    
    echo ""
    echo "=========================================="
    echo "✅ Setup complete! Databases ready."
    echo "=========================================="
else
    echo "❌ PostgreSQL is not responding"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check PostgreSQL logs:"
    echo "   tail -f /usr/local/var/postgresql@14/server.log"
    echo "   or"
    echo "   tail -f /opt/homebrew/var/postgresql@14/server.log"
    echo ""
    echo "2. Check if port 5432 is in use:"
    echo "   lsof -i :5432"
    echo ""
    echo "3. Try manual start:"
    echo "   pg_ctl -D /usr/local/var/postgresql@14 start"
    echo "   or"
    echo "   pg_ctl -D /opt/homebrew/var/postgresql@14 start"
    echo ""
    exit 1
fi
