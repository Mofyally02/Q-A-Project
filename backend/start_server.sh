#!/bin/bash

# Start Backend Server Script
# This script starts the FastAPI backend server

set -e

echo "=========================================="
echo "Starting AL-Tech Academy Q&A Backend"
echo "=========================================="

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}/src"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating default .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://mofyally@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://mofyally@localhost:5432/qa_auth

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# RabbitMQ (Optional)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# App Configuration
APP_NAME=AL-Tech Academy Q&A Platform
APP_VERSION=1.0.0
ENVIRONMENT=development
EOF
    echo "✅ Created default .env file"
    echo "   Please update with your actual configuration"
fi

# Check if PostgreSQL is running
echo ""
echo "Checking PostgreSQL connection..."
if ! psql -h localhost -U mofyally -d qa_system -c "SELECT 1;" > /dev/null 2>&1; then
    echo "⚠️  Warning: Cannot connect to PostgreSQL"
    echo "   Please ensure PostgreSQL is running"
    echo "   You can start it with: brew services start postgresql@15"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version and recommend compatible version
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Python 3.14 has compatibility issues with many packages
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    echo "⚠️  WARNING: Python 3.14 detected"
    echo "   Python 3.14 is very new and many packages don't support it yet."
    echo "   Recommended: Use Python 3.12 or 3.13 instead"
    echo ""
    echo "   To use Python 3.12:"
    echo "     brew install python@3.12"
    echo "     python3.12 -m venv venv"
    echo ""
    echo "   To use Python 3.13:"
    echo "     brew install python@3.13"
    echo "     python3.13 -m venv venv"
    echo ""
    read -p "Continue with Python 3.14 anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    
    # Try to use Python 3.13, 3.12, or 3.11 if available (avoid 3.14)
    if command -v python3.13 &> /dev/null; then
        echo "✅ Using Python 3.13 (recommended)..."
        python3.13 -m venv venv
    elif command -v python3.12 &> /dev/null; then
        echo "✅ Using Python 3.12 (recommended)..."
        python3.12 -m venv venv
    elif command -v python3.11 &> /dev/null; then
        echo "✅ Using Python 3.11 (compatible)..."
        python3.11 -m venv venv
    else
        echo "⚠️  Using default Python 3 (may be 3.14 which has issues)..."
        python3 -m venv venv
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Upgrade pip and setuptools first
echo "Upgrading pip, setuptools, and wheel..."
pip install -q --upgrade pip setuptools wheel

# Check Python version
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
echo "Python version: $PYTHON_VERSION"

# Install system dependencies for Pillow (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list libjpeg &> /dev/null 2>&1; then
        echo "⚠️  libjpeg not found. Pillow may fail to build."
        echo "   Install with: brew install libjpeg zlib libtiff"
    fi
fi

# Install dependencies with better error handling
echo "Installing Python dependencies..."

# For Python 3.14+, try installing Pillow separately with latest version
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    echo "⚠️  Python 3.14+ detected. Installing Pillow separately..."
    
    # Install all dependencies except Pillow first
    echo "Installing core dependencies..."
    pip install -q $(grep -v -i "^Pillow" requirements.txt | grep -v "^pillow")
    
    # Try installing latest Pillow (which should have Python 3.14 support)
    echo "Installing Pillow (latest version for Python 3.14)..."
    pip install -q --upgrade "Pillow>=10.4.0" || {
        echo "⚠️  Pillow installation failed. Trying pre-release version..."
        pip install -q --pre --upgrade Pillow || {
            echo "⚠️  Pillow installation failed. Continuing without it..."
            echo "   Image processing features may not work."
            echo "   To fix: brew install libjpeg zlib libtiff && pip install Pillow"
        }
    }
else
    # Normal installation for Python < 3.14
    pip install -q -r requirements.txt || {
        echo "⚠️  Some dependencies failed to install"
        echo "   Check the error messages above"
    }
fi

echo "✅ Dependency installation complete"

# Start the server
echo ""
echo "=========================================="
echo "Starting server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "=========================================="
echo ""

python -m app.main
