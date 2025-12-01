# 🚀 Complete Setup Instructions

## Current Status
- ✅ PostgreSQL client installed (psql 14.20)
- ⚠️  PostgreSQL server needs to be started
- ✅ All backend code ready
- ✅ Database migrations ready

---

## Quick Start (3 Steps)

### Step 1: Start PostgreSQL
```bash
cd backend
./START_POSTGRES.sh
```

**Or manually:**
```bash
# Check if PostgreSQL is installed
brew list postgresql@14 || brew list postgresql@15 || brew list postgresql

# If not installed, install it:
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15
```

### Step 2: Update .env File
Make sure your `.env` file has the correct database URL:

```bash
cd backend
```

**For Homebrew PostgreSQL (default macOS user, no password):**
```env
DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
```

**Or if you created a postgres user:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
```

### Step 3: Run Database Setup
```bash
./setup_database.sh
```

---

## Detailed Setup

### Option A: Homebrew PostgreSQL (Your Current Setup)

**1. Check PostgreSQL Status:**
```bash
brew services list | grep postgresql
```

**2. Start PostgreSQL:**
```bash
# If you have postgresql@15
brew services start postgresql@15

# If you have postgresql@14
brew services start postgresql@14

# If you have just postgresql
brew services start postgresql
```

**3. Verify It's Running:**
```bash
pg_isready -h localhost -p 5432
```

**4. Create Database User (if needed):**
```bash
# Connect to PostgreSQL
psql -d postgres

# Create user (if you want to use 'postgres' user)
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER USER postgres CREATEDB;

# Or use your macOS username (no password needed)
# Just use: DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
```

**5. Update .env:**
```bash
# For macOS user (no password)
DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system

# For postgres user (with password)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
```

**6. Run Setup:**
```bash
./setup_database.sh
```

---

### Option B: Docker (If You Install Docker Later)

**1. Install Docker Desktop:**
- Download from: https://www.docker.com/products/docker-desktop

**2. Start Services:**
```bash
cd backend
docker-compose up -d postgres
```

**3. Run Setup:**
```bash
./setup_database.sh
```

---

## Verify Everything Works

### Check PostgreSQL is Running
```bash
pg_isready -h localhost -p 5432
```

**Expected output:**
```
localhost:5432 - accepting connections
```

### Test Connection
```bash
psql -h localhost -d postgres -c "SELECT version();"
```

### Check Database Setup
```bash
cd backend
./setup_database.sh
```

**Expected output:**
```
✓ PostgreSQL connection successful
✓ Database ready
Running database migrations...
INFO  [alembic.runtime.migration] Context impl AsyncPGImpl.
...
✅ Database setup complete!
```

---

## Troubleshooting

### "Cannot connect to PostgreSQL"

**Check if running:**
```bash
pg_isready -h localhost -p 5432
brew services list | grep postgresql
```

**Start it:**
```bash
./START_POSTGRES.sh
# OR
brew services start postgresql@15
```

### "Database does not exist"

The setup script will create it automatically. If it fails:

```bash
# Create manually
createdb qa_system

# Or connect and create
psql -d postgres -c "CREATE DATABASE qa_system;"
```

### "Authentication failed"

**For macOS user (no password):**
```env
DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
```

**For postgres user:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
```

### "Port 5432 already in use"

**Find what's using it:**
```bash
lsof -i :5432
```

**Kill the process or use different port:**
```bash
# Kill process
kill -9 <PID>

# Or change port in .env
DATABASE_URL=postgresql://user@localhost:5433/qa_system
```

---

## Next Steps After Setup

1. **Start Server:**
   ```bash
   ./start_server.sh
   ```

2. **Test API:**
   - Visit: http://localhost:8000/docs
   - Test health endpoints
   - Test protected endpoints (will return 401 - that's expected!)

3. **Set Up Authentication:**
   - Create test users
   - Get JWT tokens
   - Test full workflows

---

## Quick Reference

```bash
# Start PostgreSQL
./START_POSTGRES.sh

# Setup database
./setup_database.sh

# Start server
./start_server.sh

# Check PostgreSQL
pg_isready -h localhost -p 5432

# Connect to database
psql -h localhost -d qa_system
```

---

**Status**: 🟢 **Ready to Start PostgreSQL**

Run `./START_POSTGRES.sh` to get started!

