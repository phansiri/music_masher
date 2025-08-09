"""
Content Generation Service for Lit Music Mashup AI Platform.

This module provides educational content generation capabilities using Ollama
integration with context-enhanced prompting and comprehensive validation.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage

from app.config import get_settings
from app.db import AsyncConversationDB, ConversationPhase, MessageRole

# Configure logging
logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    """Types of educational content that can be generated."""
    THEORY_LESSON = "theory_lesson"
    CULTURAL_CONTEXT = "cultural_context"
    PRACTICAL_EXERCISE = "practical_exercise"
    HISTORICAL_BACKGROUND = "historical_background"
    COMPOSITION_GUIDE = "composition_guide"
    ANALYSIS = "analysis"
    TEACHING_NOTES = "teaching_notes"

class SkillLevel(str, Enum):
    """Educational skill levels for content adaptation."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentQuality(str, Enum):
    """Quality levels for generated content."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"

@dataclass
class GenerationRequest:
    """Request model for content generation."""
    prompt: str
    content_type: ContentType
    skill_level: SkillLevel
    context: Dict[str, Any]
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None

@dataclass
class GenerationResponse:
    """Response model for generated content."""
    content: str
    content_type: ContentType
    skill_level: SkillLevel
    quality_score: float
    quality_level: ContentQuality
    confidence_score: float
    generation_time: float
    model_used: str
    context_used: Dict[str, Any]
    suggestions: List[str]
    metadata: Dict[str, Any]

class ContentValidationResult(BaseModel):
    """Result of content validation."""
    is_appropriate: bool = Field(..., description="Whether content is appropriate")
    cultural_sensitivity_score: float = Field(..., ge=0.0, le=1.0, description="Cultural sensitivity score")
    educational_value_score: float = Field(..., ge=0.0, le=1.0, description="Educational value score")
    age_appropriateness: bool = Field(..., description="Whether content is age appropriate")
    issues: List[str] = Field(default_factory=list, description="List of identified issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class QualityMetrics(BaseModel):
    """Quality metrics for generated content."""
    educational_value: float = Field(..., ge=0.0, le=10.0, description="Educational value score")
    cultural_accuracy: float = Field(..., ge=0.0, le=10.0, description="Cultural accuracy score")
    engagement_level: float = Field(..., ge=0.0, le=10.0, description="Engagement level score")
    content_relevance: float = Field(..., ge=0.0, le=10.0, description="Content relevance score")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall quality score")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in scoring")

class OllamaClient:
    """Async client for Ollama model interactions."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.available_models = {
            "mistral-small3.2": "mistral-small3.2:latest",
            "llama3.1-8b": "llama3.1:8b",
            "command-r": "command-r:latest",
            "deepseek-r1": "deepseek-r1:32b"
        }
        self.default_model = "mistral-small3.2:latest"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate content using Ollama."""
        if model is None:
            model = self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

class PromptBuilder:
    """Builds context-enhanced prompts for educational content generation."""
    
    def __init__(self):
        self.skill_level_prompts = {
            SkillLevel.BEGINNER: "Explain in simple terms suitable for beginners with no prior music theory knowledge.",
            SkillLevel.INTERMEDIATE: "Provide intermediate-level explanations with some technical depth and practical examples.",
            SkillLevel.ADVANCED: "Offer advanced-level content with detailed technical analysis and sophisticated concepts."
        }
        
        self.content_type_prompts = {
            ContentType.THEORY_LESSON: "Create an educational music theory lesson that covers fundamental concepts.",
            ContentType.CULTURAL_CONTEXT: "Provide cultural and historical context for the musical concepts discussed.",
            ContentType.PRACTICAL_EXERCISE: "Design practical exercises and activities for hands-on learning.",
            ContentType.HISTORICAL_BACKGROUND: "Present historical background and evolution of musical concepts.",
            ContentType.COMPOSITION_GUIDE: "Offer guidance on composition techniques and creative approaches.",
            ContentType.ANALYSIS: "Provide detailed analysis of musical works or concepts.",
            ContentType.TEACHING_NOTES: "Create comprehensive teaching notes for educators."
        }
    
    def build_context_enhanced_prompt(self, request: GenerationRequest) -> str:
        """Build a context-enhanced prompt for content generation."""
        
        # Base prompt components
        skill_prompt = self.skill_level_prompts.get(request.skill_level, "")
        content_prompt = self.content_type_prompts.get(request.content_type, "")
        
        # Context integration
        context_str = self._format_context(request.context)
        
        # Web search results integration
        web_results = request.context.get("web_search_results", [])
        web_context = self._format_web_results(web_results)
        
        # Conversation context
        conversation_context = request.context.get("conversation_history", [])
        conversation_str = self._format_conversation_context(conversation_context)
        
        # Build the enhanced prompt
        enhanced_prompt = f"""
