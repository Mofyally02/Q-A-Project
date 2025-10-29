#!/bin/bash
# Script to start Redis and RabbitMQ services
# Supports both Docker and local installations

echo "🚀 Starting required services for AL-Tech Academy Q&A System"
echo ""

# Check for Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    
    # Start Redis
    echo "Starting Redis..."
    docker run -d --name altech-redis \
        -p 6379:6379 \
        redis:7-alpine 2>/dev/null || \
        docker start altech-redis 2>/dev/null && \
        echo "✓ Redis started (or already running)" || \
        echo "✗ Failed to start Redis"
    
    # Start RabbitMQ
    echo "Starting RabbitMQ..."
    docker run -d --name altech-rabbitmq \
        -p 5672:5672 \
        -p 15672:15672 \
        -e RABBITMQ_DEFAULT_USER=qa_user \
        -e RABBITMQ_DEFAULT_PASS=qa_password \
        rabbitmq:3-management 2>/dev/null || \
        docker start altech-rabbitmq 2>/dev/null && \
        echo "✓ RabbitMQ started (or already running)" || \
        echo "✗ Failed to start RabbitMQ"
    
    echo ""
    echo "Services Status:"
    docker ps | grep -E "altech-redis|altech-rabbitmq"
    
elif command -v brew &> /dev/null; then
    echo "Using Homebrew services..."
    
    # Start Redis via brew
    if command -v redis-server &> /dev/null; then
        echo "Starting Redis..."
        brew services start redis 2>/dev/null || redis-server --daemonize yes
        echo "✓ Redis started"
    else
        echo "⚠ Redis not installed. Install with: brew install redis"
    fi
    
    # Start RabbitMQ via brew
    if command -v rabbitmq-server &> /dev/null; then
        echo "Starting RabbitMQ..."
        brew services start rabbitmq 2>/dev/null || rabbitmq-server -detached
        echo "✓ RabbitMQ started"
    else
        echo "⚠ RabbitMQ not installed. Install with: brew install rabbitmq"
    fi
    
else
    echo "⚠ Docker and Homebrew not found"
    echo ""
    echo "Manual setup required:"
    echo ""
    echo "For Redis:"
    echo "  1. Install: brew install redis"
    echo "  2. Start: redis-server"
    echo ""
    echo "For RabbitMQ:"
    echo "  1. Install: brew install rabbitmq"
    echo "  2. Start: rabbitmq-server"
    echo ""
    echo "OR use Docker:"
    echo "  1. Install Docker Desktop"
    echo "  2. Run: docker run -d -p 6379:6379 redis:7-alpine"
    echo "  3. Run: docker run -d -p 5672:5672 rabbitmq:3-management"
fi

echo ""
echo "Testing connections..."

# Test Redis
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✓ Redis is responding"
else
    echo "✗ Redis is not responding"
fi

# Test RabbitMQ
if rabbitmqctl ping 2>/dev/null; then
    echo "✓ RabbitMQ is responding"
else
    echo "✗ RabbitMQ is not responding (may take a moment to start)"
fi

echo ""
echo "✅ Setup complete! Run 'python verify_setup.py' to verify all services."

