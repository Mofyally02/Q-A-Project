#!/bin/bash

# AL-Tech Academy Q&A Frontend Startup Script

echo "🚀 Starting AL-Tech Academy Q&A Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ to continue."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm to continue."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please update it with your configuration."
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend not detected on http://localhost:8000"
    echo "   Make sure the backend is running before starting the frontend"
    echo "   You can start the backend with: cd ../backend && python start.sh"
fi

# Start the development server
echo "🎯 Starting Nuxt.js development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   API base URL: ${NUXT_PUBLIC_API_BASE:-http://localhost:8000}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Nuxt.js
npm run dev

echo ""
echo "👋 AL-Tech Academy Q&A Frontend stopped"
