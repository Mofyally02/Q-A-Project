import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.submission_service import SubmissionService
from app.models import QuestionCreate, QuestionType

class TestSubmissionService:
    """Test cases for SubmissionService"""
    
    @pytest.fixture
    def submission_service(self):
        return SubmissionService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def sample_question(self):
        return QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": "What is the capital of France?"},
            subject="Geography"
        )
    
    @pytest.mark.asyncio
    async def test_submit_question_success(self, submission_service, mock_db, sample_question):
        """Test successful question submission"""
        # Mock database operations
        mock_db.execute.return_value = None
        
        # Mock queue service
        with patch.object(submission_service, 'queue_service') as mock_queue:
            mock_queue.enqueue_ai_processing.return_value = None
            
            # Mock audit service
            with patch.object(submission_service, 'audit_service') as mock_audit:
                mock_audit.log_action.return_value = True
                
                # Test submission
                result = await submission_service.submit_question(sample_question, mock_db)
                
                # Assertions
                assert result.success is True
                assert "question_id" in result.data
                assert result.data["status"] == "submitted"
                
                # Verify database calls
                assert mock_db.execute.call_count >= 2  # Insert question + audit log
                
                # Verify queue call
                mock_queue.enqueue_ai_processing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_submit_question_validation_error(self, submission_service, mock_db):
        """Test question submission with validation error"""
        # Create invalid question (empty content)
        invalid_question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": ""},  # Empty content
            subject="Geography"
        )
        
        # Test submission
        result = await submission_service.submit_question(invalid_question, mock_db)
        
        # Assertions
        assert result.success is False
        assert "Text content cannot be empty" in result.data["errors"]
    
    @pytest.mark.asyncio
    async def test_submit_question_invalid_type(self, submission_service, mock_db):
        """Test question submission with invalid type"""
        # Create question with invalid type
        invalid_question = QuestionCreate(
            client_id="test-client-123",
            type="invalid_type",  # Invalid type
            content={"data": "Test question"},
            subject="Geography"
        )
        
        # Test submission
        result = await submission_service.submit_question(invalid_question, mock_db)
        
        # Assertions
        assert result.success is False
        assert "Invalid question type" in result.data["errors"]
    
    @pytest.mark.asyncio
    async def test_submit_question_too_long(self, submission_service, mock_db):
        """Test question submission with content too long"""
        # Create question with very long content
        long_content = "A" * 6000  # Exceeds max length
        long_question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": long_content},
            subject="Geography"
        )
        
        # Test submission
        result = await submission_service.submit_question(long_question, mock_db)
        
        # Assertions
        assert result.success is False
        assert "Text content too long" in result.data["errors"]
    
    @pytest.mark.asyncio
    async def test_get_question_status_success(self, submission_service, mock_db):
        """Test getting question status successfully"""
        # Mock database response
        mock_row = Mock()
        mock_row.question_id = "test-question-123"
        mock_row.status = "processing"
        mock_row.created_at = "2024-01-01T00:00:00"
        mock_db.fetchrow.return_value = mock_row
        
        # Test getting status
        result = await submission_service.get_question_status("test-question-123", mock_db)
        
        # Assertions
        assert result.success is True
        assert result.data["question_id"] == "test-question-123"
        assert result.data["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_get_question_status_not_found(self, submission_service, mock_db):
        """Test getting status for non-existent question"""
        # Mock database response (no row found)
        mock_db.fetchrow.return_value = None
        
        # Test getting status
        result = await submission_service.get_question_status("non-existent", mock_db)
        
        # Assertions
        assert result.success is False
        assert "Question not found" in result.message
    
    @pytest.mark.asyncio
    async def test_get_user_questions_success(self, submission_service, mock_db):
        """Test getting user questions successfully"""
        # Mock database response
        mock_rows = [
            Mock(question_id="q1", type="text", subject="Math", status="delivered", created_at="2024-01-01"),
            Mock(question_id="q2", type="image", subject="Science", status="processing", created_at="2024-01-02")
        ]
        mock_db.fetch.return_value = mock_rows
        
        # Test getting user questions
        result = await submission_service.get_user_questions("test-client-123", mock_db)
        
        # Assertions
        assert result.success is True
        assert len(result.data["questions"]) == 2
        assert result.data["count"] == 2
    
    @pytest.mark.asyncio
    async def test_validate_question_text_valid(self, submission_service):
        """Test validation of valid text question"""
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": "What is the capital of France?"},
            subject="Geography"
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_question_text_empty(self, submission_service):
        """Test validation of empty text question"""
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": ""},
            subject="Geography"
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is False
        assert "Text content cannot be empty" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_validate_question_image_valid(self, submission_service):
        """Test validation of valid image question"""
        # Mock base64 image data
        import base64
        test_image = base64.b64encode(b"fake_image_data").decode()
        
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.IMAGE,
            content={"data": test_image, "format": "jpeg"},
            subject="Geography"
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_question_image_too_large(self, submission_service):
        """Test validation of image question that's too large"""
        # Mock large base64 image data (exceeds 5MB limit)
        import base64
        large_image = base64.b64encode(b"x" * (6 * 1024 * 1024)).decode()  # 6MB
        
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.IMAGE,
            content={"data": large_image, "format": "jpeg"},
            subject="Geography"
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is False
        assert "File too large" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_validate_question_invalid_base64(self, submission_service):
        """Test validation of image question with invalid base64"""
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.IMAGE,
            content={"data": "invalid_base64_data"},
            subject="Geography"
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is False
        assert "Invalid base64 image data" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_validate_question_missing_subject(self, submission_service):
        """Test validation of question with missing subject"""
        question = QuestionCreate(
            client_id="test-client-123",
            type=QuestionType.TEXT,
            content={"data": "What is the capital of France?"},
            subject=""  # Empty subject
        )
        
        result = await submission_service._validate_question(question)
        
        assert result["valid"] is False
        assert "Subject is required" in result["errors"]
