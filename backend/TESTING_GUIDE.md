# Backend Testing Guide

## 🧪 Testing All 90 Endpoints

This guide will help you test all 90 implemented endpoints to ensure they're working correctly.

---

## 📋 Prerequisites

1. **Database Setup**
   ```bash
   # Ensure PostgreSQL is running
   # Run migrations
   cd backend
   alembic upgrade head
   ```

2. **Environment Variables**
   ```bash
   # Ensure .env file is configured
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services**
   ```bash
   # Start Redis (optional)
   redis-server
   
   # Start RabbitMQ (optional)
   rabbitmq-server
   ```

---

## 🚀 Quick Start Testing

### 1. Start the Backend Server

```bash
cd backend
python -m app.main
# Or
uvicorn app.main:app --reload
```

The server should start on `http://localhost:8000`

### 2. Test Health Endpoints (No Auth Required)

```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/api/v1/health

# Test database health
curl http://localhost:8000/api/v1/health/db

# Test cache health
curl http://localhost:8000/api/v1/health/cache

# Test queue health
curl http://localhost:8000/api/v1/health/queue
```

### 3. Run Automated Test Script

```bash
# Run the test script
python test_backend.py
```

This will test all endpoints and provide a summary.

---

## 📊 Endpoint Categories

### Health & Root (5 endpoints)
- ✅ `GET /` - Root endpoint
- ✅ `GET /api/v1/health` - Full health check
- ✅ `GET /api/v1/health/db` - Database health
- ✅ `GET /api/v1/health/cache` - Cache health
- ✅ `GET /api/v1/health/queue` - Queue health

### Admin Endpoints (71 endpoints)

#### User Management (7)
- `GET /api/v1/admin/users` - List users
- `GET /api/v1/admin/users/{id}` - Get user
- `POST /api/v1/admin/users/{id}/role` - Change role
- `POST /api/v1/admin/users/{id}/ban` - Ban user
- `POST /api/v1/admin/users/{id}/unban` - Unban user
- `POST /api/v1/admin/users/{id}/reset-password` - Reset password
- `POST /api/v1/admin/users/{id}/promote-expert` - Promote to expert

#### API Keys (5)
- `GET /api/v1/admin/api-keys` - List keys
- `POST /api/v1/admin/api-keys` - Create/update key
- `DELETE /api/v1/admin/api-keys/{provider}` - Delete key
- `POST /api/v1/admin/api-keys/{provider}/test` - Test connection
- `POST /api/v1/admin/api-keys/{provider}/rotate` - Rotate key

#### System Settings (4)
- `GET /api/v1/admin/settings` - Get settings
- `PUT /api/v1/admin/settings/{key}` - Update setting
- `POST /api/v1/admin/settings/maintenance-mode` - Toggle maintenance
- `GET /api/v1/admin/settings/health` - System health

#### Question Oversight (8)
- `GET /api/v1/admin/questions` - List questions
- `GET /api/v1/admin/questions/{id}` - Get question
- `POST /api/v1/admin/questions/{id}/reassign` - Reassign
- `POST /api/v1/admin/questions/{id}/force-delivery` - Force delivery
- `POST /api/v1/admin/questions/{id}/admin-correction` - Admin correction
- `POST /api/v1/admin/questions/{id}/flag-plagiarism` - Flag plagiarism
- `POST /api/v1/admin/questions/{id}/escalate` - Escalate
- `GET /api/v1/admin/questions/pipeline` - Get pipeline

#### Expert Management (8)
- `GET /api/v1/admin/experts` - List experts
- `GET /api/v1/admin/experts/{id}` - Get expert
- `POST /api/v1/admin/experts/{id}/suspend` - Suspend expert
- `GET /api/v1/admin/experts/{id}/performance` - Get performance
- `GET /api/v1/admin/experts/leaderboard` - Get leaderboard
- `GET /api/v1/admin/experts/{id}/reviews` - Get reviews
- `GET /api/v1/admin/experts/stats` - Get stats
- `PUT /api/v1/admin/experts/{id}` - Update expert

#### Compliance & Audit (7)
- `GET /api/v1/admin/audit-logs` - Get audit logs
- `GET /api/v1/admin/audit-logs/{id}` - Get audit log
- `GET /api/v1/admin/compliance/flagged` - Get flagged content
- `GET /api/v1/admin/compliance/users/{id}` - Get user compliance
- `POST /api/v1/admin/compliance/flag/{id}` - Flag content
- `GET /api/v1/admin/compliance/stats` - Get compliance stats
- `POST /api/v1/admin/audit-logs/export` - Export audit logs

#### Admin Management (4)
- `GET /api/v1/admin/admins` - List admins
- `POST /api/v1/admin/admins/invite` - Invite admin
- `POST /api/v1/admin/admins/{id}/suspend` - Suspend admin
- `DELETE /api/v1/admin/admins/{id}` - Revoke admin

#### Notifications (5)
- `POST /api/v1/admin/notifications/broadcast` - Broadcast
- `POST /api/v1/admin/notifications/broadcast/segment` - Broadcast to segment
- `GET /api/v1/admin/notifications/history` - Get history
- `GET /api/v1/admin/notifications/templates` - Get templates
- `POST /api/v1/admin/notifications/templates` - Create template

#### Revenue (6)
- `GET /api/v1/admin/revenue/dashboard` - Revenue dashboard
- `GET /api/v1/admin/revenue/transactions` - Get transactions
- `POST /api/v1/admin/revenue/credits/grant` - Grant credits
- `POST /api/v1/admin/revenue/credits/revoke` - Revoke credits
- `GET /api/v1/admin/revenue/credits/stats` - Credits stats

