# 🗄️ Complete Database Setup for All 90 Endpoints

## ✅ Database Schema Created

All tables needed for all 90 endpoints have been created via Alembic migrations.

### Migration Files

1. **001_initial_schema.py** - Initial tables (users, questions, answers, ratings, expert_reviews, audit_logs)
2. **002_add_users_table.py** - Extended users table with additional fields
3. **003_add_admin_tables.py** - Admin-related tables (admin_actions, api_keys, system_settings, notification_templates, compliance_flags)
4. **004_complete_schema_for_all_endpoints.py** - Complete schema for all endpoints:
   - Questions (with proper structure)
   - Answers
   - Ratings
   - Expert Reviews
   - Transactions (for wallet/credits)
   - Notifications
   - Expert Metrics (for earnings)
   - Client Wallet (for credits management)

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
cd backend
./setup_database.sh
```

This script will:
- ✅ Check PostgreSQL connection
- ✅ Create database if needed
- ✅ Run all migrations
- ✅ Set up all tables

### Option 2: Manual Setup
```bash
cd backend

# 1. Ensure PostgreSQL is running
# 2. Update .env with your database credentials

# 3. Run migrations
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
alembic upgrade head
```

---

## 📊 Database Tables

### Core Tables
- ✅ **users** - All users (clients, experts, admins)
- ✅ **questions** - All submitted questions
- ✅ **answers** - AI and expert responses
- ✅ **ratings** - Client ratings for answers
- ✅ **expert_reviews** - Expert review submissions

### Admin Tables
- ✅ **admin_actions** - Admin action audit log
- ✅ **api_keys** - External API key management
- ✅ **system_settings** - Platform-wide settings
- ✅ **notification_templates** - Reusable notification templates
- ✅ **compliance_flags** - Compliance and audit flags

### Client Tables
- ✅ **client_wallet** - Client credits and subscriptions
- ✅ **transactions** - All credit transactions
- ✅ **notifications** - User notifications

### Expert Tables
- ✅ **expert_metrics** - Expert earnings and performance metrics

### System Tables
- ✅ **audit_logs** - System-wide audit trail

---

## 🔍 Verify Database Setup

### Check Tables Exist
```bash
psql -h localhost -U postgres -d qa_system -c "\dt"
```

### Check Migration Status
```bash
cd backend
alembic current
alembic history
```

### Test Connection
```bash
cd backend
python -c "
import asyncio
from app.db.session import db
asyncio.run(db.connect())
print('✅ Database connection successful!')
"
```

---

## 📝 Table Structure Summary

### Questions Table
- `id` (UUID, Primary Key)
- `client_id` (UUID, Foreign Key → users.id)
- `type` (text, image, mixed)
- `content` (JSONB)
- `subject` (String)
- `status` (submitted, processing, ai_generated, humanized, expert_review, approved, delivered, rated, rejected, cancelled)
- `priority` (low, normal, high, urgent)
- `expert_id` (UUID, Foreign Key → users.id)
- `word_count`, `estimated_time`, `credits_cost`
- `metadata` (JSONB)
- Timestamps: `created_at`, `updated_at`, `submitted_at`, `processed_at`, `delivered_at`

### Answers Table
- `id` (UUID, Primary Key)
- `question_id` (UUID, Foreign Key → questions.id)
- `expert_id` (UUID, Foreign Key → users.id)
- `ai_response`, `humanized_response`, `expert_response`, `final_response` (JSONB)
- `confidence_score` (Float 0.0-1.0)
- `is_approved` (Boolean)
- `rejection_reason` (Text)
- `metadata` (JSONB)
- Timestamps: `created_at`, `updated_at`

### Transactions Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key → users.id)
- `type` (credit, debit, refund, topup, purchase, reward)
- `amount` (Integer)
- `balance_after` (Integer)
- `description` (Text)
- `reference_id`, `reference_type` (for linking to questions, etc.)
- `metadata` (JSONB)
- `created_at` (Timestamp)

### Notifications Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key → users.id)
- `type` (info, success, warning, error, question, answer, rating, system)
- `title` (String)
- `message` (Text)
- `is_read` (Boolean)
- `read_at` (Timestamp)
- `action_url` (String)
- `metadata` (JSONB)
- `created_at` (Timestamp)

---

## ✅ Verification Checklist

- [ ] PostgreSQL is running
- [ ] Database created
- [ ] Migrations run successfully (`alembic upgrade head`)
- [ ] All tables exist
- [ ] Foreign keys are correct
- [ ] Indexes are created
- [ ] Server can connect to database

---

## 🎯 Next Steps

1. **Verify Setup**: Run `./setup_database.sh` or manually run migrations
2. **Start Server**: `./start_server.sh`
3. **Test Endpoints**: Visit http://localhost:8000/docs
4. **Create Test Users**: Use admin endpoints to create test users
5. **Test Full Workflows**: Test question submission, expert review, ratings, etc.

---

## 🐛 Troubleshooting

### Migration Errors
```bash
# Check current migration
alembic current

# Check migration history
alembic history

# Rollback if needed
alembic downgrade -1

# Re-run migrations
alembic upgrade head
```

### Connection Errors
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Check database exists: `psql -l | grep qa_system`

### Table Not Found Errors
- Run migrations: `alembic upgrade head`
- Check tables exist: `psql -c "\dt"`

---

## 📚 Additional Resources

- **Migration Files**: `alembic/versions/`
- **Models**: `src/app/models/`
- **CRUD Operations**: `src/app/crud/`
- **Database Session**: `src/app/db/session.py`

---

**Status**: 🟢 **DATABASE SCHEMA READY**

All tables for all 90 endpoints are defined and ready to be created!

