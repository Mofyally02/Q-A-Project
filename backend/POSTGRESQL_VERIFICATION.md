# PostgreSQL Connection Verification Guide

## Overview

This guide helps verify that PostgreSQL is properly connected and working in all sections of the backend, including the login page.

## Quick Verification

Run the quick verification script:

```powershell
cd backend
python verify_backend_setup.py
```

## Comprehensive Test

Run the comprehensive test script:

```powershell
cd backend
python test_postgresql_connection.py
```

## What Gets Tested

### 1. Database Connections
- ✅ Main database connection (`qa_system`)
- ✅ Auth database connection (`qa_auth`)
- ✅ Connection pools initialization
- ✅ Pool connection acquisition

### 2. Database Schema
- ✅ Users table exists and has correct structure
- ✅ All required tables exist:
  - `users`, `clients`, `experts`, `admins`
  - `questions`, `answers`, `ratings`
  - `expert_reviews`, `expert_metrics`, `audit_logs`

### 3. Login Functionality
- ✅ User authentication query works
- ✅ Password hashing and verification
- ✅ User lookup by email
- ✅ Login endpoint database access

### 4. Auth Service
- ✅ User creation
- ✅ User authentication
- ✅ JWT token generation
- ✅ Role-based access

## Configuration Check

### Required Environment Variables

Make sure your `.env` file has:

```env
DATABASE_URL=postgresql://qa_user:qa_password@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://qa_user:qa_password@localhost:5432/qa_auth
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
```

### Database Setup

1. **PostgreSQL must be running**
2. **Databases must exist:**
   - `qa_system` (main database)
   - `qa_auth` (authentication database)
3. **User must have access:**
   - Username: `qa_user`
   - Password: `qa_password`

## Troubleshooting

### Connection Failed

**Error:** `connection refused` or `could not connect`

**Solutions:**
1. Check if PostgreSQL is running:
   ```powershell
   # Windows
   Get-Service postgresql*
   ```

2. Verify connection string in `.env`:
   - Check host (localhost)
   - Check port (5432)
   - Check database name
   - Check username/password

3. Test connection manually:
   ```powershell
   psql -U qa_user -d qa_system -h localhost
   ```

### Tables Missing

**Error:** `relation "users" does not exist`

**Solutions:**
1. Run Alembic migrations:
   ```powershell
   cd backend
   alembic upgrade head
   ```

2. Check migration files exist:
   ```powershell
   dir alembic\versions\*.py
   ```

### Login Not Working

**Error:** Login returns "Invalid email or password"

**Check:**
1. Users exist in database:
   ```sql
   SELECT email, role FROM users;
   ```

2. Password hashing works:
   - Check `app/utils/security.py`
   - Verify bcrypt is installed

3. Database connection in auth routes:
   - Check `app/routes/auth.py` uses `get_auth_db()`
   - Verify auth database has users table

## Database Connection Flow

### Login Request Flow

1. **Frontend** → POST `/auth/login`
2. **Backend Route** (`app/routes/auth.py`) → `login()` function
3. **Database Dependency** → `get_auth_db()` → Auth database pool
4. **Auth Service** → `authenticate_user()` → Query users table
5. **Password Verification** → `verify_password()` → Compare hashes
6. **JWT Generation** → `create_access_token()` → Return token

### Database Pools

- **Main Pool** (`db.pool`): Used for questions, answers, ratings, etc.
- **Auth Pool** (`db.auth_pool`): Used for authentication and user management

Both pools are initialized in `app/database.py` and connected on startup.

## Verification Checklist

- [ ] PostgreSQL is running
- [ ] Databases `qa_system` and `qa_auth` exist
- [ ] User `qa_user` has access to both databases
- [ ] `.env` file exists with correct connection strings
- [ ] Alembic migrations have been run
- [ ] All tables exist in both databases
- [ ] Quick verification script passes
- [ ] Comprehensive test script passes
- [ ] Login endpoint works (test with Postman/curl)
- [ ] Registration endpoint works

## Testing Login Endpoint

### Using curl:

```powershell
curl -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "test@example.com", "password": "test123"}
)
print(response.json())
```

## Next Steps

After verification:
1. ✅ Start backend server: `python start.py` or `uvicorn app.main:app --reload`
2. ✅ Test login from frontend
3. ✅ Verify all endpoints work with database
4. ✅ Check admin controls work
5. ✅ Test question submission flow

