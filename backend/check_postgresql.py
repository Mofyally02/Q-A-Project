#!/usr/bin/env python3
"""
PostgreSQL Availability Checker
This script checks if PostgreSQL is available and provides setup instructions
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLChecker:
    """Check PostgreSQL availability and provide setup instructions"""
    
    def __init__(self):
        self.postgres_available = False
        self.docker_available = False
        self.docker_running = False
    
    async def check_postgresql(self):
        """Check if PostgreSQL is available"""
        logger.info("🔍 Checking PostgreSQL availability...")
        
        # Try to connect to PostgreSQL
        try:
            import asyncpg

            # Try different connection strings
            connection_strings = [
                "postgresql://postgres:password@localhost:5432/postgres",
                "postgresql://postgres:postgres@localhost:5432/postgres",
                "postgresql://postgres:@localhost:5432/postgres",
                "postgresql://postgres@localhost:5432/postgres"
            ]
            
            for conn_str in connection_strings:
                try:
                    conn = await asyncpg.connect(conn_str)
                    await conn.close()
                    logger.info(f"  ✅ PostgreSQL is running and accessible!")
                    logger.info(f"  📡 Connection string: {conn_str}")
                    self.postgres_available = True
                    return True
                except Exception as e:
                    logger.info(f"  ❌ Failed: {str(e)[:50]}...")
            
            logger.info("  ❌ PostgreSQL is not accessible")
            return False
            
        except ImportError:
            logger.error("  ❌ asyncpg not installed. Run: pip install asyncpg")
            return False
    
    def check_docker(self):
        """Check if Docker is available and running"""
        logger.info("🐳 Checking Docker availability...")
        
        try:
            # Check if docker command exists
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"  ✅ Docker installed: {result.stdout.strip()}")
                self.docker_available = True
                
                # Check if Docker daemon is running
                try:
                    result = subprocess.run(['docker', 'ps'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        logger.info("  ✅ Docker daemon is running")
                        self.docker_running = True
                        return True
                    else:
                        logger.info("  ⚠️  Docker daemon is not running")
                        logger.info("  💡 Start Docker Desktop and try again")
                        return False
                except subprocess.TimeoutExpired:
                    logger.info("  ⚠️  Docker daemon is not responding")
                    return False
            else:
                logger.info("  ❌ Docker not installed")
                return False
                
        except FileNotFoundError:
            logger.info("  ❌ Docker not found in PATH")
            return False
        except subprocess.TimeoutExpired:
            logger.info("  ⚠️  Docker command timed out")
            return False
    
    def provide_setup_instructions(self):
        """Provide setup instructions based on current state"""
        logger.info("\n" + "="*60)
        logger.info("📋 SETUP INSTRUCTIONS")
        logger.info("="*60)
        
        if self.postgres_available:
            logger.info("🎉 PostgreSQL is already running!")
            logger.info("   You can now run: python setup_postgresql.py")
            return
        
        if self.docker_available and self.docker_running:
            logger.info("🐳 Docker is available and running!")
            logger.info("   Run these commands to start PostgreSQL:")
            logger.info("   ")
            logger.info("   docker run -d --name qa-postgres -p 5432:5432 \\")
            logger.info("     -e POSTGRES_PASSWORD=password \\")
            logger.info("     -e POSTGRES_DB=qa_system postgres:15")
            logger.info("   ")
            logger.info("   docker exec -it qa-postgres psql -U postgres \\")
            logger.info("     -c \"CREATE DATABASE qa_auth;\"")
            logger.info("   ")
            logger.info("   python setup_postgresql.py")
            
        elif self.docker_available and not self.docker_running:
            logger.info("🐳 Docker is installed but not running!")
            logger.info("   ")
            logger.info("   1. Start Docker Desktop")
            logger.info("   2. Wait for it to fully start")
            logger.info("   3. Run this script again")
            
        else:
            logger.info("📥 PostgreSQL setup options:")
            logger.info("   ")
            logger.info("   Option 1: Install Docker Desktop")
            logger.info("   - Download from: https://www.docker.com/products/docker-desktop")
            logger.info("   - Install and start Docker Desktop")
            logger.info("   - Run this script again")
            logger.info("   ")
            logger.info("   Option 2: Install PostgreSQL locally")
            logger.info("   - Download from: https://www.postgresql.org/download/windows/")
            logger.info("   - Install with default settings")
            logger.info("   - Remember the password for 'postgres' user")
            logger.info("   - Run: python setup_postgresql.py")
            logger.info("   ")
            logger.info("   Option 3: Use cloud database")
            logger.info("   - Supabase (free): https://supabase.com/")
            logger.info("   - Railway (free): https://railway.app/")
            logger.info("   - Neon (free): https://neon.tech/")
    
    def print_summary(self):
        """Print summary of current state"""
        logger.info("\n" + "="*60)
        logger.info("📊 CURRENT STATUS")
        logger.info("="*60)
        logger.info(f"PostgreSQL Available: {'✅ Yes' if self.postgres_available else '❌ No'}")
        logger.info(f"Docker Installed: {'✅ Yes' if self.docker_available else '❌ No'}")
        logger.info(f"Docker Running: {'✅ Yes' if self.docker_running else '❌ No'}")
        logger.info("="*60)

async def main():
    """Main checker function"""
    logger.info("🚀 PostgreSQL Availability Checker")
    logger.info("="*60)
    
    checker = PostgreSQLChecker()
    
    # Check PostgreSQL
    await checker.check_postgresql()
    
    # Check Docker
    checker.check_docker()
    
    # Print summary
    checker.print_summary()
    
    # Provide instructions
    checker.provide_setup_instructions()
    
    return checker.postgres_available

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


