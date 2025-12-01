# Quick Start Guide - Backbone Backend

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
python3 --version  # Should be 3.12+
docker --version   # Optional but recommended
```

### 1. Setup Environment (1 minute)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)
```bash
cp env.example .env
# Edit .env with your database credentials
```

**Minimum required in `.env`:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/altech_qa
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

### 3. Start Services (1 minute)
```bash
# Option A: Docker Compose (Recommended)
docker-compose up -d postgres redis rabbitmq

# Option B: Manual
# Start PostgreSQL, Redis, and RabbitMQ manually
```

### 4. Run Migrations (1 minute)
```bash
alembic upgrade head
```

### 5. Start Application (1 minute)
```bash
# Option A: Using startup script
./run.sh

# Option B: Direct
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Verify (30 seconds)
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Should return:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

## ✅ Success!

Your backbone is running! Visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health/
- **Root**: http://localhost:8000/

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
# Format: postgresql://user:password@host:port/database
```

### Redis Connection Error
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping  # Should return PONG
```

### Port Already in Use
```bash
# Change port in .env
PORT=8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill
```

## 📚 Next Steps

1. Review `BACKBONE_README.md` for detailed documentation
2. Check `BACKBONE_IMPLEMENTATION_SUMMARY.md` for what's implemented
3. Start building role-specific features (admin, client, expert)

---

**Need Help?** Check the full documentation in `BACKBONE_README.md`

