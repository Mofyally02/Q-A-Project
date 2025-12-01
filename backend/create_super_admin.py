#!/usr/bin/env python3
"""
Script to create the super admin user in the database
Email: allansaiti02@gmail.com
Password: MofyAlly.21
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.security import SecurityUtils
from app.db.session import db
from app.core.security import SecurityUtils
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_super_admin():
    """Create super admin user in the database"""
    
    await db.connect()
    
    try:
        async for conn in db.get_auth_connection():
            # Check if user already exists
            existing_user = await conn.fetchrow("""
                SELECT user_id, email, role 
                FROM users 
                WHERE email = $1
            """, "allansaiti02@gmail.com")
            
            if existing_user:
                logger.info(f"User {existing_user['email']} already exists with role: {existing_user['role']}")
                
                # Update role to super_admin if not already
                if existing_user['role'] != 'super_admin':
                    await conn.execute("""
                        UPDATE users 
                        SET role = 'super_admin'::userrole,
                            is_active = TRUE,
                            email_verified = TRUE,
                            updated_at = NOW()
                        WHERE email = $1
                    """, "allansaiti02@gmail.com")
                    logger.info("Updated user role to super_admin")
                else:
                    logger.info("User is already a super_admin")
                return
            
            # Hash password
            password_hash = SecurityUtils.hash_password("MofyAlly.21")
            
            # Create super admin user
            await conn.execute("""
                INSERT INTO users (
                    email,
                    password_hash,
                    first_name,
                    last_name,
                    role,
                    is_active,
                    email_verified,
                    created_at,
                    updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5::userrole, $6, $7, NOW(), NOW()
                )
            """, 
                "allansaiti02@gmail.com",
                password_hash,
                "Allan",
                "Saiti",
                "super_admin",
                True,
                True
            )
            
            logger.info("✅ Super admin user created successfully!")
            logger.info("   Email: allansaiti02@gmail.com")
            logger.info("   Password: MofyAlly.21")
            logger.info("   Role: super_admin")
            
    except Exception as e:
        logger.error(f"❌ Error creating super admin: {e}")
        raise
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(create_super_admin())

