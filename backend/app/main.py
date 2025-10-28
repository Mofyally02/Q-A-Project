from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List
from app.config import settings
from app.database import db, get_db, get_redis
from app.services.queue_service import QueueService
from app.services.notification_service import NotificationService
from app.services.ai_service import AIService
from app.services.humanization_service import HumanizationService
from app.services.originality_service import OriginalityService
from app.services.expert_review_service import ExpertReviewService
from app.services.delivery_service import DeliveryService
from app.services.rating_service import RatingService
from app.services.submission_service import SubmissionService
from app.services.audit_service import AuditService
from app.services.admin_service import AdminService
from app.services.poe_service import PoeService
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.admin import router as admin_router
from app.models import (
    QuestionCreate, QuestionResponse, RatingCreate, RatingResponse,
    ExpertReviewCreate, ExpertReviewResponse, AdminAnalytics, AdminOverride,
    APIResponse, ErrorResponse
)
import asyncpg
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
queue_service = QueueService()
notification_service = NotificationService()
ai_service = AIService()
humanization_service = HumanizationService()
originality_service = OriginalityService()
expert_review_service = ExpertReviewService()
delivery_service = DeliveryService()
rating_service = RatingService()
submission_service = SubmissionService()
audit_service = AuditService()
admin_service = AdminService()
poe_service = PoeService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up AI Q&A System...")
    
    # Initialize database connections
    await db.connect()
    
    # Initialize queue service (optional - continue if RabbitMQ not available)
    try:
        await queue_service.connect()
        logger.info("Queue service connected successfully")
        
        # Start background tasks only if queue service is available
        asyncio.create_task(process_ai_queue())
        asyncio.create_task(process_humanization_queue())
        asyncio.create_task(process_originality_queue())
        asyncio.create_task(process_expert_review_queue())
        asyncio.create_task(process_delivery_queue())
        asyncio.create_task(process_notification_queue())
    except Exception as e:
        logger.warning(f"Queue service not available (RabbitMQ may not be running): {e}")
        logger.warning("API will continue without background queue processing")
    
    logger.info("AI Q&A System started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Q&A System...")
    
    # Close database connections
    await db.disconnect()
    
    # Close queue service
    queue_service.close()
    
    logger.info("AI Q&A System shut down successfully")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Q&A System",
    description="Backend API for AL-Tech Academy's AI-powered Q&A system",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Include routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(admin_router)

# Health check endpoints for scalability and monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint - basic service availability"""
    return {"status": "healthy", "service": "q-a-system"}

