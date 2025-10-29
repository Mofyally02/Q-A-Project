# Backend & Database Configuration Verification

This guide helps you verify that all backend and database configurations are working correctly.

## Quick Verification

### 1. Run the Verification Script

```bash
cd backend
python verify_setup.py
```

This script checks:
- ✅ Environment variables configuration
- ✅ PostgreSQL database connections (main & auth)
- ✅ Database schema (required tables)
- ✅ Redis connectivity
- ✅ RabbitMQ connectivity
- ✅ API keys configuration

### 2. Test Health Endpoints

#### Basic Health Check
```bash
curl http://localhost:8000/health
```

#### Detailed Health Check
```bash
curl http://localhost:8000/health | jq
```

#### Database-specific Health Check
```bash
curl http://localhost:8000/health/database | jq
```

#### Redis Health Check
```bash
curl http://localhost:8000/health/redis | jq
```

#### RabbitMQ Health Check
```bash
curl http://localhost:8000/health/rabbitmq | jq
```

## Expected Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-10T10:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 12,
      "table_count": 15
    },
    "auth_database": {
      "status": "healthy",
      "latency_ms": 8,
      "users_table_exists": true
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 3
    },
    "rabbitmq": {
      "status": "healthy",
      "latency_ms": 8
    },
    "api_keys": {
      "openai": {
        "configured": true,
        "masked": "sk-...xyz"
      },
      "xai": {
        "configured": false,
        "masked": "not_set"
      }
    }
  },
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

## Step-by-Step Configuration Verification

### 1. Database (PostgreSQL)

#### Check Connection
```bash
psql $DATABASE_URL -c "SELECT version();"
psql $AUTH_DATABASE_URL -c "SELECT version();"
```

#### Check Tables
```bash
psql $DATABASE_URL -c "\dt"
psql $AUTH_DATABASE_URL -c "\dt"
```

#### Check UUID Extension
```bash
psql $DATABASE_URL -c "SELECT uuid_generate_v4();"
```

#### Run Migrations (if needed)
```bash
cd backend
python run_migration.py
# OR
alembic upgrade head
```

### 2. Redis

#### Check Connection
```bash
redis-cli ping
# Should return: PONG
```

#### Test Operations
```bash
redis-cli SET test_key "test_value"
redis-cli GET test_key
redis-cli DEL test_key
```

### 3. RabbitMQ

#### Check Connection
```bash
rabbitmqctl ping
# OR via management UI
open http://localhost:15672
# Login: guest / guest
```

#### List Queues
```bash
rabbitmqctl list_queues
```

### 4. API Keys

Verify your `.env` file has the required keys:

```bash
# Check if keys are loaded
python -c "from app.config import settings; print('OpenAI:', bool(settings.openai_api_key))"
```

### 5. Environment Variables

Create `.env` file from template:

```bash
cp env.example .env
# Edit .env with your actual values
```

Required variables:
- `DATABASE_URL`
- `AUTH_DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

## Docker Setup (Alternative)

If using Docker:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- RabbitMQ on port 5672 (Management UI on 15672)
- Backend API on port 8000

Verify all services:

```bash
docker-compose ps
```

Check logs:

```bash
docker-compose logs postgres
docker-compose logs redis
docker-compose logs rabbitmq
docker-compose logs app
```

## Troubleshooting

### Database Connection Issues

**Error**: `asyncpg.exceptions.InvalidPasswordError`

**Fix**: Check your database credentials in `.env` file

```bash
# Test connection manually
psql postgresql://user:password@localhost:5432/dbname
```

### Redis Connection Issues

**Error**: `Connection refused`

**Fix**: Start Redis service

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# OR using system service
sudo systemctl start redis
```

### RabbitMQ Connection Issues

**Error**: `Connection refused`

**Fix**: Start RabbitMQ service

```bash
# Using Docker
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# OR using system service
sudo systemctl start rabbitmq-server
```

### Missing Tables

**Error**: `relation "users" does not exist`

**Fix**: Run database migrations

```bash
cd backend
python run_migration.py
# OR
python init_database.py
```

## Integration Testing

Test the complete flow:

```bash
# 1. Start services
docker-compose up -d

# 2. Run verification
python verify_setup.py

# 3. Test API endpoints
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","first_name":"Test","last_name":"User"}'

# 4. Check health endpoint
curl http://localhost:8000/health | jq

# 5. Test database operations
curl -X GET http://localhost:8000/dashboard/client?user_id=<user_id>
```

## Continuous Monitoring

Add health check to monitoring system:

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

# Docker healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Success Criteria

✅ All checks passing means:
- Database connections working
- All required tables exist
- Redis caching operational
- RabbitMQ queue system ready (optional)
- API keys configured (for AI features)
- Backend ready to accept requests

## Next Steps

Once all checks pass:

1. Start the backend server:
   ```bash
   python start.py
   ```

2. Test admin login:
   ```bash
   curl -X POST http://localhost:8000/auth/login/admin \
     -H "Content-Type: application/json" \
     -d '{"email":"allansaiti02@gmail.com","password":"MofyAlly.21#"}'
   ```

3. Access admin dashboard:
   ```
   http://localhost:3000/admin/dashboard
   ```

