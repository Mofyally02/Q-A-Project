#!/bin/bash

# Start All Services Script
# Starts database services and backend server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting All Services"
echo "=========================================="
echo ""

# Start database services
echo "Step 1: Starting database services..."
# Try Docker first, fallback to local PostgreSQL
if docker info > /dev/null 2>&1; then
    echo "Using Docker for database services..."
    bash start_database.sh
else
    echo "Docker not available, using local PostgreSQL..."
    bash start_database_local.sh
fi

echo ""
echo "Waiting 10 seconds for databases to initialize..."
sleep 10

# Run database migrations
echo ""
echo "Step 2: Running database migrations..."
if command -v alembic &> /dev/null; then
    export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}/src"
    alembic upgrade head
    echo "✅ Migrations complete"
else
    echo "⚠️  Alembic not found, skipping migrations"
fi

# Start backend server
echo ""
echo "Step 3: Starting backend server..."
echo ""
bash start_server.sh

