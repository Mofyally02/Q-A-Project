# Admin Backend - Complete Feature List

## 🎯 Executive Summary

This document lists **every single feature** that must be incorporated into the admin backend to ensure smooth, all-rounded platform operation. The admin system has **two tiers**: **Super Admin** (full control) and **Admin/Editor** (supervisor level).

---

## 📊 Complete Feature Inventory

### **1. USER & ROLE MANAGEMENT** (7 Features)
**Total Endpoints**: 7  
**Purpose**: Complete control over all platform users

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 1.1 | List All Users | `GET /admin/users` | ✅ Full | ✅ View Only |
| 1.2 | User Details | `GET /admin/users/{id}` | ✅ Full | ✅ View Only |
| 1.3 | Change User Role | `POST /admin/users/{id}/role` | ✅ | ❌ |
| 1.4 | Ban/Unban User | `POST /admin/users/{id}/ban` | ✅ | ✅ |
| 1.5 | Reset Password | `POST /admin/users/{id}/reset-password` | ✅ | ✅ |
| 1.6 | Promote to Expert | `POST /admin/users/{id}/promote-to-expert` | ✅ | ✅ |
| 1.7 | User Statistics | `GET /admin/users/stats` | ✅ | ✅ |

**Backend Logic Required:**
- Role validation and transition rules
- Ban cascade (cancel active questions, notify user)
- Password reset email generation
- Expert promotion workflow with verification

---

### **2. ADMIN MANAGEMENT** (4 Features)
**Total Endpoints**: 4  
**Purpose**: Manage admin accounts and permissions

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 2.1 | Invite New Admin | `POST /admin/invite-admin` | ✅ | ❌ |
| 2.2 | List All Admins | `GET /admin/admins` | ✅ | ✅ View |
| 2.3 | Suspend Admin | `POST /admin/admins/{id}/suspend` | ✅ | ❌ |
| 2.4 | Revoke Admin Access | `POST /admin/admins/{id}/revoke` | ✅ | ❌ |

**Backend Logic Required:**
- Magic link generation with expiration
- Email invitation system
- Admin suspension with audit trail
- Prevent self-revocation

---

### **3. API KEYS MANAGEMENT** (6 Features)
**Total Endpoints**: 6  
**Purpose**: Secure management of external service API keys

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 3.1 | List API Keys | `GET /admin/api-keys` | ✅ | ✅ View |
| 3.2 | Add API Key | `POST /admin/api-keys` | ✅ | ❌ |
| 3.3 | Update API Key | `PATCH /admin/api-keys/{id}` | ✅ | ❌ |
| 3.4 | Delete API Key | `DELETE /admin/api-keys/{id}` | ✅ | ❌ |
| 3.5 | Test API Key | `POST /admin/api-keys/{id}/test` | ✅ | ✅ |
| 3.6 | Rotate API Key | `POST /admin/api-keys/{id}/rotate` | ✅ | ❌ |

**Backend Logic Required:**
- Fernet encryption for key storage
- Key rotation with grace period
- Connection testing for each service
- Key type validation

---

### **4. SYSTEM SETTINGS & TOGGLES** (5 Features)
**Total Endpoints**: 5  
**Purpose**: Platform-wide configuration control

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 4.1 | Get All Settings | `GET /admin/settings` | ✅ | ✅ View |
| 4.2 | Update Settings | `PATCH /admin/settings` | ✅ | ❌ |
| 4.3 | Toggle Setting | `POST /admin/settings/{key}/toggle` | ✅ | ❌ |
| 4.4 | Check Maintenance | `GET /admin/settings/maintenance-mode` | ✅ | ✅ View |
| 4.5 | Toggle Maintenance | `POST /admin/settings/maintenance-mode` | ✅ | ❌ |

**Settings Managed:**
- AI processing enabled/disabled
- Force human review requirement
- Expert auto-assignment vs manual
- Originality check required
- Email/SMS notifications enabled
- Platform maintenance mode
- Max question length
- Min confidence score
- AI content threshold

**Backend Logic Required:**
- Setting validation
- Change notifications to admins
- Maintenance mode enforcement
- Setting history tracking

