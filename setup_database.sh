#!/bin/bash

# Database Setup and Integration Test Script
# This script sets up the database and runs integration tests

set -e

echo "🚀 Starting Database Setup and Integration Tests"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
else
    echo "⚠️  requirements.txt not found. Installing basic dependencies..."
    pip3 install asyncpg redis fastapi uvicorn pydantic python-dotenv
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if ! python3 -c "
import asyncpg
import asyncio
from app.config import settings

async def check_db():
    try:
        conn = await asyncpg.connect(settings.database_url)
        await conn.close()
        print('✅ PostgreSQL connection successful')
        return True
    except Exception as e:
        print(f'❌ PostgreSQL connection failed: {e}')
        return False

asyncio.run(check_db())
"; then
    echo "❌ Cannot connect to PostgreSQL. Please ensure:"
    echo "   1. PostgreSQL is running"
    echo "   2. Database 'qa_system' exists"
    echo "   3. User has proper permissions"
    echo "   4. Connection settings in .env are correct"
    exit 1
fi

# Run Alembic migrations
echo "🔄 Running database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
    echo "✅ Migrations completed successfully"
else
    echo "⚠️  Alembic not found. Running manual database setup..."
    python3 init_database.py
fi

# Run database initialization
echo "🏗️  Initializing database..."
python3 init_database.py

# Run integration tests
echo "🧪 Running database integration tests..."
python3 test_database_integration.py

echo ""
echo "🎉 Database setup and integration tests completed successfully!"
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "   1. Start the backend server: python3 app/main.py"
echo "   2. Test API endpoints with your frontend"
echo "   3. Monitor logs for any issues"
echo ""
echo "🔗 Default login credentials:"
echo "   Client:  client@demo.com / demo123"
echo "   Expert:  expert@demo.com / demo123"
echo "   Admin:   admin@demo.com / demo123"
echo ""
echo "📚 For more information, see DATABASE_SCHEMA.md"
