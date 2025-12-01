# Admin Backend - Complete Specification

## 🎯 Two-Tier Admin System

### Role Hierarchy

| Role | Description | Access Level | Can Create Admins? |
|------|-------------|--------------|-------------------|
| **super_admin** | Owner - Full God Mode | 100% | Yes |
| **admin_editor** | Supervisor - Monitor & Intervene | 70% | No |
| **expert** | Academic Expert | 30% | No |
| **client** | Student/User | 10% | No |

---

## 📋 Complete Feature Matrix

### 1. User & Role Management
**Endpoints:**
- `GET /api/v1/admin/users` - List all users (filterable)
- `GET /api/v1/admin/users/{id}` - Get user details
- `POST /api/v1/admin/users/{id}/role` - Change user role (super_admin only)
- `POST /api/v1/admin/users/{id}/ban` - Ban/unban user
- `POST /api/v1/admin/users/{id}/reset-password` - Reset user password
- `POST /api/v1/admin/users/{id}/promote-to-expert` - Promote client to expert
- `GET /api/v1/admin/users/stats` - User statistics

**Permissions:**
- Super Admin: Full access
- Admin/Editor: View only

---

### 2. Admin Management
**Endpoints:**
- `POST /api/v1/admin/invite-admin` - Invite new admin/editor (super_admin only)
- `GET /api/v1/admin/admins` - List all admins
- `POST /api/v1/admin/admins/{id}/suspend` - Suspend admin (super_admin only)
- `POST /api/v1/admin/admins/{id}/revoke` - Revoke admin access (super_admin only)

**Permissions:**
- Super Admin: Full access
- Admin/Editor: View only

---

### 3. API Keys Management
**Endpoints:**
- `GET /api/v1/admin/api-keys` - List all API keys
- `POST /api/v1/admin/api-keys` - Add new API key (super_admin only)
- `PATCH /api/v1/admin/api-keys/{id}` - Update API key (super_admin only)
- `DELETE /api/v1/admin/api-keys/{id}` - Delete API key (super_admin only)
- `POST /api/v1/admin/api-keys/{id}/test` - Test API key connection
- `POST /api/v1/admin/api-keys/{id}/rotate` - Rotate API key (super_admin only)

**Permissions:**
- Super Admin: Full CRUD
- Admin/Editor: Read-only

---

### 4. System Settings & Toggles
**Endpoints:**
- `GET /api/v1/admin/settings` - Get all system settings
- `PATCH /api/v1/admin/settings` - Update settings (super_admin only)
- `POST /api/v1/admin/settings/{key}/toggle` - Toggle specific setting (super_admin only)
- `GET /api/v1/admin/settings/maintenance-mode` - Check maintenance mode
- `POST /api/v1/admin/settings/maintenance-mode` - Enable/disable maintenance (super_admin only)

**Settings Include:**
- AI processing enabled/disabled
- Force human review
- Expert assignment auto/manual
- Originality check required
- Email notifications enabled
- SMS notifications enabled
- Platform maintenance mode

**Permissions:**
- Super Admin: Full control
- Admin/Editor: Read-only

---

### 5. Question Oversight & Manual Override
**Endpoints:**
- `GET /api/v1/admin/questions` - List all questions (filterable by status, subject, date)
- `GET /api/v1/admin/questions/{id}` - Get question details with full pipeline
- `POST /api/v1/admin/questions/{id}/reassign-expert` - Reassign to different expert
- `POST /api/v1/admin/questions/{id}/force-deliver` - Bypass review → deliver immediately
- `POST /api/v1/admin/questions/{id}/reject-and-correct` - Reject and upload admin correction
- `POST /api/v1/admin/questions/{id}/flag-plagiarism` - Flag as plagiarism + fine client
- `POST /api/v1/admin/questions/{id}/escalate` - Escalate to super admin
- `GET /api/v1/admin/questions/stats` - Question statistics

