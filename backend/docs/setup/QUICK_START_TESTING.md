# Quick Start Testing Guide

## 🚀 Quick Test - 3 Steps

### Step 1: Start the Server

```bash
cd backend
python -m app.main
```

Or with uvicorn:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ Database connections established
✓ Application startup complete
```

### Step 2: Test Basic Endpoints (No Auth Required)

Open a new terminal and run:

```bash
# Test root
curl http://localhost:8000/

# Test health
curl http://localhost:8000/api/v1/health

# Test database health
curl http://localhost:8000/api/v1/health/db
```

Expected: JSON responses with status information

### Step 3: View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You should see all 90 endpoints organized by category!

---

## ✅ Verification Checklist

### Basic Connectivity
- [ ] Server starts without errors
- [ ] Root endpoint (`/`) returns JSON
- [ ] Health endpoint (`/api/v1/health`) returns JSON
- [ ] API docs (`/docs`) loads in browser

### Endpoint Registration
- [ ] Admin endpoints visible in `/docs` (71 endpoints)
- [ ] Client endpoints visible in `/docs` (12 endpoints)
- [ ] Expert endpoints visible in `/docs` (7 endpoints)
- [ ] Health endpoints visible in `/docs` (5 endpoints)

### Authentication
- [ ] Unauthenticated requests to protected endpoints return 401
- [ ] Health endpoints work without authentication

---

## 🧪 Automated Testing

### Option 1: Simple Bash Script
```bash
cd backend
./run_tests.sh
```

### Option 2: Python Test Script
```bash
cd backend
pip install httpx  # If not already installed
python test_backend.py
```

### Option 3: Using curl
```bash
# Test all health endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/db
curl http://localhost:8000/api/v1/health/cache
curl http://localhost:8000/api/v1/health/queue
```

---

## 📊 Expected Results

### Health Endpoints (Should all work)
- ✅ `GET /` - Returns app info
- ✅ `GET /api/v1/health` - Returns health status
- ✅ `GET /api/v1/health/db` - Returns DB status
- ✅ `GET /api/v1/health/cache` - Returns cache status (may fail if Redis not running)
- ✅ `GET /api/v1/health/queue` - Returns queue status (may fail if RabbitMQ not running)

### Protected Endpoints (Will return 401 without auth)
- ⚠️ `GET /api/v1/admin/*` - Returns 401 (expected)
- ⚠️ `GET /api/v1/client/*` - Returns 401 (expected)
- ⚠️ `GET /api/v1/expert/*` - Returns 401 (expected)

**Note**: 401 responses are GOOD - it means the endpoints exist and authentication is working!

---

## 🎯 Next Steps

1. **View API Documentation**: http://localhost:8000/docs
2. **Test Individual Endpoints**: Use the interactive Swagger UI
3. **Set up Authentication**: Create test users and get JWT tokens
4. **Test Full Workflows**: Question submission → Expert review → Delivery

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Check Python version (needs 3.8+)
python --version

# Check dependencies
pip install -r requirements.txt
```

### Database Connection Error
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Run migrations
alembic upgrade head
```

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

---

## 📝 Test Results Template

```
✓ Server started successfully
✓ Root endpoint working
✓ Health endpoints working
✓ API documentation accessible
✓ All 90 endpoints registered
✓ Authentication working (401 for protected endpoints)
```

---

**Ready to test!** 🚀

Start the server and visit http://localhost:8000/docs to see all endpoints!

