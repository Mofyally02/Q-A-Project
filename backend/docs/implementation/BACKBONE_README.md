# AL-Tech Academy Q&A Platform - Backend Backbone

## 🏗️ Clean, Scalable Backbone Architecture

This is the **foundational backbone** of the AL-Tech Academy Q&A Platform backend. It provides a clean, modular, and scalable architecture that serves as the foundation for all role-specific features (admin, client, expert).

---

## 📁 Project Structure

```
backend/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI application entry point
│       ├── core/                   # Core configuration and security
│       │   ├── config.py           # Application settings (Pydantic)
│       │   └── security.py        # JWT, encryption, password hashing
│       ├── db/                     # Database management
│       │   ├── session.py         # Connection pools and session management
│       │   └── init_db.py         # Database initialization
│       ├── models/                 # SQLAlchemy models
│       │   ├── base.py            # Base model class
│       │   ├── user.py            # User model
│       │   └── audit_log.py      # Audit log model
│       ├── schemas/               # Pydantic schemas (for validation)
│       ├── crud/                  # Database operations
│       ├── api/                   # API routes
│       │   └── v1/
│       │       ├── router.py      # Main API router
│       │       └── endpoints/     # Endpoint modules
│       │           ├── root.py    # Root endpoint
│       │           └── health.py  # Health check endpoints
│       ├── services/              # Business logic services
│       ├── workers/               # Background workers (RabbitMQ consumers)
│       ├── utils/                 # Utility modules
│       │   ├── logging_config.py  # Logging setup
│       │   ├── cache.py          # Redis caching utilities
│       │   └── queue.py          # RabbitMQ queue utilities
│       └── dependencies.py       # FastAPI dependencies
├── alembic/                       # Database migrations
│   ├── env.py                    # Alembic environment config
│   └── versions/                 # Migration files
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest configuration
│   └── test_foundation.py       # Foundation tests
├── .env                          # Environment variables (not in git)
├── env.example                   # Environment variables template
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
├── pytest.ini                    # Pytest configuration
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose services
├── run.sh                        # Startup script
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.9+
- Docker & Docker Compose (optional)

### 1. Clone and Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database
DATABASE_URL=postgresql://qa_user:qa_password@localhost:5432/altech_qa
AUTH_DATABASE_URL=postgresql://qa_user:qa_password@localhost:5432/qa_auth

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=qa_user
RABBITMQ_PASSWORD=qa_password

# Security
JWT_SECRET_KEY=your-secret-key-here-change-in-production
ENCRYPTION_KEY=your-encryption-key-here-change-in-production

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

### 3. Database Setup

```bash
# Using Docker Compose (recommended)
docker-compose up -d postgres redis rabbitmq

# Or manually start PostgreSQL, Redis, and RabbitMQ

# Run migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Option 1: Using the startup script
./run.sh

# Option 2: Direct uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using Docker Compose
docker-compose up
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# API documentation (if DEBUG=True)
open http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_foundation.py

# Run with verbose output
pytest -v
```

---

## 🐳 Docker Deployment

### Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app
```

### Production

```bash
# Build production image
docker build --target production -t altech-backend:latest .

# Run production container
docker run -d \
  --name altech-backend \
  -p 8000:8000 \
  --env-file .env \
  altech-backend:latest
```

---

## 📊 Architecture Overview

### Core Components

1. **FastAPI Application** (`app/main.py`)
   - Entry point with lifespan management
   - Middleware configuration (CORS, trusted hosts)
   - Router aggregation

2. **Database Layer** (`app/db/`)
   - Async PostgreSQL connection pools
   - Redis client for caching
   - Health check utilities

3. **Models** (`app/models/`)
   - SQLAlchemy models with base class
   - User model with role-based access
   - Audit log for compliance

4. **API Layer** (`app/api/v1/`)
   - Versioned API routes
   - Health check endpoints
   - Ready for role-specific routes

5. **Utilities** (`app/utils/`)
   - Logging configuration
   - Redis caching decorators
   - RabbitMQ queue management

6. **Security** (`app/core/security.py`)
   - JWT token generation/verification
   - Password hashing (bcrypt)
   - Data encryption
   - Input sanitization

---

## 🔧 Configuration

### Application Settings

All settings are managed through `app/core/config.py` using Pydantic Settings. Settings are loaded from:
1. Environment variables
2. `.env` file
3. Default values

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 📝 API Endpoints

### Health Checks

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check (all services)
- `GET /api/v1/health/ready` - Kubernetes readiness probe
- `GET /api/v1/health/live` - Kubernetes liveness probe

### Root

- `GET /` - Root endpoint with app info
- `GET /api/v1/` - API root

---

## 🔐 Security Features

- **JWT Authentication** - Token-based auth with expiration
- **Password Hashing** - bcrypt for secure password storage
- **Data Encryption** - Fernet encryption for sensitive data
- **Input Sanitization** - Protection against injection attacks
- **CORS Configuration** - Configurable cross-origin policies
- **Rate Limiting** - Ready for rate limiting implementation

---

## 📈 Monitoring & Logging

- **Structured Logging** - File and console handlers
- **Log Rotation** - Automatic log file rotation (10MB, 5 backups)
- **Error Tracking** - Separate error log file
- **Health Checks** - Comprehensive service health monitoring

---

## 🚧 Next Steps

This backbone is ready for:

1. **Authentication & RBAC** - User registration, login, role-based access
2. **Admin Panel Backend** - Admin control endpoints
3. **Client Backend** - Client-facing APIs
4. **Expert Backend** - Expert workflow APIs
5. **AI Pipeline** - Background workers for AI processing
6. **Real-Time Engine** - WebSocket implementation

---

## 📚 Documentation

- **API Docs**: Available at `/docs` when `DEBUG=True`
- **ReDoc**: Available at `/redoc` when `DEBUG=True`
- **Code Documentation**: Inline docstrings throughout

---

## 🤝 Contributing

1. Follow the project structure
2. Write tests for new features
3. Update documentation
4. Follow PEP 8 style guide
5. Use type hints

---

## 📄 License

[Your License Here]

---

## 🆘 Support

For issues and questions, please contact the development team.

---

**Built with ❤️ for AL-Tech Academy**

