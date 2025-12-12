-- Complete Database Schema for AL-Tech Academy Q&A System
-- PostgreSQL Database Schema
-- This file creates all tables with proper relationships and indexes

-- ============================================
-- AUTHENTICATION DATABASE (qa_auth)
-- ============================================

-- Create userrole enum
DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('client', 'expert', 'admin', 'super_admin', 'admin_editor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role userrole NOT NULL DEFAULT 'client',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    last_password_change TIMESTAMP WITH TIME ZONE,
    api_key VARCHAR(255) UNIQUE,
    profile_data JSONB,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    invited_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT role_check CHECK (role IN ('client', 'expert', 'admin', 'super_admin', 'admin_editor'))
);

-- Users Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key) WHERE api_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users(is_banned) WHERE is_banned = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_invited_by ON users(invited_by) WHERE invited_by IS NOT NULL;

-- 2. Clients Table
CREATE TABLE IF NOT EXISTS clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) NOT NULL DEFAULT 'free',
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'active',
    credits_remaining INTEGER NOT NULL DEFAULT 0,
    credits_total INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT subscription_status_check CHECK (subscription_status IN ('active', 'suspended', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id);
CREATE INDEX IF NOT EXISTS idx_clients_subscription_type ON clients(subscription_type);
CREATE INDEX IF NOT EXISTS idx_clients_subscription_status ON clients(subscription_status);

-- 3. Experts Table
CREATE TABLE IF NOT EXISTS experts (
    expert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    approval_date TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(user_id),
    specialization VARCHAR(200),
    experience_years INTEGER,
    credentials JSONB,
    total_reviews INTEGER NOT NULL DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_ratings INTEGER NOT NULL DEFAULT 0,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    max_concurrent_reviews INTEGER NOT NULL DEFAULT 10,
    current_reviews INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_experts_user_id ON experts(user_id);
CREATE INDEX IF NOT EXISTS idx_experts_approved ON experts(approved);
CREATE INDEX IF NOT EXISTS idx_experts_is_available ON experts(is_available);
CREATE INDEX IF NOT EXISTS idx_experts_specialization ON experts(specialization);
CREATE INDEX IF NOT EXISTS idx_experts_average_rating ON experts(average_rating);

-- 4. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    permissions JSONB NOT NULL DEFAULT '{"all": true}',
    admin_level VARCHAR(20) NOT NULL DEFAULT 'standard',
    last_admin_action TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT admin_level_check CHECK (admin_level IN ('standard', 'super', 'readonly'))
);

CREATE INDEX IF NOT EXISTS idx_admins_user_id ON admins(user_id);
CREATE INDEX IF NOT EXISTS idx_admins_admin_level ON admins(admin_level);

-- 5. Role Change History Table
CREATE TABLE IF NOT EXISTS role_change_history (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    previous_role userrole NOT NULL,
    new_role userrole NOT NULL,
    changed_by UUID NOT NULL REFERENCES users(user_id),
    change_reason TEXT,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_role_history_user_id ON role_change_history(user_id);
CREATE INDEX IF NOT EXISTS idx_role_history_changed_by ON role_change_history(changed_by);
CREATE INDEX IF NOT EXISTS idx_role_history_changed_at ON role_change_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_role_history_new_role ON role_change_history(new_role);

-- ============================================
-- MAIN SYSTEM DATABASE (qa_system)
-- ============================================

-- 6. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    question_type VARCHAR(20) NOT NULL,
    content JSONB NOT NULL,
    subject VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'submitted',
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    word_count INTEGER,
    estimated_time INTEGER,
    assigned_expert_id UUID REFERENCES experts(expert_id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    CONSTRAINT question_type_check CHECK (question_type IN ('text', 'image', 'mixed')),
    CONSTRAINT status_check CHECK (status IN ('submitted', 'processing', 'ai_generated', 'humanized', 'expert_review', 'approved', 'delivered', 'rated', 'rejected', 'cancelled')),
    CONSTRAINT priority_check CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

CREATE INDEX IF NOT EXISTS idx_questions_client_id ON questions(client_id);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_questions_assigned_expert ON questions(assigned_expert_id);
CREATE INDEX IF NOT EXISTS idx_questions_priority ON questions(priority);
CREATE INDEX IF NOT EXISTS idx_questions_content ON questions USING GIN(content);
CREATE INDEX IF NOT EXISTS idx_questions_metadata ON questions USING GIN(metadata);

-- 7. Answers Table
CREATE TABLE IF NOT EXISTS answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL UNIQUE REFERENCES questions(question_id) ON DELETE CASCADE,
    ai_response JSONB,
    ai_model VARCHAR(100),
    ai_confidence_score DECIMAL(5,4),
    humanized_response JSONB,
    humanization_service VARCHAR(50),
    humanization_confidence DECIMAL(5,4),
    expert_response JSONB,
    expert_id UUID REFERENCES experts(expert_id),
    final_response JSONB,
    response_type VARCHAR(50) NOT NULL DEFAULT 'ai',
    word_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT response_type_check CHECK (response_type IN ('ai', 'humanized', 'expert', 'hybrid'))
);

CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_expert_id ON answers(expert_id);
CREATE INDEX IF NOT EXISTS idx_answers_created_at ON answers(created_at);
CREATE INDEX IF NOT EXISTS idx_answers_ai_response ON answers USING GIN(ai_response);
CREATE INDEX IF NOT EXISTS idx_answers_final_response ON answers USING GIN(final_response);

-- 8. Expert Reviews Table
CREATE TABLE IF NOT EXISTS expert_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES answers(answer_id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    expert_id UUID NOT NULL REFERENCES experts(expert_id) ON DELETE CASCADE,
    review_status VARCHAR(50) NOT NULL,
    is_approved BOOLEAN,
    rejection_reason TEXT,
    corrections JSONB,
    review_notes TEXT,
    review_time_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT review_status_check CHECK (review_status IN ('pending', 'in_progress', 'approved', 'rejected', 'needs_revision'))
);

CREATE INDEX IF NOT EXISTS idx_expert_reviews_answer_id ON expert_reviews(answer_id);
CREATE INDEX IF NOT EXISTS idx_expert_reviews_question_id ON expert_reviews(question_id);
CREATE INDEX IF NOT EXISTS idx_expert_reviews_expert_id ON expert_reviews(expert_id);
CREATE INDEX IF NOT EXISTS idx_expert_reviews_status ON expert_reviews(review_status);
CREATE INDEX IF NOT EXISTS idx_expert_reviews_created_at ON expert_reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_expert_reviews_is_approved ON expert_reviews(is_approved);

-- 9. Ratings Table
CREATE TABLE IF NOT EXISTS ratings (
    rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    answer_id UUID REFERENCES answers(answer_id) ON DELETE CASCADE,
    expert_id UUID REFERENCES experts(expert_id) ON DELETE SET NULL,
    client_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL,
    quality_score INTEGER,
    speed_score INTEGER,
    expertise_score INTEGER,
    comment TEXT,
    helpful BOOLEAN,
    would_recommend BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT overall_score_check CHECK (overall_score BETWEEN 1 AND 5),
    CONSTRAINT quality_score_check CHECK (quality_score IS NULL OR quality_score BETWEEN 1 AND 5),
    CONSTRAINT speed_score_check CHECK (speed_score IS NULL OR speed_score BETWEEN 1 AND 5),
    CONSTRAINT expertise_score_check CHECK (expertise_score IS NULL OR expertise_score BETWEEN 1 AND 5)
);

CREATE INDEX IF NOT EXISTS idx_ratings_question_id ON ratings(question_id);
CREATE INDEX IF NOT EXISTS idx_ratings_answer_id ON ratings(answer_id);
CREATE INDEX IF NOT EXISTS idx_ratings_expert_id ON ratings(expert_id);
CREATE INDEX IF NOT EXISTS idx_ratings_client_id ON ratings(client_id);
CREATE INDEX IF NOT EXISTS idx_ratings_created_at ON ratings(created_at);
CREATE INDEX IF NOT EXISTS idx_ratings_overall_score ON ratings(overall_score);

-- 10. AI Processing Log Table
CREATE TABLE IF NOT EXISTS ai_processing_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100),
    provider VARCHAR(50),
    request_data JSONB,
    response_data JSONB,
    tokens_used INTEGER,
    cost DECIMAL(10,6),
    processing_time_ms INTEGER,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT status_check CHECK (status IN ('success', 'failed', 'timeout', 'rate_limited'))
);