You are an expert music educator creating educational content for the Lit Music Mashup AI platform.

CONTENT TYPE: {request.content_type.value}
SKILL LEVEL: {request.skill_level.value}
USER REQUEST: {request.prompt}

{skill_prompt}
{content_prompt}

CONTEXT INFORMATION:
{context_str}

WEB SEARCH RESULTS:
{web_context}

CONVERSATION CONTEXT:
{conversation_str}

INSTRUCTIONS:
1. Generate high-quality, educational content appropriate for the specified skill level
2. Incorporate relevant context and web search results naturally
3. Ensure cultural sensitivity and accuracy
4. Provide practical examples and clear explanations
5. Structure the content for easy comprehension
6. Include teaching notes where appropriate

Please generate the requested content:
"""
        
        return enhanced_prompt.strip()
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for prompt inclusion."""
        if not context:
            return "No additional context provided."
        
        formatted_parts = []
        
        if "genre" in context:
            formatted_parts.append(f"Genre: {context['genre']}")
        
        if "cultural_background" in context:
            formatted_parts.append(f"Cultural Background: {context['cultural_background']}")
        
        if "learning_objectives" in context:
            formatted_parts.append(f"Learning Objectives: {context['learning_objectives']}")
        
        if "target_audience" in context:
            formatted_parts.append(f"Target Audience: {context['target_audience']}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific context provided."
    
    def _format_web_results(self, web_results: List[Dict[str, Any]]) -> str:
        """Format web search results for prompt inclusion."""
        if not web_results:
            return "No web search results available."
        
        formatted_results = []
        for i, result in enumerate(web_results[:5], 1):  # Limit to top 5 results
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No snippet")
            formatted_results.append(f"{i}. {title}\n   {snippet}")
        
        return "\n\n".join(formatted_results)
    
    def _format_conversation_context(self, conversation: List[Dict[str, Any]]) -> str:
        """Format conversation history for prompt inclusion."""
        if not conversation:
            return "No conversation history available."
        
        # Take last 5 messages for context
        recent_messages = conversation[-5:]
        formatted_messages = []
        
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                formatted_messages.append(f"{role.upper()}: {content[:200]}...")
        
        return "\n".join(formatted_messages)

class ContentValidator:
    """Validates generated content for appropriateness and quality."""
    
    def __init__(self):
        self.inappropriate_keywords = [
            "inappropriate", "offensive", "harmful", "dangerous",
            "illegal", "explicit", "adult", "mature"
        ]
        
        self.cultural_sensitivity_indicators = [
            "stereotype", "bias", "discriminatory", "offensive",
            "cultural appropriation", "insensitive"
        ]
    
    async def validate_content(self, content: str, skill_level: SkillLevel) -> ContentValidationResult:
        """Validate generated content for appropriateness and quality."""
        
        # Basic content validation
        is_appropriate = self._check_appropriateness(content)
        cultural_sensitivity = self._assess_cultural_sensitivity(content)
        educational_value = self._assess_educational_value(content, skill_level)
        age_appropriate = self._check_age_appropriateness(content, skill_level)
        
        # Collect issues and suggestions
        issues = []
        suggestions = []
        
        if not is_appropriate:
            issues.append("Content may contain inappropriate material")
            suggestions.append("Review and revise content for appropriateness")
        
        if cultural_sensitivity < 0.7:
            issues.append("Content may have cultural sensitivity concerns")
            suggestions.append("Review content for cultural accuracy and sensitivity")
        
        if educational_value < 0.6:
            issues.append("Content may lack sufficient educational value")
            suggestions.append("Enhance educational content and learning objectives")
        
        if not age_appropriate:
            issues.append("Content may not be age-appropriate")
            suggestions.append("Adjust content complexity for target age group")
        
        return ContentValidationResult(
            is_appropriate=is_appropriate,
            cultural_sensitivity_score=cultural_sensitivity,
            educational_value_score=educational_value,
            age_appropriateness=age_appropriate,
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_appropriateness(self, content: str) -> bool:
        """Check if content is appropriate."""
        content_lower = content.lower()
        return not any(keyword in content_lower for keyword in self.inappropriate_keywords)
    
    def _assess_cultural_sensitivity(self, content: str) -> float:
        """Assess cultural sensitivity of content (0.0 to 1.0)."""
        content_lower = content.lower()
        
        # Simple heuristic-based scoring
        sensitivity_indicators = sum(1 for indicator in self.cultural_sensitivity_indicators 
                                  if indicator in content_lower)
        
        # Base score starts high, decreases with issues
        base_score = 0.9
        penalty = sensitivity_indicators * 0.1
        
        return max(0.0, min(1.0, base_score - penalty))
    
    def _assess_educational_value(self, content: str, skill_level: SkillLevel) -> float:
        """Assess educational value of content (0.0 to 1.0)."""
        # Simple heuristic-based scoring
        educational_indicators = [
            "explain", "understand", "learn", "practice", "example",
            "concept", "theory", "technique", "method", "approach"
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in educational_indicators 
                            if indicator in content_lower)
        
        # Base score based on educational indicators
        base_score = min(1.0, indicator_count * 0.1)
        
        # Adjust for skill level appropriateness
        if skill_level == SkillLevel.BEGINNER and "advanced" in content_lower:
            base_score *= 0.8
        elif skill_level == SkillLevel.ADVANCED and "basic" in content_lower:
            base_score *= 0.9
        
        return base_score
    
    def _check_age_appropriateness(self, content: str, skill_level: SkillLevel) -> bool:
        """Check if content is age-appropriate for the skill level."""
        content_lower = content.lower()
        
        # Simple age-appropriateness check
        inappropriate_for_young = [
            "explicit", "mature", "adult", "complex theory",
            "advanced mathematics", "sophisticated analysis"
        ]
        
        if skill_level == SkillLevel.BEGINNER:
            return not any(term in content_lower for term in inappropriate_for_young)
        
        return True

class QualityScorer:
    """Scores the quality of generated content."""
    
    def __init__(self):
        self.scoring_criteria = {
            "educational_value": {
                "weight": 0.3,
                "indicators": ["explain", "understand", "learn", "practice", "example"]
            },
            "cultural_accuracy": {
                "weight": 0.25,
                "indicators": ["cultural", "historical", "context", "background"]
            },
            "engagement_level": {
                "weight": 0.25,
                "indicators": ["interesting", "engaging", "exciting", "fun", "creative"]
            },
            "content_relevance": {
                "weight": 0.2,
                "indicators": ["relevant", "appropriate", "suitable", "targeted"]
            }
        }
    
    async def score_content(self, content: str, content_type: ContentType, 
                          skill_level: SkillLevel, context: Dict[str, Any]) -> QualityMetrics:
        """Score the quality of generated content."""
        
        content_lower = content.lower()
        
        # Score each dimension
        educational_value = self._score_dimension(content_lower, "educational_value")
        cultural_accuracy = self._score_dimension(content_lower, "cultural_accuracy")
        engagement_level = self._score_dimension(content_lower, "engagement_level")
        content_relevance = self._score_dimension(content_lower, "content_relevance")
        
        # Calculate weighted overall score
        weights = {k: v["weight"] for k, v in self.scoring_criteria.items()}
        overall_score = (
            educational_value * weights["educational_value"] +
            cultural_accuracy * weights["cultural_accuracy"] +
            engagement_level * weights["engagement_level"] +
            content_relevance * weights["content_relevance"]
        )
        
        # Calculate confidence level based on content length and complexity
        confidence_level = min(1.0, len(content) / 1000)  # Simple heuristic
        
        return QualityMetrics(
            educational_value=educational_value,
            cultural_accuracy=cultural_accuracy,
            engagement_level=engagement_level,
            content_relevance=content_relevance,
            overall_score=overall_score,
            confidence_level=confidence_level
        )
    
    def _score_dimension(self, content: str, dimension: str) -> float:
        """Score a specific quality dimension (0.0 to 10.0)."""
        criteria = self.scoring_criteria[dimension]
        indicators = criteria["indicators"]
        
        # Count indicator occurrences
        indicator_count = sum(1 for indicator in indicators if indicator in content)
        
        # Convert to score (0-10 scale)
        base_score = min(10.0, indicator_count * 2.0)
        
        # Add bonus for content length and structure
        if len(content) > 500:
            base_score += 1.0
        if len(content) > 1000:
            base_score += 1.0
        
        return min(10.0, base_score)

class AsyncEnhancedGenerationService:
    """Enhanced content generation service with Ollama integration."""
    
    def __init__(self, db: Optional[AsyncConversationDB] = None):
        self.db = db
        self.ollama_client = OllamaClient()
        self.prompt_builder = PromptBuilder()
        self.content_validator = ContentValidator()
        self.quality_scorer = QualityScorer()
        self.settings = get_settings()
        
        # Performance tracking
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.ollama_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def generate_with_context(self, request: GenerationRequest) -> GenerationResponse:
        """Generate educational content with context enhancement."""
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Build enhanced prompt
            enhanced_prompt = self.prompt_builder.build_context_enhanced_prompt(request)
            
            # Generate content using Ollama
            generation_start = datetime.now(timezone.utc)
            ollama_response = await self.ollama_client.generate(
                prompt=enhanced_prompt,
                model=self._select_model(request.content_type, request.skill_level)
            )
            generation_time = (datetime.now(timezone.utc) - generation_start).total_seconds()
            
            # Extract generated content
            content = ollama_response.get("response", "")
            
            # Validate content
            validation_result = await self.content_validator.validate_content(
                content, request.skill_level
            )
            
            # Score content quality
            quality_metrics = await self.quality_scorer.score_content(
                content, request.content_type, request.skill_level, request.context
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(quality_metrics.overall_score)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(validation_result, quality_metrics)
            
            # Update statistics
            self._update_stats(generation_time, True)
            
            # Create response
            response = GenerationResponse(
                content=content,
                content_type=request.content_type,
                skill_level=request.skill_level,
                quality_score=quality_metrics.overall_score,
                quality_level=quality_level,
                confidence_score=quality_metrics.confidence_level,
                generation_time=generation_time,
                model_used=ollama_response.get("model", "unknown"),
                context_used=request.context,
                suggestions=suggestions,
                metadata={
                    "validation_result": validation_result.dict(),
                    "quality_metrics": quality_metrics.dict(),
                    "prompt_length": len(enhanced_prompt),
                    "content_length": len(content)
                }
            )
            
            # Log generation
            await self._log_generation(request, response)
            
            return response
            
        except Exception as e:
            self._update_stats(0.0, False)
            logger.error(f"Error generating content: {e}")
            raise
    
    def _select_model(self, content_type: ContentType, skill_level: SkillLevel) -> str:
        """Select appropriate model based on content type and skill level."""
        
        # Use faster model for simple content types
        if content_type in [ContentType.TEACHING_NOTES, ContentType.PRACTICAL_EXERCISE]:
            return "llama3.1:8b"
        
        # Use more powerful model for complex content
        if content_type in [ContentType.THEORY_LESSON, ContentType.ANALYSIS]:
            return "mistral-small3.2:latest"
        
        # Default to primary model
        return "mistral-small3.2:latest"
    
    def _determine_quality_level(self, overall_score: float) -> ContentQuality:
        """Determine quality level based on overall score."""
        if overall_score >= 8.0:
            return ContentQuality.EXCELLENT
        elif overall_score >= 6.0:
            return ContentQuality.GOOD
        elif overall_score >= 4.0:
            return ContentQuality.ACCEPTABLE
        else:
            return ContentQuality.NEEDS_IMPROVEMENT
    
    def _generate_suggestions(self, validation_result: ContentValidationResult, 
                            quality_metrics: QualityMetrics) -> List[str]:
        """Generate improvement suggestions based on validation and quality metrics."""
        suggestions = []
        
        # Add validation-based suggestions
        suggestions.extend(validation_result.suggestions)
        
        # Add quality-based suggestions
        if quality_metrics.educational_value < 6.0:
            suggestions.append("Consider adding more educational content and examples")
        
        if quality_metrics.engagement_level < 6.0:
            suggestions.append("Consider making the content more engaging and interactive")
        
        if quality_metrics.cultural_accuracy < 6.0:
            suggestions.append("Consider enhancing cultural context and accuracy")
        
        if quality_metrics.content_relevance < 6.0:
            suggestions.append("Consider making the content more relevant to the topic")
        
        return suggestions
    
    def _update_stats(self, generation_time: float, success: bool):
        """Update generation statistics."""
        self.generation_stats["total_generations"] += 1
        
        if success:
            self.generation_stats["successful_generations"] += 1
        else:
            self.generation_stats["failed_generations"] += 1
        
        # Update average generation time
        current_avg = self.generation_stats["average_generation_time"]
        total_successful = self.generation_stats["successful_generations"]
        
        if total_successful > 0:
            self.generation_stats["average_generation_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )
    
    async def _log_generation(self, request: GenerationRequest, response: GenerationResponse):
        """Log generation details to database if available."""
        if self.db:
            try:
                # Log to database (implementation depends on schema)
                logger.info(f"Generated content for session {request.session_id}: "
                          f"{response.content_type.value} - {response.quality_level.value}")
            except Exception as e:
                logger.error(f"Error logging generation: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the generation service."""
        ollama_healthy = await self.ollama_client.health_check()
        
        return {
            "service": "generation",
            "status": "healthy" if ollama_healthy else "unhealthy",
            "ollama_available": ollama_healthy,
            "models_available": len(await self.ollama_client.list_models()),
            "generation_stats": self.generation_stats
        }
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        return await self.ollama_client.list_models()

# Service factory functions
async def get_generation_service(db: Optional[AsyncConversationDB] = None) -> AsyncEnhancedGenerationService:
    """Get an instance of the generation service."""
    return AsyncEnhancedGenerationService(db)

async def get_generation_service_dep() -> AsyncEnhancedGenerationService:
    """Dependency function for FastAPI."""
    return await get_generation_service()
