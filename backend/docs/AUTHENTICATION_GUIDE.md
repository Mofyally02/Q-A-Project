# Authentication System Guide

This guide explains the authentication system for the AL-Tech Academy Q&A System, including login routes for clients, experts, and admins with PostgreSQL database integration.

## Overview

The authentication system provides:
- JWT-based authentication
- Role-based access control (Client, Expert, Admin)
- PostgreSQL database integration
- Secure password hashing
- Role-specific dashboards

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role userrole NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    api_key VARCHAR(255) UNIQUE,
    profile_data JSONB
);
```

### User Roles
- `client`: Students who ask questions
- `expert`: Reviewers who approve/reject AI answers
- `admin`: System administrators

## API Endpoints

### Authentication Routes (`/auth`)

#### General Authentication
- `POST /auth/login` - Login for any user type
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout (client-side token removal)

#### Role-Specific Login
- `POST /auth/login/client` - Client login only
- `POST /auth/login/expert` - Expert login only
- `POST /auth/login/admin` - Admin login only

#### Role-Specific Registration
- `POST /auth/register/client` - Register as client
- `POST /auth/register/expert` - Register as expert (requires admin approval)
- `POST /auth/register/admin` - Register as admin (requires existing admin privileges)

### Dashboard Routes (`/dashboard`)

#### Role-Based Dashboards
- `GET /dashboard/client` - Client dashboard (questions, answers, statistics)
- `GET /dashboard/expert` - Expert dashboard (pending reviews, statistics)
- `GET /dashboard/admin` - Admin dashboard (system analytics, user management)

#### General Dashboard
- `GET /dashboard/stats` - User-specific statistics based on role

## Usage Examples

### 1. Client Login
```bash
curl -X POST "http://localhost:8000/auth/login/client" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@demo.com",
    "password": "demo123"
  }'
```

### 2. Expert Login
```bash
curl -X POST "http://localhost:8000/auth/login/expert" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "expert@demo.com",
    "password": "demo123"
  }'
```

### 3. Admin Login
```bash
curl -X POST "http://localhost:8000/auth/login/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.com",
    "password": "demo123"
  }'
```

### 4. Access Protected Route
```bash
curl -X GET "http://localhost:8000/dashboard/client" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Setup Instructions

### 1. Database Setup
```bash
# Run the migration script
python run_migration.py
```

### 2. Environment Variables
Create a `.env` file with:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/qa_system
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Start the Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Default Users

The system comes with pre-configured demo users:

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| client@demo.com | demo123 | Client | Demo student user |
| expert@demo.com | demo123 | Expert | Demo expert reviewer |
| admin@demo.com | demo123 | Admin | Demo system administrator |

## Security Features

1. **Password Hashing**: SHA-256 with salt
2. **JWT Tokens**: 24-hour expiration
3. **Role-Based Access**: Different permissions for each role
4. **Input Validation**: Pydantic models for request validation
5. **SQL Injection Protection**: Parameterized queries
6. **CORS Configuration**: Configurable allowed origins

## Frontend Integration

### Login Component Example
```typescript
const login = async (email: string, password: string, role: string) => {
  const response = await fetch(`/api/auth/login/${role}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('token', data.access_token);
    // Redirect to appropriate dashboard
  }
};
```

### Protected Route Example
```typescript
const fetchDashboard = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('/api/dashboard/client', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return response.json();
};
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "details": {
    "field": "Additional error details"
  }
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials)
- `403`: Forbidden (insufficient permissions)
- `500`: Internal Server Error

## Database Migration

The system includes Alembic migrations for database schema management:

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"
```

## Monitoring and Logging

All authentication events are logged:
- Login attempts (success/failure)
- Token generation/validation
- Role-based access attempts
- User registration

Check logs for security monitoring and debugging.
