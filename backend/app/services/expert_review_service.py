import asyncio
import base64
import logging
from typing import Dict, Any, Optional, List
import asyncpg
import boto3
from PIL import Image
import io
from app.models import ExpertReviewCreate, ExpertReviewResponse, APIResponse
from app.config import settings
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class ExpertReviewService:
    """Service for handling expert reviews and corrections"""
    
    def __init__(self):
        self.audit_service = AuditService()
        self.s3_client = None
        self._init_s3()
    
    def _init_s3(self):
        """Initialize S3 client for file storage"""
        try:
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
    
    async def submit_review(
        self,
        review_data: ExpertReviewCreate,
        db: asyncpg.Connection
    ) -> APIResponse:
        """Submit expert review for an answer"""
        try:
            # Validate review data
            validation_result = await self._validate_review(review_data)
            if not validation_result["valid"]:
                return APIResponse(
                    success=False,
                    message=validation_result["message"],
                    data={"errors": validation_result["errors"]}
                )
            
            # Handle correction if provided
            correction_data = None
            if review_data.correction:
                correction_data = await self._process_correction(
                    review_data.correction,
                    review_data.answer_id
                )
            
            # Store review in database
            review_id = await self._store_review(db, review_data, correction_data)
            
            # Update answer status
            await self._update_answer_status(db, review_data.answer_id, review_data.is_approved)
            
            # Log review action
            await self.audit_service.log_action(
                db=db,
                action="expert_review",
                user_id=review_data.expert_id,
                question_id=await self._get_question_id_from_answer(db, review_data.answer_id),
                details={
                    "review_id": str(review_id),
                    "is_approved": review_data.is_approved,
                    "has_correction": bool(review_data.correction)
                }
            )
            
            logger.info(f"Expert review {review_id} submitted successfully")
            
            return APIResponse(
                success=True,
                message="Expert review submitted successfully",
                data={
                    "review_id": str(review_id),
                    "is_approved": review_data.is_approved,
                    "has_correction": bool(review_data.correction)
                }
            )
            
        except Exception as e:
            logger.error(f"Error submitting expert review: {e}")
            return APIResponse(
                success=False,
                message="Failed to submit expert review",
                data={"error": str(e)}
            )
    
    async def _validate_review(self, review_data: ExpertReviewCreate) -> Dict[str, Any]:
        """Validate expert review data"""
        errors = []
        
        # Check if rejection reason is provided for rejected reviews
        if not review_data.is_approved and not review_data.rejection_reason:
            errors.append("Rejection reason is required for rejected reviews")
        
        # Validate correction data if provided
        if review_data.correction:
            correction_errors = await self._validate_correction(review_data.correction)
            errors.extend(correction_errors)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Validation failed" if errors else "Validation passed"
        }
    
    async def _validate_correction(self, correction: Dict[str, Any]) -> List[str]:
        """Validate correction data"""
        errors = []
        
        correction_type = correction.get("type")
        if not correction_type:
            errors.append("Correction type is required")
        elif correction_type not in ["text", "digital", "image"]:
            errors.append("Invalid correction type. Must be 'text', 'digital', or 'image'")
        
        content = correction.get("content")
        if not content:
            errors.append("Correction content is required")
        
        # Validate based on type
        if correction_type == "image":
            try:
                # Validate base64 image
                base64.b64decode(content)
            except Exception:
                errors.append("Invalid base64 image data")
        
        return errors
    
    async def _process_correction(
        self,
        correction: Dict[str, Any],
        answer_id: str
    ) -> Dict[str, Any]:
        """Process correction data and upload files if necessary"""
        try:
            correction_type = correction.get("type")
            content = correction.get("content")
            
            if correction_type == "text":
                return {
                    "type": "text",
                    "content": content,
                    "file_url": None
                }
            
            elif correction_type == "digital":
                # Upload digital file to S3
                file_url = await self._upload_digital_file(content, answer_id)
                return {
                    "type": "digital",
                    "content": content,
                    "file_url": file_url
                }
            
            elif correction_type == "image":
                # Process and upload image
                processed_image = await self._process_image(content)
                file_url = await self._upload_image(processed_image, answer_id)
                return {
                    "type": "image",
                    "content": content,
                    "file_url": file_url,
                    "processed_image": processed_image
                }
            
            return correction
            
        except Exception as e:
            logger.error(f"Error processing correction: {e}")
            raise
    
    async def _upload_digital_file(self, content: str, answer_id: str) -> str:
        """Upload digital file to S3"""
        try:
            if not self.s3_client:
                raise Exception("S3 client not initialized")
            
            # Decode base64 content
            file_data = base64.b64decode(content)
            
            # Generate file key
            file_key = f"corrections/{answer_id}/digital_file.pdf"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.aws_s3_bucket,
                Key=file_key,
                Body=file_data,
                ContentType="application/pdf"
            )
            
            # Return public URL
            return f"https://{settings.aws_s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{file_key}"
            
        except Exception as e:
            logger.error(f"Error uploading digital file: {e}")
            raise
    
    async def _process_image(self, content: str) -> str:
        """Process image for better quality"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(content)
            image = Image.open(io.BytesIO(image_data))
            
            # Enhance image quality
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast and sharpness
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Convert back to base64
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            processed_image = base64.b64encode(output.getvalue()).decode()
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            # Return original content if processing fails
            return content
    
    async def _upload_image(self, image_content: str, answer_id: str) -> str:
        """Upload processed image to S3"""
        try:
            if not self.s3_client:
                raise Exception("S3 client not initialized")
            
            # Decode base64 image
            image_data = base64.b64decode(image_content)
            
            # Generate file key
            file_key = f"corrections/{answer_id}/image.jpg"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.aws_s3_bucket,
                Key=file_key,
                Body=image_data,
                ContentType="image/jpeg"
            )
            
            # Return public URL
            return f"https://{settings.aws_s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{file_key}"
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise
    
    async def _store_review(
        self,
        db: asyncpg.Connection,
        review_data: ExpertReviewCreate,
        correction_data: Optional[Dict[str, Any]]
    ) -> str:
        """Store expert review in database"""
        try:
            review_id = await db.fetchval(
                """
                INSERT INTO expert_reviews (review_id, answer_id, expert_id, is_approved, rejection_reason, correction)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5)
                RETURNING review_id
                """,
                review_data.answer_id,
                review_data.expert_id,
                review_data.is_approved,
                review_data.rejection_reason,
                correction_data
            )
            
            return str(review_id)
            
        except Exception as e:
            logger.error(f"Error storing expert review: {e}")
            raise
    
    async def _update_answer_status(
        self,
        db: asyncpg.Connection,
        answer_id: str,
        is_approved: bool
    ) -> None:
        """Update answer status based on expert review"""
        try:
            await db.execute(
                """
                UPDATE answers 
                SET is_approved = $1, rejection_reason = $2
                WHERE answer_id = $3
                """,
                is_approved,
                None if is_approved else "Rejected by expert review",
                answer_id
            )
            
        except Exception as e:
            logger.error(f"Error updating answer status: {e}")
            raise
    
    async def _get_question_id_from_answer(
        self,
        db: asyncpg.Connection,
        answer_id: str
    ) -> Optional[str]:
        """Get question ID from answer ID"""
        try:
            question_id = await db.fetchval(
                "SELECT question_id FROM answers WHERE answer_id = $1",
                answer_id
            )
            return str(question_id) if question_id else None
            
        except Exception as e:
            logger.error(f"Error getting question ID from answer: {e}")
            return None
    
    async def get_expert_reviews(
        self,
        db: asyncpg.Connection,
        expert_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> APIResponse:
        """Get expert reviews with optional filtering"""
        try:
            query = """
                SELECT er.*, q.subject, q.type as question_type
                FROM expert_reviews er
                JOIN answers a ON er.answer_id = a.answer_id
                JOIN questions q ON a.question_id = q.question_id
                WHERE 1=1
            """
            params = []
            param_count = 0
            
            if expert_id:
                param_count += 1
                query += f" AND er.expert_id = ${param_count}"
                params.append(expert_id)
            
            query += f" ORDER BY er.created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            
            rows = await db.fetch(query, *params)
            
            reviews = []
            for row in rows:
                reviews.append({
                    "review_id": str(row["review_id"]),
                    "answer_id": str(row["answer_id"]),
                    "expert_id": str(row["expert_id"]),
                    "is_approved": row["is_approved"],
                    "rejection_reason": row["rejection_reason"],
                    "correction": row["correction"],
                    "created_at": row["created_at"].isoformat(),
                    "question_subject": row["subject"],
                    "question_type": row["question_type"]
                })
            
            return APIResponse(
                success=True,
                message="Expert reviews retrieved successfully",
                data={"reviews": reviews, "count": len(reviews)}
            )
            
        except Exception as e:
            logger.error(f"Error getting expert reviews: {e}")
            return APIResponse(
                success=False,
                message="Failed to get expert reviews",
                data={"error": str(e)}
            )
    
    async def get_pending_reviews(
        self,
        db: asyncpg.Connection,
        expert_id: Optional[str] = None,
        limit: int = 20
    ) -> APIResponse:
        """Get pending reviews for expert assignment"""
        try:
            query = """
                SELECT q.question_id, q.subject, q.type, q.created_at, a.answer_id, a.confidence_score
                FROM questions q
                JOIN answers a ON q.question_id = a.question_id
                WHERE q.status = 'review' 
                AND a.is_approved IS NULL
            """
            params = []
            param_count = 0
            
            if expert_id:
                param_count += 1
                query += f" AND a.expert_id = ${param_count}"
                params.append(expert_id)
            
            query += f" ORDER BY q.created_at ASC LIMIT ${param_count + 1}"
            params.append(limit)
            
            rows = await db.fetch(query, *params)
            
            pending_reviews = []
            for row in rows:
                pending_reviews.append({
                    "question_id": str(row["question_id"]),
                    "answer_id": str(row["answer_id"]),
                    "subject": row["subject"],
                    "type": row["type"],
                    "created_at": row["created_at"].isoformat(),
                    "confidence_score": row["confidence_score"]
                })
            
            return APIResponse(
                success=True,
                message="Pending reviews retrieved successfully",
                data={"pending_reviews": pending_reviews, "count": len(pending_reviews)}
            )
            
        except Exception as e:
            logger.error(f"Error getting pending reviews: {e}")
            return APIResponse(
                success=False,
                message="Failed to get pending reviews",
                data={"error": str(e)}
            )
    
    async def assign_expert_to_review(
        self,
        db: asyncpg.Connection,
        question_id: str,
        expert_id: str
    ) -> APIResponse:
        """Assign an expert to review a question"""
        try:
            # Update question status to review
            await db.execute(
                "UPDATE questions SET status = 'review' WHERE question_id = $1",
                question_id
            )
            
            # Update answer with expert assignment
            await db.execute(
                "UPDATE answers SET expert_id = $1 WHERE question_id = $2",
                expert_id,
                question_id
            )
            
            # Log assignment
            await self.audit_service.log_action(
                db=db,
                action="expert_assigned",
                user_id=expert_id,
                question_id=question_id,
                details={"assigned_to": expert_id}
            )
            
            return APIResponse(
                success=True,
                message="Expert assigned to review successfully",
                data={"question_id": question_id, "expert_id": expert_id}
            )
            
        except Exception as e:
            logger.error(f"Error assigning expert to review: {e}")
            return APIResponse(
                success=False,
                message="Failed to assign expert to review",
                data={"error": str(e)}
            )

