import asyncio
import logging
from typing import Dict, Any, Optional, List
import asyncpg
from app.models import RatingCreate, RatingResponse, APIResponse
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class RatingService:
    """Service for handling ratings and feedback"""
    
    def __init__(self):
        self.audit_service = AuditService()
        self.notification_service = NotificationService()
    
    async def submit_rating(
        self,
        rating_data: RatingCreate,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Submit a rating for an answer"""
        try:
            # Validate rating data
            validation_result = await self._validate_rating(rating_data)
            if not validation_result["valid"]:
                return APIResponse(
                    success=False,
                    message=validation_result["message"],
                    data={"errors": validation_result["errors"]}
                )
            
            # Check if rating already exists
            existing_rating = await self._get_existing_rating(
                db,
                rating_data.question_id
            )
            
            if existing_rating:
                return APIResponse(
                    success=False,
                    message="Rating already exists for this question"
                )
            
            # Store rating in database
            rating_id = await self._store_rating(db, rating_data)
            
            # Update expert metrics
            await self._update_expert_metrics(db, rating_data)
            
            # Send notification to expert
            await self._notify_expert_about_rating(
                db,
                rating_data.question_id,
                rating_data.score,
                rating_data.comment
            )
            
            # Log rating submission
            await self.audit_service.log_action(
                db=db,
                action="rating_submitted",
                user_id=await self._get_client_id_from_question(db, rating_data.question_id),
                question_id=rating_data.question_id,
                details={
                    "rating_id": str(rating_id),
                    "score": rating_data.score,
                    "has_comment": bool(rating_data.comment)
                }
            )
            
            logger.info(f"Rating {rating_id} submitted successfully")
            
            return APIResponse(
                success=True,
                message="Rating submitted successfully",
                data={
                    "rating_id": str(rating_id),
                    "score": rating_data.score,
                    "comment": rating_data.comment
                }
            )
            
        except Exception as e:
            logger.error(f"Error submitting rating: {e}")
            return APIResponse(
                success=False,
                message="Failed to submit rating",
                data={"error": str(e)}
            )
    
    async def _validate_rating(self, rating_data: RatingCreate) -> Dict[str, Any]:
        """Validate rating data"""
        errors = []
        
        # Check score range
        if not (1 <= rating_data.score <= 5):
            errors.append("Rating score must be between 1 and 5")
        
        # Check comment length
        if rating_data.comment and len(rating_data.comment) > 1000:
            errors.append("Comment too long. Maximum 1000 characters allowed")
        
        # Check for inappropriate content in comment
        if rating_data.comment:
            inappropriate_words = ["spam", "scam", "fake", "terrible", "awful", "horrible"]
            comment_lower = rating_data.comment.lower()
            for word in inappropriate_words:
                if word in comment_lower:
                    errors.append("Comment contains inappropriate content")
                    break
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Validation failed" if errors else "Validation passed"
        }
    
    async def _get_existing_rating(
        self,
        db: asyncpg.Connection,
        question_id: str
    ) -> Optional[Dict[str, Any]]:
        """Check if rating already exists for question"""
        try:
            row = await db.fetchrow(
                "SELECT rating_id, score, comment FROM ratings WHERE question_id = $1",
                question_id
            )
            
            if row:
                return {
                    "rating_id": str(row["rating_id"]),
                    "score": row["score"],
                    "comment": row["comment"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking existing rating: {e}")
            return None
    
    async def _store_rating(
        self,
        db: asyncpg.Connection,
        rating_data: RatingCreate
    ) -> str:
        """Store rating in database"""
        try:
            rating_id = await db.fetchval(
                """
                INSERT INTO ratings (rating_id, question_id, expert_id, score, comment)
                VALUES (gen_random_uuid(), $1, $2, $3, $4)
                RETURNING rating_id
                """,
                rating_data.question_id,
                rating_data.expert_id,
                rating_data.score,
                rating_data.comment
            )
            
            return str(rating_id)
            
        except Exception as e:
            logger.error(f"Error storing rating: {e}")
            raise
    
    async def _update_expert_metrics(
        self,
        db: asyncpg.Connection,
        rating_data: RatingCreate
    ) -> None:
        """Update expert metrics based on rating"""
        try:
            if rating_data.expert_id:
                # Get current expert metrics
                current_metrics = await db.fetchrow(
                    """
                    SELECT avg_rating, total_ratings, total_score
                    FROM expert_metrics
                    WHERE expert_id = $1
                    """,
                    rating_data.expert_id
                )
                
                if current_metrics:
                    # Update existing metrics
                    new_total_ratings = current_metrics["total_ratings"] + 1
                    new_total_score = current_metrics["total_score"] + rating_data.score
                    new_avg_rating = new_total_score / new_total_ratings
                    
                    await db.execute(
                        """
                        UPDATE expert_metrics
                        SET avg_rating = $1, total_ratings = $2, total_score = $3
                        WHERE expert_id = $4
                        """,
                        new_avg_rating,
                        new_total_ratings,
                        new_total_score,
                        rating_data.expert_id
                    )
                else:
                    # Create new metrics record
                    await db.execute(
                        """
                        INSERT INTO expert_metrics (expert_id, avg_rating, total_ratings, total_score)
                        VALUES ($1, $2, 1, $3)
                        """,
                        rating_data.expert_id,
                        rating_data.score,
                        rating_data.score
                    )
                
        except Exception as e:
            logger.error(f"Error updating expert metrics: {e}")
    
    async def _notify_expert_about_rating(
        self,
        db: asyncpg.Connection,
        question_id: str,
        score: int,
        comment: str
    ) -> None:
        """Send notification to expert about new rating"""
        try:
            # Get expert ID from question
            expert_id = await self._get_expert_id_from_question(db, question_id)
            if expert_id:
                await self.notification_service.send_rating_notification(
                    expert_id,
                    question_id,
                    score,
                    comment
                )
                
        except Exception as e:
            logger.error(f"Error notifying expert about rating: {e}")
    
    async def _get_client_id_from_question(
        self,
        db: asyncpg.Connection,
        question_id: str
    ) -> Optional[str]:
        """Get client ID from question ID"""
        try:
            client_id = await db.fetchval(
                "SELECT client_id FROM questions WHERE question_id = $1",
                question_id
            )
            return str(client_id) if client_id else None
            
        except Exception as e:
            logger.error(f"Error getting client ID from question: {e}")
            return None
    
    async def _get_expert_id_from_question(
        self,
        db: asyncpg.Connection,
        question_id: str
    ) -> Optional[str]:
        """Get expert ID from question ID"""
        try:
            expert_id = await db.fetchval(
                """
                SELECT a.expert_id FROM answers a
                JOIN questions q ON a.question_id = q.question_id
                WHERE q.question_id = $1
                """,
                question_id
            )
            return str(expert_id) if expert_id else None
            
        except Exception as e:
            logger.error(f"Error getting expert ID from question: {e}")
            return None
    
    async def get_ratings(
        self,
        db: asyncpg.Connection,
        question_id: Optional[str] = None,
        expert_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> APIResponse:
        """Get ratings with optional filtering"""
        try:
            query = """
                SELECT r.*, q.subject, q.type as question_type
                FROM ratings r
                JOIN questions q ON r.question_id = q.question_id
                WHERE 1=1
            """
            params = []
            param_count = 0
            
            if question_id:
                param_count += 1
                query += f" AND r.question_id = ${param_count}"
                params.append(question_id)
            
            if expert_id:
                param_count += 1
                query += f" AND r.expert_id = ${param_count}"
                params.append(expert_id)
            
            query += f" ORDER BY r.created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            
            rows = await db.fetch(query, *params)
            
            ratings = []
            for row in rows:
                ratings.append({
                    "rating_id": str(row["rating_id"]),
                    "question_id": str(row["question_id"]),
                    "expert_id": str(row["expert_id"]) if row["expert_id"] else None,
                    "score": row["score"],
                    "comment": row["comment"],
                    "created_at": row["created_at"].isoformat(),
                    "question_subject": row["subject"],
                    "question_type": row["type"]
                })
            
            return APIResponse(
                success=True,
                message="Ratings retrieved successfully",
                data={"ratings": ratings, "count": len(ratings)}
            )
            
        except Exception as e:
            logger.error(f"Error getting ratings: {e}")
            return APIResponse(
                success=False,
                message="Failed to get ratings",
                data={"error": str(e)}
            )
    
    async def get_expert_ratings(
        self,
        db: asyncpg.Connection,
        expert_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> APIResponse:
        """Get ratings for a specific expert"""
        try:
            # Get ratings
            ratings_result = await self.get_ratings(
                db=db,
                expert_id=expert_id,
                limit=limit,
                offset=offset
            )
            
            if not ratings_result.success:
                return ratings_result
            
            # Get expert metrics
            metrics = await self._get_expert_metrics(db, expert_id)
            
            return APIResponse(
                success=True,
                message="Expert ratings retrieved successfully",
                data={
                    "ratings": ratings_result.data["ratings"],
                    "count": ratings_result.data["count"],
                    "metrics": metrics
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting expert ratings: {e}")
            return APIResponse(
                success=False,
                message="Failed to get expert ratings",
                data={"error": str(e)}
            )
    
    async def _get_expert_metrics(
        self,
        db: asyncpg.Connection,
        expert_id: str
    ) -> Dict[str, Any]:
        """Get expert metrics"""
        try:
            row = await db.fetchrow(
                """
                SELECT avg_rating, total_ratings, total_score
                FROM expert_metrics
                WHERE expert_id = $1
                """,
                expert_id
            )
            
            if row:
                return {
                    "avg_rating": float(row["avg_rating"]),
                    "total_ratings": row["total_ratings"],
                    "total_score": row["total_score"]
                }
            else:
                return {
                    "avg_rating": 0.0,
                    "total_ratings": 0,
                    "total_score": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting expert metrics: {e}")
            return {
                "avg_rating": 0.0,
                "total_ratings": 0,
                "total_score": 0
            }
    
    async def get_rating_statistics(
        self,
        db: asyncpg.Connection,
        expert_id: Optional[str] = None,
        days: int = 30
    ) -> APIResponse:
        """Get rating statistics"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_ratings,
                    AVG(score) as avg_rating,
                    MIN(score) as min_rating,
                    MAX(score) as max_rating,
                    COUNT(CASE WHEN score = 5 THEN 1 END) as five_star_count,
                    COUNT(CASE WHEN score = 4 THEN 1 END) as four_star_count,
                    COUNT(CASE WHEN score = 3 THEN 1 END) as three_star_count,
                    COUNT(CASE WHEN score = 2 THEN 1 END) as two_star_count,
                    COUNT(CASE WHEN score = 1 THEN 1 END) as one_star_count
                FROM ratings r
                WHERE r.created_at >= NOW() - INTERVAL '%s days'
            """
            params = [days]
            
            if expert_id:
                query += " AND r.expert_id = $2"
                params.append(expert_id)
            
            row = await db.fetchrow(query, *params)
            
            if row:
                statistics = {
                    "total_ratings": row["total_ratings"],
                    "avg_rating": float(row["avg_rating"]) if row["avg_rating"] else 0.0,
                    "min_rating": row["min_rating"],
                    "max_rating": row["max_rating"],
                    "rating_distribution": {
                        "5_star": row["five_star_count"],
                        "4_star": row["four_star_count"],
                        "3_star": row["three_star_count"],
                        "2_star": row["two_star_count"],
                        "1_star": row["one_star_count"]
                    }
                }
                
                return APIResponse(
                    success=True,
                    message="Rating statistics retrieved successfully",
                    data=statistics
                )
            else:
                return APIResponse(
                    success=True,
                    message="No ratings found",
                    data={
                        "total_ratings": 0,
                        "avg_rating": 0.0,
                        "min_rating": 0,
                        "max_rating": 0,
                        "rating_distribution": {
                            "5_star": 0,
                            "4_star": 0,
                            "3_star": 0,
                            "2_star": 0,
                            "1_star": 0
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Error getting rating statistics: {e}")
            return APIResponse(
                success=False,
                message="Failed to get rating statistics",
                data={"error": str(e)}
            )
    
    async def update_rating(
        self,
        rating_id: str,
        new_score: int,
        new_comment: str,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Update an existing rating"""
        try:
            # Validate new rating data
            if not (1 <= new_score <= 5):
                return APIResponse(
                    success=False,
                    message="Rating score must be between 1 and 5"
                )
            
            if new_comment and len(new_comment) > 1000:
                return APIResponse(
                    success=False,
                    message="Comment too long. Maximum 1000 characters allowed"
                )
            
            # Get current rating
            current_rating = await db.fetchrow(
                "SELECT score, expert_id FROM ratings WHERE rating_id = $1",
                rating_id
            )
            
            if not current_rating:
                return APIResponse(
                    success=False,
                    message="Rating not found"
                )
            
            # Update rating
            await db.execute(
                "UPDATE ratings SET score = $1, comment = $2 WHERE rating_id = $3",
                new_score,
                new_comment,
                rating_id
            )
            
            # Update expert metrics if score changed
            if current_rating["score"] != new_score and current_rating["expert_id"]:
                await self._update_expert_metrics_for_rating_change(
                    db,
                    current_rating["expert_id"],
                    current_rating["score"],
                    new_score
                )
            
            # Log rating update
            await self.audit_service.log_action(
                db=db,
                action="rating_updated",
                user_id=await self._get_client_id_from_rating(db, rating_id),
                question_id=await self._get_question_id_from_rating(db, rating_id),
                details={
                    "rating_id": rating_id,
                    "old_score": current_rating["score"],
                    "new_score": new_score,
                    "score_changed": current_rating["score"] != new_score
                }
            )
            
            return APIResponse(
                success=True,
                message="Rating updated successfully",
                data={
                    "rating_id": rating_id,
                    "score": new_score,
                    "comment": new_comment
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating rating: {e}")
            return APIResponse(
                success=False,
                message="Failed to update rating",
                data={"error": str(e)}
            )
    
    async def _update_expert_metrics_for_rating_change(
        self,
        db: asyncpg.Connection,
        expert_id: str,
        old_score: int,
        new_score: int
    ) -> None:
        """Update expert metrics when rating score changes"""
        try:
            score_difference = new_score - old_score
            
            await db.execute(
                """
                UPDATE expert_metrics
                SET total_score = total_score + $1,
                    avg_rating = (total_score + $1) / total_ratings
                WHERE expert_id = $2
                """,
                score_difference,
                expert_id
            )
            
        except Exception as e:
            logger.error(f"Error updating expert metrics for rating change: {e}")
    
    async def _get_client_id_from_rating(
        self,
        db: asyncpg.Connection,
        rating_id: str
    ) -> Optional[str]:
        """Get client ID from rating ID"""
        try:
            client_id = await db.fetchval(
                """
                SELECT q.client_id FROM ratings r
                JOIN questions q ON r.question_id = q.question_id
                WHERE r.rating_id = $1
                """,
                rating_id
            )
            return str(client_id) if client_id else None
            
        except Exception as e:
            logger.error(f"Error getting client ID from rating: {e}")
            return None
    
    async def _get_question_id_from_rating(
        self,
        db: asyncpg.Connection,
        rating_id: str
    ) -> Optional[str]:
        """Get question ID from rating ID"""
        try:
            question_id = await db.fetchval(
                "SELECT question_id FROM ratings WHERE rating_id = $1",
                rating_id
            )
            return str(question_id) if question_id else None
            
        except Exception as e:
            logger.error(f"Error getting question ID from rating: {e}")
            return None

