#!/bin/bash

# AI-Powered Q&A System Startup Script
# This script sets up and starts the entire system

set -e

echo "🚀 Starting AI-Powered Q&A System for AL-Tech Academy"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_warning "Please edit .env file with your configuration before continuing."
    print_warning "Required: Database URL, API keys, and security settings."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version check passed: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if PostgreSQL is running
print_status "Checking PostgreSQL connection..."
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    print_warning "PostgreSQL is not running. Please start PostgreSQL and try again."
    print_warning "You can start PostgreSQL with: brew services start postgresql (macOS) or systemctl start postgresql (Linux)"
    exit 1
fi

# Check if Redis is running
print_status "Checking Redis connection..."
if ! redis-cli ping &> /dev/null; then
    print_warning "Redis is not running. Please start Redis and try again."
    print_warning "You can start Redis with: brew services start redis (macOS) or systemctl start redis (Linux)"
    exit 1
fi

# Check if RabbitMQ is running
print_status "Checking RabbitMQ connection..."
if ! rabbitmq-diagnostics ping &> /dev/null; then
    print_warning "RabbitMQ is not running. Please start RabbitMQ and try again."
    print_warning "You can start RabbitMQ with: brew services start rabbitmq (macOS) or systemctl start rabbitmq (Linux)"
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
alembic upgrade head

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp

# Set permissions
chmod 755 logs uploads temp

# Start the application
print_status "Starting AI-Powered Q&A System..."
print_success "System is starting up..."

# Start the application with uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
