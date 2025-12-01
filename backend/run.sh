#!/bin/bash

# Startup script for AL-Tech Academy Q&A Platform Backend

set -e

echo "=========================================="
echo "AL-Tech Academy Q&A Platform - Backend"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "Please update .env with your configuration"
    else
        echo "Error: env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
echo "=========================================="

if [ "$ENVIRONMENT" = "development" ] || [ "$DEBUG" = "True" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi

