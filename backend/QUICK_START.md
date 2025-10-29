# Quick Start Guide - Backend Services

## Issues Found & Fixed

✅ **Missing Database Tables** - Created successfully
- `questions` table ✓
- `answers` table ✓
- `ratings` table ✓
- `expert_reviews` table ✓

⚠️ **Redis Not Running** - Needs to be started
⚠️ **RabbitMQ Not Running** - Needs to be started

## Quick Fix Commands

### Option 1: Using Docker (Recommended)

```bash
# Start Redis
docker run -d --name altech-redis -p 6379:6379 redis:7-alpine

# Start RabbitMQ
docker run -d --name altech-rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=qa_user \
  -e RABBITMQ_DEFAULT_PASS=qa_password \
  rabbitmq:3-management

# Or use the script
./start_services.sh
```

### Option 2: Using Homebrew (macOS)

```bash
# Install (if not installed)
brew install redis rabbitmq

# Start services
brew services start redis
brew services start rabbitmq
```

### Option 3: Using Docker Compose

```bash
docker-compose up -d redis rabbitmq
```

## Verify Everything Works

```bash
# Run full verification
python verify_setup.py

# Test health endpoint (after starting backend)
curl http://localhost:8000/health | jq
```

## Current Status

| Component | Status | Action Needed |
|-----------|--------|---------------|
| PostgreSQL | ✅ Working | None |
| Database Tables | ✅ Created | None |
| Redis | ⚠️ Not Running | Start service |
| RabbitMQ | ⚠️ Not Running | Start service |
| API Keys | ✅ Configured | None |

## Next Steps

1. **Start Redis and RabbitMQ** using one of the options above
2. **Verify setup**: `python verify_setup.py`
3. **Start backend**: `python start.py`
4. **Test health**: `curl http://localhost:8000/health`

## Service Management

### Check Redis Status
```bash
redis-cli ping
# Should return: PONG
```

### Check RabbitMQ Status
```bash
rabbitmqctl status
# OR access web UI: http://localhost:15672 (guest/guest)
```

### Stop Services

**Docker:**
```bash
docker stop altech-redis altech-rabbitmq
```

**Homebrew:**
```bash
brew services stop redis rabbitmq
```

## Troubleshooting

### Redis Connection Refused

**Solution:** Redis service not running
```bash
# Docker
docker run -d --name altech-redis -p 6379:6379 redis:7-alpine

# OR Homebrew
brew services start redis
```

### RabbitMQ Connection Refused

**Solution:** RabbitMQ service not running
```bash
# Docker
docker run -d --name altech-rabbitmq -p 5672:5672 rabbitmq:3-management

# OR Homebrew
brew services start rabbitmq
```

### Port Already in Use

If ports 6379 or 5672 are already in use:
```bash
# Find what's using the port
lsof -i :6379
lsof -i :5672

# Stop the conflicting service or use different ports
```

## Complete Setup

Once all services are running, you should see:

```
✓ Main Database                  Connected
✓ Auth Database                  Connected
✓ UUID Extension                 Installed
✓ Main: questions                
✓ Main: answers                  
✓ Main: ratings                  
✓ Main: expert_reviews           
✓ Redis Connection               Connected
✓ RabbitMQ Connection           Connected
```

Then your backend is **fully configured and ready**! 🎉

