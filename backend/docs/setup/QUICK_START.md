# 🚀 Quick Start Guide

## Starting the Backend and Database

### Option 1: Start Everything (Recommended)

```bash
cd backend
./start_all.sh
```

This will:
1. Start PostgreSQL (via Docker or local installation)
2. Run database migrations
3. Start the FastAPI backend server

### Option 2: Start Services Separately

#### Start Database Services

**With Docker (if Docker Desktop is running):**
```bash
cd backend
./start_database.sh
```

**Without Docker (using local PostgreSQL):**
```bash
cd backend
./start_database_local.sh
```

This starts:
- PostgreSQL on port 5432 (local installation)
- Creates databases if they don't exist
- Checks Redis (optional)

#### Start Backend Server Only

```bash
cd backend
./start_server.sh
```

This will:
- Check for `.env` file (creates default if missing)
- Verify PostgreSQL connection
- Activate virtual environment
- Install dependencies
- Start server on `http://localhost:8000`

### Option 3: Manual Start

#### 1. Start PostgreSQL Locally

**macOS with Homebrew:**
```bash
# Install PostgreSQL (if not installed)
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Or start manually
pg_ctl -D /opt/homebrew/var/postgresql@15 start  # Apple Silicon
# OR
pg_ctl -D /usr/local/var/postgresql@15 start    # Intel Mac
```

**Create databases:**
```bash
createdb -h localhost -U $(whoami) qa_system
createdb -h localhost -U $(whoami) qa_auth
```

#### 2. Start Backend Server

```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m app.main
```

Or with uvicorn directly:

```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://mofyally@localhost:5432/qa_system
AUTH_DATABASE_URL=postgresql://mofyally@localhost:5432/qa_auth

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# RabbitMQ (Optional - requires Docker)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

**Note:** Replace `mofyally` with your PostgreSQL username (usually your macOS username).

## Testing the Backend

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

### 2. View API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Test Login Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "allansaiti02@gmail.com",
    "password": "MofyAlly.21"
  }'
```

## Troubleshooting

### Database Connection Issues

1. **Check PostgreSQL is running:**
   ```bash
   psql -h localhost -U $(whoami) -d postgres -c "SELECT 1;"
   ```

2. **Check database exists:**
   ```bash
   psql -h localhost -U $(whoami) -l | grep qa
   ```

3. **Create databases if missing:**
   ```bash
   createdb -h localhost -U $(whoami) qa_system
   createdb -h localhost -U $(whoami) qa_auth
   ```

4. **Check PostgreSQL service status:**
   ```bash
   brew services list | grep postgresql
   ```

5. **Start PostgreSQL if not running:**
   ```bash
   brew services start postgresql@15
   # OR
   brew services start postgresql
   ```

### Port Already in Use

If port 8000 is already in use:

1. Change port in `.env`:
   ```env
   PORT=8001
   ```

2. Or kill the process:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

### Redis/RabbitMQ Connection Errors

These are optional services. The server will start without them but show warnings.

**To start Redis locally:**
```bash
brew install redis
brew services start redis
```

**To start RabbitMQ (requires Docker):**
```bash
./start_database.sh  # Uses Docker
```

## Frontend Configuration

Make sure your frontend `.env` file has:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Or:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

## Common Commands

### Stop Services

```bash
# Stop PostgreSQL (Homebrew)
brew services stop postgresql@15

# Stop Docker services (if using Docker)
docker-compose down
```

### View Logs

```bash
# Backend logs (if running in terminal)
# Just view the terminal output

# Docker logs (if using Docker)
docker-compose logs -f

# PostgreSQL logs (Homebrew)
tail -f /opt/homebrew/var/log/postgresql@15.log  # Apple Silicon
# OR
tail -f /usr/local/var/log/postgresql@15.log     # Intel Mac
```

### Database Management

```bash
# Connect to main database
psql -h localhost -U $(whoami) -d qa_system

# Connect to auth database
psql -h localhost -U $(whoami) -d qa_auth

# Run migrations
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
alembic upgrade head
```

### Install PostgreSQL (if not installed)

```bash
# macOS
brew install postgresql@15

# Initialize database (first time only)
initdb /opt/homebrew/var/postgresql@15  # Apple Silicon
# OR
initdb /usr/local/var/postgresql@15     # Intel Mac

# Start service
brew services start postgresql@15
```

---

**Need Help?** Check the logs in the terminal or PostgreSQL logs for detailed error messages.
