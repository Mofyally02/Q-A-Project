"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
import asyncpg
from app.core.config import settings
from app.db.session import db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[asyncpg.Pool, None]:
    """Create a test database connection pool"""
    # Use test database URL if available, otherwise use main DB
    test_db_url = settings.database_url.replace("altech_qa", "altech_qa_test")
    
    pool = await asyncpg.create_pool(
        test_db_url,
        min_size=2,
        max_size=5
    )
    
    yield pool
    
    await pool.close()


@pytest.fixture
async def db_session(test_db):
    """Create a database session for testing"""
    async with test_db.acquire() as connection:
        # Start a transaction
        async with connection.transaction():
            yield connection
            # Transaction will rollback automatically


@pytest.fixture(autouse=True)
async def setup_test_db(test_db):
    """Setup test database before each test"""
    # Run migrations or create test schema
    # This is a placeholder - implement based on your needs
    yield
    # Cleanup after test

