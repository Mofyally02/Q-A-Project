"""
FastAPI Application Entry Point
Clean backbone implementation with health checks and routing
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.core.config import settings
from app.db.session import db
from app.api.v1.router import api_router
from app.utils.logging_config import setup_logging
from app.utils.cache import cache
from app.utils.queue import queue_service

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 60)
    
    try:
        # Initialize database connections
        await db.connect()
        logger.info("✓ Database connections established")
        
        # Initialize cache
        try:
            await cache.connect()
            logger.info("✓ Cache (Redis) connection established")
        except Exception as e:
            logger.warning(f"⚠ Cache connection failed: {e}. Continuing without cache.")
        
        # Initialize queue service
        try:
            await queue_service.connect()
            logger.info("✓ Queue service (RabbitMQ) connection established")
        except Exception as e:
            logger.warning(f"⚠ Queue service connection failed: {e}. Continuing without queue.")
        
        logger.info("✓ Application startup complete")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down application...")
    
    try:
        # Close queue service
        try:
            await queue_service.disconnect()
            logger.info("✓ Queue service connection closed")
        except Exception as e:
            logger.warning(f"⚠ Queue service disconnect error: {e}")
        
        # Close cache
        try:
            await cache.disconnect()
            logger.info("✓ Cache connection closed")
        except Exception as e:
            logger.warning(f"⚠ Cache disconnect error: {e}")
        
        # Close database connections
        await db.disconnect()
        logger.info("✓ Database connections closed")
        
        logger.info("✓ Application shutdown complete")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for AL-Tech Academy's AI-powered Q&A system",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (optional, can be configured)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure based on your domain
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

