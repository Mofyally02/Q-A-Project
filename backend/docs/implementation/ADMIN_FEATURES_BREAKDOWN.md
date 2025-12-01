# Admin Backend - Complete Feature Breakdown

## 🎯 Overview

This document breaks down **every single feature** that must be incorporated into the admin backend to ensure smooth, all-rounded platform operation.

---

## 📊 Feature Categories

### 1. **User & Role Management** (7 endpoints)
**Purpose**: Complete control over all platform users

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| List Users | `GET /admin/users` | ✅ | ✅ View | Filter by role, status, date, search |
| User Details | `GET /admin/users/{id}` | ✅ | ✅ View | Full user profile + activity |
| Change Role | `POST /admin/users/{id}/role` | ✅ | ❌ | Promote/demote users |
| Ban/Unban User | `POST /admin/users/{id}/ban` | ✅ | ✅ | Immediate ban with reason |
| Reset Password | `POST /admin/users/{id}/reset-password` | ✅ | ✅ | Generate temp password |
| Promote to Expert | `POST /admin/users/{id}/promote-to-expert` | ✅ | ✅ | Convert client → expert |
| User Statistics | `GET /admin/users/stats` | ✅ | ✅ | User metrics dashboard |

**Backend Logic:**
- Role validation (prevent invalid role changes)
- Ban cascade (cancel active questions, notify user)
- Password reset email generation
- Expert promotion workflow (verification, onboarding)

---

### 2. **Admin Management** (4 endpoints)
**Purpose**: Manage admin accounts and permissions

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Invite Admin | `POST /admin/invite-admin` | ✅ | ❌ | Generate magic link |
| List Admins | `GET /admin/admins` | ✅ | ✅ View | All admin accounts |
| Suspend Admin | `POST /admin/admins/{id}/suspend` | ✅ | ❌ | Temporarily disable |
| Revoke Admin | `POST /admin/admins/{id}/revoke` | ✅ | ❌ | Permanent removal |

**Backend Logic:**
- Magic link generation with expiration
- Email invitation with setup instructions
- Admin suspension (preserve audit trail)
- Prevent self-revocation

---

### 3. **API Keys Management** (6 endpoints)
**Purpose**: Secure management of external service API keys

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| List Keys | `GET /admin/api-keys` | ✅ | ✅ View | All API keys |
| Add Key | `POST /admin/api-keys` | ✅ | ❌ | Add new key (encrypted) |
| Update Key | `PATCH /admin/api-keys/{id}` | ✅ | ❌ | Update key value |
| Delete Key | `DELETE /admin/api-keys/{id}` | ✅ | ❌ | Remove key |
| Test Key | `POST /admin/api-keys/{id}/test` | ✅ | ✅ | Verify connection |
| Rotate Key | `POST /admin/api-keys/{id}/rotate` | ✅ | ❌ | Generate new key |

**Backend Logic:**
- Fernet encryption for storage
- Key rotation (keep old key for 24h, then delete)
- Connection testing (ping service)
- Key type validation
- Usage tracking

---

### 4. **System Settings & Toggles** (5 endpoints)
**Purpose**: Platform-wide configuration control

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Get Settings | `GET /admin/settings` | ✅ | ✅ View | All system settings |
| Update Settings | `PATCH /admin/settings` | ✅ | ❌ | Bulk update |
| Toggle Setting | `POST /admin/settings/{key}/toggle` | ✅ | ❌ | Single toggle |
| Maintenance Mode | `GET /admin/settings/maintenance-mode` | ✅ | ✅ View | Check status |
| Maintenance Mode | `POST /admin/settings/maintenance-mode` | ✅ | ❌ | Enable/disable |

**Settings Include:**
- `ai_processing_enabled` - Enable/disable AI
- `force_human_review` - Require expert review
- `expert_auto_assignment` - Auto vs manual
- `originality_check_required` - Turnitin check
- `email_notifications_enabled` - Email on/off
- `sms_notifications_enabled` - SMS on/off
- `maintenance_mode` - Platform on/off
- `max_question_length` - Character limit
- `min_confidence_score` - AI threshold
- `ai_content_threshold` - Max AI % allowed

**Backend Logic:**
- Setting validation
- Change notifications (broadcast to admins)
- Maintenance mode (reject all non-admin requests)
- Setting history (audit log)

---

### 5. **Question Oversight & Manual Override** (8 endpoints)
**Purpose**: Complete visibility and control over question pipeline

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| List Questions | `GET /admin/questions` | ✅ | ✅ | Filter by status, subject, date |
| Question Details | `GET /admin/questions/{id}` | ✅ | ✅ | Full pipeline view |
| Reassign Expert | `POST /admin/questions/{id}/reassign-expert` | ✅ | ✅ | Change expert |
| Force Deliver | `POST /admin/questions/{id}/force-deliver` | ✅ | ✅ | Bypass review |
| Reject & Correct | `POST /admin/questions/{id}/reject-and-correct` | ✅ | ✅ | Admin correction |
| Flag Plagiarism | `POST /admin/questions/{id}/flag-plagiarism` | ✅ | ✅ | Trigger fine |
| Escalate | `POST /admin/questions/{id}/escalate` | ✅ | ❌ | To super admin |
| Question Stats | `GET /admin/questions/stats` | ✅ | ✅ | Metrics dashboard |

