import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.models import APIResponse

logger = logging.getLogger(__name__)

class OriginalityService:
    """Service for checking originality and plagiarism using Turnitin API"""
    
    def __init__(self):
        self.turnitin_api_key = settings.turnitin_api_key
        self.turnitin_base_url = "https://api.turnitin.com/v1"  # Example URL
        self.copyleaks_api_key = settings.turnitin_api_key  # Using same key for now
        self.copyleaks_base_url = "https://api.copyleaks.com/v3"  # Example URL
    
    async def check_originality(self, text: str, question_id: str = "") -> APIResponse:
        """Check text for originality and plagiarism"""
        try:
            # Try Turnitin API first
            if self.turnitin_api_key:
                turnitin_result = await self._check_with_turnitin(text, question_id)
                if turnitin_result:
                    return turnitin_result
            
            # Fallback to Copyleaks API
            if self.copyleaks_api_key:
                copyleaks_result = await self._check_with_copyleaks(text, question_id)
                if copyleaks_result:
                    return copyleaks_result
            
            # Fallback to basic rule-based check
            basic_result = await self._basic_originality_check(text)
            
            return APIResponse(
                success=True,
                message="Originality check completed",
                data=basic_result
            )
            
        except Exception as e:
            logger.error(f"Error in originality check: {e}")
            return APIResponse(
                success=False,
                message="Originality check failed",
                data={"error": str(e)}
            )
    
    async def _check_with_turnitin(self, text: str, question_id: str) -> Optional[APIResponse]:
        """Check originality using Turnitin API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.turnitin_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": text,
                    "title": f"Question {question_id}",
                    "author": "AL-Tech Academy",
                    "submission_type": "text"
                }
                
                # Submit for similarity check
                response = await client.post(
                    f"{self.turnitin_base_url}/submissions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    submission_id = data.get("submission_id")
                    
                    if submission_id:
                        # Wait for processing and get results
                        await asyncio.sleep(5)  # Wait for processing
                        
                        results_response = await client.get(
                            f"{self.turnitin_base_url}/submissions/{submission_id}/similarity",
                            headers=headers
                        )
                        
                        if results_response.status_code == 200:
                            results_data = results_response.json()
                            return self._process_turnitin_results(results_data)
                
                logger.warning(f"Turnitin API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Turnitin API: {e}")
            return None
    
    async def _check_with_copyleaks(self, text: str, question_id: str) -> Optional[APIResponse]:
        """Check originality using Copyleaks API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.copyleaks_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": text,
                    "title": f"Question {question_id}",
                    "author": "AL-Tech Academy",
                    "scan_type": "web"
                }
                
                # Submit for scan
                response = await client.post(
                    f"{self.copyleaks_base_url}/scans",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    scan_id = data.get("scan_id")
                    
                    if scan_id:
                        # Wait for processing and get results
                        await asyncio.sleep(5)  # Wait for processing
                        
                        results_response = await client.get(
                            f"{self.copyleaks_base_url}/scans/{scan_id}/results",
                            headers=headers
                        )
                        
                        if results_response.status_code == 200:
                            results_data = results_response.json()
                            return self._process_copyleaks_results(results_data)
                
                logger.warning(f"Copyleaks API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Copyleaks API: {e}")
            return None
    
    def _process_turnitin_results(self, results_data: Dict[str, Any]) -> APIResponse:
        """Process Turnitin API results"""
        try:
            similarity_score = results_data.get("similarity_score", 0.0)
            matches = results_data.get("matches", [])
            
            # Calculate AI content score (if available)
            ai_score = results_data.get("ai_score", 0.0)
            
            # Check thresholds
            is_original = similarity_score < (1.0 - settings.uniqueness_threshold)
            is_ai_compliant = ai_score < settings.ai_content_threshold
            
            return APIResponse(
                success=True,
                message="Turnitin originality check completed",
                data={
                    "similarity_score": similarity_score,
                    "ai_score": ai_score,
                    "is_original": is_original,
                    "is_ai_compliant": is_ai_compliant,
                    "uniqueness_percentage": (1.0 - similarity_score) * 100,
                    "ai_percentage": ai_score * 100,
                    "matches": matches,
                    "provider": "turnitin",
                    "compliance_status": "compliant" if is_original and is_ai_compliant else "non_compliant"
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing Turnitin results: {e}")
            return None
    
    def _process_copyleaks_results(self, results_data: Dict[str, Any]) -> APIResponse:
        """Process Copyleaks API results"""
        try:
            similarity_score = results_data.get("similarity_score", 0.0)
            matches = results_data.get("matches", [])
            
            # Calculate AI content score (if available)
            ai_score = results_data.get("ai_score", 0.0)
            
            # Check thresholds
            is_original = similarity_score < (1.0 - settings.uniqueness_threshold)
            is_ai_compliant = ai_score < settings.ai_content_threshold
            
            return APIResponse(
                success=True,
                message="Copyleaks originality check completed",
                data={
                    "similarity_score": similarity_score,
                    "ai_score": ai_score,
                    "is_original": is_original,
                    "is_ai_compliant": is_ai_compliant,
                    "uniqueness_percentage": (1.0 - similarity_score) * 100,
                    "ai_percentage": ai_score * 100,
                    "matches": matches,
                    "provider": "copyleaks",
                    "compliance_status": "compliant" if is_original and is_ai_compliant else "non_compliant"
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing Copyleaks results: {e}")
            return None
    
    async def _basic_originality_check(self, text: str) -> Dict[str, Any]:
        """Basic rule-based originality check as fallback"""
        try:
            # Check for common AI patterns
            ai_patterns = [
                r"it is important to note that",
                r"furthermore, it should be noted",
                r"in conclusion",
                r"it is evident that",
                r"it is crucial to understand",
                r"it is worth mentioning",
                r"it is essential to",
                r"it is necessary to",
                r"it is recommended that",
                r"it is suggested that",
                r"it is advised that",
                r"it is important to consider",
                r"it is worth considering",
                r"it is crucial to",
                r"it is vital to",
                r"it is imperative to",
                r"it is essential that",
                r"it is necessary that",
                r"it is recommended that",
                r"it is suggested that",
                r"it is advised that",
                r"it is important to note",
                r"it is worth noting",
                r"it is crucial to note",
                r"it is essential to note",
                r"it is necessary to note",
                r"it is recommended to note",
                r"it is suggested to note",
                r"it is advised to note",
                r"it is important to understand",
                r"it is worth understanding",
                r"it is crucial to understand",
                r"it is essential to understand",
                r"it is necessary to understand",
                r"it is recommended to understand",
                r"it is suggested to understand",
                r"it is advised to understand"
            ]
            
            import re
            ai_pattern_count = 0
            for pattern in ai_patterns:
                ai_pattern_count += len(re.findall(pattern, text.lower()))
            
            # Calculate AI content score
            ai_score = min(ai_pattern_count * 0.05, 1.0)  # Each pattern adds 5%
            
            # Check for repetitive phrases
            words = text.lower().split()
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Calculate repetition score
            total_words = len(words)
            unique_words = len(word_counts)
            repetition_score = 1.0 - (unique_words / total_words) if total_words > 0 else 0.0
            
            # Check for very long sentences (AI characteristic)
            sentences = text.split('.')
            long_sentence_count = sum(1 for sentence in sentences if len(sentence.split()) > 30)
            long_sentence_score = long_sentence_count / len(sentences) if sentences else 0.0
            
            # Calculate overall originality score
            originality_score = 1.0 - (ai_score * 0.4 + repetition_score * 0.3 + long_sentence_score * 0.3)
            
            # Check thresholds
            is_original = originality_score >= settings.uniqueness_threshold
            is_ai_compliant = ai_score < settings.ai_content_threshold
            
            return {
                "similarity_score": 1.0 - originality_score,
                "ai_score": ai_score,
                "is_original": is_original,
                "is_ai_compliant": is_ai_compliant,
                "uniqueness_percentage": originality_score * 100,
                "ai_percentage": ai_score * 100,
                "matches": [],
                "provider": "basic_rule_based",
                "compliance_status": "compliant" if is_original and is_ai_compliant else "non_compliant",
                "details": {
                    "ai_pattern_count": ai_pattern_count,
                    "repetition_score": repetition_score,
                    "long_sentence_score": long_sentence_score,
                    "total_words": total_words,
                    "unique_words": unique_words
                }
            }
            
        except Exception as e:
            logger.error(f"Error in basic originality check: {e}")
            return {
                "similarity_score": 0.0,
                "ai_score": 0.0,
                "is_original": True,
                "is_ai_compliant": True,
                "uniqueness_percentage": 100.0,
                "ai_percentage": 0.0,
                "matches": [],
                "provider": "basic_rule_based",
                "compliance_status": "compliant",
                "details": {"error": str(e)}
            }
    
    async def check_ai_content(self, text: str) -> Dict[str, Any]:
        """Check specifically for AI-generated content"""
        try:
            # AI detection patterns
            ai_patterns = [
                r"it is important to note that",
                r"furthermore, it should be noted",
                r"in conclusion",
                r"it is evident that",
                r"it is crucial to understand",
                r"it is worth mentioning",
                r"it is essential to",
                r"it is necessary to",
                r"it is recommended that",
                r"it is suggested that",
                r"it is advised that"
            ]
            
            import re
            ai_pattern_count = 0
            for pattern in ai_patterns:
                ai_pattern_count += len(re.findall(pattern, text.lower()))
            
            # Calculate AI score
            ai_score = min(ai_pattern_count * 0.1, 1.0)  # Each pattern adds 10%
            
            # Check for AI-typical sentence structures
            sentences = text.split('.')
            ai_sentence_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Check for passive voice (AI characteristic)
                    if re.search(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', sentence):
                        ai_sentence_count += 1
                    
                    # Check for very formal language
                    if re.search(r'\b(thus|therefore|hence|consequently|moreover|furthermore|additionally)\b', sentence):
                        ai_sentence_count += 1
                    
                    # Check for repetitive sentence starters
                    if sentence.startswith(('It is', 'This is', 'That is', 'There is', 'There are')):
                        ai_sentence_count += 1
            
            # Calculate AI sentence score
            ai_sentence_score = ai_sentence_count / len(sentences) if sentences else 0.0
            
            # Calculate overall AI score
            overall_ai_score = (ai_score + ai_sentence_score) / 2
            
            return {
                "ai_score": overall_ai_score,
                "ai_percentage": overall_ai_score * 100,
                "is_ai_compliant": overall_ai_score < settings.ai_content_threshold,
                "ai_pattern_count": ai_pattern_count,
                "ai_sentence_count": ai_sentence_count,
                "total_sentences": len(sentences),
                "compliance_status": "compliant" if overall_ai_score < settings.ai_content_threshold else "non_compliant"
            }
            
        except Exception as e:
            logger.error(f"Error checking AI content: {e}")
            return {
                "ai_score": 0.0,
                "ai_percentage": 0.0,
                "is_ai_compliant": True,
                "ai_pattern_count": 0,
                "ai_sentence_count": 0,
                "total_sentences": 0,
                "compliance_status": "compliant"
            }

