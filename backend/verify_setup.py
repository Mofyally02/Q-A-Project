#!/usr/bin/env python3
"""
Backend & Database Configuration Verification Script
Checks all interconnected components and reports their status
"""
import asyncio
import asyncpg
import redis
import os
import sys
from typing import Dict, Any, List
from app.config import settings

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_status(name: str, status: bool, message: str = ""):
    icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"  {icon} {name:30} {message}")

async def check_postgresql() -> Dict[str, Any]:
    """Check PostgreSQL database connectivity"""
    results = {"main": False, "auth": False, "tables_main": [], "tables_auth": []}
    
    try:
        # Check main database
        conn = await asyncpg.connect(settings.database_url)
        results["main"] = True
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        results["tables_main"] = [t["table_name"] for t in tables]
        
        # Check UUID extension
        has_uuid_ext = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp'
            )
        """)
        results["uuid_extension"] = has_uuid_ext
        
        await conn.close()
    except Exception as e:
        results["main_error"] = str(e)
    
    try:
        # Check auth database
        conn = await asyncpg.connect(settings.auth_database_url)
        results["auth"] = True
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        results["tables_auth"] = [t["table_name"] for t in tables]
        await conn.close()
    except Exception as e:
        results["auth_error"] = str(e)
    
    return results

def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity"""
    results = {"connected": False}
    try:
        client = redis.from_url(settings.redis_url)
        client.ping()
        results["connected"] = True
        
        # Test basic operations
        test_key = "health_check_test"
        client.set(test_key, "test", ex=10)
        value = client.get(test_key)
        client.delete(test_key)
        results["operations"] = value == b"test"
    except Exception as e:
        results["error"] = str(e)
    
    return results

def check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ connectivity"""
    results = {"connected": False}
    try:
        import pika
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            connection_attempts=2,
            retry_delay=1
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Try to list queues
        queue_list = channel.queue_declare(queue="health_check", durable=False, auto_delete=True)
        connection.close()
        
        results["connected"] = True
    except ImportError:
        results["error"] = "pika package not installed"
    except Exception as e:
        results["error"] = str(e)
    
    return results

def check_api_keys() -> Dict[str, Any]:
    """Check if API keys are configured"""
    keys = {
        "openai": settings.openai_api_key,
        "xai": settings.xai_api_key,
        "google": settings.google_api_key,
        "anthropic": settings.anthropic_api_key,
        "stealth": settings.stealth_api_key,
        "turnitin": settings.turnitin_api_key,
    }
    
    results = {}
    for name, key in keys.items():
        results[name] = {
            "configured": bool(key and len(key) > 10),
            "length": len(key) if key else 0
        }
    
    return results

def check_env_variables() -> Dict[str, Any]:
    """Check if required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "AUTH_DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET_KEY",
    ]
    
    results = {}
    for var in required_vars:
        value = os.getenv(var)
        results[var] = {
            "set": bool(value),
            "has_value": bool(value and len(value) > 5)
        }
    
    return results

async def check_database_schema() -> Dict[str, Any]:
    """Check if required database tables exist"""
    results = {"main_tables": {}, "auth_tables": {}}
    
    required_main_tables = ["questions", "answers", "ratings", "expert_reviews", "audit_logs"]
    required_auth_tables = ["users", "clients", "experts", "admins"]
    
    try:
        # Check main database tables
        conn = await asyncpg.connect(settings.database_url)
        for table in required_main_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            results["main_tables"][table] = exists
        await conn.close()
    except Exception as e:
        results["main_error"] = str(e)
    
    try:
        # Check auth database tables
        conn = await asyncpg.connect(settings.auth_database_url)
        for table in required_auth_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            results["auth_tables"][table] = exists
        await conn.close()
    except Exception as e:
        results["auth_error"] = str(e)
    
    return results

