"""
Comprehensive Health Check Endpoint
Returns status of all interconnected services in one API call
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncpg
import time
import os
from datetime import datetime
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Track startup time for uptime calculation
START_TIME = time.time()


async def check_database(db: asyncpg.Connection) -> Dict[str, Any]:
    """Check main database connectivity and basic query"""
    start = time.time()
    try:
        # Test basic query
        result = await db.fetchval("SELECT 1")
        if result != 1:
            return {"status": "unhealthy", "error": "Database query failed", "latency_ms": int((time.time() - start) * 1000)}
        
        # Check if tables exist
        table_count = await db.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "table_count": table_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": int((time.time() - start) * 1000)
        }


async def check_auth_database(auth_db: asyncpg.Connection) -> Dict[str, Any]:
    """Check auth database connectivity"""
    start = time.time()
    try:
        result = await auth_db.fetchval("SELECT 1")
        if result != 1:
            return {"status": "unhealthy", "error": "Auth database query failed", "latency_ms": int((time.time() - start) * 1000)}
        
        # Check if users table exists
        users_table = await auth_db.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "users_table_exists": users_table
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": int((time.time() - start) * 1000)
        }


def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity"""
    start = time.time()
    try:
        from app.database import db
        redis_client = db.redis_client
        
        if redis_client is None:
            return {
                "status": "unhealthy",
                "error": "Redis client not initialized",
                "latency_ms": int((time.time() - start) * 1000)
            }
        
        redis_client.ping()
        
        # Test basic operations
        test_key = "health_check_test"
        redis_client.set(test_key, "test", ex=10)
        value = redis_client.get(test_key)
        redis_client.delete(test_key)
        
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": int((time.time() - start) * 1000)
        }


async def check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ connectivity"""
    start = time.time()
    try:
        import pika
        from app.config import settings
        
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=1
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Try to declare a test queue
        channel.queue_declare(queue="health_check", durable=False, auto_delete=True)
        connection.close()
        
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms
        }
    except ImportError:
        return {
            "status": "degraded",
            "error": "pika not installed",
            "latency_ms": int((time.time() - start) * 1000)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": int((time.time() - start) * 1000)
        }


async def check_external_api(name: str, url: str, headers: Dict[str, str] = None, timeout: int = 5) -> Dict[str, Any]:
    """Check external API connectivity"""
    start = time.time()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                latency_ms = int((time.time() - start) * 1000)
                return {
                    "status": "healthy",
                    "latency_ms": latency_ms
                }
            else:
                return {
                    "status": "degraded",
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": int((time.time() - start) * 1000)
                }
    except ImportError:
        return {
            "status": "degraded",
            "error": "httpx not installed",
            "latency_ms": int((time.time() - start) * 1000)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": int((time.time() - start) * 1000)
        }


def check_api_keys() -> Dict[str, Any]:
    """Check if API keys are configured (not their validity, just presence)"""
    keys_status = {}
    
    api_keys = {
        "openai": settings.openai_api_key,
        "xai": settings.xai_api_key,
        "google": settings.google_api_key,
        "anthropic": settings.anthropic_api_key,
        "stealth": settings.stealth_api_key,
        "turnitin": settings.turnitin_api_key,
    }
    
    for key_name, key_value in api_keys.items():
        keys_status[key_name] = {
            "configured": bool(key_value and len(key_value) > 10),
            "masked": f"{key_value[:4]}...{key_value[-4:]}" if key_value and len(key_value) > 8 else "not_set"
        }
    
    return keys_status


@router.get("")
async def health_check():
    """
    Comprehensive health check endpoint
    
    Returns status of all interconnected services:
    - Database (main and auth)
    - Redis
    - RabbitMQ
    - External APIs (if configured)
    - API Keys configuration
    """
    from app.database import db
    
    # Get connections manually for health check
    db_status = {"status": "unhealthy", "error": "Not checked"}
    auth_db_status = {"status": "unhealthy", "error": "Not checked"}
    
    try:
        async with db.pool.acquire() as conn:
            db_status = await check_database(conn)
    except Exception as e:
        db_status = {"status": "unhealthy", "error": str(e)}
    
    try:
        async with db.auth_pool.acquire() as conn:
            auth_db_status = await check_auth_database(conn)
    except Exception as e:
        auth_db_status = {"status": "unhealthy", "error": str(e)}
    redis_status = check_redis()
    rabbitmq_status = await check_rabbitmq()
    api_keys_status = check_api_keys()
    
    # Build services dict
    services = {
        "database": db_status,
        "auth_database": auth_db_status,
        "redis": redis_status,
        "rabbitmq": rabbitmq_status,
        "api_keys": api_keys_status
    }
    
    # Check external APIs if keys are configured
    if settings.openai_api_key:
        openai_headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        services["openai"] = await check_external_api(
            "openai",
            "https://api.openai.com/v1/models",
            openai_headers
        )
    
    # Determine overall status
    critical_services = ["database", "auth_database", "redis"]
    overall_status = "healthy"
    
    for svc in critical_services:
        if services.get(svc, {}).get("status") != "healthy":
            overall_status = "unhealthy"
            break
    
    # If any critical service is degraded, mark as degraded
    if overall_status == "healthy":
        for svc in critical_services:
            if services.get(svc, {}).get("status") == "degraded":
                overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": services,
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - START_TIME)
    }


@router.get("/database")
async def database_health_check():
    """Detailed database health check"""
    from app.database import db
    try:
        async with db.pool.acquire() as conn:
            # Get database info
            version = await conn.fetchval("SELECT version()")
            db_name = await conn.fetchval("SELECT current_database()")
            
            # Get table list
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            # Get row counts for main tables
            table_counts = {}
            main_tables = ["questions", "answers", "ratings", "expert_reviews", "audit_logs"]
            for table in main_tables:
                try:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = count
                except Exception:
                    table_counts[table] = "table_not_found"
            
            return {
                "status": "healthy",
                "database": db_name,
                "version": version.split(",")[0],  # Just the PostgreSQL version
                "tables": [t["table_name"] for t in tables],
                "table_counts": table_counts
            }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database health check failed: {str(e)}")


@router.get("/redis")
def redis_health_check():
    """Redis health check"""
    return check_redis()


@router.get("/full")
async def full_health_check():
    """
    Full system health check with detailed diagnostics
    Includes database schema validation, connection pool status, etc.
    """
    from app.database import db
    
    results = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }
    
    # Database pool status
    try:
        pool_status = {
            "main_pool_size": db.pool.get_size() if db.pool else 0,
            "main_pool_idle": db.pool.get_idle_size() if db.pool else 0,
            "auth_pool_size": db.auth_pool.get_size() if db.auth_pool else 0,
            "auth_pool_idle": db.auth_pool.get_idle_size() if db.auth_pool else 0,
        }
        results["checks"]["connection_pools"] = {"status": "healthy", "data": pool_status}
    except Exception as e:
        results["checks"]["connection_pools"] = {"status": "unhealthy", "error": str(e)}
    
    # Run all standard health checks
    health_result = await health_check()
    results["checks"]["services"] = health_result.get("services", {})
    results["status"] = health_result.get("status", "unhealthy")
    
    return results


@router.get("/rabbitmq")
async def rabbitmq_health_check():
    """RabbitMQ health check"""
    return await check_rabbitmq()

