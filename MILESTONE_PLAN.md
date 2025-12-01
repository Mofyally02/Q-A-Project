# AL-Tech Academy – Master Milestone Plan
## AI + Human Q&A Platform

**Clean, Professional, Scalable Architecture from Day 1**

**Tech Stack**: Python (FastAPI) + PostgreSQL + Redis + RabbitMQ + React (Next.js)

---

## CORE PRINCIPLES (Non-Negotiable)

| Principle | Rule |
|-----------|------|
| **Admin is the engine** | Everything starts and ends with Admin control |
| **One source of truth** | PostgreSQL owns all data |
| **Role-based everything** | `client`, `expert`, `admin` — strictly enforced |
| **No shortcuts** | Full testing, typing, docs, migrations |
| **Real-time from day 1** | WebSocket architecture baked in early |
| **Mobile-first thinking** | All APIs must support mobile push & deep linking |

---

## FINAL MILESTONE SEQUENCE (9 Phases)

| Phase | Name | Duration | Goal | Status |
|-------|------|----------|------|--------|
| 1 | **Foundation & Admin Core** | 10 days | Build the unbreakable admin backbone | 🔄 In Progress |
| 2 | **Authentication & RBAC** | 5 days | Secure login + role system | ✅ Complete |
| 3 | **Admin Panel Backend** | 12 days | Full admin control over everything | ✅ Complete |
| 4 | **Client Backend** | 10 days | Client-facing APIs | ✅ Complete |
| 5 | **Expert Backend** | 10 days | Expert workflow | ✅ Complete |
| 6 | **AI + Human Pipeline** | 12 days | Multi-LLM → Humanization → Originality → Expert Review | ✅ Complete |
| 7 | **Real-Time Engine** | 7 days | WebSocket + Push Notifications | 🔄 In Progress |
| 8 | **Mobile & Web Frontend** | 18 days | React + Capacitor (iOS/Android/PWA) | 🔄 In Progress |
| 9 | **Admin Web Dashboard** | 10 days | Futuristic glassmorphism admin panel | 🔄 In Progress |

**Total: ~13 weeks (3 months)**

---

## PHASE 1: FOUNDATION & ADMIN CORE

**Goal**: Build the DNA of the entire platform.

### Components

| Component | Structure | Notes |
|-----------|-----------|-------|
| **Project Layout** | Clean `src/` structure | See structure below |
| **PostgreSQL** | Single DB: `altech_qa`<br>Extensions: `uuid-ossp`, `pgcrypto` | Use Alembic |
| **Base Models** | `User`, `APIKey`, `AuditLog`, `Notification`, `CreditTransaction` | Admin creates everything |
| **Config System** | Pydantic Settings + `.env` + encrypted secrets table | Admin can update keys |
| **Health Check** | `/health` → checks DB, Redis, RabbitMQ, external APIs | Must be green |

**Deliverable**: `docker-compose up` → API alive, DB connected, health = green

---

## PHASE 2: AUTHENTICATION & RBAC ✅

| Feature | Implementation |
|----------|----------------|
| User Model | `role: ENUM('client','expert','admin') DEFAULT 'client'` |
| Registration | Only email + password → becomes `client` |
| Login | Returns JWT with `sub`, `role`, `email` |
| Dependencies | `get_current_user`, `get_current_admin`, `get_current_expert` |
| Admin Seeding | One super admin created via script |

**Deliverable**: Only admin can access `/admin/*` routes

---

## PHASE 3: ADMIN PANEL BACKEND ✅

**This is built FIRST and controls everything else.**

| Admin Module | API Routes | Purpose |
|--------------|------------|---------|
| API Key Management | `/admin/api-keys` | Store & encrypt all external keys |
| User Management | `/admin/users`, `/admin/promote-to-expert` | Full control over roles |
| Expert Onboarding | `/admin/experts/invite` | Send magic link |
| Question Oversight | `/admin/questions` | See AI → Human path |
| Notification Broadcast | `/admin/notifications/send` | Push to any user/group |
| Analytics Dashboard | `/admin/analytics/*` | All charts & reports |
| Compliance & Audit | `/admin/audit`, `/admin/flags` | Plagiarism, AI %, fines |
| System Settings | `/admin/settings` | Toggle features, maintenance mode |

**Deliverable**: Admin can control 100% of platform from API

---

## PHASE 4: CLIENT BACKEND ✅

