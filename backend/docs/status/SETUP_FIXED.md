# ✅ Database Setup Script Fixed

## Issue Resolved

The script was failing with:
```
export: `Q&A': not a valid identifier
```

This was caused by the `APP_NAME=AL-Tech Academy Q&A Platform` variable containing special characters (`&` and spaces) that weren't properly handled.

## Fix Applied

The script now:
- ✅ Only loads the specific variables needed for database setup
- ✅ Safely handles special characters in values
- ✅ Uses safer parsing methods that don't break on `&`, spaces, etc.

## How to Use

### Option 1: Run the Fixed Script
```bash
cd backend
./setup_database.sh
```

The script will:
1. Extract `DATABASE_URL` and `AUTH_DATABASE_URL` from `.env`
2. Check PostgreSQL connection
3. Create database if needed
4. Run migrations

### Option 2: Manual Setup (If PostgreSQL Issues)
```bash
cd backend

# 1. Ensure PostgreSQL is running
# Check: pg_isready

# 2. Update .env with correct credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/qa_system

# 3. Run migrations manually
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
alembic upgrade head
```

## Expected Output

**If PostgreSQL is running:**
```
==========================================
Database Setup for AL-Tech Academy Q&A
==========================================

Database Configuration:
  Host: localhost
  Port: 5432
  Database: qa_system
  User: postgres

Checking PostgreSQL connection...
✓ PostgreSQL connection successful

Creating database if it doesn't exist...
✓ Database ready

Running database migrations...
INFO  [alembic.runtime.migration] Context impl AsyncPGImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
...
✓ Database setup complete!
```

**If PostgreSQL is not running:**
```
❌ Cannot connect to PostgreSQL.
   Please ensure PostgreSQL is running and credentials are correct.
```

## Next Steps

1. **Start PostgreSQL** (if not running):
   ```bash
   # macOS (Homebrew)
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   
   # Docker
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
   ```

2. **Run the setup script**:
   ```bash
   ./setup_database.sh
   ```

3. **Start the server**:
   ```bash
   ./start_server.sh
   ```

4. **Test the API**:
   Visit http://localhost:8000/docs

---

**Status**: ✅ **SCRIPT FIXED - Ready to Use**

