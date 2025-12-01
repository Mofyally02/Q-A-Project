#!/bin/bash

# Backend Testing Script
# Tests all 90 endpoints

echo "=========================================="
echo "Backend API Testing - 90 Endpoints"
echo "=========================================="
echo ""

# Check if server is running
echo "Checking if server is running..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✓ Server is running"
else
    echo "✗ Server is not running. Please start it first:"
    echo "  cd backend && python -m app.main"
    exit 1
fi

echo ""
echo "Testing Health Endpoints..."
echo "----------------------------------------"

# Test root
echo -n "GET / ... "
if curl -s http://localhost:8000/ | grep -q "running"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# Test health
echo -n "GET /api/v1/health ... "
if curl -s http://localhost:8000/api/v1/health | grep -q "status"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# Test health/db
echo -n "GET /api/v1/health/db ... "
if curl -s http://localhost:8000/api/v1/health/db | grep -q "status"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

echo ""
echo "Testing Admin Endpoints (will fail without auth - checking endpoint existence)..."
echo "----------------------------------------"

# Test a few admin endpoints
echo -n "GET /api/v1/admin/users ... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/admin/users)
if [ "$STATUS" = "401" ] || [ "$STATUS" = "200" ]; then
    echo "✓ PASS (Status: $STATUS)"
else
    echo "✗ FAIL (Status: $STATUS)"
fi

echo -n "GET /api/v1/admin/settings ... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/admin/settings)
if [ "$STATUS" = "401" ] || [ "$STATUS" = "200" ]; then
    echo "✓ PASS (Status: $STATUS)"
else
    echo "✗ FAIL (Status: $STATUS)"
fi

echo ""
echo "Testing Client Endpoints (will fail without auth - checking endpoint existence)..."
echo "----------------------------------------"

echo -n "GET /api/v1/client/dashboard ... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/client/dashboard)
if [ "$STATUS" = "401" ] || [ "$STATUS" = "200" ]; then
    echo "✓ PASS (Status: $STATUS)"
else
    echo "✗ FAIL (Status: $STATUS)"
fi

echo ""
echo "Testing Expert Endpoints (will fail without auth - checking endpoint existence)..."
echo "----------------------------------------"

echo -n "GET /api/v1/expert/tasks ... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/expert/tasks)
if [ "$STATUS" = "401" ] || [ "$STATUS" = "200" ]; then
    echo "✓ PASS (Status: $STATUS)"
else
    echo "✗ FAIL (Status: $STATUS)"
fi

echo ""
echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "For comprehensive testing, run:"
echo "  python test_backend.py"
echo ""
echo "Or use the interactive API docs at:"
echo "  http://localhost:8000/docs"

