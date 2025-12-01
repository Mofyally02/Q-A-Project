"""
Health check endpoints
Comprehensive health checks for all services
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import asyncpg
from datetime import datetime

from app.db.session import db, get_db, get_redis
from app.utils.queue import queue_service
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    Returns simple status without deep checks
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint
    Checks all services: PostgreSQL, Redis, RabbitMQ
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "services": {}
    }
    
    overall_healthy = True
    
    # Check PostgreSQL
    try:
        async for conn in get_db():
            await conn.fetchval("SELECT 1")
            health_status["services"]["postgresql"] = {
                "status": "healthy",
                "message": "Connection successful"
            }
            break
    except Exception as e:
        overall_healthy = False
        health_status["services"]["postgresql"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Check Redis (optional)
    try:
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
            health_status["services"]["redis"] = {
                "status": "healthy",
                "message": "Connection successful"
            }
        else:
            health_status["services"]["redis"] = {
                "status": "not_configured",
                "message": "Redis not available (optional service)"
            }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        # Don't mark overall as unhealthy - Redis is optional
    
    # Check RabbitMQ (optional)
    try:
        if queue_service.connection and not queue_service.connection.is_closed:
            health_status["services"]["rabbitmq"] = {
                "status": "healthy",
                "message": "Connection active"
            }
        else:
            health_status["services"]["rabbitmq"] = {
                "status": "not_configured",
                "message": "RabbitMQ not available (optional service)"
            }
    except Exception as e:
        health_status["services"]["rabbitmq"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        # Don't mark overall as unhealthy - RabbitMQ is optional
    
    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "degraded"
    
    # Return appropriate status code
    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    Checks if service is ready to accept traffic
    """
    try:
        # Check database
        async for conn in get_db():
            await conn.fetchval("SELECT 1")
            break
        
        # Check Redis (optional)
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
        # If Redis is None, that's okay - it's optional
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe
    Simple check if service is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/db")
async def db_health_check() -> Dict[str, Any]:
    """Check database health"""
    try:
        async for conn in get_db():
            result = await conn.fetchval("SELECT 1")
            return {
                "status": "healthy",
                "service": "postgresql",
                "message": "Connection successful",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "postgresql",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/cache")
async def cache_health_check() -> Dict[str, Any]:
    """Check cache (Redis) health"""
    try:
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
            return {
                "status": "healthy",
                "service": "redis",
                "message": "Connection successful",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "not_configured",
                "service": "redis",
                "message": "Redis not available (optional service)",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "redis",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/queue")
async def queue_health_check() -> Dict[str, Any]:
    """Check queue (RabbitMQ) health"""
    try:
        if queue_service.connection:
            # Check if connection is still open
            try:
                if hasattr(queue_service.connection, 'is_closed') and not queue_service.connection.is_closed:
                    return {
                        "status": "healthy",
                        "service": "rabbitmq",
                        "message": "Connection active",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except:
                pass
        return {
            "status": "not_configured",
            "service": "rabbitmq",
            "message": "RabbitMQ not available (optional service)",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "rabbitmq",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