---

### **5. QUESTION OVERSIGHT & MANUAL OVERRIDE** (8 Features)
**Total Endpoints**: 8  
**Purpose**: Complete visibility and control over question pipeline

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 5.1 | List Questions | `GET /admin/questions` | ✅ | ✅ |
| 5.2 | Question Details | `GET /admin/questions/{id}` | ✅ | ✅ |
| 5.3 | Reassign Expert | `POST /admin/questions/{id}/reassign-expert` | ✅ | ✅ |
| 5.4 | Force Deliver | `POST /admin/questions/{id}/force-deliver` | ✅ | ✅ |
| 5.5 | Reject & Correct | `POST /admin/questions/{id}/reject-and-correct` | ✅ | ✅ |
| 5.6 | Flag Plagiarism | `POST /admin/questions/{id}/flag-plagiarism` | ✅ | ✅ |
| 5.7 | Escalate Question | `POST /admin/questions/{id}/escalate` | ✅ | ❌ |
| 5.8 | Question Statistics | `GET /admin/questions/stats` | ✅ | ✅ |

**Backend Logic Required:**
- Expert reassignment with notifications
- Force deliver bypassing all checks
- Admin correction upload system
- Plagiarism flagging with fine calculation
- Pipeline state machine validation
- Complete question history tracking

---

### **6. EXPERT PERFORMANCE DASHBOARD** (8 Features)
**Total Endpoints**: 8  
**Purpose**: Monitor and manage expert performance

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 6.1 | List Experts | `GET /admin/experts` | ✅ | ✅ |
| 6.2 | Expert Details | `GET /admin/experts/{id}` | ✅ | ✅ |
| 6.3 | Expert Statistics | `GET /admin/experts/stats` | ✅ | ✅ |
| 6.4 | Performance Metrics | `GET /admin/experts/{id}/performance` | ✅ | ✅ |
| 6.5 | Suspend Expert | `POST /admin/experts/{id}/suspend` | ✅ | ❌ |
| 6.6 | Activate Expert | `POST /admin/experts/{id}/activate` | ✅ | ✅ |
| 6.7 | Review History | `GET /admin/experts/{id}/reviews` | ✅ | ✅ |
| 6.8 | Leaderboard | `GET /admin/experts/leaderboard` | ✅ | ✅ |

**Metrics Tracked:**
- Total questions answered
- Average rating
- Response time (avg, median)
- Rejection rate
- On-time delivery rate
- Total earnings
- Active questions count
- Compliance score

**Backend Logic Required:**
- Real-time performance calculation
- Leaderboard ranking (cached)
- Expert suspension with question reassignment
- Performance alert system

---

### **7. COMPLIANCE & AUDIT LOGS** (7 Features)
**Total Endpoints**: 7  
**Purpose**: Full transparency and compliance tracking

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 7.1 | Audit Logs | `GET /admin/audit-logs` | ✅ | ✅ |
| 7.2 | Log Details | `GET /admin/audit-logs/{id}` | ✅ | ✅ |
| 7.3 | Flagged Content | `GET /admin/compliance/flagged` | ✅ | ✅ |
| 7.4 | User Compliance | `GET /admin/compliance/users/{id}` | ✅ | ✅ |
| 7.5 | Flag Content | `POST /admin/compliance/flag/{id}` | ✅ | ✅ |
| 7.6 | Compliance Stats | `GET /admin/compliance/stats` | ✅ | ✅ |
| 7.7 | Export Logs | `POST /admin/audit-logs/export` | ✅ | ✅ |

**Compliance Checks:**
- AI content detection (>10% threshold)
- Plagiarism detection (Turnitin)
- VPN usage detection
- Suspicious activity patterns
- Rate limit violations
- Multiple account detection

**Backend Logic Required:**
- Real-time compliance checking
- Automated flagging system
- Compliance scoring algorithm
- Export formatting (CSV, JSON)
- Log retention policy (90 days)

---

