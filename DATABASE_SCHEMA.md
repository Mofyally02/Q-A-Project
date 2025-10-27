# Database Schema Documentation

## Overview
This document describes the complete database schema for the AI Q&A System backend. The database uses PostgreSQL with asyncpg for async operations.

## Database Configuration

### Connection Settings
- **Main Database**: `qa_system` - Stores questions, answers, ratings, reviews
- **Auth Database**: `qa_auth` - Stores user authentication data
- **Redis**: Used for caching and session management

### Connection URLs
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/qa_system"
AUTH_DATABASE_URL = "postgresql://qa_user:qa_password@localhost:5432/qa_auth"
REDIS_URL = "redis://localhost:6379"
```

## Schema Tables

### 1. Users Table
**Purpose**: Stores user authentication and profile information

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'expert', 'admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login TIMESTAMP,
    api_key VARCHAR(255) UNIQUE,
    profile_data JSONB
);
```

**Indexes**:
- `idx_users_email` on `email`
- `idx_users_role` on `role`
- `idx_users_is_active` on `is_active`
- `idx_users_created_at` on `created_at`
- `idx_users_first_name` on `first_name`
- `idx_users_last_name` on `last_name`
- `idx_users_api_key` on `api_key`

### 2. Clients Table
**Purpose**: Stores client-specific information

```sql
CREATE TABLE clients (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) DEFAULT 'basic',
    credits_remaining INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_clients_subscription` on `subscription_type`

### 3. Experts Table
**Purpose**: Stores expert-specific information

```sql
CREATE TABLE experts (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    approved BOOLEAN DEFAULT false,
    specialization VARCHAR(100),
    experience_years INTEGER,
    rating FLOAT DEFAULT 0.0,
    total_reviews INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_experts_approved` on `approved`
- `idx_experts_rating` on `rating`

### 4. Admins Table
**Purpose**: Stores admin-specific information

```sql
CREATE TABLE admins (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    permissions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Questions Table
**Purpose**: Stores submitted questions

```sql
CREATE TABLE questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES users(user_id),
    type VARCHAR(10) NOT NULL CHECK (type IN ('text', 'image')),
    content JSONB NOT NULL,
    subject VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('submitted', 'processing', 'humanized', 'review', 'delivered', 'rated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_questions_client_id` on `client_id`
- `idx_questions_status` on `status`
- `idx_questions_created_at` on `created_at`

### 6. Answers Table
**Purpose**: Stores AI-generated and processed answers

```sql
CREATE TABLE answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id),
    expert_id UUID REFERENCES users(user_id),
    ai_response JSONB,
    humanized_response JSONB,
    expert_response JSONB,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    is_approved BOOLEAN,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_answers_question_id` on `question_id`
- `idx_answers_expert_id` on `expert_id`

### 7. Ratings Table
**Purpose**: Stores user ratings for answers

```sql
CREATE TABLE ratings (
    rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id),
    expert_id UUID REFERENCES users(user_id),
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_ratings_question_id` on `question_id`
- `idx_ratings_expert_id` on `expert_id`

### 8. Expert Reviews Table
**Purpose**: Stores expert reviews and corrections

```sql
CREATE TABLE expert_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES answers(answer_id),
    expert_id UUID NOT NULL REFERENCES users(user_id),
    is_approved BOOLEAN NOT NULL,
    rejection_reason TEXT,
    correction JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9. Expert Metrics Table
**Purpose**: Stores aggregated expert performance metrics

```sql
CREATE TABLE expert_metrics (
    expert_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    avg_rating FLOAT NOT NULL DEFAULT 0.0,
    total_ratings INTEGER NOT NULL DEFAULT 0,
    total_score INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 10. Audit Logs Table
**Purpose**: Stores audit trail for compliance and monitoring

```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(user_id),
    question_id UUID REFERENCES questions(question_id),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- `idx_audit_logs_user_id` on `user_id`
- `idx_audit_logs_question_id` on `question_id`
- `idx_audit_logs_created_at` on `created_at`

## Data Relationships

### Entity Relationship Diagram
```
Users (1) ----< (N) Questions
Users (1) ----< (N) Answers (as expert_id)
Users (1) ----< (N) Ratings (as expert_id)
Users (1) ----< (N) Expert Reviews
Users (1) ----< (1) Clients
Users (1) ----< (1) Experts
Users (1) ----< (1) Admins
Users (1) ----< (1) Expert Metrics

Questions (1) ----< (1) Answers
Questions (1) ----< (N) Ratings
Questions (1) ----< (N) Audit Logs

Answers (1) ----< (N) Expert Reviews
```

## Service Integration

### Authentication Service
- **Database**: Uses `qa_auth` database
- **Tables**: `users`, `clients`, `experts`, `admins`
- **Operations**: User registration, login, token verification

### Submission Service
- **Database**: Uses main `qa_system` database
- **Tables**: `questions`, `answers`
- **Operations**: Question submission, status tracking

### Rating Service
- **Database**: Uses main `qa_system` database
- **Tables**: `ratings`, `expert_metrics`
- **Operations**: Rating submission, expert metrics calculation

### Expert Review Service
- **Database**: Uses main `qa_system` database
- **Tables**: `expert_reviews`, `answers`
- **Operations**: Review submission, expert assignment

### Admin Service
- **Database**: Uses main `qa_system` database
- **Tables**: All tables for analytics
- **Operations**: Analytics, data export, admin overrides

### Audit Service
- **Database**: Uses main `qa_system` database
- **Tables**: `audit_logs`
- **Operations**: Logging, compliance tracking

## Migration Management

### Alembic Migrations
- **001_initial_schema.py**: Creates core tables (users, questions, answers, ratings, expert_reviews, audit_logs)
- **002_add_users_table.py**: Adds missing columns and role-specific tables

### Running Migrations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1
```

## Database Initialization

### Default Data
The system creates default users for testing:
- **Client**: `client@demo.com` / `demo123`
- **Expert**: `expert@demo.com` / `demo123`
- **Admin**: `admin@demo.com` / `demo123`

### Initialization Script
Run `python init_database.py` to:
- Create default users
- Set up role-specific records
- Verify database integrity

## Testing

### Integration Tests
Run `python test_database_integration.py` to test:
- Database connections
- Service integrations
- CRUD operations
- Data integrity

## Performance Considerations

### Indexing Strategy
- Primary keys are UUIDs with default `gen_random_uuid()`
- Foreign keys are indexed for join performance
- Status and role columns are indexed for filtering
- Timestamps are indexed for time-based queries

### Connection Pooling
- Main database: 5-20 connections
- Auth database: 2-10 connections
- Redis: Single connection with connection pooling

### Query Optimization
- Use prepared statements with asyncpg
- Implement pagination for large result sets
- Use JSONB for flexible data storage
- Leverage PostgreSQL's advanced features

## Security

### Data Protection
- Passwords are hashed using bcrypt
- API keys are generated securely
- Sensitive data is encrypted
- Audit logs track all actions

### Access Control
- Role-based access control (RBAC)
- JWT tokens for authentication
- Database-level constraints
- Input validation and sanitization

## Monitoring

### Health Checks
- Database connection status
- Query performance metrics
- Error rate monitoring
- Resource utilization tracking

### Logging
- All database operations are logged
- Audit trail for compliance
- Error logging with stack traces
- Performance metrics logging