CREATE INDEX IF NOT EXISTS idx_ai_logs_question_id ON ai_processing_logs(question_id);
CREATE INDEX IF NOT EXISTS idx_ai_logs_service_name ON ai_processing_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_ai_logs_provider ON ai_processing_logs(provider);
CREATE INDEX IF NOT EXISTS idx_ai_logs_status ON ai_processing_logs(status);
CREATE INDEX IF NOT EXISTS idx_ai_logs_created_at ON ai_processing_logs(created_at);

-- 11. Humanization Log Table
CREATE TABLE IF NOT EXISTS humanization_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES answers(answer_id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    original_text TEXT,
    humanized_text TEXT,
    changes_made INTEGER,
    confidence_score DECIMAL(5,4),
    ai_detection_score_before DECIMAL(5,4),
    ai_detection_score_after DECIMAL(5,4),
    processing_time_ms INTEGER,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT status_check CHECK (status IN ('success', 'failed', 'skipped'))
);

CREATE INDEX IF NOT EXISTS idx_humanization_logs_answer_id ON humanization_logs(answer_id);
CREATE INDEX IF NOT EXISTS idx_humanization_logs_service_name ON humanization_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_humanization_logs_status ON humanization_logs(status);
CREATE INDEX IF NOT EXISTS idx_humanization_logs_created_at ON humanization_logs(created_at);

