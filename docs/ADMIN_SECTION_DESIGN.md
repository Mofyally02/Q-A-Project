# Admin Section Design - AL-Tech Academy Q&A System

## Overview

The admin section is the **engine** of the platform, providing the superadmin with complete control over system operations, user management, configurations, and analytics. It integrates AI agents with human approval workflows, ensuring compliance, quality, and security.

## Access Control

### Login Trigger
- Admin login via `/auth/login` with `admin@demo.com` / `demo123`
- JWT token contains `role: "admin"`
- Frontend decodes JWT and redirects to `/admin/dashboard`
- All `/admin/*` routes protected by `admin_required` dependency

### Security
- All admin APIs require JWT with `role=admin`
- Actions logged in `audit_logs` table
- VPN detection (optional)
- Session management with refresh tokens

## Admin Dashboard Structure

### Layout
```
┌─────────────────────────────────────────────────────┐
│ Header: Logo | Search | Notifications | Logout      │
├─────────┬───────────────────────────────────────────┤
│ Sidebar │                                           │
│         │         Main Content Area                 │
│ - Dashboard                                         │
│ - API Keys                (Component)               │
│ - Users & Experts                                   │
│ - Notifications                                    │
│ - Analytics & Reports                              │
│ - Compliance                                       │
│ - Settings                                         │
└─────────┴───────────────────────────────────────────┘
```

## Feature Breakdown

### 1. Dashboard Overview (`/admin/dashboard`)

**Purpose**: Real-time system health and activity summary

**Features**:
- **Stats Cards**:
  - Total Questions: Count from `questions` table
  - Pending Reviews: Questions with `status='pending'`
  - Average Rating: AVG from `ratings` table
  - Active Users: Count active clients + experts
  - System Health: API status, queue depth, error rate
  
- **Charts**:
  - Questions per Day (line chart)
  - Top Subjects (pie chart)
  - Expert Performance (bar chart with avg ratings)
  - AI Confidence Distribution (histogram)
  
- **Recent Activity Feed**:
  - Latest question submissions
  - Recent expert approvals/rejections
  - Client feedback/ratings
  - System alerts
  
- **Quick Actions**:
  - Add New Expert
  - Send Notification
  - Manage API Keys
  - Generate Report
  
- **AI-Human Workflow Metrics**:
  - AI confidence score averages
  - Humanization success rate
  - Expert override frequency
  - Compliance violations (>10% AI content)

**Backend API**: `GET /admin/dashboard`

**Frontend Components**: 
- `DashboardOverview.vue` - Main container
- `StatCard.vue` - Reusable stat display
- `ActivityFeed.vue` - Recent activities list

---

### 2. API Key Management (`/admin/api-keys`)

**Purpose**: Configure and manage API keys used by the platform

**Features**:
- **API Providers**:
  - OpenAI (GPT-4, GPT-3.5)
  - Google (Gemini)
  - Anthropic (Claude)
  - xAI (Grok)
  - Stealth (AI detection bypass)
  - Turnitin (Plagiarism detection)
  - Poe API (Various models)
  
- **Key Actions**:
  - Add/Update API keys
  - Mask keys for security (show only last 4 chars)
  - Test connectivity to each API
  - Set usage limits/quotas
  - View usage statistics
  
- **Validation**:
  - Test button for each provider
  - Mock API call to verify validity
  - Automatic retry on failure
  
- **Audit Trail**:
  - History of key changes
  - Who changed what and when
  - IP address logging

**Backend API**: 
- `GET /admin/api-keys` - List all keys (masked)
- `POST /admin/api-keys` - Add/update key
- `POST /admin/api-keys/test/{provider}` - Test API connection
- `DELETE /admin/api-keys/{provider}` - Remove key

**Frontend Components**:
- `APIKeysManager.vue` - Main container
- `APIKeyForm.vue` - Add/edit form
- `APIKeyCard.vue` - Individual provider card

---

### 3. User Management (`/admin/users`)

**Purpose**: Manage all users, manually add experts, assign roles

**Features**:
- **User List View**:
  - Searchable table: ID, Email, Role, Status, Join Date, Last Login
  - Filters: Role, Status, Date Range
  - Pagination (50 users per page)
  - Sortable columns
  
- **Add Expert**:
  - Modal form to add expert manually
  - Search existing users or create new
  - Assign 'expert' role automatically
  - Set specialization and experience level
  - Send welcome email
  
- **Role Management**:
  - Promote client to expert
  - Demote expert to client
  - Cannot create another admin (security)
  - Bulk role updates
  
