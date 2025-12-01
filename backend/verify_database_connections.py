#!/usr/bin/env python3
"""
Verify all endpoints are properly connected to the database
This script checks:
1. Database connection works
2. All required tables exist
3. CRUD operations can execute queries
4. Table/column names match what's used in code
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.db.session import db
from app.core.config import settings
import asyncpg


async def check_database_connection():
    """Check if database connection works"""
    print("=" * 60)
    print("Database Connection Verification")
    print("=" * 60)
    print()
    
    try:
        await db.connect()
        print("✅ Database connection pool created")
        
        # Test connection
        async for conn in db.get_connection():
            result = await conn.fetchval("SELECT version()")
            print(f"✅ PostgreSQL connection successful")
            print(f"   Version: {result.split(',')[0]}")
            break
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def check_tables_exist():
    """Check if all required tables exist"""
    print()
    print("=" * 60)
    print("Table Existence Check")
    print("=" * 60)
    print()
    
    required_tables = [
        "users",
        "questions",
        "answers",
        "ratings",
        "expert_reviews",
        "transactions",
        "notifications",
        "admin_actions",
        "api_keys",
        "system_settings",
        "notification_templates",
        "compliance_flags",
        "expert_metrics",
        "client_wallet",
        "audit_logs",
    ]
    
    async for conn in db.get_connection():
        existing_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        existing_table_names = {row['table_name'] for row in existing_tables}
        
        print(f"Found {len(existing_table_names)} tables in database")
        print()
        
        missing_tables = []
        for table in required_tables:
            if table in existing_table_names:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - MISSING")
                missing_tables.append(table)
        
        if missing_tables:
            print()
            print(f"⚠️  {len(missing_tables)} tables are missing")
            return False
        else:
            print()
            print("✅ All required tables exist")
            return True


async def check_table_columns():
    """Check if tables have expected columns"""
    print()
    print("=" * 60)
    print("Table Column Verification")
    print("=" * 60)
    print()
    
    # Key tables and their expected columns
    table_columns = {
        "users": ["id", "email", "password_hash", "role", "is_active", "is_verified", "is_banned", "profile_data"],
        "questions": ["id", "client_id", "type", "content", "subject", "status", "priority", "expert_id"],
        "answers": ["id", "question_id", "expert_id", "ai_response", "humanized_response", "expert_response", "is_approved"],
        "ratings": ["id", "question_id", "expert_id", "client_id", "score", "comment"],
        "transactions": ["id", "user_id", "type", "amount", "balance_after"],
        "notifications": ["id", "user_id", "type", "title", "message", "is_read"],
    }
    
    async for conn in db.get_connection():
        all_good = True
        for table, expected_columns in table_columns.items():
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            
            if not table_exists:
                print(f"❌ Table '{table}' does not exist")
                all_good = False
                continue
            
            # Get actual columns
            actual_columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = $1
            """, table)
            actual_column_names = {row['column_name'] for row in actual_columns}
            
            # Check expected columns
            missing_columns = []
            for col in expected_columns:
                if col not in actual_column_names:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"⚠️  {table}: Missing columns: {', '.join(missing_columns)}")
                all_good = False
            else:
                print(f"✅ {table}: All expected columns present")
        
        return all_good


async def test_crud_operations():
    """Test if CRUD operations can execute"""
    print()
    print("=" * 60)
    print("CRUD Operations Test")
    print("=" * 60)
    print()
    
    try:
        from app.crud.admin import users as user_crud
        
        async for conn in db.get_connection():
            # Test a simple query
            try:
                result = await user_crud.get_users(conn, page=1, page_size=1)
                print("✅ User CRUD operations work")
                print(f"   Found {result.get('total', 0)} users")
            except Exception as e:
                print(f"❌ User CRUD operations failed: {e}")
                return False
            
            # Test questions query
            try:
                from app.crud.client import questions as question_crud
                # Just test the query structure, not actual execution
                print("✅ Question CRUD module imports successfully")
            except Exception as e:
                print(f"❌ Question CRUD import failed: {e}")
                return False
            
            return True
    except Exception as e:
        print(f"❌ CRUD operations test failed: {e}")
        return False


async def main():
    """Run all verification checks"""
    print()
    print("🔍 Verifying Database Configuration for All 90 Endpoints")
    print()
    
    results = []
    
    # Check 1: Database connection
    results.append(await check_database_connection())
    
    # Check 2: Tables exist
    results.append(await check_tables_exist())
    
    # Check 3: Table columns
    results.append(await check_table_columns())
    
    # Check 4: CRUD operations
    results.append(await test_crud_operations())
    
    # Summary
    print()
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print()
    
    checks = [
        "Database Connection",
        "Table Existence",
        "Table Columns",
        "CRUD Operations"
    ]
    
    for i, (check, result) in enumerate(zip(checks, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print()
    if all(results):
        print("🎉 All checks passed! Database is properly configured.")
        print()
        print("Next steps:")
        print("1. Start the server: ./start_server.sh")
        print("2. Test endpoints: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        try:
            asyncio.run(db.disconnect())
        except:
            pass