-- 12. Originality Check Table
CREATE TABLE IF NOT EXISTS originality_checks (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES answers(answer_id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    originality_score DECIMAL(5,4),
    ai_detection_score DECIMAL(5,4),
    similarity_score DECIMAL(5,4),
    flagged_sources JSONB,
    matches JSONB,
    is_original BOOLEAN NOT NULL,
    passes_threshold BOOLEAN NOT NULL,
    check_result JSONB,
    processing_time_ms INTEGER,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT status_check CHECK (status IN ('success', 'failed', 'warning'))
);

CREATE INDEX IF NOT EXISTS idx_originality_checks_answer_id ON originality_checks(answer_id);
CREATE INDEX IF NOT EXISTS idx_originality_checks_service_name ON originality_checks(service_name);
CREATE INDEX IF NOT EXISTS idx_originality_checks_is_original ON originality_checks(is_original);
CREATE INDEX IF NOT EXISTS idx_originality_checks_created_at ON originality_checks(created_at);

-- 13. Audit Log Table
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    action_data JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs(success);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_data ON audit_logs USING GIN(action_data);

-- 14. Notification Table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    message TEXT NOT NULL,
    link TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT notification_type_check CHECK (notification_type IN ('info', 'warning', 'error', 'success', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- 15. Queue Management Table
CREATE TABLE IF NOT EXISTS queue_items (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    priority INTEGER NOT NULL DEFAULT 5,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    job_data JSONB,
    error_message TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT status_check CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_queue_items_status ON queue_items(status);
CREATE INDEX IF NOT EXISTS idx_queue_items_job_type ON queue_items(job_type);
CREATE INDEX IF NOT EXISTS idx_queue_items_scheduled_at ON queue_items(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_queue_items_priority ON queue_items(priority);
CREATE INDEX IF NOT EXISTS idx_queue_items_pending ON queue_items(status, scheduled_at) WHERE status = 'pending';

-- 16. API Usage Tracking Table
CREATE TABLE IF NOT EXISTS api_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    api_endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_status INTEGER,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT method_check CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'))
);

CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(api_endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_date ON api_usage(user_id, created_at);

-- ============================================
-- TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_experts_updated_at BEFORE UPDATE ON experts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admins_updated_at BEFORE UPDATE ON admins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answers_updated_at BEFORE UPDATE ON answers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expert_reviews_updated_at BEFORE UPDATE ON expert_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS
-- ============================================

-- Expert Performance View
CREATE OR REPLACE VIEW expert_performance AS
SELECT 
    e.expert_id,
    e.user_id,
    u.email,
    u.first_name,
    u.last_name,
    e.total_reviews,
    e.average_rating,
    COUNT(DISTINCT er.review_id) as reviews_completed,
    AVG(er.review_time_seconds) as avg_review_time,
    COUNT(DISTINCT CASE WHEN er.is_approved = true THEN er.review_id END) as approved_count
FROM experts e
JOIN users u ON e.user_id = u.user_id
LEFT JOIN expert_reviews er ON e.expert_id = er.expert_id
GROUP BY e.expert_id, e.user_id, u.email, u.first_name, u.last_name, e.total_reviews, e.average_rating;

-- Question Status Summary View
CREATE OR REPLACE VIEW question_status_summary AS
SELECT 
    status,
    COUNT(*) as total,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage,
    AVG(EXTRACT(EPOCH FROM (COALESCE(processed_at, NOW()) - created_at))) as avg_processing_time_seconds
FROM questions
GROUP BY status;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Calculate Expert Rating Function
CREATE OR REPLACE FUNCTION calculate_expert_rating(p_expert_id UUID)
RETURNS TABLE (
    average_rating DECIMAL,
    total_ratings BIGINT,
    rating_distribution JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(r.overall_score)::DECIMAL(3,2) as average_rating,
        COUNT(*)::BIGINT as total_ratings,
        jsonb_build_object(
            '5_star', COUNT(*) FILTER (WHERE r.overall_score = 5),
            '4_star', COUNT(*) FILTER (WHERE r.overall_score = 4),
            '3_star', COUNT(*) FILTER (WHERE r.overall_score = 3),
            '2_star', COUNT(*) FILTER (WHERE r.overall_score = 2),
            '1_star', COUNT(*) FILTER (WHERE r.overall_score = 1)
        ) as rating_distribution
    FROM ratings r
    WHERE r.expert_id = p_expert_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ACHIEVEMENTS & STREAKS TABLES
-- ============================================

-- 20. Achievements Table
CREATE TABLE IF NOT EXISTS achievements (
    achievement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    achievement_type VARCHAR(50) NOT NULL,
    achievement_key VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    progress INTEGER DEFAULT 1,
    target INTEGER DEFAULT 1,
    unlocked_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_client_achievement UNIQUE (client_id, achievement_key)
);

CREATE INDEX IF NOT EXISTS idx_achievements_client_id ON achievements(client_id);
CREATE INDEX IF NOT EXISTS idx_achievements_type ON achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_achievements_unlocked_at ON achievements(unlocked_at) WHERE unlocked_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_achievements_key ON achievements(achievement_key);

-- 21. Achievement Progress Table
CREATE TABLE IF NOT EXISTS achievement_progress (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    achievement_key VARCHAR(100) NOT NULL,
    current_value INTEGER NOT NULL DEFAULT 0,
    target_value INTEGER NOT NULL DEFAULT 1,
    progress_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    metadata JSONB,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_client_progress UNIQUE (client_id, achievement_key)
);

CREATE INDEX IF NOT EXISTS idx_achievement_progress_client_id ON achievement_progress(client_id);
CREATE INDEX IF NOT EXISTS idx_achievement_progress_key ON achievement_progress(achievement_key);

-- 22. Streaks Table
CREATE TABLE IF NOT EXISTS streaks (
    streak_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    streak_type VARCHAR(50) NOT NULL,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_activity_date DATE NOT NULL,
    streak_started_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_client_streak_type UNIQUE (client_id, streak_type)
);

CREATE INDEX IF NOT EXISTS idx_streaks_client_id ON streaks(client_id);
CREATE INDEX IF NOT EXISTS idx_streaks_type ON streaks(streak_type);
CREATE INDEX IF NOT EXISTS idx_streaks_last_activity ON streaks(last_activity_date);

-- ============================================
-- END OF SCHEMA
-- ============================================