**Permissions:**
- Super Admin: Full access
- Admin/Editor: Full access (except escalate)

---

### 6. Expert Performance Dashboard
**Endpoints:**
- `GET /api/v1/admin/experts` - List all experts
- `GET /api/v1/admin/experts/{id}` - Get expert details
- `GET /api/v1/admin/experts/stats` - Expert statistics & leaderboard
- `GET /api/v1/admin/experts/{id}/performance` - Expert performance metrics
- `POST /api/v1/admin/experts/{id}/suspend` - Suspend expert (super_admin only)
- `POST /api/v1/admin/experts/{id}/activate` - Activate expert
- `GET /api/v1/admin/experts/{id}/reviews` - Expert review history
- `GET /api/v1/admin/experts/leaderboard` - Expert leaderboard

**Permissions:**
- Super Admin: Full access
- Admin/Editor: View + activate (cannot suspend)

---

### 7. Compliance & Audit Logs
**Endpoints:**
- `GET /api/v1/admin/audit-logs` - Get audit logs (searchable, filterable)
- `GET /api/v1/admin/audit-logs/{id}` - Get specific audit log
- `GET /api/v1/admin/compliance/flagged` - Get flagged content (AI >10%, plagiarism, VPN)
- `GET /api/v1/admin/compliance/users/{id}` - Get user compliance history
- `POST /api/v1/admin/compliance/flag/{id}` - Manually flag content
- `GET /api/v1/admin/compliance/stats` - Compliance statistics
- `POST /api/v1/admin/audit-logs/export` - Export audit logs

**Permissions:**
- Super Admin: Full access
- Admin/Editor: Full access

---

### 8. Broadcast Notifications
**Endpoints:**
- `POST /api/v1/admin/notifications/broadcast` - Broadcast to all users
- `POST /api/v1/admin/notifications/broadcast-segment` - Broadcast to segment (role, status)
- `GET /api/v1/admin/notifications/templates` - Get notification templates
- `POST /api/v1/admin/notifications/templates` - Create template (super_admin only)
- `GET /api/v1/admin/notifications/history` - Broadcast history

**Permissions:**
- Super Admin: Full access
- Admin/Editor: Full access

---

### 9. Financial & Revenue Control
**Endpoints:**
- `GET /api/v1/admin/revenue/dashboard` - Revenue dashboard
- `GET /api/v1/admin/revenue/credits` - Credits sold statistics
- `GET /api/v1/admin/revenue/transactions` - All transactions
- `POST /api/v1/admin/credits/grant` - Grant free credits (super_admin only)
- `POST /api/v1/admin/credits/revoke` - Revoke credits (super_admin only)
- `GET /api/v1/admin/revenue/export` - Export revenue data

**Permissions:**
- Super Admin: Full access
- Admin/Editor: Read-only

---

### 10. Backend Logic Override Triggers (God Mode)
**Endpoints:**
- `POST /api/v1/admin/override/ai-bypass/{question_id}` - Skip AI → go to expert (super_admin only)
- `POST /api/v1/admin/override/originality-pass/{id}` - Force pass Turnitin (super_admin only)
- `POST /api/v1/admin/override/confidence-override/{id}` - Accept low-confidence AI (super_admin only)
- `POST /api/v1/admin/override/humanization-skip/{id}` - Skip humanization (super_admin only)
- `POST /api/v1/admin/override/expert-bypass/{id}` - Skip expert review (super_admin only)

**Permissions:**
- Super Admin: Full access
- Admin/Editor: No access

---

### 11. Worker & Queue Control
**Endpoints:**
- `GET /api/v1/admin/queues/status` - Get queue status (all queues)
- `GET /api/v1/admin/queues/{queue_name}/status` - Get specific queue status
- `POST /api/v1/admin/queues/pause-ai` - Pause AI processing (super_admin only)
- `POST /api/v1/admin/queues/resume-ai` - Resume AI processing (super_admin only)
- `POST /api/v1/admin/queues/purge/{queue_name}` - Purge queue (super_admin only)
- `GET /api/v1/admin/queues/stats` - Queue statistics