- **User Actions**:
  - Activate/deactivate users
  - Reset password
  - View user details (questions, ratings, history)
  - Export user list (CSV/PDF)
  
- **Expert Performance Dashboard**:
  - Per-expert metrics
  - Total reviews completed
  - Average rating received
  - Rejection rate
  - Average review time
  
- **Client Analytics**:
  - Query history
  - Feedback summary
  - Churn risk score
  - Subscription status

**Backend API**:
- `GET /admin/users` - List all users (paginated, filtered)
- `POST /admin/users/expert` - Add new expert
- `POST /admin/users/{user_id}/role` - Change user role
- `POST /admin/users/{user_id}/status` - Activate/deactivate
- `GET /admin/users/{user_id}/details` - User details

**Frontend Components**:
- `UsersManager.vue` - Main container
- `UserTable.vue` - Searchable table
- `AddExpertModal.vue` - Expert creation form
- `UserDetailsModal.vue` - User info view

---

### 4. Notifications Management (`/admin/notifications`)

**Purpose**: Send custom notifications to clients, experts, or groups

**Features**:
- **Compose Notification**:
  - Recipient selection:
    - All clients
    - All experts
    - Specific user
    - Custom group
  - Notification type:
    - Email
    - In-app notification
    - Push notification (if mobile app)
    - WebSocket (real-time)
  
- **Content Editor**:
  - Rich text editor (WYSIWYG)
  - Subject line
  - Body content
  - Attachments (optional)
  
- **Templates**:
  - Pre-built templates for common scenarios:
    - "New Question Assigned" (to experts)
    - "Feedback Requested" (to clients)
    - "Welcome to Platform" (new users)
    - "System Maintenance Notice"
  
- **Scheduling**:
  - Send immediately
  - Schedule for later
  - Recurring notifications
  
- **History & Analytics**:
  - List of sent notifications
  - Open rates (for emails)
  - Read rates (for in-app)
  - Click-through rates
  
- **Bulk Operations**:
  - Send to multiple users
  - A/B testing
  - Campaign management

**Backend API**:
- `POST /admin/notifications/send` - Send notification
- `GET /admin/notifications/history` - Notification history
- `GET /admin/notifications/templates` - Get templates
- `POST /admin/notifications/schedule` - Schedule notification

**Frontend Components**:
- `NotificationsManager.vue` - Main container
- `ComposeNotification.vue` - Editor form
- `NotificationHistory.vue` - History table
- `TemplateSelector.vue` - Template picker

---

### 5. Analytics & Reports (`/admin/analytics`)

**Purpose**: Comprehensive system analytics, questions tracking, expert performance, feedback analysis

**Features**:
- **Dashboard Overview**:
  - Total questions submitted (all time, this month, today)
  - Questions by status (pending, in-review, approved, rejected)
  - Average processing time
  - Client satisfaction score (NPS)
  
- **Questions Log**:
  - Searchable table of ALL questions
  - Columns: ID, Client, Content (truncated), Status, AI Response, Expert Review, Feedback
  - Filters: Date range, status, subject, expert
  - Export to CSV/PDF
  
- **Expert Performance**:
  - Per-expert breakdown:
    - Total reviews
    - Approval rate
    - Average rating received
    - Average review time
    - Rejection reasons
  - Top performers
  - Underperformers (flag for review)
  
- **Client Feedback Analysis**:
  - Rating distribution (1-5 stars)
  - Comments/feedback summaries
  - NPS (Net Promoter Score)
  - Churn risk prediction
  - Client retention metrics
  
- **AI-Human Workflow Analytics**:
  - AI confidence score distribution
  - Humanization success rate
  - Expert override frequency
  - Average AI response time
  - AI vs Human quality comparison
  
- **Reports Generation**:
  - Daily/Weekly/Monthly reports
  - Compliance report (AI detection, plagiarism)
  - Financial report (if monetized)
  - Workflow efficiency report
  - Expert performance report
  
- **Charts & Visualizations**:
  - Questions over time (line chart)
  - Subject distribution (pie chart)
  - Expert performance (bar chart)
  - Rating trends (area chart)
  - AI confidence distribution (histogram)

**Backend API**:
- `GET /admin/analytics/overview` - Summary stats
- `GET /admin/analytics/questions` - Filtered questions list
- `GET /admin/analytics/experts` - Expert performance data
- `GET /admin/analytics/feedback` - Client feedback stats
- `GET /admin/analytics/reports/{type}` - Generate report

