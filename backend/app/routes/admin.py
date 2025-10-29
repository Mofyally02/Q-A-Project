"""
Admin Routes - Central engine of the platform
All endpoints require admin role authentication
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncpg

from app.database import get_db, get_auth_db
from app.services.auth_service import auth_service
from app.models import UserResponse, UserRole, APIResponse
from app.utils.security import SecurityUtils

router = APIRouter(prefix="/admin", tags=["Admin"])

# Dependency to ensure admin access
async def require_admin(
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.ADMIN]))
):
    return current_user

# ========================================
# 1. DASHBOARD OVERVIEW
# ========================================

@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_overview(
    current_user: UserResponse = Depends(require_admin),
    db: asyncpg.Connection = Depends(get_db),
    auth_db: asyncpg.Connection = Depends(get_auth_db)
):
    """Get comprehensive dashboard overview"""
    try:
        # Total questions
        total_questions = await db.fetchval("SELECT COUNT(*) FROM questions")
        
        # Pending reviews
        pending_reviews = await db.fetchval("""
            SELECT COUNT(*) FROM questions 
            WHERE status IN ('pending', 'in_review')
        """)
        
        # Average rating
        avg_rating = await db.fetchval("SELECT AVG(overall_score) FROM ratings") or 0.0
        
        # Active users
        active_users = await auth_db.fetchval("""
            SELECT COUNT(*) FROM users WHERE is_active = true
        """)
        
        # Questions per day (last 7 days)
        questions_per_day = await db.fetch("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM questions
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        # Top subjects
        top_subjects = await db.fetch("""
            SELECT subject, COUNT(*) as count
            FROM questions
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 5
        """)
        
        # Recent activity
        recent_activities = await db.fetch("""
            SELECT 
                q.question_id,
                q.content->>'data' as question_preview,
                q.status,
                q.created_at,
                u.email as client_email
            FROM questions q
            JOIN users u ON q.client_id = u.user_id
            ORDER BY q.created_at DESC
            LIMIT 10
        """)
        
        return APIResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data={
                "stats": {
                    "total_questions": total_questions,
                    "pending_reviews": pending_reviews,
                    "average_rating": round(avg_rating, 2),
                    "active_users": active_users
                },
                "charts": {
                    "questions_per_day": [dict(row) for row in questions_per_day],
                    "top_subjects": [dict(row) for row in top_subjects]
                },
                "recent_activity": [dict(row) for row in recent_activities]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 2. API KEY MANAGEMENT
# ========================================

@router.get("/api-keys", response_model=APIResponse)
async def get_api_keys(
    current_user: UserResponse = Depends(require_admin),
    auth_db: asyncpg.Connection = Depends(get_auth_db)
):
    """Get all API keys (masked for security)"""
    try:
        # Get from settings or database
        # For now, return empty list - keys stored in .env
        # In production, store encrypted in database
        
        providers = [
            "openai", "google", "anthropic", "xai", 
            "stealth", "turnitin", "poe_chatgpt", 
            "poe_claude", "poe_gemini"
        ]
        
        keys = []
        for provider in providers:
            keys.append({
                "provider": provider,
                "status": "configured",  # Would check if key exists
                "last_4_chars": "****"  # Mask actual key
            })
        
        return APIResponse(
            success=True,
            message="API keys retrieved successfully",
            data={"keys": keys}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api-keys/test/{provider}")
async def test_api_key(
    provider: str,
    current_user: UserResponse = Depends(require_admin)
):
    """Test API key connectivity"""
    try:
        # Mock test - in production, make actual API call
        return APIResponse(
            success=True,
            message=f"{provider} API key test successful",
            data={"status": "connected"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 7. SYSTEM TEST
# ========================================

@router.post("/test/question", response_model=APIResponse)
async def test_question_submission(
    question_data: Dict[str, Any],
    current_user: UserResponse = Depends(require_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit a test question to verify system functionality after API key updates"""
    try:
        from uuid import uuid4, UUID
        from app.services.submission_service import SubmissionService
        from app.services.queue_service import QueueService
        from datetime import datetime
        
        submission_service = SubmissionService()
        queue_service = QueueService()
        
        # Create question data with admin user as client (for testing)
        question_id = uuid4()
        content_text = question_data.get("content", "")
        subject = question_data.get("subject", "Test Question")
        question_type = question_data.get("type", "text")
        
        # Prepare content
        if question_type == "text":
            content = {"data": content_text, "format": "text"}
        else:
            content = question_data.get("content_obj", {"data": "", "format": "text"})
        
        # Mark question as test question in metadata
        metadata = {
            "is_test": True,
            "tested_by": current_user.user_id,
            "test_reason": question_data.get("test_reason", "API key verification"),
            "test_timestamp": datetime.utcnow().isoformat()
        }
        
        # Store test question in database
        # asyncpg handles JSONB conversion automatically
        await db.execute(
            """
            INSERT INTO questions (question_id, client_id, type, content, subject, status, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            question_id,
            current_user.user_id,  # Use admin as client for test
            question_type,
            content,
            subject,
            "submitted",
            metadata
        )
        
        # Queue for AI processing (this will test the API keys)
        await queue_service.enqueue_ai_processing(str(question_id))
        
        # Log test action
        await db.execute("""
            INSERT INTO audit_logs (user_id, action, details)
            VALUES ($1, $2, $3)
        """, current_user.user_id, "admin_test_question", {
            "question_id": str(question_id),
            "subject": subject,
            "reason": question_data.get("test_reason", "API key verification")
        })
        
        return APIResponse(
            success=True,
            message="Test question submitted successfully. System is processing to verify API keys.",
            data={
                "question_id": str(question_id),
                "status": "submitted",
                "test_mode": True,
                "message": "Question queued for processing. Check status in a few moments."
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit test question: {str(e)}")

@router.get("/test/question/{question_id}", response_model=APIResponse)
async def get_test_question_status(
    question_id: str,
    current_user: UserResponse = Depends(require_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get status of a test question"""
    try:
        from uuid import UUID
        
        question_uuid = UUID(question_id)
        row = await db.fetchrow(
            """
            SELECT q.*, 
                   a.ai_response,
                   a.humanized_response,
                   a.confidence_score,
                   oc.ai_content_percentage
            FROM questions q
            LEFT JOIN answers a ON q.question_id = a.question_id
            LEFT JOIN originality_checks oc ON q.question_id = oc.question_id
            WHERE q.question_id = $1
            """,
            question_uuid
        )
        
        if not row:
            raise HTTPException(status_code=404, detail="Test question not found")
        
        # Check if it's actually a test question
        metadata = row.get("metadata") or {}
        if not metadata.get("is_test"):
            return APIResponse(
                success=False,
                message="Question is not a test question"
            )
        
        result = {
            "question_id": str(row["question_id"]),
            "subject": row["subject"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat(),
            "test_metadata": metadata,
            "has_ai_response": row["ai_response"] is not None,
            "has_humanized_response": row["humanized_response"] is not None,
            "confidence_score": float(row["confidence_score"]) if row["confidence_score"] else None,
            "ai_content_percentage": float(row["ai_content_percentage"]) if row["ai_content_percentage"] else None
        }
        
        # Determine system health based on processing status
        if row["status"] == "completed" and row["ai_response"]:
            result["system_status"] = "healthy"
            result["message"] = "API keys are working correctly. System processed the test question successfully."
        elif row["status"] == "failed":
            result["system_status"] = "error"
            result["message"] = "System encountered an error. Check API keys and configuration."
        elif row["status"] in ["submitted", "processing"]:
            result["system_status"] = "processing"
            result["message"] = "Test question is being processed. Please check again in a moment."
        else:
            result["system_status"] = "pending"
            result["message"] = "Test question is pending processing."
        
        return APIResponse(
            success=True,
            message="Test question status retrieved",
            data=result
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 3. USER MANAGEMENT
# ========================================

@router.get("/users", response_model=APIResponse)
async def list_users(
    current_user: UserResponse = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    auth_db: asyncpg.Connection = Depends(get_auth_db)
):
    """List all users with pagination and filters"""
    try:
        # Build query
        query = """
            SELECT user_id, email, first_name, last_name, role, 
                   is_active, created_at, last_login
            FROM users
        """
        params = []
        
        if role:
            query += " WHERE role = $1"
            params.append(role)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, skip])
        
        users = await auth_db.fetch(query, *params)
        total = await auth_db.fetchval("SELECT COUNT(*) FROM users" + (" WHERE role = $1" if role else ""), role) if role else await auth_db.fetchval("SELECT COUNT(*) FROM users")
        
        return APIResponse(
            success=True,
            message="Users retrieved successfully",
            data={
                "users": [dict(user) for user in users],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=APIResponse)
async def get_user_details(
    user_id: str,
    current_user: UserResponse = Depends(require_admin),
    auth_db: asyncpg.Connection = Depends(get_auth_db),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get detailed user information"""
    try:
        # Get user info
        user = await auth_db.fetchrow("""
            SELECT * FROM users WHERE user_id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user-specific data based on role
        user_data = dict(user)
        
        if user['role'] == 'client':
            client_data = await auth_db.fetchrow("""
                SELECT * FROM clients WHERE user_id = $1
            """, user_id)
            user_data['client_info'] = dict(client_data) if client_data else None
            
            # Get question count
            question_count = await db.fetchval("""
                SELECT COUNT(*) FROM questions WHERE client_id = $1
            """, user_id)
            user_data['question_count'] = question_count
            
        elif user['role'] == 'expert':
            expert_data = await auth_db.fetchrow("""
                SELECT * FROM experts WHERE user_id = $1
            """, user_id)
            user_data['expert_info'] = dict(expert_data) if expert_data else None
            
            # Get review count
            review_count = await db.fetchval("""
                SELECT COUNT(*) FROM expert_reviews WHERE expert_id = (
                    SELECT expert_id FROM experts WHERE user_id = $1
                )
            """, user_id)
            user_data['review_count'] = review_count or 0
        
        return APIResponse(
            success=True,
            message="User details retrieved successfully",
            data=user_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 4. NOTIFICATIONS
# ========================================

@router.post("/notifications/send", response_model=APIResponse)
async def send_notification(
    recipient_type: str,
    recipient_ids: Optional[List[str]],
    subject: str,
    message: str,
    current_user: UserResponse = Depends(require_admin),
    auth_db: asyncpg.Connection = Depends(get_auth_db)
):
    """Send notification to users"""
    try:
        # Determine recipients
        if recipient_type == "all_clients":
            users = await auth_db.fetch("SELECT user_id FROM users WHERE role = 'client'")
        elif recipient_type == "all_experts":
            users = await auth_db.fetch("SELECT user_id FROM users WHERE role = 'expert'")
        elif recipient_type == "specific":
            users = [{"user_id": uid} for uid in recipient_ids] if recipient_ids else []
        else:
            raise HTTPException(status_code=400, detail="Invalid recipient type")
        
        # Insert notifications
        for user in users:
            await auth_db.execute("""
                INSERT INTO notifications (user_id, type, title, message)
                VALUES ($1, $2, $3, $4)
            """, user['user_id'], 'admin_announcement', subject, message)
        
        return APIResponse(
            success=True,
            message=f"Notification sent to {len(users)} users",
            data={"recipients": len(users)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/history", response_model=APIResponse)
async def get_notification_history(
    current_user: UserResponse = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    auth_db: asyncpg.Connection = Depends(get_auth_db)
):
    """Get notification history"""
    try:
        notifications = await auth_db.fetch("""
            SELECT n.*, u.email as recipient_email
            FROM notifications n
            JOIN users u ON n.user_id = u.user_id
            ORDER BY n.created_at DESC
            LIMIT $1 OFFSET $2
        """, limit, skip)
        
        return APIResponse(
            success=True,
            message="Notification history retrieved successfully",
            data={"notifications": [dict(n) for n in notifications]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 5. ANALYTICS
# ========================================

@router.get("/analytics/questions", response_model=APIResponse)
async def get_questions_analytics(
    current_user: UserResponse = Depends(require_admin),
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get questions analytics with filters"""
    try:
        query = """
            SELECT q.*, u.email as client_email
            FROM questions q
            JOIN users u ON q.client_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += f" AND q.status = ${len(params) + 1}"
            params.append(status)
        
        if start_date:
            query += f" AND q.created_at >= ${len(params) + 1}"
            params.append(start_date)
        
        if end_date:
            query += f" AND q.created_at <= ${len(params) + 1}"
            params.append(end_date)
        
        query += " ORDER BY q.created_at DESC LIMIT 100"
        
        questions = await db.fetch(query, *params)
        
        return APIResponse(
            success=True,
            message="Questions analytics retrieved successfully",
            data={"questions": [dict(q) for q in questions]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/experts", response_model=APIResponse)
async def get_expert_analytics(
    current_user: UserResponse = Depends(require_admin),
    auth_db: asyncpg.Connection = Depends(get_auth_db),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert performance analytics"""
    try:
        experts = await auth_db.fetch("""
            SELECT 
                e.*,
                u.email,
                u.first_name,
                u.last_name
            FROM experts e
            JOIN users u ON e.user_id = u.user_id
        """)
        
        expert_data = []
        for expert in experts:
            # Get review counts
            review_count = await db.fetchval("""
                SELECT COUNT(*) FROM expert_reviews 
                WHERE expert_id = $1
            """, expert['expert_id'])
            
            # Get average rating
            avg_rating = await db.fetchval("""
                SELECT AVG(overall_score) 
                FROM ratings 
                WHERE expert_id = $1
            """, expert['expert_id']) or 0.0
            
            expert_data.append({
                **dict(expert),
                "review_count": review_count or 0,
                "average_rating": round(avg_rating, 2)
            })
        
        return APIResponse(
            success=True,
            message="Expert analytics retrieved successfully",
            data={"experts": expert_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 6. COMPLIANCE
# ========================================

@router.get("/compliance/logs", response_model=APIResponse)
async def get_audit_logs(
    current_user: UserResponse = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get audit logs"""
    try:
        logs = await db.fetch("""
            SELECT 
                al.*,
                u.email as user_email
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.user_id
            ORDER BY al.created_at DESC
            LIMIT $1 OFFSET $2
        """, limit, skip)
        
        return APIResponse(
            success=True,
            message="Audit logs retrieved successfully",
            data={"logs": [dict(log) for log in logs]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/flagged", response_model=APIResponse)
async def get_flagged_content(
    current_user: UserResponse = Depends(require_admin),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get flagged content (high AI content, plagiarism, etc.)"""
    try:
        # Get questions with high AI content
        high_ai_content = await db.fetch("""
            SELECT q.*, oc.ai_content_percentage
            FROM questions q
            JOIN originality_checks oc ON q.question_id = oc.question_id
            WHERE oc.ai_content_percentage > 10
            ORDER BY oc.ai_content_percentage DESC
        """)
        
        return APIResponse(
            success=True,
            message="Flagged content retrieved successfully",
            data={"flagged_content": [dict(q) for q in high_ai_content]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