#### Override Triggers (5) - Super Admin Only
- `POST /api/v1/admin/override/ai-bypass/{id}` - Bypass AI check
- `POST /api/v1/admin/override/originality-pass/{id}` - Pass originality
- `POST /api/v1/admin/override/confidence-override/{id}` - Override confidence
- `POST /api/v1/admin/override/humanization-skip/{id}` - Skip humanization
- `POST /api/v1/admin/override/expert-bypass/{id}` - Bypass expert review

#### Queue Control (6)
- `GET /api/v1/admin/queues/status` - Get queue status
- `GET /api/v1/admin/queues/workers` - Get worker status
- `POST /api/v1/admin/queues/{name}/pause` - Pause queue
- `POST /api/v1/admin/queues/{name}/resume` - Resume queue
- `POST /api/v1/admin/queues/{name}/purge` - Purge queue
- `POST /api/v1/admin/queues/{name}/retry` - Retry failed tasks

#### Backup & Recovery (4) - Super Admin Only
- `POST /api/v1/admin/backup/create` - Create backup
- `GET /api/v1/admin/backup` - List backups
- `GET /api/v1/admin/backup/{id}` - Get backup
- `DELETE /api/v1/admin/backup/{id}` - Delete backup

### Client Endpoints (12 endpoints)

#### Dashboard (1)
- `GET /api/v1/client/dashboard` - Get dashboard

#### Questions (4)
- `POST /api/v1/client/questions/ask` - Submit question
- `GET /api/v1/client/questions/{id}` - Get question status
- `GET /api/v1/client/questions/history` - Get history
- `GET /api/v1/client/questions/chat/{id}` - Get chat thread

#### Wallet (2)
- `GET /api/v1/client/wallet` - Get wallet info
- `POST /api/v1/client/wallet/topup` - Initiate topup

#### Notifications (3)
- `GET /api/v1/client/notifications` - Get notifications
- `POST /api/v1/client/notifications/{id}/read` - Mark as read
- `POST /api/v1/client/notifications/read-all` - Mark all read

#### Settings (2)
- `GET /api/v1/client/settings/profile` - Get profile
- `PUT /api/v1/client/settings/profile` - Update profile

### Expert Endpoints (7 endpoints)

#### Tasks (3)
- `GET /api/v1/expert/tasks` - Get tasks
- `GET /api/v1/expert/tasks/{id}` - Get task detail
- `POST /api/v1/expert/tasks/{id}/start` - Start task

#### Reviews (2)
- `POST /api/v1/expert/reviews/submit` - Submit review
- `GET /api/v1/expert/reviews` - Get reviews

#### Earnings (1)
- `GET /api/v1/expert/earnings` - Get earnings

#### Ratings (1)
- `GET /api/v1/expert/ratings` - Get ratings

---

## 🔐 Authentication Testing

Most endpoints require JWT authentication. To test authenticated endpoints:

1. **Get a JWT token** (you'll need to implement auth endpoints first, or use existing tokens)

2. **Include token in requests:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/client/dashboard
   ```

3. **Test with Python:**
   ```python
   import httpx
   
   headers = {"Authorization": "Bearer YOUR_TOKEN"}
   response = httpx.get("http://localhost:8000/api/v1/client/dashboard", headers=headers)
   print(response.json())
   ```

---

## 📝 Testing Checklist

### Phase 1: Basic Connectivity
- [ ] Server starts without errors
- [ ] Root endpoint responds
- [ ] Health endpoints respond
- [ ] API documentation accessible at `/docs`

### Phase 2: Endpoint Existence
- [ ] All 90 endpoints are registered
- [ ] No 404 errors for valid endpoints
- [ ] Proper HTTP methods (GET, POST, PUT, DELETE)

### Phase 3: Authentication
- [ ] Unauthenticated requests return 401
- [ ] Authenticated requests work
- [ ] Role-based access control works

### Phase 4: Functionality
- [ ] CRUD operations work
- [ ] Data validation works
- [ ] Error handling works
- [ ] Pagination works

### Phase 5: Integration
- [ ] Database operations work
- [ ] Cache operations work (if Redis available)
- [ ] Queue operations work (if RabbitMQ available)

---

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Connection Errors**
   ```bash
   # Check PostgreSQL is running
   # Verify DATABASE_URL in .env
   # Run migrations
   alembic upgrade head
   ```

3. **Port Already in Use**
   ```bash
   # Change port in .env or use different port
   uvicorn app.main:app --port 8001
   ```

4. **Missing Tables**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

---

## 📈 Expected Results

When running `test_backend.py`, you should see:

- **Health endpoints**: All should pass (no auth required)
- **Authenticated endpoints**: Will fail with 401 without tokens (expected)
- **Endpoint existence**: All endpoints should be reachable (not 404)

---

## 🎯 Next Steps

1. **Implement Authentication Endpoints** (if not already done)
2. **Create Test Users** (admin, client, expert)
3. **Generate JWT Tokens** for testing
4. **Test Full Workflows** (question submission → expert review → delivery)
5. **Load Testing** (use tools like Locust or Apache Bench)

---

## 📚 Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- API Documentation: http://localhost:8000/docs (when server is running)
- ReDoc Documentation: http://localhost:8000/redoc (when server is running)

---

**Status**: Ready for Testing! 🚀