**Frontend Components**:
- `AnalyticsDashboard.vue` - Main container
- `QuestionsLog.vue` - Questions table
- `ExpertPerformance.vue` - Expert metrics
- `FeedbackAnalysis.vue` - Client feedback
- `ReportGenerator.vue` - Report builder

---

### 6. Compliance & Oversight (`/admin/compliance`)

**Purpose**: Monitor platform integrity, audit logs, flagged content

**Features**:
- **Audit Logs Viewer**:
  - Searchable/filterable table
  - Columns: Timestamp, User, Action, Resource, Details
  - Filters: Date range, user, action type
  - Export logs
  
- **Flagged Content**:
  - High AI content (>10% threshold)
  - Plagiarism violations
  - Rejected questions
  - Manual review queue
  
- **System Health**:
  - API key status (active/expired)
  - Queue depth (RabbitMQ)
  - Cache hit rate (Redis)
  - Database performance
  - Error rate alerts
  
- **Content Management**:
  - Review flagged content
  - Override AI detections
  - Ban/unban users
  - Enforce platform policies
  
- **Backup & Recovery**:
  - Database backup status
  - Restore from backup
  - Export data snapshots
  
- **Security Monitoring**:
  - Failed login attempts
  - Suspicious activity
  - IP address tracking
  - VPN detection alerts

**Backend API**:
- `GET /admin/compliance/logs` - Audit logs
- `GET /admin/compliance/flagged` - Flagged content
- `POST /admin/compliance/review/{content_id}` - Manual review
- `POST /admin/compliance/ban/{user_id}` - Ban user
- `GET /admin/compliance/health` - System health

**Frontend Components**:
- `ComplianceDashboard.vue` - Main container
- `AuditLogs.vue` - Logs table
- `FlaggedContent.vue` - Content review
- `SystemHealth.vue` - Health metrics

---

### 7. Settings (`/admin/settings`)

**Purpose**: Platform-wide settings and configuration

**Features**:
- **General Settings**:
  - Platform name, logo
  - Default language
  - Timezone
  - Date format
  
- **AI Configuration**:
  - Default AI model (GPT-4, Claude, etc.)
  - Confidence threshold
  - Humanization settings
  - AI content limit (10%)
  - Uniqueness threshold (90%)
  
- **Workflow Settings**:
  - Auto-assignment rules
  - Review queue management
  - Notification preferences
  - Delivery settings
  
- **Security Settings**:
  - Password policy
  - Session timeout
  - 2FA requirements
  - IP whitelist
  
- **Integration Settings**:
  - SMTP configuration
  - Payment gateway (if monetized)
  - Third-party integrations

**Backend API**:
- `GET /admin/settings` - Get all settings
- `PUT /admin/settings/{category}` - Update settings

**Frontend Components**:
- `SettingsPanel.vue` - Main container
- `SettingsForm.vue` - Settings editor

---

## Implementation Priority

### Phase 1 (MVP) - Week 1-2
1. Dashboard Overview
2. User Management (basic)
3. API Key Management

### Phase 2 - Week 3-4
4. Notifications Management
5. Basic Analytics

### Phase 3 - Week 5-6
6. Advanced Analytics & Reports
7. Compliance & Oversight

### Phase 4 - Week 7-8
8. Settings Panel
9. Advanced Features (A/B testing, campaigns)

---

## Technical Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (qa_auth, qa_system)
- **Cache**: Redis
- **Queue**: RabbitMQ
- **APIs**: REST + WebSockets

### Frontend
- **Framework**: Nuxt 3
- **UI**: Tailwind CSS + Headless UI
- **Charts**: Chart.js / Recharts
- **Tables**: TanStack Table
- **Forms**: VeeValidate

---

## Security Considerations

1. **Authentication**: JWT with role validation
2. **Authorization**: All endpoints require admin role
3. **Audit Logging**: All actions logged
4. **API Key Encryption**: AES-256 encryption
5. **Rate Limiting**: Prevent abuse
6. **Input Validation**: Sanitize all inputs
7. **CORS**: Restrict to approved domains

---

## Next Steps

1. ✅ Design document complete
2. 🔲 Implement backend APIs
3. 🔲 Build frontend components
4. 🔲 Integrate authentication
5. 🔲 Add WebSocket real-time updates
6. 🔲 Testing & QA
7. 🔲 Deployment

---

**Status**: Design Complete - Ready for Implementation
**Date**: October 27, 2024
**Version**: 1.0

