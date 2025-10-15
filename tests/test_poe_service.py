import pytest
from unittest.mock import Mock, patch
from app.services.poe_service import PoeService
from app.models import APIResponse

class TestPoeService:
    """Test cases for PoeService"""
    
    @pytest.fixture
    def poe_service(self):
        return PoeService()
    
    def test_init(self, poe_service):
        """Test PoeService initialization"""
        assert poe_service is not None
        assert hasattr(poe_service, 'poe_models')
        assert len(poe_service.poe_models) > 0
        
        # Check that all expected models are present
        expected_models = [
            "gpt-5", "gpt-5-pro", "claude-sonnet-4.5", "gemini-2.5-pro",
            "grok-4", "qwen-3-next-80b-think", "deepseek-v3.2-exp",
            "gpt-oss-120b-t", "kimi-k2-0905-t"
        ]
        
        for model in expected_models:
            assert model in poe_service.poe_models
    
    @pytest.mark.asyncio
    async def test_list_available_models(self, poe_service):
        """Test listing available models"""
        result = await poe_service.list_available_models()
        
        assert isinstance(result, APIResponse)
        assert result.success is True
        assert "models" in result.data
        assert "total_models" in result.data
        assert "configured_models" in result.data
        assert len(result.data["models"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_model_info_valid(self, poe_service):
        """Test getting info for valid model"""
        result = await poe_service.get_model_info("gpt-5")
        
        assert isinstance(result, APIResponse)
        assert result.success is True
        assert result.data["model"] == "gpt-5"
        assert "display_name" in result.data
        assert "description" in result.data
        assert "api_key_configured" in result.data
    
    @pytest.mark.asyncio
    async def test_get_model_info_invalid(self, poe_service):
        """Test getting info for invalid model"""
        result = await poe_service.get_model_info("invalid-model")
        
        assert isinstance(result, APIResponse)
        assert result.success is False
        assert "not found" in result.message.lower()
        assert "available_models" in result.data
    
    @pytest.mark.asyncio
    async def test_query_model_success(self, poe_service):
        """Test successful model query"""
        with patch('openai.OpenAI') as mock_openai:
            # Mock the OpenAI client
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock the chat completion response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage = Mock()
            mock_response.usage.dict.return_value = {"tokens": 100}
            
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await poe_service.query_model(
                "gpt-5", "Test question", "Test subject"
            )
            
            assert isinstance(result, APIResponse)
            assert result.success is True
            assert result.data["response"] == "Test response"
            assert result.data["model"] == "gpt-5"
    
    @pytest.mark.asyncio
    async def test_query_model_invalid_model(self, poe_service):
        """Test querying invalid model"""
        result = await poe_service.query_model(
            "invalid-model", "Test question", "Test subject"
        )
        
        assert isinstance(result, APIResponse)
        assert result.success is False
        assert "not supported" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_query_multiple_models_success(self, poe_service):
        """Test successful multiple model query"""
        with patch.object(poe_service, 'query_model') as mock_query:
            # Mock successful responses
            mock_response = APIResponse(
                success=True,
                message="Success",
                data={
                    "model": "gpt-5",
                    "response": "Test response",
                    "model_info": {"description": "Test model"}
                }
            )
            mock_query.return_value = mock_response
            
            result = await poe_service.query_multiple_models(
                ["gpt-5", "claude-sonnet-4.5"], "Test question", "Test subject"
            )
            
            assert isinstance(result, APIResponse)
            assert result.success is True
            assert "aggregated_response" in result.data
            assert "individual_responses" in result.data
            assert len(result.data["individual_responses"]) == 2
    
    @pytest.mark.asyncio
    async def test_query_multiple_models_no_available(self, poe_service):
        """Test multiple model query with no available models"""
        result = await poe_service.query_multiple_models(
            ["invalid-model-1", "invalid-model-2"], "Test question", "Test subject"
        )
        
        assert isinstance(result, APIResponse)
        assert result.success is False
        assert "no available models" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_get_system_prompt(self, poe_service):
        """Test system prompt generation"""
        prompt = poe_service._get_system_prompt("Mathematics", "gpt-5")
        
        assert isinstance(prompt, str)
        assert "Mathematics" in prompt
        assert "academic tutor" in prompt.lower()
        assert "gpt-5" in prompt.lower() or "reasoning" in prompt.lower()
    
    def test_calculate_similarities(self, poe_service):
        """Test similarity calculation"""
        texts = [
            "This is a test response about mathematics.",
            "This is a test response about mathematics and science.",
            "This is a completely different response about history."
        ]
        
        similarities = poe_service._calculate_similarities(texts)
        
        assert isinstance(similarities, list)
        assert len(similarities) > 0
        # First two should be more similar than with the third
        assert similarities[0] > similarities[1]
    
    def test_weighted_majority_vote(self, poe_service):
        """Test weighted majority voting"""
        responses = [
            {"model": "gpt-5", "response": "Response 1"},
            {"model": "claude-sonnet-4.5", "response": "Response 2"},
            {"model": "gemini-2.5-pro", "response": "Response 1"}
        ]
        texts = ["Response 1", "Response 2", "Response 1"]
        similarities = [0.8, 0.3, 0.8]
        
        result = poe_service._weighted_majority_vote(responses, texts, similarities)
        
        assert isinstance(result, str)
        assert result in texts
    
    def test_calculate_confidence_score(self, poe_service):
        """Test confidence score calculation"""
        similarities = [0.8, 0.7, 0.9]
        num_responses = 3
        
        score = poe_service._calculate_confidence_score(similarities, num_responses)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high with good similarities
    
    def test_calculate_confidence_score_single_response(self, poe_service):
        """Test confidence score with single response"""
        similarities = []
        num_responses = 1
        
        score = poe_service._calculate_confidence_score(similarities, num_responses)
        
        assert score == 0.5  # Should be 0.5 for single response
    
    def test_aggregate_responses(self, poe_service):
        """Test response aggregation"""
        responses = [
            {
                "model": "gpt-5",
                "response": "This is a test response about mathematics.",
                "model_info": {"description": "GPT-5 model"},
                "usage": {"tokens": 100}
            },
            {
                "model": "claude-sonnet-4.5",
                "response": "This is a test response about mathematics and algebra.",
                "model_info": {"description": "Claude model"},
                "usage": {"tokens": 120}
            }
        ]
        
        result = poe_service._aggregate_responses(responses)
        
        assert isinstance(result, dict)
        assert "response" in result
        assert "confidence_score" in result
        assert "sources" in result
        assert "individual_responses" in result
        assert len(result["sources"]) == 2
        assert 0.0 <= result["confidence_score"] <= 1.0
    
    def test_aggregate_responses_empty(self, poe_service):
        """Test response aggregation with empty list"""
        result = poe_service._aggregate_responses([])
        
        assert isinstance(result, dict)
        assert result["response"] == ""
        assert result["confidence_score"] == 0.0
        assert result["sources"] == []
