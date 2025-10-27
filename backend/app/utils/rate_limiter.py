import asyncio
import time
from typing import Dict, Any, Optional
from app.database import get_redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting utility for API endpoints"""
    
    def __init__(self):
        self.redis_client = None
    
    async def _get_redis(self):
        """Get Redis client"""
        if not self.redis_client:
            self.redis_client = get_redis()
        return self.redis_client
    
    async def check_rate_limit(
        self,
        user_id: str,
        action: str,
        max_requests: int = 100,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check if user has exceeded rate limit for an action"""
        try:
            redis_client = await self._get_redis()
            
            # Create rate limit key
            key = f"rate_limit:{user_id}:{action}"
            
            # Get current count
            current_count = await redis_client.get(key)
            
            if current_count is None:
                # First request in window
                await redis_client.setex(key, window_seconds, 1)
                return {
                    "allowed": True,
                    "remaining": max_requests - 1,
                    "reset_time": int(time.time()) + window_seconds
                }
            
            current_count = int(current_count)
            
            if current_count >= max_requests:
                # Rate limit exceeded
                ttl = await redis_client.ttl(key)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": int(time.time()) + ttl,
                    "message": f"Rate limit exceeded. Try again in {ttl} seconds."
                }
            
            # Increment counter
            await redis_client.incr(key)
            
            return {
                "allowed": True,
                "remaining": max_requests - current_count - 1,
                "reset_time": int(time.time()) + window_seconds
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request if rate limiting fails
            return {
                "allowed": True,
                "remaining": max_requests,
                "reset_time": int(time.time()) + window_seconds,
                "error": "Rate limiting temporarily unavailable"
            }
    
    async def check_endpoint_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Dict[str, Any]:
        """Check rate limit for specific endpoint"""
        return await self.check_rate_limit(
            user_id,
            f"endpoint:{endpoint}",
            max_requests,
            window_seconds
        )
    
    async def check_question_submission_limit(
        self,
        user_id: str,
        max_questions: int = 10,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check rate limit for question submissions"""
        return await self.check_rate_limit(
            user_id,
            "question_submission",
            max_questions,
            window_seconds
        )
    
    async def check_rating_limit(
        self,
        user_id: str,
        max_ratings: int = 5,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check rate limit for ratings"""
        return await self.check_rate_limit(
            user_id,
            "rating_submission",
            max_ratings,
            window_seconds
        )
    
    async def check_expert_review_limit(
        self,
        expert_id: str,
        max_reviews: int = 20,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check rate limit for expert reviews"""
        return await self.check_rate_limit(
            expert_id,
            "expert_review",
            max_reviews,
            window_seconds
        )
    
    async def reset_rate_limit(
        self,
        user_id: str,
        action: str
    ) -> bool:
        """Reset rate limit for user and action"""
        try:
            redis_client = await self._get_redis()
            key = f"rate_limit:{user_id}:{action}"
            await redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
            return False
    
    async def get_rate_limit_status(
        self,
        user_id: str,
        action: str
    ) -> Dict[str, Any]:
        """Get current rate limit status without incrementing"""
        try:
            redis_client = await self._get_redis()
            key = f"rate_limit:{user_id}:{action}"
            
            current_count = await redis_client.get(key)
            ttl = await redis_client.ttl(key)
            
            if current_count is None:
                return {
                    "current_count": 0,
                    "remaining": 100,  # Default max
                    "reset_time": int(time.time()) + 3600,
                    "is_limited": False
                }
            
            current_count = int(current_count)
            
            return {
                "current_count": current_count,
                "remaining": max(0, 100 - current_count),  # Default max
                "reset_time": int(time.time()) + ttl,
                "is_limited": current_count >= 100  # Default max
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {
                "current_count": 0,
                "remaining": 100,
                "reset_time": int(time.time()) + 3600,
                "is_limited": False,
                "error": str(e)
            }
    
    async def check_global_rate_limit(
        self,
        ip_address: str,
        max_requests: int = 1000,
        window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Check global rate limit by IP address"""
        return await self.check_rate_limit(
            f"ip:{ip_address}",
            "global",
            max_requests,
            window_seconds
        )
    
    async def check_user_question_limit(
        self,
        user_id: str,
        max_questions_per_day: int = 50
    ) -> Dict[str, Any]:
        """Check daily question limit for user"""
        return await self.check_rate_limit(
            user_id,
            "daily_questions",
            max_questions_per_day,
            86400  # 24 hours
        )
    
    async def check_expert_workload_limit(
        self,
        expert_id: str,
        max_questions_per_day: int = 100
    ) -> Dict[str, Any]:
        """Check daily workload limit for expert"""
        return await self.check_rate_limit(
            expert_id,
            "daily_expert_work",
            max_questions_per_day,
            86400  # 24 hours
        )
    
    async def get_user_rate_limits(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get all rate limits for a user"""
        try:
            redis_client = await self._get_redis()
            
            # Get all rate limit keys for user
            pattern = f"rate_limit:{user_id}:*"
            keys = await redis_client.keys(pattern)
            
            rate_limits = {}
            
            for key in keys:
                action = key.split(":")[-1]
                current_count = await redis_client.get(key)
                ttl = await redis_client.ttl(key)
                
                rate_limits[action] = {
                    "current_count": int(current_count) if current_count else 0,
                    "reset_time": int(time.time()) + ttl if ttl > 0 else 0
                }
            
            return rate_limits
            
        except Exception as e:
            logger.error(f"Error getting user rate limits: {e}")
            return {}
    
    async def clear_user_rate_limits(
        self,
        user_id: str
    ) -> bool:
        """Clear all rate limits for a user"""
        try:
            redis_client = await self._get_redis()
            
            # Get all rate limit keys for user
            pattern = f"rate_limit:{user_id}:*"
            keys = await redis_client.keys(pattern)
            
            if keys:
                await redis_client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing user rate limits: {e}")
            return False