### **8. BROADCAST NOTIFICATIONS** (5 Features)
**Total Endpoints**: 5  
**Purpose**: Communicate with all or segments of users

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 8.1 | Broadcast All | `POST /admin/notifications/broadcast` | ✅ | ✅ |
| 8.2 | Broadcast Segment | `POST /admin/notifications/broadcast-segment` | ✅ | ✅ |
| 8.3 | List Templates | `GET /admin/notifications/templates` | ✅ | ✅ |
| 8.4 | Create Template | `POST /admin/notifications/templates` | ✅ | ❌ |
| 8.5 | Broadcast History | `GET /admin/notifications/history` | ✅ | ✅ |

**Segmentation Options:**
- By role (client, expert, admin)
- By status (active, banned, verified)
- By registration date
- By activity level
- Custom query filters

**Backend Logic Required:**
- Template variable substitution
- Queue-based sending (RabbitMQ)
- Delivery tracking
- Failure handling with retry
- Rate limiting to prevent spam

---

### **9. FINANCIAL & REVENUE CONTROL** (6 Features)
**Total Endpoints**: 6  
**Purpose**: Revenue tracking and credit management

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 9.1 | Revenue Dashboard | `GET /admin/revenue/dashboard` | ✅ | ✅ View |
| 9.2 | Credits Statistics | `GET /admin/revenue/credits` | ✅ | ✅ View |
| 9.3 | All Transactions | `GET /admin/revenue/transactions` | ✅ | ✅ View |
| 9.4 | Grant Credits | `POST /admin/credits/grant` | ✅ | ❌ |
| 9.5 | Revoke Credits | `POST /admin/credits/revoke` | ✅ | ❌ |
| 9.6 | Export Revenue | `GET /admin/revenue/export` | ✅ | ✅ View |

**Metrics Tracked:**
- Daily/weekly/monthly revenue
- Credits sold (by package)
- Average transaction value
- Refund rate
- Top spending users
- Revenue trends

**Backend Logic Required:**
- Credit grant with reason logging
- Credit revocation with refund logic
- Real-time revenue calculation
- Transaction reconciliation

---

### **10. BACKEND LOGIC OVERRIDE TRIGGERS** (5 Features)
**Total Endpoints**: 5  
**Purpose**: God mode - bypass automated logic (Super Admin Only)

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 10.1 | AI Bypass | `POST /admin/override/ai-bypass/{id}` | ✅ | ❌ |
| 10.2 | Originality Pass | `POST /admin/override/originality-pass/{id}` | ✅ | ❌ |
| 10.3 | Confidence Override | `POST /admin/override/confidence-override/{id}` | ✅ | ❌ |
| 10.4 | Humanization Skip | `POST /admin/override/humanization-skip/{id}` | ✅ | ❌ |
| 10.5 | Expert Bypass | `POST /admin/override/expert-bypass/{id}` | ✅ | ❌ |

**Backend Logic Required:**
- Override validation (check applicability)
- State machine bypass
- Critical audit logging
- Admin notification alerts
- Rollback capability

---

### **11. WORKER & QUEUE CONTROL** (6 Features)
**Total Endpoints**: 6  
**Purpose**: Monitor and control background workers

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 11.1 | Queue Status | `GET /admin/queues/status` | ✅ | ✅ |
| 11.2 | Queue Details | `GET /admin/queues/{name}/status` | ✅ | ✅ |
| 11.3 | Pause AI Processing | `POST /admin/queues/pause-ai` | ✅ | ❌ |
| 11.4 | Resume AI Processing | `POST /admin/queues/resume-ai` | ✅ | ❌ |
| 11.5 | Purge Queue | `POST /admin/queues/purge/{name}` | ✅ | ❌ |
| 11.6 | Queue Statistics | `GET /admin/queues/stats` | ✅ | ✅ |

**Queues Monitored:**
- `ai_processing` - AI question processing
- `humanization` - Text humanization
- `originality_check` - Plagiarism checks
- `expert_review` - Expert review queue
- `notifications` - Notification delivery
- `email` - Email sending
- `sms` - SMS sending

**Backend Logic Required:**
- Queue length monitoring
- Worker health checks
- Pause/resume state management
- Queue purging with confirmation
- Dead letter queue handling

