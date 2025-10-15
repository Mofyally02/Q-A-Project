import asyncio
import base64
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional
import httpx
import pytesseract
from PIL import Image
import io
from app.config import settings
from app.models import APIResponse
from app.services.poe_service import PoeService

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI processing using multiple LLM providers"""
    
    def __init__(self):
        self.llm_clients = {
            # Direct API clients
            "openai": {"api_key": settings.openai_api_key, "base_url": "https://api.openai.com/v1"},
            "anthropic": {"api_key": settings.anthropic_api_key, "base_url": "https://api.anthropic.com/v1"},
            "google": {"api_key": settings.google_api_key, "base_url": "https://generativelanguage.googleapis.com/v1beta"},
            "xai": {"api_key": settings.xai_api_key, "base_url": "https://api.x.ai/v1"}
        }
        
        # Initialize Poe service for latest models
        self.poe_service = PoeService()
    
    async def process_question(self, question_data: Dict[str, Any]) -> APIResponse:
        """Process a question using multiple AI providers"""
        try:
            # Extract text from question (handle both text and image)
            question_text = await self._extract_question_text(question_data)
            
            if not question_text:
                return APIResponse(
                    success=False,
                    message="Failed to extract text from question"
                )
            
            # Query multiple LLM providers in parallel
            responses = await self._query_llm_providers(question_text, question_data.get("subject", ""))
            
            if not responses:
                return APIResponse(
                    success=False,
                    message="No AI responses received"
                )
            
            # Aggregate responses and calculate confidence
            aggregated_response = await self._aggregate_responses(responses)
            
            # Check confidence threshold
            if aggregated_response["confidence_score"] < settings.min_confidence_score:
                logger.warning(f"Low confidence score: {aggregated_response['confidence_score']}")
                # Could trigger expert review here
            
            return APIResponse(
                success=True,
                message="AI processing completed",
                data=aggregated_response
            )
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            return APIResponse(
                success=False,
                message="AI processing failed",
                data={"error": str(e)}
            )
    
    async def _extract_question_text(self, question_data: Dict[str, Any]) -> Optional[str]:
        """Extract text from question content (handles both text and image)"""
        try:
            question_type = question_data.get("type")
            content = question_data.get("content", {})
            
            if question_type == "text":
                return content.get("data", "")
            
            elif question_type == "image":
                # Extract text from image using OCR
                image_data = content.get("data", "")
                if not image_data:
                    return None
                
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Use OCR to extract text
                extracted_text = pytesseract.image_to_string(image)
                return extracted_text.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting question text: {e}")
            return None
    
    async def _query_llm_providers(self, question_text: str, subject: str) -> List[Dict[str, Any]]:
        """Query multiple LLM providers in parallel"""
        tasks = []
        
        # Create tasks for direct API providers
        for provider, config in self.llm_clients.items():
            if config["api_key"]:
                task = self._query_single_provider(provider, question_text, subject, config)
                tasks.append(task)
        
        # Create task for Poe API models (latest models)
        poe_task = self._query_poe_models(question_text, subject)
        tasks.append(poe_task)
        
        # Execute all queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid responses
        valid_responses = []
        for i, result in enumerate(results):
            if isinstance(result, dict) and "response" in result:
                valid_responses.append(result)
            elif isinstance(result, Exception):
                provider_name = list(self.llm_clients.keys())[i] if i < len(self.llm_clients) else "Poe API"
                logger.error(f"Error querying provider {provider_name}: {result}")
        
        return valid_responses
    
    async def _query_single_provider(self, provider: str, question_text: str, subject: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Query a single LLM provider"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if provider == "openai":
                    return await self._query_openai(client, question_text, subject, config)
                elif provider == "anthropic":
                    return await self._query_anthropic(client, question_text, subject, config)
                elif provider == "google":
                    return await self._query_google(client, question_text, subject, config)
                elif provider == "xai":
                    return await self._query_xai(client, question_text, subject, config)
                else:
                    raise ValueError(f"Unknown provider: {provider}")
        
        except Exception as e:
            logger.error(f"Error querying {provider}: {e}")
            return {"provider": provider, "error": str(e)}
    
    async def _query_openai(self, client: httpx.AsyncClient, question_text: str, subject: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Query OpenAI API"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are an expert academic tutor specializing in {subject}. Provide detailed, accurate, and well-structured answers to academic questions."
                },
                {
                    "role": "user",
                    "content": question_text
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = await client.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "provider": "openai",
                "response": data["choices"][0]["message"]["content"],
                "model": data["model"],
                "usage": data.get("usage", {})
            }
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    async def _query_anthropic(self, client: httpx.AsyncClient, question_text: str, subject: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Query Anthropic Claude API"""
        headers = {
            "x-api-key": config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": f"Subject: {subject}\n\nQuestion: {question_text}\n\nPlease provide a detailed academic answer."
                }
            ]
        }
        
        response = await client.post(
            f"{config['base_url']}/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "provider": "anthropic",
                "response": data["content"][0]["text"],
                "model": data["model"],
                "usage": data.get("usage", {})
            }
        else:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    async def _query_google(self, client: httpx.AsyncClient, question_text: str, subject: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Query Google Gemini API"""
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Subject: {subject}\n\nQuestion: {question_text}\n\nPlease provide a detailed academic answer."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2000
            }
        }
        
        response = await client.post(
            f"{config['base_url']}/models/gemini-pro:generateContent?key={config['api_key']}",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "provider": "google",
                "response": data["candidates"][0]["content"]["parts"][0]["text"],
                "model": "gemini-pro",
                "usage": data.get("usageMetadata", {})
            }
        else:
            raise Exception(f"Google API error: {response.status_code} - {response.text}")
    
    async def _query_xai(self, client: httpx.AsyncClient, question_text: str, subject: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Query xAI Grok API"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-beta",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are an expert academic tutor specializing in {subject}. Provide detailed, accurate, and well-structured answers to academic questions."
                },
                {
                    "role": "user",
                    "content": question_text
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = await client.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "provider": "xai",
                "response": data["choices"][0]["message"]["content"],
                "model": data["model"],
                "usage": data.get("usage", {})
            }
        else:
            raise Exception(f"xAI API error: {response.status_code} - {response.text}")
    
    async def _query_poe_models(self, question_text: str, subject: str) -> Dict[str, Any]:
        """Query Poe API models using the dedicated Poe service"""
        try:
            # Select best models for the query
            selected_models = ["gpt-5", "claude-sonnet-4.5", "gemini-2.5-pro"]
            
            # Query multiple Poe models
            result = await self.poe_service.query_multiple_models(
                selected_models, question_text, subject
            )
            
            if result.success:
                aggregated_data = result.data["aggregated_response"]
                return {
                    "provider": "poe_api",
                    "response": aggregated_data["response"],
                    "model": "multiple_poe_models",
                    "confidence_score": aggregated_data["confidence_score"],
                    "sources": aggregated_data["sources"],
                    "usage": {}
                }
            else:
                return {"provider": "poe_api", "error": result.message}
                
        except Exception as e:
            logger.error(f"Error querying Poe models: {e}")
            return {"provider": "poe_api", "error": str(e)}
    
    async def _aggregate_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple AI responses and calculate confidence score"""
        if not responses:
            return {"response": "", "confidence_score": 0.0, "sources": []}
        
        # Extract response texts
        response_texts = [r["response"] for r in responses if "response" in r]
        
        if not response_texts:
            return {"response": "", "confidence_score": 0.0, "sources": []}
        
        # Calculate similarity between responses
        similarities = self._calculate_similarities(response_texts)
        
        # Use majority voting for final response
        final_response = self._majority_vote(response_texts, similarities)
        
        # Calculate confidence score based on agreement
        confidence_score = np.mean(similarities) if similarities else 0.0
        
        # Prepare sources
        sources = [
            {
                "provider": r["provider"],
                "model": r.get("model", "unknown"),
                "usage": r.get("usage", {})
            }
            for r in responses if "provider" in r
        ]
        
        return {
            "response": final_response,
            "confidence_score": float(confidence_score),
            "sources": sources,
            "individual_responses": responses
        }
    
    def _calculate_similarities(self, texts: List[str]) -> List[float]:
        """Calculate pairwise similarities between response texts"""
        if len(texts) < 2:
            return [1.0]
        
        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                # Simple similarity based on common words
                words1 = set(texts[i].lower().split())
                words2 = set(texts[j].lower().split())
                
                if len(words1) == 0 and len(words2) == 0:
                    similarity = 1.0
                else:
                    intersection = len(words1.intersection(words2))
                    union = len(words1.union(words2))
                    similarity = intersection / union if union > 0 else 0.0
                
                similarities.append(similarity)
        
        return similarities
    
    def _majority_vote(self, texts: List[str], similarities: List[float]) -> str:
        """Select the best response using majority voting"""
        if len(texts) == 1:
            return texts[0]
        
        # For now, return the longest response as a simple heuristic
        # In a more sophisticated implementation, you could use semantic similarity
        return max(texts, key=len)