**Permissions:**
- Super Admin: Full control
- Admin/Editor: Read-only

---

### 12. Backup & Disaster Recovery
**Endpoints:**
- `POST /api/v1/admin/backup/now` - Trigger database backup (super_admin only)
- `GET /api/v1/admin/backup/list` - List backups (super_admin only)
- `POST /api/v1/admin/backup/restore/{backup_id}` - Restore from backup (super_admin only)
- `GET /api/v1/admin/backup/status` - Backup status

**Permissions:**
- Super Admin: Full access
- Admin/Editor: No access

---

## 🗄️ Database Schema Additions

### User Model Extensions
```sql
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'client' CHECK (role IN ('client', 'expert', 'admin_editor', 'super_admin'));
ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN banned_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN banned_by UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN invited_by UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN last_active TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
```

### Admin Actions Table
```sql
CREATE TABLE admin_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES users(id),
    action_type TEXT NOT NULL,
    target_type TEXT,  -- 'question', 'user', 'expert', 'system'
    target_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX idx_admin_actions_action_type ON admin_actions(action_type);
CREATE INDEX idx_admin_actions_target ON admin_actions(target_type, target_id);
CREATE INDEX idx_admin_actions_created_at ON admin_actions(created_at);
```

### API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    key_type TEXT NOT NULL,  -- 'openai', 'anthropic', 'turnitin', etc.
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_tested_at TIMESTAMPTZ,
    last_tested_status TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_key_type ON api_keys(key_type);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

### System Settings Table
```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_settings_key ON system_settings(key);
```

### Notification Templates Table
```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    template_type TEXT,  -- 'email', 'sms', 'push'
    variables JSONB,  -- Available variables
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔐 Security & Permissions

### JWT Claims
```json
{
  "sub": "user_id",
  "user_id": "user_id",
  "email": "admin@example.com",
  "role": "super_admin" | "admin_editor" | "expert" | "client",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Dependency Functions
- `require_super_admin()` - Only super_admin
- `require_admin_or_super()` - admin_editor or super_admin
- `get_current_admin()` - Get current admin user
- `log_admin_action()` - Log all admin actions

---

## 📦 Implementation Structure

```
src/app/
├── api/v1/admin/
│   ├── __init__.py
│   ├── users.py          # User management
│   ├── admins.py         # Admin management
│   ├── api_keys.py       # API keys
│   ├── settings.py       # System settings
│   ├── questions.py      # Question oversight
│   ├── experts.py        # Expert management
│   ├── compliance.py     # Compliance & audit
│   ├── notifications.py  # Broadcast
│   ├── revenue.py        # Financial
│   ├── override.py       # Override triggers
│   ├── queues.py         # Queue control
│   └── backup.py         # Backup & recovery
├── models/
│   ├── admin_action.py
│   ├── api_key.py
│   ├── system_setting.py
│   └── notification_template.py
├── schemas/admin/
│   ├── user.py
│   ├── question.py
│   ├── expert.py
│   └── ...
├── crud/admin/
│   ├── users.py
│   ├── questions.py
│   └── ...
└── services/admin/
    ├── user_service.py
    ├── question_service.py
    └── ...
```

---

## ✅ Implementation Checklist

- [ ] Database migrations for admin system
- [ ] User model extensions
- [ ] Admin models (admin_actions, api_keys, settings, templates)
- [ ] Admin schemas (Pydantic)
- [ ] Admin CRUD operations
- [ ] Admin services (business logic)
- [ ] Authentication dependencies (role-based)
- [ ] All admin API routes
- [ ] Admin action logging
- [ ] Permission enforcement
- [ ] Tests for admin endpoints

---

**Total Estimated Implementation**: 3-4 weeks for production-ready admin backend

