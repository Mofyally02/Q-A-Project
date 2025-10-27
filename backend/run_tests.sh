#!/bin/bash

# Test Runner Script for AI-Powered Q&A System

set -e

echo "🧪 Running Tests for AI-Powered Q&A System"

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

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run start.sh first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install test dependencies
print_status "Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov

# Run tests
print_status "Running tests..."
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Check test results
if [ $? -eq 0 ]; then
    print_success "All tests passed!"
    print_status "Coverage report generated in htmlcov/index.html"
else
    print_error "Some tests failed!"
    exit 1
fi
