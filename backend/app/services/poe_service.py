import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
import openai
from app.config import settings
from app.models import APIResponse

logger = logging.getLogger(__name__)

class PoeService:
    """Enhanced service for Poe API integration with latest models"""
    
    def __init__(self):
        self.poe_models = {
            "gpt-5": {
                "api_key": settings.poe_api_key_chatgpt,
                "model": "GPT-5",
                "description": "Latest GPT-5 model for advanced reasoning"
            },
            "gpt-5-pro": {
                "api_key": settings.poe_api_key_chatgpt,
                "model": "GPT-5-Pro",
                "description": "Professional version of GPT-5"
            },
            "claude-sonnet-4.5": {
                "api_key": settings.poe_api_key_claude,
                "model": "Claude-Sonnet-4.5",
                "description": "Latest Claude model with enhanced reasoning"
            },
            "gemini-2.5-pro": {
                "api_key": settings.poe_api_key_gemini,
                "model": "Gemini-2.5-Pro",
                "description": "Google's latest Gemini model"
            },
            "grok-4": {
                "api_key": settings.poe_api_key_grok,
                "model": "Grok-4",
                "description": "xAI's latest Grok model"
            },
            "qwen-3-next-80b-think": {
                "api_key": settings.poe_api_key_qwen,
                "model": "Qwen-3-Next-80B-Think",
                "description": "Advanced reasoning model with 80B parameters"
            },
            "deepseek-v3.2-exp": {
                "api_key": settings.poe_api_key_deepseek,
                "model": "DeepSeek-V3.2-Exp",
                "description": "DeepSeek's experimental model"
            },
            "gpt-oss-120b-t": {
                "api_key": settings.poe_api_key_gpt_oss,
                "model": "GPT-OSS-120B-T",
                "description": "Open source GPT model with 120B parameters"
            },
            "kimi-k2-0905-t": {
                "api_key": settings.poe_api_key_kimi,
                "model": "Kimi-K2-0905-T",
                "description": "Kimi's latest model for complex reasoning"
            }
        }
    
    async def query_model(
        self,
        model_name: str,
        question_text: str,
        subject: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> APIResponse:
        """Query a specific Poe model"""
        try:
            if model_name not in self.poe_models:
                return APIResponse(
                    success=False,
                    message=f"Model {model_name} not supported",
                    data={"available_models": list(self.poe_models.keys())}
                )
            
            model_config = self.poe_models[model_name]
            
            # Use OpenAI client with Poe API
            client = openai.OpenAI(
                api_key=model_config["api_key"],
                base_url="https://api.poe.com/v1",
            )
            
            # Create chat completion
            chat = client.chat.completions.create(
                model=model_config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(subject, model_name)
                    },
                    {
                        "role": "user",
                        "content": question_text
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = chat.choices[0].message.content
            
            return APIResponse(
                success=True,
                message=f"Response from {model_name}",
                data={
                    "model": model_name,
                    "response": response_text,
                    "usage": chat.usage.dict() if chat.usage else {},
                    "model_info": model_config
                }
            )
            
        except Exception as e:
            logger.error(f"Error querying {model_name}: {e}")
            return APIResponse(
                success=False,
                message=f"Failed to query {model_name}",
                data={"error": str(e)}
            )
    
    async def query_multiple_models(
        self,
        model_names: List[str],
        question_text: str,
        subject: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> APIResponse:
        """Query multiple Poe models in parallel"""
        try:
            # Filter available models
            available_models = [name for name in model_names if name in self.poe_models]
            
            if not available_models:
                return APIResponse(
                    success=False,
                    message="No available models found",
                    data={"available_models": list(self.poe_models.keys())}
                )
            
            # Create tasks for parallel execution
            tasks = [
                self.query_model(model, question_text, subject, max_tokens, temperature)
                for model in available_models
            ]
            
            # Execute all queries in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_responses = []
            failed_responses = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_responses.append({
                        "model": available_models[i],
                        "error": str(result)
                    })
                elif result.success:
                    successful_responses.append(result.data)
                else:
                    failed_responses.append({
                        "model": available_models[i],
                        "error": result.message
                    })
            
            # Aggregate successful responses
            aggregated_response = self._aggregate_responses(successful_responses)
            
            return APIResponse(
                success=True,
                message="Multiple model query completed",
                data={
                    "aggregated_response": aggregated_response,
                    "individual_responses": successful_responses,
                    "failed_responses": failed_responses,
                    "total_models": len(available_models),
                    "successful_models": len(successful_responses),
                    "failed_models": len(failed_responses)
                }
            )
            
        except Exception as e:
            logger.error(f"Error querying multiple models: {e}")
            return APIResponse(
                success=False,
                message="Failed to query multiple models",
                data={"error": str(e)}
            )
    
    async def get_model_info(self, model_name: str) -> APIResponse:
        """Get information about a specific model"""
        try:
            if model_name not in self.poe_models:
                return APIResponse(
                    success=False,
                    message=f"Model {model_name} not found",
                    data={"available_models": list(self.poe_models.keys())}
                )
            
            model_config = self.poe_models[model_name]
            
            return APIResponse(
                success=True,
                message="Model information retrieved",
                data={
                    "model": model_name,
                    "display_name": model_config["model"],
                    "description": model_config["description"],
                    "api_key_configured": bool(model_config["api_key"]),
                    "base_url": "https://api.poe.com/v1"
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return APIResponse(
                success=False,
                message="Failed to get model info",
                data={"error": str(e)}
            )
    
    async def list_available_models(self) -> APIResponse:
        """List all available Poe models"""
        try:
            models_info = []
            
            for model_name, config in self.poe_models.items():
                models_info.append({
                    "model": model_name,
                    "display_name": config["model"],
                    "description": config["description"],
                    "api_key_configured": bool(config["api_key"]),
                    "base_url": "https://api.poe.com/v1"
                })
            
            return APIResponse(
                success=True,
                message="Available models retrieved",
                data={
                    "models": models_info,
                    "total_models": len(models_info),
                    "configured_models": len([m for m in models_info if m["api_key_configured"]])
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return APIResponse(
                success=False,
                message="Failed to list models",
                data={"error": str(e)}
            )
    
    def _get_system_prompt(self, subject: str, model_name: str) -> str:
        """Get system prompt based on subject and model"""
        base_prompt = f"""You are an expert academic tutor specializing in {subject}. 
        Provide detailed, accurate, and well-structured answers to academic questions. 
        Use clear explanations and provide examples when appropriate.
        
        Guidelines:
        - Provide comprehensive answers with proper structure
        - Use academic language and terminology
        - Include relevant examples and explanations
        - Ensure accuracy and cite sources when possible
        - Format your response clearly with proper paragraphs
        """
        
        # Model-specific enhancements
        if "gpt-5" in model_name.lower():
            base_prompt += "\n- Leverage your advanced reasoning capabilities for complex problems"
        elif "claude" in model_name.lower():
            base_prompt += "\n- Use your strong analytical skills for detailed explanations"
        elif "gemini" in model_name.lower():
            base_prompt += "\n- Utilize your multimodal capabilities when relevant"
        elif "grok" in model_name.lower():
            base_prompt += "\n- Apply your real-time knowledge and reasoning"
        elif "qwen" in model_name.lower():
            base_prompt += "\n- Use your advanced thinking capabilities for complex reasoning"
        elif "deepseek" in model_name.lower():
            base_prompt += "\n- Leverage your experimental features for innovative solutions"
        elif "kimi" in model_name.lower():
            base_prompt += "\n- Apply your complex reasoning abilities for thorough analysis"
        
        return base_prompt
    
    def _aggregate_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple responses with advanced analysis"""
        if not responses:
            return {"response": "", "confidence_score": 0.0, "sources": []}
        
        # Extract response texts
        response_texts = [r["response"] for r in responses if "response" in r]
        
        if not response_texts:
            return {"response": "", "confidence_score": 0.0, "sources": []}
        
        # Calculate similarity between responses
        similarities = self._calculate_similarities(response_texts)
        
        # Use advanced aggregation (weighted by model capabilities)
        final_response = self._weighted_majority_vote(responses, response_texts, similarities)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(similarities, len(responses))
        
        # Prepare sources
        sources = [
            {
                "model": r["model"],
                "model_info": r.get("model_info", {}),
                "usage": r.get("usage", {})
            }
            for r in responses if "model" in r
        ]
        
        return {
            "response": final_response,
            "confidence_score": confidence_score,
            "sources": sources,
            "individual_responses": responses,
            "similarity_scores": similarities
        }
    
    def _calculate_similarities(self, texts: List[str]) -> List[float]:
        """Calculate pairwise similarities between response texts"""
        if len(texts) < 2:
            return [1.0]
        
        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                # Enhanced similarity calculation
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
    
    def _weighted_majority_vote(self, responses: List[Dict[str, Any]], texts: List[str], similarities: List[float]) -> str:
        """Weighted majority voting based on model capabilities"""
        if len(texts) == 1:
            return texts[0]
        
        # Model weights based on capabilities
        model_weights = {
            "gpt-5": 1.0,
            "gpt-5-pro": 1.1,
            "claude-sonnet-4.5": 1.0,
            "gemini-2.5-pro": 0.9,
            "grok-4": 0.9,
            "qwen-3-next-80b-think": 0.8,
            "deepseek-v3.2-exp": 0.8,
            "gpt-oss-120b-t": 0.7,
            "kimi-k2-0905-t": 0.8
        }
        
        # Calculate weighted scores
        weighted_scores = []
        for i, response in enumerate(responses):
            model_name = response.get("model", "")
            weight = model_weights.get(model_name, 0.5)
            
            # Factor in similarity to other responses
            similarity_score = sum(similarities) / len(similarities) if similarities else 0.0
            weighted_score = weight * (1 + similarity_score * 0.2)
            
            weighted_scores.append((i, weighted_score))
        
        # Sort by weighted score
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the response with highest weighted score
        best_index = weighted_scores[0][0]
        return texts[best_index]
    
    def _calculate_confidence_score(self, similarities: List[float], num_responses: int) -> float:
        """Calculate confidence score based on agreement and number of responses"""
        if num_responses == 1:
            return 0.5  # Lower confidence with single response
        
        # Base confidence from similarity
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Boost confidence with more responses (up to a point)
        response_boost = min(0.2, (num_responses - 1) * 0.05)
        
        # Final confidence score
        confidence = min(1.0, avg_similarity + response_boost)
        
        return confidence

