import logging
from typing import Dict, Any, Optional
from uuid import uuid4
import asyncpg
from app.models import AuditLogCreate, AuditLogResponse
from app.config import settings

logger = logging.getLogger(__name__)

class AuditService:
    """Service for handling audit logging and compliance tracking"""
    
    async def log_action(
        self,
        db: asyncpg.Connection,
        action: str,
        user_id: str,
        question_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log an action for audit purposes"""
        try:
            log_id = uuid4()
            
            await db.execute(
                """
                INSERT INTO audit_logs (log_id, action, user_id, question_id, details)
                VALUES ($1, $2, $3, $4, $5)
                """,
                log_id,
                action,
                user_id,
                question_id,
                details or {}
            )
            
            logger.info(f"Audit log created: {action} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            return False
    
    async def get_audit_logs(
        self,
        db: asyncpg.Connection,
        user_id: Optional[str] = None,
        question_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """Retrieve audit logs with optional filtering"""
        try:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            param_count = 0
            
            if user_id:
                param_count += 1
                query += f" AND user_id = ${param_count}"
                params.append(user_id)
            
            if question_id:
                param_count += 1
                query += f" AND question_id = ${param_count}"
                params.append(question_id)
            
            if action:
                param_count += 1
                query += f" AND action = ${param_count}"
                params.append(action)
            
            query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            
            rows = await db.fetch(query, *params)
            
            logs = []
            for row in rows:
                logs.append({
                    "log_id": str(row["log_id"]),
                    "action": row["action"],
                    "user_id": str(row["user_id"]),
                    "question_id": str(row["question_id"]) if row["question_id"] else None,
                    "details": row["details"],
                    "created_at": row["created_at"].isoformat()
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            return []
    
    async def get_user_activity_summary(
        self,
        db: asyncpg.Connection,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get activity summary for a user over specified days"""
        try:
            # Get total actions
            total_actions = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
                """,
                user_id,
                days
            )
            
            # Get actions by type
            action_counts = await db.fetch(
                """
                SELECT action, COUNT(*) as count 
                FROM audit_logs 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY action
                ORDER BY count DESC
                """,
                user_id,
                days
            )
            
            # Get recent activity
            recent_activity = await db.fetch(
                """
                SELECT action, question_id, created_at, details
                FROM audit_logs 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT 10
                """,
                user_id
            )
            
            return {
                "total_actions": total_actions,
                "action_breakdown": {row["action"]: row["count"] for row in action_counts},
                "recent_activity": [
                    {
                        "action": row["action"],
                        "question_id": str(row["question_id"]) if row["question_id"] else None,
                        "created_at": row["created_at"].isoformat(),
                        "details": row["details"]
                    }
                    for row in recent_activity
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get user activity summary: {e}")
            return {}
    
    async def check_compliance_violations(
        self,
        db: asyncpg.Connection,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Check for compliance violations for a user"""
        try:
            # Check for plagiarism violations
            plagiarism_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE user_id = $1 
                AND action = 'plagiarism_detected'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                user_id,
                days
            )
            
            # Check for AI content violations
            ai_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE user_id = $1 
                AND action = 'ai_content_exceeded'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                user_id,
                days
            )
            
            # Check for VPN violations
            vpn_violations = await db.fetchval(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE user_id = $1 
                AND action = 'vpn_detected'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                user_id,
                days
            )
            
            # Calculate risk score
            risk_score = (plagiarism_violations * 3 + ai_violations * 2 + vpn_violations * 1) / max(days, 1)
            
            return {
                "plagiarism_violations": plagiarism_violations,
                "ai_violations": ai_violations,
                "vpn_violations": vpn_violations,
                "risk_score": min(risk_score, 10.0),  # Cap at 10
                "compliance_status": "compliant" if risk_score < 1.0 else "at_risk" if risk_score < 3.0 else "non_compliant"
            }
            
        except Exception as e:
            logger.error(f"Failed to check compliance violations: {e}")
            return {}
    
    async def log_plagiarism_detection(
        self,
        db: asyncpg.Connection,
        question_id: str,
        user_id: str,
        similarity_score: float,
        source_urls: list
    ) -> bool:
        """Log plagiarism detection for compliance tracking"""
        return await self.log_action(
            db=db,
            action="plagiarism_detected",
            user_id=user_id,
            question_id=question_id,
            details={
                "similarity_score": similarity_score,
                "source_urls": source_urls,
                "penalty_applied": similarity_score > 0.1  # 10% threshold
            }
        )
    
    async def log_ai_content_detection(
        self,
        db: asyncpg.Connection,
        question_id: str,
        user_id: str,
        ai_score: float
    ) -> bool:
        """Log AI content detection for compliance tracking"""
        return await self.log_action(
            db=db,
            action="ai_content_exceeded",
            user_id=user_id,
            question_id=question_id,
            details={
                "ai_score": ai_score,
                "threshold_exceeded": ai_score > settings.ai_content_threshold
            }
        )
    
    async def log_vpn_detection(
        self,
        db: asyncpg.Connection,
        user_id: str,
        ip_address: str,
        vpn_provider: str
    ) -> bool:
        """Log VPN detection for compliance tracking"""
        return await self.log_action(
            db=db,
            action="vpn_detected",
            user_id=user_id,
            details={
                "ip_address": ip_address,
                "vpn_provider": vpn_provider,
                "blocked": True
            }
        )
