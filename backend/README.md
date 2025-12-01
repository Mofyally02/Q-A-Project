# AL-Tech Academy Q&A Platform - Backend

## 🏗️ Clean Backbone Architecture

This is the **foundational backbone** of the AL-Tech Academy Q&A Platform backend. It provides a clean, modular, and scalable architecture ready for role-specific feature integration.

## 📁 Project Structure

```
backend/
├── src/app/              # Main application code
│   ├── main.py          # FastAPI entry point
│   ├── core/            # Configuration & security
│   ├── db/              # Database sessions
│   ├── models/          # SQLAlchemy models
│   ├── api/v1/         # API routes
│   ├── utils/           # Cache, queue, logging
│   └── dependencies.py  # FastAPI dependencies
├── alembic/             # Database migrations
├── tests/               # Test suite
├── docker-compose.yml   # Services
└── Dockerfile           # Container build
```

## 🚀 Quick Start

See **[QUICK_START_BACKBONE.md](./QUICK_START_BACKBONE.md)** for a 5-minute setup guide.

## 📚 Documentation

- **[BACKBONE_README.md](./BACKBONE_README.md)** - Complete documentation
- **[BACKBONE_IMPLEMENTATION_SUMMARY.md](./BACKBONE_IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[QUICK_START_BACKBONE.md](./QUICK_START_BACKBONE.md)** - Quick start guide

## ✅ Backbone Features

- ✅ Async PostgreSQL with connection pooling
- ✅ Redis caching layer
- ✅ RabbitMQ queue management
- ✅ JWT authentication ready
- ✅ Comprehensive health checks
- ✅ Structured logging
- ✅ Database migrations (Alembic)
- ✅ Docker support
- ✅ Test suite foundation

## 🔧 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d postgres redis rabbitmq

# Run migrations
alembic upgrade head

# Start application
./run.sh
```

## 🧪 Testing

```bash
pytest
```

## 📊 Health Checks

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed service checks
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## 🎯 Next Steps

The backbone is ready for:
1. Authentication & RBAC
2. Admin backend
3. Client backend
4. Expert backend
5. AI pipeline workers
6. WebSocket real-time features

---

**For detailed information, see [BACKBONE_README.md](./BACKBONE_README.md)**
