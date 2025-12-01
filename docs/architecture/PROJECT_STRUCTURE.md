# Q-A-Project Structure

This document outlines the reorganized structure of the Q-A-Project.

## Directory Structure

```
Q-A-Project/
├── backend/                    # Backend application and services
│   ├── app/                   # FastAPI application core
│   │   ├── routes/           # API route handlers
│   │   ├── services/         # Business logic services
│   │   ├── utils/            # Utility functions
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   └── models.py         # Data models
│   ├── database/             # Database scripts and docs
│   │   ├── init.sql          # Database initialization
│   │   ├── setup_database.sh # Database setup script
│   │   ├── DATABASE_SCHEMA.md
│   │   ├── DATABASE_SETUP_GUIDE.md
│   │   └── POSTGRESQL_SETUP_INSTRUCTIONS.md
│   ├── docs/                 # Backend documentation
│   │   ├── POE_API_INTEGRATION.md
│   │   └── AUTHENTICATION_GUIDE.md
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test suite
│   ├── alembic.ini           # Alembic configuration
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker configuration
│   ├── docker-compose.yml    # Docker Compose config
│   ├── env.example           # Environment variables template
│   ├── start.py              # Simple startup script
│   ├── start.sh              # Full startup script
│   ├── start_backend.py      # Detailed startup script
│   ├── run_tests.py          # Test runner
│   ├── run_tests.sh          # Test runner script
│   ├── run_migration.py      # Migration runner
│   ├── init_database.py      # Database initialization
│   ├── setup_postgresql.py   # PostgreSQL setup
│   ├── check_postgresql.py   # PostgreSQL checker
│   └── test_database_integration.py
├── frontend/                  # Frontend application
│   ├── docs/                 # Frontend documentation
│   │   └── FRONTEND_SUMMARY.md
│   ├── assets/               # Static assets
│   ├── components/           # Vue components
│   ├── composables/          # Vue composables
│   ├── layouts/              # Layout components
│   ├── middleware/           # Route middleware
│   ├── pages/                # Pages/routes
│   ├── plugins/              # Nuxt plugins
│   ├── stores/               # Pinia stores
│   ├── types/                # TypeScript types
│   ├── app.vue               # Root component
│   ├── nuxt.config.ts        # Nuxt configuration
│   ├── package.json          # NPM dependencies
│   └── ...                   # Other frontend files
├── docs/                      # Project-wide documentation
│   └── PROJECT_SUMMARY.md
├── database/                  # Database resources (if any)
├── README.md                  # Main project README
└── .gitignore                # Git ignore rules
```

## Organization Rationale

### Backend Files
All backend-related files have been consolidated into the `backend/` directory:
- **Application code**: `backend/app/` contains all FastAPI application code
- **Database**: `backend/database/` contains all database-related scripts and documentation
- **Documentation**: `backend/docs/` contains backend-specific documentation
- **Migrations**: `backend/alembic/` contains database migration scripts
- **Tests**: `backend/tests/` contains all test files
- **Scripts**: All Python scripts for running, testing, and setting up the backend

### Frontend Files
The frontend remains self-contained in the `frontend/` directory:
- All frontend code, components, and configuration stay in one place
- Frontend-specific documentation in `frontend/docs/`

### Database Files
Database-related files are organized in `backend/database/`:
- SQL scripts
- Database setup documentation
- Database schema documentation
- Setup and initialization scripts

### Project Documentation
High-level project documentation stays at the root:
- `README.md`: Main project overview and quick start guide
- `docs/`: Project-wide documentation that doesn't fit in backend/frontend

## Running the Project

### Backend
```bash
cd backend
python start_backend.py
# or
./start.sh
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
python run_tests.py
```

### Database Setup
```bash
cd backend/database
./setup_database.sh
# or
cd backend
python setup_postgresql.py
```

## Migration Notes

All imports remain the same (e.g., `from app.config import settings`) as the `app` module is still in `backend/app/`. The Python path is automatically adjusted when running scripts from the `backend/` directory.