**Backend Logic:**
- Expert reassignment (notify both experts)
- Force deliver (bypass all checks, log override)
- Admin correction (upload answer, mark as admin-answered)
- Plagiarism flag (calculate fine, notify client, log violation)
- Pipeline state machine (validate transitions)
- Question history (full audit trail)

---

### 6. **Expert Performance Dashboard** (8 endpoints)
**Purpose**: Monitor and manage expert performance

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| List Experts | `GET /admin/experts` | ✅ | ✅ | All experts |
| Expert Details | `GET /admin/experts/{id}` | ✅ | ✅ | Full profile |
| Expert Stats | `GET /admin/experts/stats` | ✅ | ✅ | Overall metrics |
| Performance | `GET /admin/experts/{id}/performance` | ✅ | ✅ | Individual metrics |
| Suspend Expert | `POST /admin/experts/{id}/suspend` | ✅ | ❌ | Disable expert |
| Activate Expert | `POST /admin/experts/{id}/activate` | ✅ | ✅ | Enable expert |
| Review History | `GET /admin/experts/{id}/reviews` | ✅ | ✅ | All reviews |
| Leaderboard | `GET /admin/experts/leaderboard` | ✅ | ✅ | Rankings |

**Metrics Tracked:**
- Total questions answered
- Average rating
- Response time (avg, median)
- Rejection rate
- On-time delivery rate
- Earnings (total, this month)
- Active questions
- Compliance score

**Backend Logic:**
- Performance calculation (real-time)
- Leaderboard ranking (cached, refresh hourly)
- Expert suspension (reassign active questions)
- Performance alerts (low rating, high rejection)

---

### 7. **Compliance & Audit Logs** (7 endpoints)
**Purpose**: Full transparency and compliance tracking

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Audit Logs | `GET /admin/audit-logs` | ✅ | ✅ | Searchable logs |
| Log Details | `GET /admin/audit-logs/{id}` | ✅ | ✅ | Single log entry |
| Flagged Content | `GET /admin/compliance/flagged` | ✅ | ✅ | AI >10%, plagiarism |
| User Compliance | `GET /admin/compliance/users/{id}` | ✅ | ✅ | User history |
| Flag Content | `POST /admin/compliance/flag/{id}` | ✅ | ✅ | Manual flag |
| Compliance Stats | `GET /admin/compliance/stats` | ✅ | ✅ | Metrics |
| Export Logs | `POST /admin/audit-logs/export` | ✅ | ✅ | CSV/JSON export |

**Compliance Checks:**
- AI content detection (>10% threshold)
- Plagiarism detection (Turnitin)
- VPN usage detection
- Suspicious activity patterns
- Rate limit violations
- Multiple account detection

**Backend Logic:**
- Real-time compliance checking
- Automated flagging
- Compliance scoring
- Export formatting (CSV, JSON)
- Log retention (90 days default)

---

### 8. **Broadcast Notifications** (5 endpoints)
**Purpose**: Communicate with all or segments of users

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Broadcast All | `POST /admin/notifications/broadcast` | ✅ | ✅ | All users |
| Broadcast Segment | `POST /admin/notifications/broadcast-segment` | ✅ | ✅ | By role/status |
| List Templates | `GET /admin/notifications/templates` | ✅ | ✅ | All templates |
| Create Template | `POST /admin/notifications/templates` | ✅ | ❌ | New template |
| Broadcast History | `GET /admin/notifications/history` | ✅ | ✅ | Past broadcasts |

**Segmentation Options:**
- By role (client, expert, admin)
- By status (active, banned, verified)
- By date (registered after X)
- By activity (active in last 30 days)
- Custom query

**Backend Logic:**
- Template variable substitution
- Queue-based sending (RabbitMQ)
- Delivery tracking
- Failure handling (retry logic)
- Rate limiting (prevent spam)

---

### 9. **Financial & Revenue Control** (6 endpoints)
**Purpose**: Revenue tracking and credit management

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Revenue Dashboard | `GET /admin/revenue/dashboard` | ✅ | ✅ View | Overview |
| Credits Stats | `GET /admin/revenue/credits` | ✅ | ✅ View | Credits sold |
| Transactions | `GET /admin/revenue/transactions` | ✅ | ✅ View | All transactions |
| Grant Credits | `POST /admin/credits/grant` | ✅ | ❌ | Free credits |
| Revoke Credits | `POST /admin/credits/revoke` | ✅ | ❌ | Remove credits |
| Export Revenue | `GET /admin/revenue/export` | ✅ | ✅ View | CSV export |

**Metrics Tracked:**
- Daily/weekly/monthly revenue
- Credits sold (total, by package)
- Average transaction value
- Refund rate
- Top spending users
- Revenue trends

**Backend Logic:**
- Credit grant (with reason, log)
- Credit revocation (refund if applicable)
- Revenue calculation (real-time)
- Transaction reconciliation

---