---

### **12. BACKUP & DISASTER RECOVERY** (4 Features)
**Total Endpoints**: 4  
**Purpose**: Data protection and recovery (Super Admin Only)

| # | Feature | Endpoint | Super Admin | Admin/Editor |
|---|---------|----------|-------------|--------------|
| 12.1 | Trigger Backup | `POST /admin/backup/now` | ✅ | ❌ |
| 12.2 | List Backups | `GET /admin/backup/list` | ✅ | ❌ |
| 12.3 | Restore Backup | `POST /admin/backup/restore/{id}` | ✅ | ❌ |
| 12.4 | Backup Status | `GET /admin/backup/status` | ✅ | ❌ |

**Backend Logic Required:**
- Database snapshot (pg_dump)
- Backup storage (S3/local)
- Backup rotation (keep last 30)
- Restore validation
- Maintenance mode during restore

---

## 🔄 AUTOMATIC BACKEND CHECKS

These features run automatically but can be monitored/overridden by admins:

### **1. AI Content Detection**
- **Automatic**: Check every answer for AI content
- **Threshold**: >10% AI content = flag
- **Admin Override**: Force pass originality check

### **2. Plagiarism Detection**
- **Automatic**: Turnitin check on all answers
- **Threshold**: <90% uniqueness = flag
- **Admin Override**: Force pass plagiarism check

### **3. VPN Detection**
- **Automatic**: Check user IP against VPN databases
- **Action**: Flag account, require verification
- **Admin Override**: Whitelist IP/user

### **4. Rate Limiting**
- **Automatic**: Limit requests per user/IP
- **Thresholds**: Configurable per endpoint
- **Admin Override**: Bypass rate limit

### **5. Expert Assignment**
- **Automatic**: Auto-assign based on subject, availability
- **Logic**: Round-robin, load balancing
- **Admin Override**: Manual assignment

### **6. Confidence Score Validation**
- **Automatic**: Reject AI answers with low confidence
- **Threshold**: <70% confidence = reject
- **Admin Override**: Accept low confidence answer

### **7. Humanization Check**
- **Automatic**: Humanize all AI responses
- **Service**: Stealth API
- **Admin Override**: Skip humanization

### **8. Expert Review Requirement**
- **Automatic**: Require expert review for all answers
- **Logic**: Configurable (always/never/conditional)
- **Admin Override**: Skip expert review

---

## 📊 Feature Summary

| Category | Features | Endpoints | Super Admin | Admin/Editor |
|----------|----------|-----------|-------------|--------------|
| User Management | 7 | 7 | ✅ Full | ✅ View |
| Admin Management | 4 | 4 | ✅ Full | ✅ View |
| API Keys | 6 | 6 | ✅ Full | ✅ View |
| System Settings | 5 | 5 | ✅ Full | ✅ View |
| Question Oversight | 8 | 8 | ✅ Full | ✅ Full |
| Expert Management | 8 | 8 | ✅ Full | ✅ Limited |
| Compliance | 7 | 7 | ✅ Full | ✅ Full |
| Notifications | 5 | 5 | ✅ Full | ✅ Full |
| Revenue | 6 | 6 | ✅ Full | ✅ View |
| Override Triggers | 5 | 5 | ✅ Full | ❌ None |
| Queue Control | 6 | 6 | ✅ Full | ✅ View |
| Backup/Recovery | 4 | 4 | ✅ Full | ❌ None |
| **TOTAL** | **71** | **71** | **100%** | **~70%** |

---

## ✅ Implementation Status

### Completed ✅
- [x] Admin specification document
- [x] Feature breakdown document
- [x] User model extended
- [x] Admin models created
- [x] Admin dependencies created

### Next Steps
1. Create database migrations
2. Create admin schemas
3. Create admin CRUD operations
4. Create admin services
5. Create admin API routes
6. Test all endpoints

---

**Total Features**: 71 endpoints + 8 automatic checks = **79 features**  
**Estimated Implementation**: 3-4 weeks  
**Current Progress**: Foundation Complete (20%)

