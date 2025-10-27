import asyncio
import logging
import re
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.models import APIResponse

logger = logging.getLogger(__name__)

class HumanizationService:
    """Service for humanizing AI-generated content using Stealth API"""
    
    def __init__(self):
        self.stealth_api_key = settings.stealth_api_key
        self.stealth_base_url = "https://api.stealthwriter.com/v1"  # Example URL
    
    async def humanize_text(self, ai_response: str, question_subject: str = "") -> APIResponse:
        """Humanize AI-generated text to make it more natural and less detectable"""
        try:
            # First, try using Stealth API
            if self.stealth_api_key:
                humanized_text = await self._humanize_with_stealth(ai_response, question_subject)
                if humanized_text:
                    return APIResponse(
                        success=True,
                        message="Text humanized successfully",
                        data={
                            "original_text": ai_response,
                            "humanized_text": humanized_text,
                            "method": "stealth_api"
                        }
                    )
            
            # Fallback to rule-based humanization
            humanized_text = await self._rule_based_humanization(ai_response)
            
            return APIResponse(
                success=True,
                message="Text humanized successfully",
                data={
                    "original_text": ai_response,
                    "humanized_text": humanized_text,
                    "method": "rule_based"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in humanization: {e}")
            return APIResponse(
                success=False,
                message="Humanization failed",
                data={"error": str(e)}
            )
    
    async def _humanize_with_stealth(self, text: str, subject: str) -> Optional[str]:
        """Humanize text using Stealth API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.stealth_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": text,
                    "subject": subject,
                    "style": "academic",
                    "tone": "professional",
                    "humanize_level": "high"
                }
                
                response = await client.post(
                    f"{self.stealth_base_url}/humanize",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("humanized_text", "")
                else:
                    logger.warning(f"Stealth API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Stealth API: {e}")
            return None
    
    async def _rule_based_humanization(self, text: str) -> str:
        """Apply rule-based humanization techniques"""
        try:
            humanized_text = text
            
            # 1. Add natural variations to sentence structure
            humanized_text = self._vary_sentence_structure(humanized_text)
            
            # 2. Replace AI-typical phrases with more human expressions
            humanized_text = self._replace_ai_phrases(humanized_text)
            
            # 3. Add transitional phrases and connectors
            humanized_text = self._add_transitions(humanized_text)
            
            # 4. Vary vocabulary and add synonyms
            humanized_text = self._vary_vocabulary(humanized_text)
            
            # 5. Add personal touches and opinions where appropriate
            humanized_text = self._add_personal_touches(humanized_text)
            
            # 6. Ensure proper academic tone
            humanized_text = self._ensure_academic_tone(humanized_text)
            
            return humanized_text
            
        except Exception as e:
            logger.error(f"Error in rule-based humanization: {e}")
            return text
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure to make it more natural"""
        sentences = text.split('. ')
        varied_sentences = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Occasionally start with different connectors
                if i > 0 and i % 3 == 0:
                    connectors = ["Furthermore,", "Additionally,", "Moreover,", "In addition,"]
                    if not any(sentence.startswith(conn) for conn in connectors):
                        sentence = f"{connectors[i % len(connectors)]} {sentence.lower()}"
                
                varied_sentences.append(sentence)
        
        return '. '.join(varied_sentences)
    
    def _replace_ai_phrases(self, text: str) -> str:
        """Replace AI-typical phrases with more human expressions"""
        replacements = {
            "It is important to note that": "It's worth noting that",
            "Furthermore, it should be noted": "Additionally",
            "In conclusion": "To summarize",
            "It is evident that": "It's clear that",
            "It is crucial to understand": "It's important to understand",
            "It is worth mentioning": "It's worth mentioning",
            "It is essential to": "It's essential to",
            "It is necessary to": "It's necessary to",
            "It is recommended that": "I recommend that",
            "It is suggested that": "I suggest that",
            "It is advised that": "I advise that",
            "It is important to consider": "Consider",
            "It is worth considering": "Consider",
            "It is crucial to": "It's crucial to",
            "It is vital to": "It's vital to",
            "It is imperative to": "It's imperative to",
            "It is essential that": "It's essential that",
            "It is necessary that": "It's necessary that",
            "It is recommended that": "I recommend that",
            "It is suggested that": "I suggest that",
            "It is advised that": "I advise that",
            "It is important to note": "Note that",
            "It is worth noting": "Note that",
            "It is crucial to note": "Note that",
            "It is essential to note": "Note that",
            "It is necessary to note": "Note that",
            "It is recommended to note": "Note that",
            "It is suggested to note": "Note that",
            "It is advised to note": "Note that",
            "It is important to understand": "Understand that",
            "It is worth understanding": "Understand that",
            "It is crucial to understand": "Understand that",
            "It is essential to understand": "Understand that",
            "It is necessary to understand": "Understand that",
            "It is recommended to understand": "Understand that",
            "It is suggested to understand": "Understand that",
            "It is advised to understand": "Understand that"
        }
        
        for ai_phrase, human_phrase in replacements.items():
            text = text.replace(ai_phrase, human_phrase)
        
        return text
    
    def _add_transitions(self, text: str) -> str:
        """Add natural transitional phrases"""
        # This is a simplified version - in practice, you'd want more sophisticated logic
        transitions = [
            "However,", "On the other hand,", "Conversely,", "In contrast,",
            "Similarly,", "Likewise,", "In the same way,", "Correspondingly,",
            "Therefore,", "Consequently,", "As a result,", "Thus,",
            "For example,", "For instance,", "Specifically,", "In particular,",
            "In addition,", "Furthermore,", "Moreover,", "Additionally,",
            "Finally,", "In conclusion,", "To summarize,", "Overall,"
        ]
        
        # Add transitions at the beginning of some sentences
        sentences = text.split('. ')
        for i in range(1, len(sentences)):
            if i % 4 == 0 and not any(sentences[i].startswith(trans) for trans in transitions):
                sentences[i] = f"{transitions[i % len(transitions)]} {sentences[i].lower()}"
        
        return '. '.join(sentences)
    
    def _vary_vocabulary(self, text: str) -> str:
        """Replace common words with synonyms to vary vocabulary"""
        synonyms = {
            "important": ["crucial", "vital", "essential", "significant"],
            "good": ["excellent", "outstanding", "superior", "remarkable"],
            "bad": ["poor", "inadequate", "substandard", "deficient"],
            "big": ["large", "substantial", "considerable", "significant"],
            "small": ["minor", "minimal", "negligible", "insignificant"],
            "many": ["numerous", "multiple", "various", "diverse"],
            "few": ["limited", "scarce", "minimal", "restricted"],
            "often": ["frequently", "commonly", "regularly", "typically"],
            "sometimes": ["occasionally", "periodically", "intermittently", "sporadically"],
            "always": ["consistently", "invariably", "perpetually", "constantly"],
            "never": ["rarely", "seldom", "infrequently", "hardly ever"],
            "very": ["extremely", "highly", "significantly", "considerably"],
            "really": ["genuinely", "truly", "actually", "indeed"],
            "quite": ["rather", "fairly", "somewhat", "relatively"],
            "just": ["merely", "simply", "only", "barely"],
            "also": ["additionally", "furthermore", "moreover", "likewise"],
            "but": ["however", "nevertheless", "nonetheless", "yet"],
            "so": ["therefore", "consequently", "thus", "hence"],
            "because": ["since", "as", "due to", "owing to"],
            "if": ["provided that", "assuming that", "in case", "supposing that"],
            "when": ["whenever", "at the time", "during", "while"],
            "where": ["wherever", "in which", "at which", "wherein"],
            "how": ["in what way", "by what means", "the manner in which", "the way in which"],
            "why": ["for what reason", "on what grounds", "the reason why", "the cause of"],
            "what": ["which", "that which", "the thing that", "the one that"],
            "who": ["whom", "the person who", "the one who", "the individual who"],
            "which": ["that", "the one that", "the thing that", "the item that"]
        }
        
        words = text.split()
        for i, word in enumerate(words):
            # Remove punctuation for comparison
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in synonyms:
                # Choose a synonym (you could make this more sophisticated)
                synonym = synonyms[clean_word][i % len(synonyms[clean_word])]
                # Preserve original capitalization and punctuation
                if word.isupper():
                    synonym = synonym.upper()
                elif word.istitle():
                    synonym = synonym.title()
                words[i] = word.replace(clean_word, synonym)
        
        return ' '.join(words)
    
    def _add_personal_touches(self, text: str) -> str:
        """Add personal touches to make the text more human"""
        # Add occasional personal opinions or experiences
        personal_touches = [
            "In my experience,",
            "From what I've observed,",
            "I've found that",
            "In my view,",
            "I believe that",
            "I think that",
            "I would argue that",
            "I would suggest that",
            "I would recommend that",
            "I would advise that"
        ]
        
        # Add personal touches to some sentences
        sentences = text.split('. ')
        for i in range(1, len(sentences)):
            if i % 5 == 0 and not any(sentences[i].startswith(touch) for touch in personal_touches):
                sentences[i] = f"{personal_touches[i % len(personal_touches)]} {sentences[i].lower()}"
        
        return '. '.join(sentences)
    
    def _ensure_academic_tone(self, text: str) -> str:
        """Ensure the text maintains an academic tone"""
        # Remove informal language
        informal_replacements = {
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "hasn't": "has not",
            "haven't": "have not",
            "hadn't": "had not",
            "doesn't": "does not",
            "didn't": "did not",
            "wouldn't": "would not",
            "shouldn't": "should not",
            "couldn't": "could not",
            "mustn't": "must not",
            "needn't": "need not",
            "oughtn't": "ought not",
            "shan't": "shall not",
            "ain't": "is not",
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "kinda": "kind of",
            "sorta": "sort of",
            "lots of": "many",
            "a lot of": "many",
            "tons of": "many",
            "loads of": "many",
            "heaps of": "many",
            "bunch of": "group of",
            "couple of": "two",
            "few of": "some",
            "some of": "several",
            "most of": "the majority of",
            "all of": "all",
            "every one of": "each",
            "each one of": "each",
            "every single": "every",
            "each and every": "every",
            "every last": "every",
            "every single one": "every one",
            "each and every one": "every one",
            "every last one": "every one"
        }
        
        for informal, formal in informal_replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    async def validate_humanization_quality(self, original_text: str, humanized_text: str) -> Dict[str, Any]:
        """Validate the quality of humanization"""
        try:
            # Check for AI detection patterns
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
            
            ai_pattern_count = 0
            for pattern in ai_patterns:
                ai_pattern_count += len(re.findall(pattern, humanized_text.lower()))
            
            # Check for informal language
            informal_patterns = [
                r"don't", r"can't", r"won't", r"isn't", r"aren't",
                r"gonna", r"wanna", r"gotta", r"kinda", r"sorta"
            ]
            
            informal_count = 0
            for pattern in informal_patterns:
                informal_count += len(re.findall(pattern, humanized_text.lower()))
            
            # Calculate quality score
            quality_score = 1.0 - (ai_pattern_count * 0.1) - (informal_count * 0.05)
            quality_score = max(0.0, min(1.0, quality_score))
            
            return {
                "quality_score": quality_score,
                "ai_patterns_found": ai_pattern_count,
                "informal_language_found": informal_count,
                "is_acceptable": quality_score >= 0.7
            }
            
        except Exception as e:
            logger.error(f"Error validating humanization quality: {e}")
            return {
                "quality_score": 0.0,
                "ai_patterns_found": 0,
                "informal_language_found": 0,
                "is_acceptable": False
            }

