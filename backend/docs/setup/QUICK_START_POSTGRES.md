# 🚀 Quick Start - PostgreSQL Setup

## Fastest Way: Docker (2 Commands)

```bash
cd backend

# 1. Start PostgreSQL
docker-compose up -d postgres

# 2. Wait 5 seconds, then run setup
sleep 5 && ./setup_database.sh
```

That's it! ✅

---

## Alternative: Homebrew (macOS)

```bash
# 1. Install PostgreSQL
brew install postgresql@15

# 2. Start PostgreSQL
brew services start postgresql@15

# 3. Create database
createdb qa_system

# 4. Run setup
cd backend
./setup_database.sh
```

---

## Verify It's Working

```bash
# Check PostgreSQL is running
docker ps | grep postgres
# OR
brew services list | grep postgresql

# Test connection
psql -h localhost -U postgres -d postgres -c "SELECT 1"
```

---

## If You Get Errors

**"Cannot connect to PostgreSQL":**
- Start PostgreSQL first (see commands above)
- Check `.env` has correct `DATABASE_URL`

**"Database does not exist":**
- The setup script will create it automatically
- Or create manually: `createdb qa_system`

**"Permission denied":**
- For Docker: Use `postgres:postgres` (default)
- For Homebrew: Use your macOS username (no password)

---

**Need more help?** See `POSTGRESQL_SETUP.md` for detailed instructions.

