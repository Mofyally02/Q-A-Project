#!/usr/bin/env python3
"""
Backend Server Startup Script
This script starts the FastAPI backend server
"""

import logging
import sys
from pathlib import Path

import uvicorn

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("🚀 Starting AI Q&A System Backend Server")
        logger.info("=" * 50)
        
        # Import settings to check configuration
        from app.config import settings
        
        logger.info(f"📡 Server will run on: http://{settings.host}:{settings.port}")
        logger.info(f"🔧 Debug mode: {settings.debug}")
        logger.info(f"🌐 CORS origins: {settings.cors_origins}")
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all dependencies are installed:")
        logger.error("pip install fastapi uvicorn asyncpg redis pydantic python-dotenv")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()