### 10. **Backend Logic Override Triggers** (5 endpoints)
**Purpose**: God mode - bypass automated logic

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| AI Bypass | `POST /admin/override/ai-bypass/{id}` | ✅ | ❌ | Skip AI → expert |
| Originality Pass | `POST /admin/override/originality-pass/{id}` | ✅ | ❌ | Force pass Turnitin |
| Confidence Override | `POST /admin/override/confidence-override/{id}` | ✅ | ❌ | Accept low confidence |
| Humanization Skip | `POST /admin/override/humanization-skip/{id}` | ✅ | ❌ | Skip humanization |
| Expert Bypass | `POST /admin/override/expert-bypass/{id}` | ✅ | ❌ | Skip expert review |

**Backend Logic:**
- Override validation (check if applicable)
- State machine bypass
- Override logging (critical audit)
- Notification (alert other admins)
- Rollback capability (undo override)

---

### 11. **Worker & Queue Control** (6 endpoints)
**Purpose**: Monitor and control background workers

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Queue Status | `GET /admin/queues/status` | ✅ | ✅ | All queues |
| Queue Details | `GET /admin/queues/{name}/status` | ✅ | ✅ | Specific queue |
| Pause AI | `POST /admin/queues/pause-ai` | ✅ | ❌ | Pause processing |
| Resume AI | `POST /admin/queues/resume-ai` | ✅ | ❌ | Resume processing |
| Purge Queue | `POST /admin/queues/purge/{name}` | ✅ | ❌ | Clear queue |
| Queue Stats | `GET /admin/queues/stats` | ✅ | ✅ | Metrics |

**Queues Monitored:**
- `ai_processing` - AI question processing
- `humanization` - Text humanization
- `originality_check` - Plagiarism checks
- `expert_review` - Expert review queue
- `notifications` - Notification delivery
- `email` - Email sending
- `sms` - SMS sending

**Backend Logic:**
- Queue length monitoring
- Worker health checks
- Pause/resume state management
- Queue purging (with confirmation)
- Dead letter queue handling

---

### 12. **Backup & Disaster Recovery** (4 endpoints)
**Purpose**: Data protection and recovery

| Feature | Endpoint | Super Admin | Admin/Editor | Description |
|---------|----------|-------------|--------------|-------------|
| Trigger Backup | `POST /admin/backup/now` | ✅ | ❌ | Manual backup |
| List Backups | `GET /admin/backup/list` | ✅ | ❌ | All backups |
| Restore Backup | `POST /admin/backup/restore/{id}` | ✅ | ❌ | Restore DB |
| Backup Status | `GET /admin/backup/status` | ✅ | ❌ | Current status |

**Backend Logic:**
- Database snapshot (pg_dump)
- Backup storage (S3/local)
- Backup rotation (keep last 30)
- Restore validation
- Maintenance mode during restore

---

## 🔄 Automatic Backend Checks

These are features that run automatically but can be monitored/overridden by admins:

### 1. **AI Content Detection**
- **Automatic**: Check every answer for AI content
- **Threshold**: >10% AI content = flag
- **Admin Override**: Force pass originality check

### 2. **Plagiarism Detection**
- **Automatic**: Turnitin check on all answers
- **Threshold**: <90% uniqueness = flag
- **Admin Override**: Force pass plagiarism check

### 3. **VPN Detection**
- **Automatic**: Check user IP against VPN databases
- **Action**: Flag account, require verification
- **Admin Override**: Whitelist IP/user

### 4. **Rate Limiting**
- **Automatic**: Limit requests per user/IP
- **Thresholds**: Configurable per endpoint
- **Admin Override**: Bypass rate limit

### 5. **Expert Assignment**
- **Automatic**: Auto-assign based on subject, availability
- **Logic**: Round-robin, load balancing
- **Admin Override**: Manual assignment

### 6. **Confidence Score Validation**
- **Automatic**: Reject AI answers with low confidence
- **Threshold**: <70% confidence = reject
- **Admin Override**: Accept low confidence answer

### 7. **Humanization Check**
- **Automatic**: Humanize all AI responses
- **Service**: Stealth API
- **Admin Override**: Skip humanization

### 8. **Expert Review Requirement**
- **Automatic**: Require expert review for all answers
- **Logic**: Configurable (always/never/conditional)
- **Admin Override**: Skip expert review

---

## 📋 Implementation Priority

### Phase 1: Core Admin (Week 1)
1. User & Role Management
2. Admin Management
3. Authentication & Permissions

### Phase 2: System Control (Week 2)
4. API Keys Management
5. System Settings
6. Question Oversight

### Phase 3: Monitoring (Week 3)
7. Expert Performance
8. Compliance & Audit
9. Queue Control

### Phase 4: Advanced Features (Week 4)
10. Broadcast Notifications
11. Revenue Control
12. Override Triggers
13. Backup & Recovery

---

## ✅ Total Feature Count

- **12 Feature Categories**
- **70+ API Endpoints**
- **15+ Automatic Backend Checks**
- **100% Platform Control**

---

**Status**: Ready for implementation
**Estimated Time**: 3-4 weeks for complete admin backend

