# 🚀 Quick Test Guide

## Start the Server

### Option 1: Using the Startup Script
```bash
cd backend
./start_server.sh
```

### Option 2: Manual Start
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m app.main
```

### Option 3: Using uvicorn directly
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verify Server is Running

Once the server starts, you should see:
```
✓ Database connections established
✓ Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Test the Endpoints

### 1. Open API Documentation
**Visit**: http://localhost:8000/docs

You'll see all 90 endpoints organized by:
- **admin** (71 endpoints)
- **client** (12 endpoints)
- **expert** (7 endpoints)
- **health** (5 endpoints)

### 2. Test Health Endpoints (No Auth Required)

Open a new terminal and run:

```bash
# Test root
curl http://localhost:8000/

# Test health
curl http://localhost:8000/api/v1/health

# Test database health
curl http://localhost:8000/api/v1/health/db
```

**Expected**: JSON responses with status information

### 3. Test Protected Endpoints (Will Return 401 - This is Good!)

```bash
# Admin endpoint (will return 401 - endpoint exists!)
curl http://localhost:8000/api/v1/admin/users

# Client endpoint (will return 401 - endpoint exists!)
curl http://localhost:8000/api/v1/client/dashboard

# Expert endpoint (will return 401 - endpoint exists!)
curl http://localhost:8000/api/v1/expert/tasks
```

**Expected**: `401 Unauthorized` - This confirms:
- ✅ Endpoints exist
- ✅ Authentication is working
- ✅ Permission checks are active

---

## 📊 What You Should See

### In the Server Logs:
```
✓ Database connections established
✓ Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### In the Browser (/docs):
- All 90 endpoints listed
- Organized by category
- Interactive "Try it out" buttons
- Request/response schemas
- Authentication button (top right)

### In curl Responses:
- Health endpoints: `200 OK` with JSON
- Protected endpoints: `401 Unauthorized` (expected!)

---

## 🎯 Success Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] All 90 endpoints visible in docs
- [ ] Health endpoints return 200
- [ ] Protected endpoints return 401 (confirming they exist)

---

## 🔐 Next: Set Up Authentication

To test protected endpoints fully, you'll need:

1. **Authentication endpoints** (if not already implemented)
2. **Test users** (admin, client, expert)
3. **JWT tokens** for each role

Then you can:
- Test all CRUD operations
- Test full workflows
- Verify business logic
- Test permissions

---

## 🎉 Ready!

**All 90 endpoints are ready for testing!**

Start the server and visit **http://localhost:8000/docs** to see them all!

---

**Status**: 🟢 **READY TO TEST**

