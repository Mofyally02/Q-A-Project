# 🐘 PostgreSQL Setup Guide

## Quick Setup Options

### Option 1: Docker (Recommended - Easiest) ✅

**Start all services (PostgreSQL, Redis, RabbitMQ):**
```bash
cd backend
```

**Check if running:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs postgres
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove data:**
```bash
docker-compose down -v
```

---

### Option 2: Homebrew (macOS)

**Install PostgreSQL:**
```bash
brew install postgresql@15
```

**Start PostgreSQL:**
```bash
brew services start postgresql@15
```

**Check if running:**
```bash
brew services list | grep postgresql
```

**Create database:**
```bash
createdb qa_system
```

**Connect to PostgreSQL:**
```bash
psql -d qa_system
```

---

### Option 3: PostgreSQL.app (macOS GUI)

1. Download from: https://postgresapp.com/
2. Install and open the app
3. Click "Initialize" to create a new server
4. Default connection: `postgresql://localhost:5432`

---

## 🔧 Configuration

### Update .env File

After PostgreSQL is running, update your `.env` file:

```bash
cd backend
```

**If using Docker (default):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qa_system
```

**If using Homebrew:**
```env
DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://$(whoami)@localhost:5432/qa_system
```

**Or with specific user:**
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/qa_system
```

---

## ✅ Verify PostgreSQL is Running

### Check Connection
```bash
# Using psql
psql -h localhost -U postgres -d postgres -c "SELECT version();"

# Or check if port is open
nc -zv localhost 5432
```

### Check Docker Container
```bash
docker ps | grep postgres
```

### Check Homebrew Service
```bash
brew services list | grep postgresql
```

---

## 🚀 Complete Setup Process

### Step 1: Start PostgreSQL

**Using Docker (Recommended):**
```bash
cd backend
docker-compose up -d postgres
```

**Using Homebrew:**
```bash
brew services start postgresql@15
```

### Step 2: Verify Connection
```bash
psql -h localhost -U postgres -d postgres -c "SELECT 1"
```

### Step 3: Update .env
Make sure your `.env` file has the correct `DATABASE_URL`.

### Step 4: Run Database Setup
```bash
cd backend
./setup_database.sh
```

### Step 5: Start Server
```bash
./start_server.sh
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to PostgreSQL"

**Check if PostgreSQL is running:**
```bash
# Docker
docker ps | grep postgres

# Homebrew
brew services list | grep postgresql

# System
pg_isready -h localhost -p 5432
```

**Start PostgreSQL:**
```bash
# Docker
docker-compose up -d postgres

# Homebrew
brew services start postgresql@15
```

### Issue: "Authentication failed"

**Check credentials in .env:**
```bash
cat .env | grep DATABASE_URL
```

**Reset PostgreSQL password (Docker):**
```bash
docker-compose down -v
docker-compose up -d postgres
```

**Reset PostgreSQL password (Homebrew):**
```bash
psql -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

### Issue: "Database does not exist"

**Create database manually:**
```bash
# Using psql
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE qa_system;"

# Or let the setup script create it
./setup_database.sh
```

### Issue: "Port 5432 already in use"

**Find what's using the port:**
```bash
lsof -i :5432
```

**Kill the process or use a different port:**
```bash
# In docker-compose.yml, change:
ports:
  - "5433:5432"  # Use port 5433 instead
```

---

## 📊 Database Management

### Connect to Database
```bash
# Docker
docker exec -it qa_postgres psql -U postgres -d qa_system

# Homebrew
psql -h localhost -U postgres -d qa_system
```

### List Tables
```sql
\dt
```

### View Table Structure
```sql
\d table_name
```

### Backup Database
```bash
# Docker
docker exec qa_postgres pg_dump -U postgres qa_system > backup.sql

# Homebrew
pg_dump -h localhost -U postgres qa_system > backup.sql
```

### Restore Database
```bash
# Docker
docker exec -i qa_postgres psql -U postgres qa_system < backup.sql

# Homebrew
psql -h localhost -U postgres qa_system < backup.sql
```

---

## 🎯 Recommended Setup (Docker)

For the easiest setup, use Docker:

```bash
cd backend

# 1. Start PostgreSQL (and optional services)
docker-compose up -d

# 2. Wait a few seconds for PostgreSQL to be ready
sleep 5

# 3. Run database setup
./setup_database.sh

# 4. Start server
./start_server.sh
```

This will:
- ✅ Start PostgreSQL on port 5432
- ✅ Start Redis on port 6379 (optional)
- ✅ Start RabbitMQ on port 5672 (optional)
- ✅ Create all database tables
- ✅ Set up everything automatically

---

## ✅ Verification Checklist

- [ ] PostgreSQL is running
- [ ] Can connect to PostgreSQL (`psql` works)
- [ ] `.env` file has correct `DATABASE_URL`
- [ ] Database `qa_system` exists
- [ ] `./setup_database.sh` runs successfully
- [ ] Migrations complete without errors
- [ ] Server starts without database errors

---

**Status**: 🟢 **Ready to Set Up PostgreSQL**

Choose your preferred method above and follow the steps!