@app.get("/ready")
async def readiness_check():
    """Readiness check - service is ready to accept requests"""
    try:
        # Check database connectivity
        async for conn in get_db():
            await conn.fetchval("SELECT 1")
            break
        
        # Check Redis connectivity
        redis_client = get_redis()
        redis_client.ping()
        
        return {"status": "ready", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/live")
async def liveness_check():
    """Liveness check - service is alive and running"""
    return {"status": "alive", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}

# Background task processors
async def process_ai_queue():
    """Process AI processing queue"""
    while True:
        try:
            await queue_service.consume_ai_processing(handle_ai_processing)
        except Exception as e:
            logger.error(f"Error processing AI queue: {e}")
            await asyncio.sleep(5)

async def process_humanization_queue():
    """Process humanization queue"""
    while True:
        try:
            await queue_service.consume_humanization(handle_humanization)
        except Exception as e:
            logger.error(f"Error processing humanization queue: {e}")
            await asyncio.sleep(5)

async def process_originality_queue():
    """Process originality check queue"""
    while True:
        try:
            await queue_service.consume_originality_check(handle_originality_check)
        except Exception as e:
            logger.error(f"Error processing originality queue: {e}")
            await asyncio.sleep(5)

async def process_expert_review_queue():
    """Process expert review queue"""
    while True:
        try:
            await queue_service.consume_expert_review(handle_expert_review)
        except Exception as e:
            logger.error(f"Error processing expert review queue: {e}")
            await asyncio.sleep(5)

async def process_delivery_queue():
    """Process delivery queue"""
    while True:
        try:
            await queue_service.consume_delivery(handle_delivery)
        except Exception as e:
            logger.error(f"Error processing delivery queue: {e}")
            await asyncio.sleep(5)

async def process_notification_queue():
    """Process notification queue"""
    while True:
        try:
            await queue_service.consume_notification(handle_notification)
        except Exception as e:
            logger.error(f"Error processing notification queue: {e}")
            await asyncio.sleep(5)

# Queue handlers
async def handle_ai_processing(data: dict):
    """Handle AI processing task"""
    try:
        question_id = data.get("question_id")
        if not question_id:
            logger.error("No question_id in AI processing task")
            return
        
        # Get question data from database
        async for db_conn in get_db():
            question_data = await db_conn.fetchrow(
                "SELECT * FROM questions WHERE question_id = $1",
                question_id
            )
            
            if not question_data:
                logger.error(f"Question {question_id} not found")
                return
            
            # Process with AI service
            result = await ai_service.process_question(dict(question_data))
            
            if result.success:
                # Store AI response
                await db_conn.execute(
                    """
                    INSERT INTO answers (answer_id, question_id, ai_response, confidence_score)
                    VALUES (gen_random_uuid(), $1, $2, $3)
                    """,
                    question_id,
                    result.data,
                    result.data.get("confidence_score", 0.0)
                )
                
                # Update question status
                await db_conn.execute(
                    "UPDATE questions SET status = 'processing' WHERE question_id = $1",
                    question_id
                )
                
                # Queue for humanization
                await queue_service.enqueue_humanization(question_id)
                
            else:
                logger.error(f"AI processing failed for question {question_id}: {result.message}")
                
    except Exception as e:
        logger.error(f"Error handling AI processing: {e}")

async def handle_humanization(data: dict):
    """Handle humanization task"""
    try:
        answer_id = data.get("answer_id")
        if not answer_id:
            logger.error("No answer_id in humanization task")
            return
        
        # Get answer data
        async for db_conn in get_db():
            answer_data = await db_conn.fetchrow(
                "SELECT * FROM answers WHERE answer_id = $1",
                answer_id
            )
            
            if not answer_data:
                logger.error(f"Answer {answer_id} not found")
                return
            
            # Humanize text
            ai_response = answer_data.get("ai_response", {})
            if ai_response and "response" in ai_response:
                result = await humanization_service.humanize_text(
                    ai_response["response"],
                    answer_data.get("subject", "")
                )
                
                if result.success:
                    # Update answer with humanized response
                    await db_conn.execute(
                        "UPDATE answers SET humanized_response = $1 WHERE answer_id = $2",
                        result.data,
                        answer_id
                    )
                    
                    # Queue for originality check
                    await queue_service.enqueue_originality_check(answer_id)
                    
    except Exception as e:
        logger.error(f"Error handling humanization: {e}")

async def handle_originality_check(data: dict):
    """Handle originality check task"""
    try:
        answer_id = data.get("answer_id")
        if not answer_id:
            logger.error("No answer_id in originality check task")
            return
        
        # Get answer data
        async for db_conn in get_db():
            answer_data = await db_conn.fetchrow(
                "SELECT * FROM answers WHERE answer_id = $1",
                answer_id
            )
            
            if not answer_data:
                logger.error(f"Answer {answer_id} not found")
                return
            
            # Check originality
            humanized_response = answer_data.get("humanized_response", {})
            if humanized_response and "humanized_text" in humanized_response:
                result = await originality_service.check_originality(
                    humanized_response["humanized_text"],
                    answer_id
                )
                
                if result.success:
                    # Check if compliant
                    if result.data.get("compliance_status") == "compliant":
                        # Queue for expert review
                        await queue_service.enqueue_expert_review(answer_id)
                    else:
                        # Log violation and queue for re-humanization
                        await audit_service.log_ai_content_detection(
                            db_conn,
                            answer_id,
                            answer_data.get("client_id"),
                            result.data.get("ai_score", 0.0)
                        )
                        await queue_service.enqueue_humanization(answer_id)
                    
    except Exception as e:
        logger.error(f"Error handling originality check: {e}")

async def handle_expert_review(data: dict):
    """Handle expert review task"""
    try:
        question_id = data.get("question_id")
        expert_id = data.get("expert_id")
        
        if not question_id:
            logger.error("No question_id in expert review task")
            return
        
        # Update question status
        async for db_conn in get_db():
            await db_conn.execute(
                "UPDATE questions SET status = 'review' WHERE question_id = $1",
                question_id
            )
            
            # Assign expert if provided
            if expert_id:
                await expert_review_service.assign_expert_to_review(
                    db_conn,
                    question_id,
                    expert_id
                )
                
    except Exception as e:
        logger.error(f"Error handling expert review: {e}")

async def handle_delivery(data: dict):
    """Handle delivery task"""
    try:
        question_id = data.get("question_id")
        if not question_id:
            logger.error("No question_id in delivery task")
            return
        
        # Deliver answer
        async for db_conn in get_db():
            result = await delivery_service.deliver_answer(question_id, db_conn)
            
            if result.success:
                logger.info(f"Answer delivered for question {question_id}")
            else:
                logger.error(f"Delivery failed for question {question_id}: {result.message}")
                
    except Exception as e:
        logger.error(f"Error handling delivery: {e}")

async def handle_notification(data: dict):
    """Handle notification task"""
    try:
        user_id = data.get("user_id")
        message = data.get("message")
        notification_type = data.get("type", "info")
        
        if not user_id or not message:
            logger.error("Invalid notification data")
            return
        
        # Send notification
        await notification_service.send_websocket_notification(
            user_id,
            {
                "type": notification_type,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling notification: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI-Powered Q&A System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

# Question endpoints
@app.post("/submit-question", response_model=APIResponse)
async def submit_question(
    question: QuestionCreate,
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit a new question for processing"""
    return await submission_service.submit_question(question, db)

@app.get("/question/{question_id}/status", response_model=APIResponse)
async def get_question_status(
    question_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get question status"""
    return await submission_service.get_question_status(question_id, db)

@app.get("/user/{client_id}/questions", response_model=APIResponse)
async def get_user_questions(
    client_id: str,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user's questions"""
    return await submission_service.get_user_questions(client_id, db, limit, offset)

@app.get("/questions", response_model=APIResponse)
async def get_questions(
    limit: int = 50,
    offset: int = 0,
    status: str = None,
    subject: str = None,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get questions with optional filtering"""
    try:
        query = """
            SELECT q.*, u.email as client_email, u.first_name, u.last_name
            FROM questions q
            JOIN users u ON q.client_id = u.user_id
            WHERE 1=1
        """
        params = []

        if status:
            query += f" AND q.status = ${len(params) + 1}"
            params.append(status)

        if subject:
            query += f" AND q.subject ILIKE ${len(params) + 1}"
            params.append(f"%{subject}%")

        query += f" ORDER BY q.created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])

        questions = await db.fetch(query, *params)

        return APIResponse(
            success=True,
            message="Questions retrieved successfully",
            data={"questions": [dict(q) for q in questions]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rating endpoints
@app.post("/rate-answer", response_model=APIResponse)
async def rate_answer(
    rating: RatingCreate,
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit a rating for an answer"""
    return await rating_service.submit_rating(rating, db)

@app.get("/ratings", response_model=APIResponse)
async def get_ratings(
    question_id: str = None,
    expert_id: str = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get ratings with optional filtering"""
    return await rating_service.get_ratings(db, question_id, expert_id, limit, offset)

@app.get("/expert/{expert_id}/ratings", response_model=APIResponse)
async def get_expert_ratings(
    expert_id: str,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get ratings for a specific expert"""
    return await rating_service.get_expert_ratings(expert_id, db, limit, offset)

@app.get("/rating-statistics", response_model=APIResponse)
async def get_rating_statistics(
    expert_id: str = None,
    days: int = 30,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get rating statistics"""
    return await rating_service.get_rating_statistics(db, expert_id, days)

# Expert review endpoints
@app.post("/expert-review", response_model=APIResponse)
async def submit_expert_review(
    review: ExpertReviewCreate,
    db: asyncpg.Connection = Depends(get_db)
):
    """Submit expert review"""
    return await expert_review_service.submit_review(review, db)

@app.get("/expert-reviews", response_model=APIResponse)
async def get_expert_reviews(
    expert_id: str = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get expert reviews"""
    return await expert_review_service.get_expert_reviews(db, expert_id, limit, offset)

@app.get("/pending-reviews", response_model=APIResponse)
async def get_pending_reviews(
    expert_id: str = None,
    limit: int = 20,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get pending reviews"""
    return await expert_review_service.get_pending_reviews(db, expert_id, limit)

# Delivery endpoints
@app.post("/deliver-answer/{question_id}", response_model=APIResponse)
async def deliver_answer(
    question_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Deliver answer to client"""
    return await delivery_service.deliver_answer(question_id, db)

@app.get("/delivery-status/{question_id}", response_model=APIResponse)
async def get_delivery_status(
    question_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get delivery status"""
    return await delivery_service.get_delivery_status(question_id, db)

# Admin endpoints
@app.get("/admin/analytics", response_model=APIResponse)
async def get_admin_analytics(
    days: int = 30,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get admin analytics"""
    return await admin_service.get_analytics(db, days)

@app.post("/admin/override/{question_id}", response_model=APIResponse)
async def admin_override(
    question_id: str,
    override: AdminOverride,
    db: asyncpg.Connection = Depends(get_db)
):
    """Perform admin override action"""
    return await admin_service.admin_override(question_id, override, db)

@app.get("/admin/export/{data_type}", response_model=APIResponse)
async def export_data(
    data_type: str,
    days: int = 30,
    db: asyncpg.Connection = Depends(get_db)
):
    """Export data for analysis"""
    return await admin_service.export_data(db, data_type, days)

@app.get("/admin/audit-logs", response_model=APIResponse)
async def get_audit_logs(
    user_id: str = None,
    question_id: str = None,
    action: str = None,
    limit: int = 100,
    offset: int = 0,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get audit logs"""
    logs = await audit_service.get_audit_logs(
        db, user_id, question_id, action, limit, offset
    )
    return APIResponse(
        success=True,
        message="Audit logs retrieved successfully",
        data={"logs": logs, "count": len(logs)}
    )

@app.get("/admin/user-activity/{user_id}", response_model=APIResponse)
async def get_user_activity(
    user_id: str,
    days: int = 30,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user activity summary"""
    activity = await audit_service.get_user_activity_summary(db, user_id, days)
    return APIResponse(
        success=True,
        message="User activity retrieved successfully",
        data=activity
    )

@app.get("/admin/compliance-check/{user_id}", response_model=APIResponse)
async def check_compliance(
    user_id: str,
    days: int = 30,
    db: asyncpg.Connection = Depends(get_db)
):
    """Check user compliance"""
    compliance = await audit_service.check_compliance_violations(db, user_id, days)
    return APIResponse(
        success=True,
        message="Compliance check completed",
        data=compliance
    )

# Poe API endpoints for latest models
@app.get("/poe/models", response_model=APIResponse)
async def list_poe_models():
    """List all available Poe models"""
    return await poe_service.list_available_models()

@app.get("/poe/models/{model_name}", response_model=APIResponse)
async def get_poe_model_info(model_name: str):
    """Get information about a specific Poe model"""
    return await poe_service.get_model_info(model_name)

@app.post("/poe/query/{model_name}", response_model=APIResponse)
async def query_poe_model(
    model_name: str,
    question: str,
    subject: str = "General",
    max_tokens: int = 2000,
    temperature: float = 0.7
):
    """Query a specific Poe model"""
    return await poe_service.query_model(
        model_name, question, subject, max_tokens, temperature
    )

@app.post("/poe/query-multiple", response_model=APIResponse)
async def query_multiple_poe_models(
    models: List[str],
    question: str,
    subject: str = "General",
    max_tokens: int = 2000,
    temperature: float = 0.7
):
    """Query multiple Poe models in parallel"""
    return await poe_service.query_multiple_models(
        models, question, subject, max_tokens, temperature
    )

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await websocket.accept()
    
    # Register connection
    await notification_service.register_websocket_connection(user_id, websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Unregister connection
        await notification_service.unregister_websocket_connection(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