| Module | Key Endpoints |
|--------|---------------|
| Question Submission | `POST /client/questions` (text + image) |
| Question History | `GET /client/questions` (with status) |
| Live Answer Viewing | `GET /client/questions/{id}` |
| Rating & Feedback | `POST /client/rate` |
| Wallet & Credits | `GET /client/wallet`, `POST /client/topup` |
| Notifications | `GET /client/notifications` |

All routes require `role: client` or `admin`

---

## PHASE 5: EXPERT BACKEND ✅

| Module | Key Endpoints |
|--------|---------------|
| Task Queue | `GET /expert/tasks` (pending, urgent first) |
| Review Interface | `POST /expert/review/{id}` (approve/reject + correction) |
| Earnings Dashboard | `GET /expert/earnings` |
| Performance Stats | `GET /expert/stats` |
| Chat with Client | Via WebSocket (after approval) |

Only accessible with `role: expert`

---

## PHASE 6: AI + HUMAN PIPELINE ✅

Built as **background workers** (RabbitMQ + async)

| Step | Service | Trigger |
|------|---------|---------|
| 1. OCR (if image) | `ocr_worker` | New question |
| 2. Multi-LLM Query | `ai_worker` (OpenAI, Grok, etc.) | After OCR |
| 3. Aggregation + Confidence | → store raw responses | — |
| 4. Humanization | `humanize_worker` (Stealth) | After AI |
| 5. Originality Check | `originality_worker` (Turnitin) | After humanization |
| 6. Route to Expert | If pass → assign expert | Auto |

All steps logged in `audit_logs` and visible to Admin

---

## PHASE 7: REAL-TIME ENGINE 🔄

| Component | Implementation |
|-----------|----------------|
| WebSocket Gateway | `/ws` with JWT in query |
| Connection Manager | Track user → websocket |
| Events | `answer_delivered`, `expert_typing`, `new_task`, etc. |
| Push Notifications | FCM + APNs (triggered from backend) |

Built early — used by Admin, Client, Expert

**Status**: Frontend WebSocket hooks implemented, backend integration needed

---

## PHASE 8 & 9: FRONTEND 🔄

| Platform | Tech | Status |
|----------|------|--------|
| Client Mobile + Web | React + Next.js | ✅ Complete |
| Expert Mobile + Web | React + Next.js | ✅ Complete |
| Admin Dashboard | React + Tailwind + glassmorphism | ✅ Complete |

**Status**: Frontend is production-ready, mobile optimization in progress

---

## TARGET PROJECT STRUCTURE (Python Backend)

```
backend/
├── src/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/               # config, security, settings
│   │   ├── db/                 # session, base, init
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic
│   │   ├── crud/               # database operations
│   │   ├── api/
│   │   │   ├── v1/
│   │   │       ├── admin/      # Phase 3
│   │   │       ├── client/     # Phase 4
│   │   │       ├── expert/     # Phase 5
│   │   │       └── websocket/  # Phase 7
│   │   ├── services/           # AI, humanization, notifications
│   │   ├── workers/            # RabbitMQ consumers
│   │   ├── utils/              # encryption, helpers
│   │   └── dependencies/       # auth, rbac, db
│   ├── alembic/
│   ├── tests/
│   ├── .env
│   └── docker-compose.yml
```

---

## CURRENT STATE ASSESSMENT

### ✅ Completed
- Authentication & RBAC (Phase 2)
- Admin Panel Backend (Phase 3)
- Client Backend (Phase 4)
- Expert Backend (Phase 5)
- AI + Human Pipeline (Phase 6)
- Frontend (Phases 8 & 9)

### 🔄 In Progress
- Foundation restructuring (Phase 1)
- Real-Time Engine backend (Phase 7)
- Mobile optimization

### 📋 Next Steps
1. Restructure backend to match target architecture
2. Complete WebSocket backend implementation
3. Add comprehensive testing
4. Mobile app preparation

---

## DEVELOPMENT ORDER (Non-Negotiable)

1. **Admin First** → Total control
2. **Auth Second** → Security lock
3. **Client/Expert Third** → Controlled rollout
4. **AI Pipeline Fourth** → Only when safe
5. **Real-Time Fifth** → Magic layer
6. **Frontend Last** → Never before backend is perfect

This order has been used by **every successful edtech/AI startup** in the last 5 years.

