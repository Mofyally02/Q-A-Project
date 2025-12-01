"""
Admin management service
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from app.crud.admin import admins as admin_crud
from app.crud.admin import admin_actions as action_crud
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """Admin management service"""
    
    @staticmethod
    async def get_admins(
        db: asyncpg.Connection,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get all admins"""
        return await admin_crud.get_admins(db, role, is_active, page, page_size)
    
    @staticmethod
    async def invite_admin(
        db: asyncpg.Connection,
        email: str,
        role: str,
        invited_by: UUID,
        expires_in_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invite new admin"""
        if role not in ("super_admin", "admin_editor"):
            raise ValueError("Invalid admin role")
        
        # Only super_admin can invite other super_admins
        inviter = await db.fetchrow("SELECT role FROM users WHERE id = $1", invited_by)
        if not inviter or inviter["role"] != "super_admin":
            if role == "super_admin":
                raise ValueError("Only super_admin can invite other super_admins")
        
        result = await admin_crud.create_admin_invitation(
            db, email, role, invited_by, expires_in_hours
        )
        
        # Log admin action
        await action_crud.log_admin_action(
            db, invited_by, "invite_admin",
            target_type="user", target_id=result["invitation_id"],
            details={"email": email, "role": role},
            ip_address=ip_address, user_agent=user_agent
        )
        
        return result
    
    @staticmethod
    async def suspend_admin(
        db: asyncpg.Connection,
        admin_id: UUID,
        suspended: bool,
        reason: Optional[str],
        suspended_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suspend or activate admin"""
        # Cannot suspend self
        if admin_id == suspended_by:
            raise ValueError("Cannot suspend yourself")
        
        # Check permissions
        suspended_by_user = await db.fetchrow("SELECT role FROM users WHERE id = $1", suspended_by)
        target_admin = await db.fetchrow("SELECT role FROM users WHERE id = $1", admin_id)
        
        if not suspended_by_user or suspended_by_user["role"] != "super_admin":
            raise ValueError("Only super_admin can suspend admins")
        
        if not target_admin:
            raise ValueError("Admin not found")
        
        # Super admin cannot suspend another super admin (only admin_editor)
        if target_admin["role"] == "super_admin" and suspended_by_user["role"] == "super_admin":
            if admin_id != suspended_by:  # Can't suspend self, but can suspend other super_admins
                pass  # Allow for now, but could restrict
        
        success = await admin_crud.suspend_admin(
            db, admin_id, suspended, reason, suspended_by
        )
        
        if not success:
            raise ValueError("Failed to suspend admin")
        
        return {
            "success": True,
            "admin_id": admin_id,
            "suspended": suspended
        }
    
    @staticmethod
    async def revoke_admin_access(
        db: asyncpg.Connection,
        admin_id: UUID,
        revoked_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Revoke admin access"""
        # Check permissions
        revoked_by_user = await db.fetchrow("SELECT role FROM users WHERE id = $1", revoked_by)
        if not revoked_by_user or revoked_by_user["role"] != "super_admin":
            raise ValueError("Only super_admin can revoke admin access")
        
        success = await admin_crud.revoke_admin_access(db, admin_id, revoked_by)
        
        if not success:
            raise ValueError("Failed to revoke admin access")
        
        return {
            "success": True,
            "admin_id": admin_id,
            "message": "Admin access revoked successfully"
        }
    
    @staticmethod
    async def get_admin_by_id(
        db: asyncpg.Connection,
        admin_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get admin by ID"""
        return await admin_crud.get_admin_by_id(db, admin_id)
    
    @staticmethod
    async def get_dashboard_stats(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get dashboard statistics with trend calculations"""
        try:
            # Get total questions (current)
            total_questions = await db.fetchval("""
                SELECT COUNT(*) FROM questions
            """) or 0
            
            # Get total questions from previous period (30 days ago)
            total_questions_previous = await db.fetchval("""
                SELECT COUNT(*) FROM questions 
                WHERE created_at <= NOW() - INTERVAL '30 days'
            """) or 0
            
            # Get pending reviews (current)
            pending_reviews = await db.fetchval("""
                SELECT COUNT(*) FROM questions 
                WHERE status IN ('review', 'processing')
            """) or 0
            
            # Get pending reviews from previous period
            pending_reviews_previous = await db.fetchval("""
                SELECT COUNT(*) FROM questions 
                WHERE status IN ('review', 'processing')
                AND created_at <= NOW() - INTERVAL '30 days'
            """) or 0
            
            # Get average rating (current)
            avg_rating = await db.fetchval("""
                SELECT COALESCE(AVG(score), 0) FROM ratings
                WHERE created_at > NOW() - INTERVAL '30 days'
            """) or 0.0
            
            # Get average rating from previous period
            avg_rating_previous = await db.fetchval("""
                SELECT COALESCE(AVG(score), 0) FROM ratings
                WHERE created_at > NOW() - INTERVAL '60 days'
                AND created_at <= NOW() - INTERVAL '30 days'
            """) or 0.0
            
            # Get active users (last 30 days)
            active_users = await db.fetchval("""
                SELECT COUNT(DISTINCT client_id) FROM questions 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """) or 0
            
            # Get active users from previous period (30-60 days ago)
            active_users_previous = await db.fetchval("""
                SELECT COUNT(DISTINCT client_id) FROM questions 
                WHERE created_at > NOW() - INTERVAL '60 days'
                AND created_at <= NOW() - INTERVAL '30 days'
            """) or 0
            
            # Get total experts
            total_experts = await db.fetchval("""
                SELECT COUNT(*) FROM users WHERE role = 'expert'
            """) or 0
            
            # Get total clients
            total_clients = await db.fetchval("""
                SELECT COUNT(*) FROM users WHERE role = 'client'
            """) or 0
            
            # Calculate trends
            def calculate_trend(current: float, previous: float) -> Dict[str, Any]:
                if previous == 0:
                    return {"value": 0.0, "is_positive": True}
                change = ((current - previous) / previous) * 100
                return {
                    "value": abs(change),
                    "is_positive": change >= 0
                }
            
            return {
                "total_questions": total_questions,
                "total_questions_trend": calculate_trend(total_questions, total_questions_previous),
                "pending_reviews": pending_reviews,
                "pending_reviews_trend": calculate_trend(pending_reviews, pending_reviews_previous),
                "average_rating": float(avg_rating),
                "average_rating_trend": calculate_trend(avg_rating, avg_rating_previous),
                "active_users": active_users,
                "active_users_trend": calculate_trend(active_users, active_users_previous),
                "total_experts": total_experts,
                "total_clients": total_clients,
                "system_health": 100
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                "total_questions": 0,
                "total_questions_trend": {"value": 0.0, "is_positive": True},
                "pending_reviews": 0,
                "pending_reviews_trend": {"value": 0.0, "is_positive": True},
                "average_rating": 0.0,
                "average_rating_trend": {"value": 0.0, "is_positive": True},
                "active_users": 0,
                "active_users_trend": {"value": 0.0, "is_positive": True},
                "total_experts": 0,
                "total_clients": 0,
                "system_health": 100
            }
    
    @staticmethod
    async def get_dashboard_charts(db: asyncpg.Connection) -> Dict[str, Any]:
        """Get dashboard chart data"""
        try:
            # Questions per day (last 30 days)
            questions_per_day = await db.fetch("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM questions
                WHERE created_at > NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
            
            # Top subjects
            top_subjects = await db.fetch("""
                SELECT 
                    subject,
                    COUNT(*) as count
                FROM questions
                WHERE subject IS NOT NULL
                GROUP BY subject
                ORDER BY count DESC
                LIMIT 5
            """)
            
            return {
                "questions_per_day": [
                    {"date": str(row["date"]), "count": row["count"]}
                    for row in questions_per_day
                ],
                "top_subjects": [
                    {"subject": row["subject"] or "Unknown", "count": row["count"]}
                    for row in top_subjects
                ]
            }
        except Exception as e:
            logger.error(f"Error getting dashboard charts: {e}")
            return {
                "questions_per_day": [],
                "top_subjects": []
            }
    
    @staticmethod
    async def get_recent_activity(db: asyncpg.Connection, limit: int = 10) -> list:
        """Get recent activity"""
        try:
            activities = await db.fetch("""
                SELECT 
                    q.question_id,
                    q.content->>'data' as question_preview,
                    q.status,
                    q.created_at,
                    u.email as client_email
                FROM questions q
                LEFT JOIN users u ON q.client_id = u.id
                ORDER BY q.created_at DESC
                LIMIT $1
            """, limit)
            
            return [
                {
                    "question_id": str(row["question_id"]),
                    "question_preview": row["question_preview"][:100] if row["question_preview"] else None,
                    "status": row["status"],
                    "created_at": str(row["created_at"]),
                    "client_email": row["client_email"] or "Unknown"
                }
                for row in activities
            ]
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []

