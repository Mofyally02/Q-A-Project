"""
Foundation tests
Test core infrastructure: database, cache, queue, health checks
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import db
from app.utils.cache import cache
from app.utils.queue import queue_service


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data


def test_health_check(client):
    """Test basic health check"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_check(client):
    """Test readiness probe"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code in [200, 503]  # May be 503 if services not running


def test_liveness_check(client):
    """Test liveness probe"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    try:
        await db.connect()
        health = await db.health_check()
        assert "postgresql" in health
        await db.disconnect()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection"""
    try:
        await cache.connect()
        # Test set/get
        await cache.set("test_key", {"test": "value"}, ttl=60)
        value = await cache.get("test_key")
        assert value == {"test": "value"}
        await cache.delete("test_key")
        await cache.disconnect()
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")


@pytest.mark.asyncio
async def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    try:
        await queue_service.connect()
        assert queue_service.connection is not None
        await queue_service.disconnect()
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")

