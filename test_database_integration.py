#!/usr/bin/env python3
"""
Database connection and integration test script
This script tests all database connections and service integrations.
"""

import asyncio
import asyncpg
import logging
from typing import Dict, Any
from app.config import settings
from app.database import db
from app.services.auth_service import auth_service
from app.services.submission_service import submission_service
from app.services.rating_service import rating_service
from app.services.expert_review_service import expert_review_service
from app.services.admin_service import admin_service
from app.services.audit_service import audit_service
from app.models import (
    RegisterRequest, LoginRequest, QuestionCreate, RatingCreate, 
    ExpertReviewCreate, UserRole, QuestionType
)
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegrationTester:
    """Test database integration for all services"""
    
    def __init__(self):
        self.test_results = {}
        self.test_user_id = None
        self.test_question_id = None
        self.test_answer_id = None
    
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("Starting database integration tests...")
        
        try:
            # Initialize database connection
            await self.test_database_connection()
            
            # Test authentication service
            await self.test_auth_service()
            
            # Test submission service
            await self.test_submission_service()
            
            # Test rating service
            await self.test_rating_service()
            
            # Test expert review service
            await self.test_expert_review_service()
            
            # Test admin service
            await self.test_admin_service()
            
            # Test audit service
            await self.test_audit_service()
            
            # Clean up test data
            await self.cleanup_test_data()
            
            # Print results
            self.print_test_results()
            
        except Exception as e:
            logger.error(f"Integration tests failed: {e}")
            raise
    
    async def test_database_connection(self):
        """Test database connection"""
        logger.info("Testing database connection...")
        
        try:
            await db.connect()
            
            # Test main database connection
            async for conn in db.get_connection():
                result = await conn.fetchval("SELECT 1")
                assert result == 1
                break
            
            # Test auth database connection
            async for conn in db.get_auth_connection():
                result = await conn.fetchval("SELECT 1")
                assert result == 1
                break
            
            # Test Redis connection
            redis_client = db.get_redis()
            redis_client.ping()
            
            self.test_results['database_connection'] = 'PASS'
            logger.info("✓ Database connection test passed")
            
        except Exception as e:
            self.test_results['database_connection'] = f'FAIL: {e}'
            logger.error(f"✗ Database connection test failed: {e}")
            raise
    
    async def test_auth_service(self):
        """Test authentication service"""
        logger.info("Testing authentication service...")
        
        try:
            async for conn in db.get_auth_connection():
                # Test user registration
                register_data = RegisterRequest(
                    email=f"test_{uuid4().hex[:8]}@example.com",
                    password="testpassword123",
                    first_name="Test",
                    last_name="User",
                    role=UserRole.CLIENT
                )
                
                register_result = await auth_service.register_user(register_data, conn)
                assert register_result.success, f"Registration failed: {register_result.message}"
                
                self.test_user_id = register_result.user.user_id
                
                # Test user login
                login_data = LoginRequest(
                    email=register_data.email,
                    password=register_data.password
                )
                
                login_result = await auth_service.login_user(login_data, conn)
                assert login_result.success, f"Login failed: {login_result.message}"
                assert login_result.access_token is not None
                
                # Test token verification
                token_data = auth_service.verify_token(login_result.access_token)
                assert token_data is not None
                assert token_data.user_id == str(self.test_user_id)
                
                break
            
            self.test_results['auth_service'] = 'PASS'
            logger.info("✓ Authentication service test passed")
            
        except Exception as e:
            self.test_results['auth_service'] = f'FAIL: {e}'
            logger.error(f"✗ Authentication service test failed: {e}")
    
    async def test_submission_service(self):
        """Test submission service"""
        logger.info("Testing submission service...")
        
        try:
            async for conn in db.get_connection():
                # Test question submission
                question_data = QuestionCreate(
                    client_id=self.test_user_id,
                    type=QuestionType.TEXT,
                    content={"data": "What is the capital of France?"},
                    subject="Geography"
                )
                
                submit_result = await submission_service.submit_question(question_data, conn)
                assert submit_result.success, f"Question submission failed: {submit_result.message}"
                
                self.test_question_id = submit_result.data['question_id']
                
                # Test question status retrieval
                status_result = await submission_service.get_question_status(self.test_question_id, conn)
                assert status_result.success, f"Status retrieval failed: {status_result.message}"
                assert status_result.data['status'] == 'submitted'
                
                # Test user questions retrieval
                questions_result = await submission_service.get_user_questions(str(self.test_user_id), conn)
                assert questions_result.success, f"User questions retrieval failed: {questions_result.message}"
                assert len(questions_result.data['questions']) > 0
                
                break
            
            self.test_results['submission_service'] = 'PASS'
            logger.info("✓ Submission service test passed")
            
        except Exception as e:
            self.test_results['submission_service'] = f'FAIL: {e}'
            logger.error(f"✗ Submission service test failed: {e}")
    
    async def test_rating_service(self):
        """Test rating service"""
        logger.info("Testing rating service...")
        
        try:
            async for conn in db.get_connection():
                # First create an answer for the question
                self.test_answer_id = await conn.fetchval("""
                    INSERT INTO answers (answer_id, question_id, ai_response, confidence_score)
                    VALUES (gen_random_uuid(), $1, $2, $3)
                    RETURNING answer_id
                """, self.test_question_id, '{"response": "Paris is the capital of France."}', 0.95)
                
                # Test rating submission
                rating_data = RatingCreate(
                    question_id=self.test_question_id,
                    score=5,
                    comment="Excellent answer!"
                )
                
                rating_result = await rating_service.submit_rating(rating_data, conn)
                assert rating_result.success, f"Rating submission failed: {rating_result.message}"
                
                # Test ratings retrieval
                ratings_result = await rating_service.get_ratings(conn, question_id=self.test_question_id)
                assert ratings_result.success, f"Ratings retrieval failed: {ratings_result.message}"
                assert len(ratings_result.data['ratings']) > 0
                
                # Test rating statistics
                stats_result = await rating_service.get_rating_statistics(conn)
                assert stats_result.success, f"Rating statistics failed: {stats_result.message}"
                
                break
            
            self.test_results['rating_service'] = 'PASS'
            logger.info("✓ Rating service test passed")
            
        except Exception as e:
            self.test_results['rating_service'] = f'FAIL: {e}'
            logger.error(f"✗ Rating service test failed: {e}")
    
    async def test_expert_review_service(self):
        """Test expert review service"""
        logger.info("Testing expert review service...")
        
        try:
            async for conn in db.get_connection():
                # Test expert review submission
                review_data = ExpertReviewCreate(
                    answer_id=self.test_answer_id,
                    expert_id=self.test_user_id,
                    is_approved=True,
                    rejection_reason=None,
                    correction=None
                )
                
                review_result = await expert_review_service.submit_review(review_data, conn)
                assert review_result.success, f"Expert review submission failed: {review_result.message}"
                
                # Test expert reviews retrieval
                reviews_result = await expert_review_service.get_expert_reviews(conn, expert_id=str(self.test_user_id))
                assert reviews_result.success, f"Expert reviews retrieval failed: {reviews_result.message}"
                
                # Test pending reviews
                pending_result = await expert_review_service.get_pending_reviews(conn)
                assert pending_result.success, f"Pending reviews retrieval failed: {pending_result.message}"
                
                break
            
            self.test_results['expert_review_service'] = 'PASS'
            logger.info("✓ Expert review service test passed")
            
        except Exception as e:
            self.test_results['expert_review_service'] = f'FAIL: {e}'
            logger.error(f"✗ Expert review service test failed: {e}")
    
    async def test_admin_service(self):
        """Test admin service"""
        logger.info("Testing admin service...")
        
        try:
            async for conn in db.get_connection():
                # Test analytics retrieval
                analytics_result = await admin_service.get_analytics(conn, days=30)
                assert analytics_result.success, f"Analytics retrieval failed: {analytics_result.message}"
                
                # Test data export
                export_result = await admin_service.export_data(conn, "questions", days=1)
                assert export_result.success, f"Data export failed: {export_result.message}"
                
                break
            
            self.test_results['admin_service'] = 'PASS'
            logger.info("✓ Admin service test passed")
            
        except Exception as e:
            self.test_results['admin_service'] = f'FAIL: {e}'
            logger.error(f"✗ Admin service test failed: {e}")
    
    async def test_audit_service(self):
        """Test audit service"""
        logger.info("Testing audit service...")
        
        try:
            async for conn in db.get_connection():
                # Test audit log creation
                log_result = await audit_service.log_action(
                    db=conn,
                    action="test_action",
                    user_id=str(self.test_user_id),
                    question_id=self.test_question_id,
                    details={"test": "data"}
                )
                assert log_result, "Audit log creation failed"
                
                # Test audit logs retrieval
                logs = await audit_service.get_audit_logs(
                    conn, user_id=str(self.test_user_id), limit=10
                )
                assert len(logs) > 0, "No audit logs found"
                
                # Test user activity summary
                activity = await audit_service.get_user_activity_summary(
                    conn, str(self.test_user_id), days=1
                )
                assert activity is not None, "User activity summary failed"
                
                # Test compliance check
                compliance = await audit_service.check_compliance_violations(
                    conn, str(self.test_user_id), days=1
                )
                assert compliance is not None, "Compliance check failed"
                
                break
            
            self.test_results['audit_service'] = 'PASS'
            logger.info("✓ Audit service test passed")
            
        except Exception as e:
            self.test_results['audit_service'] = f'FAIL: {e}'
            logger.error(f"✗ Audit service test failed: {e}")
    
    async def cleanup_test_data(self):
        """Clean up test data"""
        logger.info("Cleaning up test data...")
        
        try:
            async for conn in db.get_connection():
                if self.test_answer_id:
                    await conn.execute("DELETE FROM answers WHERE answer_id = $1", self.test_answer_id)
                
                if self.test_question_id:
                    await conn.execute("DELETE FROM questions WHERE question_id = $1", self.test_question_id)
                
                if self.test_user_id:
                    await conn.execute("DELETE FROM users WHERE user_id = $1", self.test_user_id)
                
                break
            
            logger.info("✓ Test data cleaned up")
            
        except Exception as e:
            logger.error(f"✗ Test data cleanup failed: {e}")
    
    def print_test_results(self):
        """Print test results summary"""
        logger.info("\n" + "="*50)
        logger.info("DATABASE INTEGRATION TEST RESULTS")
        logger.info("="*50)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result == 'PASS' else "✗ FAIL"
            logger.info(f"{test_name:25} {status}")
            
            if result == 'PASS':
                passed += 1
            else:
                failed += 1
                logger.info(f"  Error: {result}")
        
        logger.info("="*50)
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info("="*50)
        
        if failed == 0:
            logger.info("🎉 All tests passed! Database integration is working correctly.")
        else:
            logger.error(f"❌ {failed} test(s) failed. Please check the errors above.")

async def main():
    """Main test runner"""
    tester = DatabaseIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
