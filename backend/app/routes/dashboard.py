from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Dict, Any, List
from app.database import get_db
from app.services.auth_service import auth_service
from app.models import UserResponse, UserRole, APIResponse
from app.services.submission_service import SubmissionService
from app.services.expert_review_service import ExpertReviewService
from app.services.admin_service import AdminService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Initialize services
submission_service = SubmissionService()
expert_review_service = ExpertReviewService()
admin_service = AdminService()

@router.get("/client", response_model=APIResponse)
async def client_dashboard(
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.CLIENT])),
    db: asyncpg.Connection = Depends(get_db)
):
    """Client dashboard - shows user's questions and answers"""
    try:
        # Get user's questions
        questions = await db.fetch("""
            SELECT q.question_id, q.content, q.subject, q.status, q.created_at,
                   a.ai_response, a.humanized_response, a.expert_response,
                   a.confidence_score, a.is_approved
            FROM questions q
            LEFT JOIN answers a ON q.question_id = a.question_id
            WHERE q.client_id = $1
            ORDER BY q.created_at DESC
            LIMIT 20
        """, current_user.user_id)
        
        # Get statistics
        stats = await db.fetchrow("""
            SELECT 
                COUNT(*) as total_questions,
                COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_questions,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as pending_questions,
                AVG(r.score) as avg_rating
            FROM questions q
            LEFT JOIN ratings r ON q.question_id = r.question_id
            WHERE q.client_id = $1
        """, current_user.user_id)
        
        dashboard_data = {
            "user": {
                "user_id": str(current_user.user_id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
                "role": current_user.role.value
            },
            "statistics": {
                "total_questions": stats['total_questions'] or 0,
                "completed_questions": stats['completed_questions'] or 0,
                "pending_questions": stats['pending_questions'] or 0,
                "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0
            },
            "recent_questions": [
                {
                    "question_id": str(q['question_id']),
                    "content": q['content'],
                    "subject": q['subject'],
                    "status": q['status'],
                    "created_at": q['created_at'].isoformat(),
                    "ai_response": q['ai_response'],
                    "humanized_response": q['humanized_response'],
                    "expert_response": q['expert_response'],
                    "confidence_score": q['confidence_score'],
                    "is_approved": q['is_approved']
                }
                for q in questions
            ]
        }
        
        return APIResponse(
            success=True,
            message="Client dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Client dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load client dashboard"
        )

@router.get("/expert", response_model=APIResponse)
async def expert_dashboard(
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.EXPERT])),
    db: asyncpg.Connection = Depends(get_db)
):
    """Expert dashboard - shows pending reviews and expert statistics"""
    try:
        # Get pending reviews
        pending_reviews = await db.fetch("""
            SELECT q.question_id, q.content, q.subject, q.created_at,
                   a.answer_id, a.ai_response, a.humanized_response,
                   a.confidence_score, a.created_at as answer_created_at
            FROM questions q
            JOIN answers a ON q.question_id = a.question_id
            WHERE q.status = 'review' AND a.is_approved IS NULL
            ORDER BY a.created_at ASC
            LIMIT 20
        """)
        
        # Get expert statistics
        stats = await db.fetchrow("""
            SELECT 
                COUNT(er.review_id) as total_reviews,
                COUNT(CASE WHEN er.is_approved = true THEN 1 END) as approved_reviews,
                COUNT(CASE WHEN er.is_approved = false THEN 1 END) as rejected_reviews,
                AVG(r.score) as avg_rating
            FROM expert_reviews er
            LEFT JOIN ratings r ON er.answer_id = r.question_id
            WHERE er.expert_id = $1
        """, current_user.user_id)
        
        # Get recent reviews
        recent_reviews = await db.fetch("""
            SELECT q.question_id, q.content, q.subject, er.is_approved,
                   er.rejection_reason, er.created_at
            FROM expert_reviews er
            JOIN answers a ON er.answer_id = a.answer_id
            JOIN questions q ON a.question_id = q.question_id
            WHERE er.expert_id = $1
            ORDER BY er.created_at DESC
            LIMIT 10
        """, current_user.user_id)
        
        dashboard_data = {
            "user": {
                "user_id": str(current_user.user_id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
                "role": current_user.role.value
            },
            "statistics": {
                "total_reviews": stats['total_reviews'] or 0,
                "approved_reviews": stats['approved_reviews'] or 0,
                "rejected_reviews": stats['rejected_reviews'] or 0,
                "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0
            },
            "pending_reviews": [
                {
                    "question_id": str(q['question_id']),
                    "answer_id": str(q['answer_id']),
                    "content": q['content'],
                    "subject": q['subject'],
                    "ai_response": q['ai_response'],
                    "humanized_response": q['humanized_response'],
                    "confidence_score": q['confidence_score'],
                    "created_at": q['created_at'].isoformat(),
                    "answer_created_at": q['answer_created_at'].isoformat()
                }
                for q in pending_reviews
            ],
            "recent_reviews": [
                {
                    "question_id": str(r['question_id']),
                    "content": r['content'],
                    "subject": r['subject'],
                    "is_approved": r['is_approved'],
                    "rejection_reason": r['rejection_reason'],
                    "created_at": r['created_at'].isoformat()
                }
                for r in recent_reviews
            ]
        }
        
        return APIResponse(
            success=True,
            message="Expert dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Expert dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load expert dashboard"
        )

@router.get("/admin", response_model=APIResponse)
async def admin_dashboard(
    current_user: UserResponse = Depends(auth_service.require_role([UserRole.ADMIN])),
    db: asyncpg.Connection = Depends(get_db)
):
    """Admin dashboard - shows system analytics and management tools"""
    try:
        # Get system statistics
        system_stats = await db.fetchrow("""
            SELECT 
                COUNT(DISTINCT q.client_id) as total_clients,
                COUNT(DISTINCT er.expert_id) as total_experts,
                COUNT(q.question_id) as total_questions,
                COUNT(CASE WHEN q.status = 'delivered' THEN 1 END) as completed_questions,
                COUNT(CASE WHEN q.status = 'processing' THEN 1 END) as processing_questions,
                COUNT(CASE WHEN q.status = 'review' THEN 1 END) as review_questions,
                AVG(r.score) as avg_rating,
                COUNT(CASE WHEN er.is_approved = false THEN 1 END) as rejected_answers
            FROM questions q
            LEFT JOIN answers a ON q.question_id = a.question_id
            LEFT JOIN expert_reviews er ON a.answer_id = er.answer_id
            LEFT JOIN ratings r ON q.question_id = r.question_id
        """)
        
        # Get recent activity
        recent_activity = await db.fetch("""
            SELECT 
                'question' as type,
                q.question_id as id,
                q.content,
                q.status,
                q.created_at,
                u.first_name || ' ' || u.last_name as user_name,
                u.role
            FROM questions q
            JOIN users u ON q.client_id = u.user_id
            WHERE q.created_at > NOW() - INTERVAL '24 hours'
            
            UNION ALL
            
            SELECT 
                'review' as type,
                er.review_id as id,
                q.content,
                CASE WHEN er.is_approved THEN 'approved' ELSE 'rejected' END as status,
                er.created_at,
                u.first_name || ' ' || u.last_name as user_name,
                u.role
            FROM expert_reviews er
            JOIN answers a ON er.answer_id = a.answer_id
            JOIN questions q ON a.question_id = q.question_id
            JOIN users u ON er.expert_id = u.user_id
            WHERE er.created_at > NOW() - INTERVAL '24 hours'
            
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        # Get user statistics by role
        user_stats = await db.fetch("""
            SELECT 
                role,
                COUNT(*) as count,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_count,
                COUNT(CASE WHEN last_login > NOW() - INTERVAL '7 days' THEN 1 END) as recent_logins
            FROM users
            GROUP BY role
        """)
        
        dashboard_data = {
            "user": {
                "user_id": str(current_user.user_id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
                "role": current_user.role.value
            },
            "system_statistics": {
                "total_clients": system_stats['total_clients'] or 0,
                "total_experts": system_stats['total_experts'] or 0,
                "total_questions": system_stats['total_questions'] or 0,
                "completed_questions": system_stats['completed_questions'] or 0,
                "processing_questions": system_stats['processing_questions'] or 0,
                "review_questions": system_stats['review_questions'] or 0,
                "average_rating": float(system_stats['avg_rating']) if system_stats['avg_rating'] else 0.0,
                "rejected_answers": system_stats['rejected_answers'] or 0
            },
            "user_statistics": [
                {
                    "role": stat['role'],
                    "total_count": stat['count'],
                    "active_count": stat['active_count'],
                    "recent_logins": stat['recent_logins']
                }
                for stat in user_stats
            ],
            "recent_activity": [
                {
                    "type": activity['type'],
                    "id": str(activity['id']),
                    "content": activity['content'][:100] + "..." if len(activity['content']) > 100 else activity['content'],
                    "status": activity['status'],
                    "user_name": activity['user_name'],
                    "user_role": activity['role'],
                    "created_at": activity['created_at'].isoformat()
                }
                for activity in recent_activity
            ]
        }
        
        return APIResponse(
            success=True,
            message="Admin dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load admin dashboard"
        )

@router.get("/stats", response_model=APIResponse)
async def get_user_stats(
    current_user: UserResponse = Depends(auth_service.get_current_user),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user-specific statistics based on role"""
    try:
        if current_user.role == UserRole.CLIENT:
            # Client stats
            stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_questions,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_questions,
                    AVG(r.score) as avg_rating
                FROM questions q
                LEFT JOIN ratings r ON q.question_id = r.question_id
                WHERE q.client_id = $1
            """, current_user.user_id)
            
            data = {
                "total_questions": stats['total_questions'] or 0,
                "completed_questions": stats['completed_questions'] or 0,
                "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0
            }
            
        elif current_user.role == UserRole.EXPERT:
            # Expert stats
            stats = await db.fetchrow("""
                SELECT 
                    COUNT(er.review_id) as total_reviews,
                    COUNT(CASE WHEN er.is_approved = true THEN 1 END) as approved_reviews,
                    AVG(r.score) as avg_rating
                FROM expert_reviews er
                LEFT JOIN ratings r ON er.answer_id = r.question_id
                WHERE er.expert_id = $1
            """, current_user.user_id)
            
            data = {
                "total_reviews": stats['total_reviews'] or 0,
                "approved_reviews": stats['approved_reviews'] or 0,
                "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0
            }
            
        else:  # Admin
            # Admin stats
            stats = await db.fetchrow("""
                SELECT 
                    COUNT(DISTINCT q.client_id) as total_clients,
                    COUNT(DISTINCT er.expert_id) as total_experts,
                    COUNT(q.question_id) as total_questions,
                    AVG(r.score) as avg_rating
                FROM questions q
                LEFT JOIN answers a ON q.question_id = a.question_id
                LEFT JOIN expert_reviews er ON a.answer_id = er.answer_id
                LEFT JOIN ratings r ON q.question_id = r.question_id
            """)
            
            data = {
                "total_clients": stats['total_clients'] or 0,
                "total_experts": stats['total_experts'] or 0,
                "total_questions": stats['total_questions'] or 0,
                "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0
            }
        
        return APIResponse(
            success=True,
            message="User statistics retrieved successfully",
            data=data
        )
        
    except Exception as e:
        logger.error(f"User stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user statistics"
        )