async def main():
    print_header("Backend & Database Configuration Verification")
    
    all_checks_passed = True
    
    # 1. Environment Variables
    print(f"{BOLD}1. Environment Variables{RESET}")
    env_check = check_env_variables()
    for var, status in env_check.items():
        passed = status["set"] and status["has_value"]
        if not passed:
            all_checks_passed = False
        print_status(var, passed, "✓ Set" if passed else "✗ Missing or empty")
    
    # 2. PostgreSQL Database
    print(f"\n{BOLD}2. PostgreSQL Database{RESET}")
    db_check = await check_postgresql()
    print_status("Main Database", db_check.get("main", False), 
                 "Connected" if db_check.get("main") else f"Error: {db_check.get('main_error', 'Unknown')}")
    print_status("Auth Database", db_check.get("auth", False),
                 "Connected" if db_check.get("auth") else f"Error: {db_check.get('auth_error', 'Unknown')}")
    print_status("UUID Extension", db_check.get("uuid_extension", False),
                 "Installed" if db_check.get("uuid_extension") else "Not installed")
    
    if db_check.get("main"):
        print(f"\n  {BLUE}Main DB Tables ({len(db_check['tables_main'])}):{RESET}")
        for table in db_check["tables_main"][:10]:  # Show first 10
            print(f"    - {table}")
        if len(db_check["tables_main"]) > 10:
            print(f"    ... and {len(db_check['tables_main']) - 10} more")
    
    if db_check.get("auth"):
        print(f"\n  {BLUE}Auth DB Tables ({len(db_check['tables_auth'])}):{RESET}")
        for table in db_check["tables_auth"][:10]:
            print(f"    - {table}")
        if len(db_check["tables_auth"]) > 10:
            print(f"    ... and {len(db_check['tables_auth']) - 10} more")
    
    if not db_check.get("main") or not db_check.get("auth"):
        all_checks_passed = False
    
    # 3. Database Schema
    print(f"\n{BOLD}3. Database Schema (Required Tables){RESET}")
    schema_check = await check_database_schema()
    
    main_tables = schema_check.get("main_tables", {})
    for table, exists in main_tables.items():
        if not exists:
            all_checks_passed = False
        print_status(f"Main: {table}", exists)
    
    auth_tables = schema_check.get("auth_tables", {})
    for table, exists in auth_tables.items():
        if not exists:
            all_checks_passed = False
        print_status(f"Auth: {table}", exists)
    
    # 4. Redis
    print(f"\n{BOLD}4. Redis Cache{RESET}")
    redis_check = check_redis()
    print_status("Redis Connection", redis_check.get("connected", False),
                 "Connected" if redis_check.get("connected") else f"Error: {redis_check.get('error', 'Unknown')}")
    if redis_check.get("connected"):
        print_status("Redis Operations", redis_check.get("operations", False), "Working")
    
    if not redis_check.get("connected"):
        all_checks_passed = False
    
    # 5. RabbitMQ
    print(f"\n{BOLD}5. RabbitMQ Message Queue{RESET}")
    rabbitmq_check = check_rabbitmq()
    print_status("RabbitMQ Connection", rabbitmq_check.get("connected", False),
                 "Connected" if rabbitmq_check.get("connected") else f"Error: {rabbitmq_check.get('error', 'Unknown')}")
    
    if not rabbitmq_check.get("connected"):
        print(f"  {YELLOW}⚠ Warning: RabbitMQ unavailable - async processing disabled{RESET}")
    
    # 6. API Keys Configuration
    print(f"\n{BOLD}6. API Keys Configuration{RESET}")
    api_keys_check = check_api_keys()
    for name, status in api_keys_check.items():
        configured = status["configured"]
        if not configured:
            print_status(name, False, "Not configured (optional)")
        else:
            print_status(name, True, f"Configured ({status['length']} chars)")
    
    # Summary
    print_header("Verification Summary")
    
    if all_checks_passed:
        print(f"{GREEN}{BOLD}✓ All critical checks passed!{RESET}")
        print(f"\n  Your backend and database are properly configured.")
        print(f"  Next steps:")
        print(f"    1. Test health endpoint: curl http://localhost:8000/health")
        print(f"    2. Start backend server: python start.py")
        print(f"    3. Check detailed health: curl http://localhost:8000/health/database")
    else:
        print(f"{RED}{BOLD}✗ Some checks failed{RESET}")
        print(f"\n  Please fix the issues above before proceeding.")
        print(f"  Common fixes:")
        print(f"    - Ensure PostgreSQL is running and databases exist")
        print(f"    - Run database migrations: python run_migration.py")
        print(f"    - Check .env file has correct connection strings")
        print(f"    - Start Redis: redis-server or docker-compose up redis")
    
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verification interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Verification failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

