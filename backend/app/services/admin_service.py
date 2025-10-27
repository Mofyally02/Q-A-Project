import asyncio
import logging
from typing import Dict, Any, Optional, List
import asyncpg
from app.models import AdminAnalytics, AdminOverride, APIResponse
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class AdminService:
    """Service for admin operations and analytics"""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    async def get_analytics(
        self,
        db: asyncpg.Connection,
        days: int = 30
    ) -> APIResponse:
        """Get comprehensive analytics for admin dashboard"""
        try:
            # Get basic statistics
            basic_stats = await self._get_basic_statistics(db, days)
            
            # Get rating analytics
            rating_analytics = await self._get_rating_analytics(db, days)
            
            # Get rejection analytics
            rejection_analytics = await self._get_rejection_analytics(db, days)
            
            # Get churn risk analysis
            churn_risk = await self._get_churn_risk_analysis(db, days)
            
            # Get recent activity
            recent_activity = await self._get_recent_activity(db, days)
            
            # Get compliance metrics
            compliance_metrics = await self._get_compliance_metrics(db, days)
            
            # Get expert performance
            expert_performance = await self._get_expert_performance(db, days)
            
            # Get system health metrics
            system_health = await self._get_system_health_metrics(db, days)
            
            analytics = AdminAnalytics(
                total_questions=basic_stats["total_questions"],
                avg_rating=rating_analytics["avg_rating"],
                rejection_rate=rejection_analytics["rejection_rate"],
                churn_risk_clients=churn_risk["at_risk_clients"],
                recent_activity=recent_activity,
                compliance_metrics=compliance_metrics,
                expert_performance=expert_performance,
                system_health=system_health,
                basic_statistics=basic_stats,
                rating_analytics=rating_analytics,
                rejection_analytics=rejection_analytics,
                churn_risk_analysis=churn_risk
            )
            
            return APIResponse(
                success=True,
                message="Analytics retrieved successfully",
                data=analytics.dict()
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return APIResponse(
                success=False,
                message="Failed to get analytics",
                data={"error": str(e)}
            )
    
    async def _get_basic_statistics(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get basic system statistics"""
        try:
            # Total questions
            total_questions = await db.fetchval(
                """
                SELECT COUNT(*) FROM questions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Questions by status
            status_counts = await db.fetch(
                """
                SELECT status, COUNT(*) as count
                FROM questions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY status
                """,
                days
            )
            
            # Questions by type
            type_counts = await db.fetch(
                """
                SELECT type, COUNT(*) as count
                FROM questions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY type
                """,
                days
            )
            
            # Questions by subject
            subject_counts = await db.fetch(
                """
                SELECT subject, COUNT(*) as count
                FROM questions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY subject
                ORDER BY count DESC
                LIMIT 10
                """,
                days
            )
            
            # Daily question counts
            daily_counts = await db.fetch(
                """
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM questions 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                days
            )
            
            return {
                "total_questions": total_questions,
                "status_distribution": {row["status"]: row["count"] for row in status_counts},
                "type_distribution": {row["type"]: row["count"] for row in type_counts},
                "subject_distribution": {row["subject"]: row["count"] for row in subject_counts},
                "daily_counts": [{"date": row["date"].isoformat(), "count": row["count"]} for row in daily_counts]
            }
            
        except Exception as e:
            logger.error(f"Error getting basic statistics: {e}")
            return {}
    
    async def _get_rating_analytics(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get rating analytics"""
        try:
            # Average rating
            avg_rating = await db.fetchval(
                """
                SELECT AVG(score) FROM ratings 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Rating distribution
            rating_distribution = await db.fetch(
                """
                SELECT score, COUNT(*) as count
                FROM ratings 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY score
                ORDER BY score
                """,
                days
            )
            
            # Rating trends over time
            rating_trends = await db.fetch(
                """
                SELECT DATE(created_at) as date, AVG(score) as avg_score, COUNT(*) as count
                FROM ratings 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                days
            )
            
            # Expert ratings
            expert_ratings = await db.fetch(
                """
                SELECT r.expert_id, AVG(r.score) as avg_rating, COUNT(r.score) as total_ratings
                FROM ratings r
                WHERE r.created_at >= NOW() - INTERVAL '%s days'
                AND r.expert_id IS NOT NULL
                GROUP BY r.expert_id
                ORDER BY avg_rating DESC
                LIMIT 10
                """,
                days
            )
            
            return {
                "avg_rating": float(avg_rating) if avg_rating else 0.0,
                "rating_distribution": {row["score"]: row["count"] for row in rating_distribution},
                "rating_trends": [
                    {
                        "date": row["date"].isoformat(),
                        "avg_score": float(row["avg_score"]) if row["avg_score"] else 0.0,
                        "count": row["count"]
                    }
                    for row in rating_trends
                ],
                "expert_ratings": [
                    {
                        "expert_id": str(row["expert_id"]),
                        "avg_rating": float(row["avg_rating"]) if row["avg_rating"] else 0.0,
                        "total_ratings": row["total_ratings"]
                    }
                    for row in expert_ratings
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting rating analytics: {e}")
            return {}
    
    async def _get_rejection_analytics(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get rejection analytics"""
        try:
            # Total rejections
            total_rejections = await db.fetchval(
                """
                SELECT COUNT(*) FROM answers 
                WHERE is_approved = false 
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Total answers
            total_answers = await db.fetchval(
                """
                SELECT COUNT(*) FROM answers 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Rejection rate
            rejection_rate = (total_rejections / total_answers) if total_answers > 0 else 0.0
            
            # Rejection reasons
            rejection_reasons = await db.fetch(
                """
                SELECT rejection_reason, COUNT(*) as count
                FROM answers 
                WHERE is_approved = false 
                AND created_at >= NOW() - INTERVAL '%s days'
                AND rejection_reason IS NOT NULL
                GROUP BY rejection_reason
                ORDER BY count DESC
                """,
                days
            )
            
            # Rejection trends
            rejection_trends = await db.fetch(
                """
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM answers 
                WHERE is_approved = false 
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                days
            )
            
            return {
                "total_rejections": total_rejections,
                "total_answers": total_answers,
                "rejection_rate": rejection_rate,
                "rejection_reasons": {row["rejection_reason"]: row["count"] for row in rejection_reasons},
                "rejection_trends": [
                    {"date": row["date"].isoformat(), "count": row["count"]}
                    for row in rejection_trends
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting rejection analytics: {e}")
            return {}
    
    async def _get_churn_risk_analysis(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get churn risk analysis"""
        try:
            # Clients with low ratings
            low_rating_clients = await db.fetch(
                """
                SELECT q.client_id, AVG(r.score) as avg_rating, COUNT(r.score) as rating_count
                FROM questions q
                JOIN ratings r ON q.question_id = r.question_id
                WHERE r.created_at >= NOW() - INTERVAL '%s days'
                GROUP BY q.client_id
                HAVING AVG(r.score) < 3.0 AND COUNT(r.score) >= 2
                ORDER BY avg_rating
                """,
                days
            )
            
            # Clients with high rejection rates
            high_rejection_clients = await db.fetch(
                """
                SELECT q.client_id, 
                       COUNT(CASE WHEN a.is_approved = false THEN 1 END) as rejections,
                       COUNT(a.answer_id) as total_answers,
                       (COUNT(CASE WHEN a.is_approved = false THEN 1 END)::float / COUNT(a.answer_id)) as rejection_rate
                FROM questions q
                JOIN answers a ON q.question_id = a.question_id
                WHERE a.created_at >= NOW() - INTERVAL '%s days'
                GROUP BY q.client_id
                HAVING (COUNT(CASE WHEN a.is_approved = false THEN 1 END)::float / COUNT(a.answer_id)) > 0.3
                ORDER BY rejection_rate DESC
                """,
                days
            )
            
            # Clients with no recent activity
            inactive_clients = await db.fetch(
                """
                SELECT client_id, MAX(created_at) as last_activity
                FROM questions
                GROUP BY client_id
                HAVING MAX(created_at) < NOW() - INTERVAL '%s days'
                ORDER BY last_activity
                """,
                days
            )
            
            # Combine all at-risk clients
            at_risk_clients = []
            
            for client in low_rating_clients:
                at_risk_clients.append({
                    "client_id": str(client["client_id"]),
                    "risk_type": "low_rating",
                    "risk_score": 1.0 - (client["avg_rating"] / 5.0),
                    "details": {
                        "avg_rating": float(client["avg_rating"]),
                        "rating_count": client["rating_count"]
                    }
                })
            
            for client in high_rejection_clients:
                at_risk_clients.append({
                    "client_id": str(client["client_id"]),
                    "risk_type": "high_rejection",
                    "risk_score": client["rejection_rate"],
                    "details": {
                        "rejection_rate": client["rejection_rate"],
                        "total_answers": client["total_answers"],
                        "rejections": client["rejections"]
                    }
                })
            
            for client in inactive_clients:
                at_risk_clients.append({
                    "client_id": str(client["client_id"]),
                    "risk_type": "inactive",
                    "risk_score": 0.8,  # High risk for inactive clients
                    "details": {
                        "last_activity": client["last_activity"].isoformat()
                    }
                })
            
            # Sort by risk score
            at_risk_clients.sort(key=lambda x: x["risk_score"], reverse=True)
            
            return {
                "at_risk_clients": at_risk_clients,
                "low_rating_count": len(low_rating_clients),
                "high_rejection_count": len(high_rejection_clients),
                "inactive_count": len(inactive_clients),
                "total_at_risk": len(at_risk_clients)
            }
            
        except Exception as e:
            logger.error(f"Error getting churn risk analysis: {e}")
            return {}
    
    async def _get_recent_activity(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        try:
            # Recent questions
            recent_questions = await db.fetch(
                """
                SELECT q.question_id, q.client_id, q.subject, q.status, q.created_at
                FROM questions q
                WHERE q.created_at >= NOW() - INTERVAL '%s days'
                ORDER BY q.created_at DESC
                LIMIT 20
                """,
                days
            )
            
            # Recent ratings
            recent_ratings = await db.fetch(
                """
                SELECT r.rating_id, r.question_id, r.score, r.created_at, q.subject
                FROM ratings r
                JOIN questions q ON r.question_id = q.question_id
                WHERE r.created_at >= NOW() - INTERVAL '%s days'
                ORDER BY r.created_at DESC
                LIMIT 20
                """,
                days
            )
            
            # Recent expert reviews
            recent_reviews = await db.fetch(
                """
                SELECT er.review_id, er.answer_id, er.is_approved, er.created_at, q.subject
                FROM expert_reviews er
                JOIN answers a ON er.answer_id = a.answer_id
                JOIN questions q ON a.question_id = q.question_id
                WHERE er.created_at >= NOW() - INTERVAL '%s days'
                ORDER BY er.created_at DESC
                LIMIT 20
                """,
                days
            )
            
            # Combine and sort activities
            activities = []
            
            for question in recent_questions:
                activities.append({
                    "type": "question_submitted",
                    "id": str(question["question_id"]),
                    "client_id": str(question["client_id"]),
                    "subject": question["subject"],
                    "status": question["status"],
                    "timestamp": question["created_at"].isoformat()
                })
            
            for rating in recent_ratings:
                activities.append({
                    "type": "rating_submitted",
                    "id": str(rating["rating_id"]),
                    "question_id": str(rating["question_id"]),
                    "score": rating["score"],
                    "subject": rating["subject"],
                    "timestamp": rating["created_at"].isoformat()
                })
            
            for review in recent_reviews:
                activities.append({
                    "type": "expert_review",
                    "id": str(review["review_id"]),
                    "answer_id": str(review["answer_id"]),
                    "is_approved": review["is_approved"],
                    "subject": review["subject"],
                    "timestamp": review["created_at"].isoformat()
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activities[:50]  # Return top 50 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    async def _get_compliance_metrics(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get compliance metrics"""
        try:
            # Plagiarism violations
            plagiarism_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE action = 'plagiarism_detected'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # AI content violations
            ai_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE action = 'ai_content_exceeded'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # VPN violations
            vpn_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE action = 'vpn_detected'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Total violations
            total_violations = plagiarism_violations + ai_violations + vpn_violations
            
            # Compliance rate
            total_actions = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            compliance_rate = 1.0 - (total_violations / total_actions) if total_actions > 0 else 1.0
            
            return {
                "plagiarism_violations": plagiarism_violations,
                "ai_violations": ai_violations,
                "vpn_violations": vpn_violations,
                "total_violations": total_violations,
                "compliance_rate": compliance_rate,
                "total_actions": total_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance metrics: {e}")
            return {}
    
    async def _get_expert_performance(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get expert performance metrics"""
        try:
            # Expert ratings
            expert_ratings = await db.fetch(
                """
                SELECT r.expert_id, 
                       AVG(r.score) as avg_rating,
                       COUNT(r.score) as total_ratings,
                       COUNT(CASE WHEN r.score >= 4 THEN 1 END) as high_ratings
                FROM ratings r
                WHERE r.created_at >= NOW() - INTERVAL '%s days'
                AND r.expert_id IS NOT NULL
                GROUP BY r.expert_id
                ORDER BY avg_rating DESC
                """,
                days
            )
            
            # Expert review counts
            expert_reviews = await db.fetch(
                """
                SELECT expert_id, 
                       COUNT(*) as total_reviews,
                       COUNT(CASE WHEN is_approved = true THEN 1 END) as approved_reviews,
                       COUNT(CASE WHEN is_approved = false THEN 1 END) as rejected_reviews
                FROM expert_reviews
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY expert_id
                """,
                days
            )
            
            # Combine expert data
            expert_performance = []
            for rating in expert_ratings:
                expert_id = str(rating["expert_id"])
                
                # Find corresponding review data
                review_data = next(
                    (r for r in expert_reviews if str(r["expert_id"]) == expert_id),
                    None
                )
                
                performance = {
                    "expert_id": expert_id,
                    "avg_rating": float(rating["avg_rating"]) if rating["avg_rating"] else 0.0,
                    "total_ratings": rating["total_ratings"],
                    "high_rating_percentage": (rating["high_ratings"] / rating["total_ratings"]) * 100 if rating["total_ratings"] > 0 else 0.0,
                    "total_reviews": review_data["total_reviews"] if review_data else 0,
                    "approval_rate": (review_data["approved_reviews"] / review_data["total_reviews"]) * 100 if review_data and review_data["total_reviews"] > 0 else 0.0
                }
                
                expert_performance.append(performance)
            
            return {
                "expert_performance": expert_performance,
                "total_experts": len(expert_performance),
                "avg_expert_rating": sum(p["avg_rating"] for p in expert_performance) / len(expert_performance) if expert_performance else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting expert performance: {e}")
            return {}
    
    async def _get_system_health_metrics(
        self,
        db: asyncpg.Connection,
        days: int
    ) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Queue lengths (placeholder - would need actual queue monitoring)
            queue_health = {
                "ai_processing_queue": 0,
                "humanization_queue": 0,
                "originality_check_queue": 0,
                "expert_review_queue": 0,
                "delivery_queue": 0
            }
            
            # Processing times
            processing_times = await db.fetch(
                """
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (a.created_at - q.created_at))) as avg_processing_time,
                    MAX(EXTRACT(EPOCH FROM (a.created_at - q.created_at))) as max_processing_time,
                    MIN(EXTRACT(EPOCH FROM (a.created_at - q.created_at))) as min_processing_time
                FROM questions q
                JOIN answers a ON q.question_id = a.question_id
                WHERE q.created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # Error rates
            error_rates = await db.fetch(
                """
                SELECT 
                    COUNT(CASE WHEN action LIKE '%error%' OR action LIKE '%failed%' THEN 1 END) as error_count,
                    COUNT(*) as total_actions
                FROM audit_logs
                WHERE created_at >= NOW() - INTERVAL '%s days'
                """,
                days
            )
            
            # System uptime (placeholder)
            uptime_percentage = 99.9  # Would be calculated from actual monitoring
            
            return {
                "queue_health": queue_health,
                "processing_times": {
                    "avg_seconds": float(processing_times[0]["avg_processing_time"]) if processing_times[0]["avg_processing_time"] else 0.0,
                    "max_seconds": float(processing_times[0]["max_processing_time"]) if processing_times[0]["max_processing_time"] else 0.0,
                    "min_seconds": float(processing_times[0]["min_processing_time"]) if processing_times[0]["min_processing_time"] else 0.0
                },
                "error_rate": (error_rates[0]["error_count"] / error_rates[0]["total_actions"]) * 100 if error_rates[0]["total_actions"] > 0 else 0.0,
                "uptime_percentage": uptime_percentage
            }
            
        except Exception as e:
            logger.error(f"Error getting system health metrics: {e}")
            return {}
    
    async def admin_override(
        self,
        question_id: str,
        override_data: AdminOverride,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Perform admin override action"""
        try:
            if override_data.action == "reassign":
                if not override_data.expert_id:
                    return APIResponse(
                        success=False,
                        message="Expert ID required for reassignment"
                    )
                
                # Reassign question to expert
                await db.execute(
                    "UPDATE questions SET status = 'review' WHERE question_id = $1",
                    question_id
                )
                
                await db.execute(
                    "UPDATE answers SET expert_id = $1 WHERE question_id = $2",
                    override_data.expert_id,
                    question_id
                )
                
                # Log override action
                await self.audit_service.log_action(
                    db=db,
                    action="admin_override_reassign",
                    user_id="admin",  # Would be actual admin user ID
                    question_id=question_id,
                    details={
                        "action": "reassign",
                        "expert_id": override_data.expert_id,
                        "reason": override_data.reason
                    }
                )
                
                return APIResponse(
                    success=True,
                    message="Question reassigned successfully",
                    data={
                        "question_id": question_id,
                        "expert_id": override_data.expert_id
                    }
                )
                
            elif override_data.action == "approve":
                # Approve answer
                await db.execute(
                    "UPDATE answers SET is_approved = true WHERE question_id = $1",
                    question_id
                )
                
                await db.execute(
                    "UPDATE questions SET status = 'delivered' WHERE question_id = $1",
                    question_id
                )
                
                # Log override action
                await self.audit_service.log_action(
                    db=db,
                    action="admin_override_approve",
                    user_id="admin",  # Would be actual admin user ID
                    question_id=question_id,
                    details={
                        "action": "approve",
                        "reason": override_data.reason
                    }
                )
                
                return APIResponse(
                    success=True,
                    message="Answer approved successfully",
                    data={"question_id": question_id}
                )
            
            else:
                return APIResponse(
                    success=False,
                    message="Invalid override action"
                )
                
        except Exception as e:
            logger.error(f"Error performing admin override: {e}")
            return APIResponse(
                success=False,
                message="Failed to perform admin override",
                data={"error": str(e)}
            )
    
    async def export_data(
        self,
        db: asyncpg.Connection,
        data_type: str,
        days: int = 30
    ) -> APIResponse:
        """Export data for analysis"""
        try:
            if data_type == "questions":
                data = await db.fetch(
                    """
                    SELECT q.*, a.ai_response, a.humanized_response, a.expert_response, a.confidence_score
                    FROM questions q
                    LEFT JOIN answers a ON q.question_id = a.question_id
                    WHERE q.created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY q.created_at DESC
                    """,
                    days
                )
                
            elif data_type == "ratings":
                data = await db.fetch(
                    """
                    SELECT r.*, q.subject, q.type
                    FROM ratings r
                    JOIN questions q ON r.question_id = q.question_id
                    WHERE r.created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY r.created_at DESC
                    """,
                    days
                )
                
            elif data_type == "audit_logs":
                data = await db.fetch(
                    """
                    SELECT * FROM audit_logs
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY created_at DESC
                    """,
                    days
                )
                
            else:
                return APIResponse(
                    success=False,
                    message="Invalid data type. Must be 'questions', 'ratings', or 'audit_logs'"
                )
            
            # Convert to JSON-serializable format
            export_data = []
            for row in data:
                export_data.append(dict(row))
            
            return APIResponse(
                success=True,
                message="Data exported successfully",
                data={
                    "data_type": data_type,
                    "count": len(export_data),
                    "data": export_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return APIResponse(
                success=False,
                message="Failed to export data",
                data={"error": str(e)}
            )

