# Database Setup - Complete Guide

## Overview

The Q&A system uses **PostgreSQL** with **16 specialized tables** organized into 2 databases for optimal traceability, performance, and scalability.

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd Q-A-Project
bash backend/database/setup_schema.sh
```

### Option 2: Manual Setup

```bash
# Start PostgreSQL first
brew services start postgresql@14  # macOS
# OR
sudo systemctl start postgresql    # Linux

# Create databases
createdb qa_auth
createdb qa_system

# Run schema
psql -d qa_auth -f backend/database/complete_schema.sql
psql -d qa_system -f backend/database/complete_schema.sql

# Initialize with default data
python backend/init_database.py
```

### Option 3: Docker Setup

```bash
# Start PostgreSQL in Docker
docker run -d \
  --name qa-postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Wait for PostgreSQL to start
sleep 5

# Create databases and run schema
docker exec -i qa-postgres psql -U postgres <<EOF
CREATE DATABASE qa_auth;
CREATE DATABASE qa_system;
EOF

# Run schema
docker exec -i qa-postgres psql -U postgres -d qa_auth < backend/database/complete_schema.sql
docker exec -i qa-postgres psql -U postgres -d qa_system < backend/database/complete_schema.sql
```

## Database Structure

### Two-Database Architecture

1. **`qa_auth`** - Authentication Database (5 tables)
   - users
   - clients
   - experts
   - admins
   - role_change_history

2. **`qa_system`** - Main System Database (11 tables)
   - questions
   - answers
   - expert_reviews
   - ratings
   - ai_processing_logs
   - humanization_logs
   - originality_checks
   - audit_logs
   - notifications
   - queue_items
   - api_usage

## Verifying Setup

### Check Databases
```sql
-- List all databases
\l

-- Check qa_auth tables
\c qa_auth
\dt

-- Check qa_system tables
\c qa_system
\dt
```

### Verify Tables
```bash
# Count tables in each database
psql -d qa_auth -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
psql -d qa_system -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

Expected output:
- qa_auth: 5 tables
- qa_system: 11 tables
- **Total: 16 tables**

### Check Indexes
```sql
-- List all indexes in qa_auth
\c qa_auth
\di

-- List all indexes in qa_system
\c qa_system
\di
```

Expected: 40+ indexes total

## Environment Configuration

Update your `.env` file:

```env
# Database URLs
DATABASE_URL=postgresql://username:password@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://username:password@localhost:5432/qa_auth

# Or with environment variable
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
```

## Troubleshooting

### Issue: PostgreSQL not running
```bash
# Check status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Start service
brew services start postgresql@14     # macOS
sudo systemctl start postgresql       # Linux
```

### Issue: Permission denied
```bash
# Grant permissions
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE qa_auth TO your_username;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE qa_system TO your_username;"
```

### Issue: Tables already exist
```bash
# Drop and recreate (CAUTION: Deletes all data)
psql -d qa_auth -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -d qa_system -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Then run schema again
psql -d qa_auth -f backend/database/complete_schema.sql
psql -d qa_system -f backend/database/complete_schema.sql
```

## Testing the Setup

### Test 1: Basic Connection
```python
import asyncpg
import asyncio

async def test_connection():
    conn = await asyncpg.connect('postgresql://user:pass@localhost:5432/qa_auth')
    result = await conn.fetchval('SELECT 1')
    print(f'Connection successful: {result}')
    await conn.close()

asyncio.run(test_connection())
```

### Test 2: Verify Tables
```python
import asyncpg
import asyncio

async def verify_tables():
    conn = await asyncpg.connect('postgresql://user:pass@localhost:5432/qa_auth')
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    print('Tables in qa_auth:')
    for table in tables:
        print(f'  - {table["table_name"]}')
    await conn.close()

asyncio.run(verify_tables())
```

### Test 3: Check Indexes
```bash
psql -d qa_system -c "
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"
```

## Production Considerations

### 1. Backup Strategy
```bash
# Daily backup
pg_dump qa_auth > backup_qa_auth_$(date +%Y%m%d).sql
pg_dump qa_system > backup_qa_system_$(date +%Y%m%d).sql

# With compression
pg_dump qa_auth | gzip > backup_qa_auth_$(date +%Y%m%d).sql.gz
pg_dump qa_system | gzip > backup_qa_system_$(date +%Y%m%d).sql.gz
```

### 2. Monitoring
```sql
-- Database size
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. Performance Tuning
- Enable `pg_stat_statements` for query monitoring
- Configure `shared_buffers` (25% of RAM)
- Set `effective_cache_size` (50-75% of RAM)
- Enable WAL archiving for point-in-time recovery

## Next Steps

1. ✅ Run schema setup
2. ✅ Verify all tables exist
3. **Next**: Initialize default data
4. **Next**: Run migrations
5. **Next**: Start the application

## Summary

✅ **16 specialized tables** created across 2 databases  
✅ **40+ indexes** for optimal performance  
✅ **Triggers, views, and functions** for automation  
✅ **Production-ready** with security and compliance features  
✅ **Complete traceability** with audit logs  
✅ **Scalable architecture** with proper indexing  

Your database is now ready for the Q&A system!
