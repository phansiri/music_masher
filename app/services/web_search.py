"""
Web search service for educational content with Tavily API integration.

This module provides the AsyncWebSearchService for web search functionality
with educational content filtering, graceful degradation, and context-aware
query enhancement for the Lit Music Mashup platform.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import re
from urllib.parse import urlparse

# Import Tavily for web search
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = None

from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class AsyncWebSearchService:
    """
    Asynchronous web search service with educational content filtering.
    
    This service provides web search functionality using the Tavily API
    with enhanced educational content filtering, graceful degradation
    when the API is unavailable, and context-aware query enhancement.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web search service.
        
        Args:
            api_key: Optional Tavily API key. If not provided, will use
                    the key from environment configuration.
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.TAVILY_API_KEY
        self.client = None
        self.is_available = False
        
        # Initialize Tavily client if available
        if TAVILY_AVAILABLE and self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                self.is_available = True
                logger.info("Tavily web search service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily client: {e}")
                self.is_available = False
        else:
            if not TAVILY_AVAILABLE:
                logger.warning("Tavily package not available. Install with: uv add tavily-python")
            if not self.api_key:
                logger.warning("Tavily API key not provided. Web search will be disabled.")
            self.is_available = False
    
    async def search_educational_content(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for educational content with context enhancement.
        
        Args:
            query: Search query string
            context: Context information for query enhancement
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Enhance query for educational content
            enhanced_query = self._enhance_query_for_education(query, context)
            
            if not self.is_available:
                logger.warning("Web search service not available. Returning empty results.")
                return self._create_empty_response(query, enhanced_query)
            
            # Perform the search
            logger.info(f"Performing web search for: {enhanced_query}")
            search_results = await self._perform_search(enhanced_query)
            
            # Filter and validate results
            filtered_results = await self._filter_and_validate_results(search_results, context)
            
            return {
                "query": query,
                "enhanced_query": enhanced_query,
                "results": filtered_results,
                "total_results": len(filtered_results),
                "search_timestamp": datetime.now(timezone.utc),
                "service_available": True,
                "processing_metadata": {
                    "query_enhancement_applied": True,
                    "educational_filtering_applied": True,
                    "source_validation_applied": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return self._create_error_response(query, str(e))
    
    def _enhance_query_for_education(self, query: str, context: Dict[str, Any]) -> str:
        """
        Enhance search query for educational content.
        
        Args:
            query: Original search query
            context: Context information
            
        Returns:
            Enhanced query string
        """
        enhanced_parts = [query]
        
        # Handle None context
        if context is None:
            context = {}
        
        # Add educational context
        if context.get("skill_level"):
            skill_level = context["skill_level"].lower()
            if skill_level in ["beginner", "basic"]:
                enhanced_parts.append("music theory basics")
            elif skill_level in ["intermediate", "advanced"]:
                enhanced_parts.append("advanced music theory")
        
        # Add cultural context
        if context.get("cultural_elements"):
            cultural_elements = context["cultural_elements"]
            if isinstance(cultural_elements, list):
                enhanced_parts.extend([f"cultural significance {element}" for element in cultural_elements[:2]])
            elif isinstance(cultural_elements, str):
                enhanced_parts.append(f"cultural significance {cultural_elements}")
        
        # Add genre context
        if context.get("genres"):
            genres = context["genres"]
            if isinstance(genres, list):
                enhanced_parts.extend([f"{genre} music history" for genre in genres[:2]])
            elif isinstance(genres, str):
                enhanced_parts.append(f"{genres} music history")
        
        # Add educational focus
        enhanced_parts.append("educational content")
        enhanced_parts.append("music education")
        
        # Combine and clean
        enhanced_query = " ".join(enhanced_parts)
        
        # Remove duplicates and clean up
        enhanced_query = re.sub(r'\s+', ' ', enhanced_query).strip()
        
        logger.debug(f"Enhanced query: '{query}' -> '{enhanced_query}'")
        return enhanced_query
    
    async def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform the actual web search.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        if not self.client:
            raise Exception("Tavily client not available")
        
        try:
            # Perform search with timeout
            search_task = asyncio.create_task(
                self._search_with_timeout(query)
            )
            
            results = await asyncio.wait_for(
                search_task, 
                timeout=self.settings.WEB_SEARCH_TIMEOUT_SECONDS
            )
            
            return results
            
        except asyncio.TimeoutError:
            logger.warning(f"Web search timed out after {self.settings.WEB_SEARCH_TIMEOUT_SECONDS} seconds")
            raise Exception("Search timeout")
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def _search_with_timeout(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform search with proper async handling.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        # Run Tavily search in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, 
            lambda: self.client.search(
                query,
                search_depth="basic",
                max_results=self.settings.WEB_SEARCH_MAX_RESULTS
            )
        )
        
        return results.get("results", [])
    
    async def _filter_and_validate_results(
        self, 
        results: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter and validate search results for educational content.
        
        Args:
            results: Raw search results
            context: Context information
            
        Returns:
            Filtered and validated results
        """
        filtered_results = []
        
        for result in results:
            try:
                # Basic validation
                if not self._validate_result_basic(result):
                    continue
                
                # Educational content filtering
                if not self._filter_educational_content(result, context):
                    continue
                
                # Source quality assessment
                quality_score = self._assess_source_quality(result)
                if quality_score < 0.3:  # Minimum quality threshold
                    continue
                
                # Add processing metadata
                processed_result = {
                    **result,
                    "educational_relevance_score": quality_score,
                    "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                    "context_alignment": self._assess_context_alignment(result, context)
                }
                
                filtered_results.append(processed_result)
                
            except Exception as e:
                logger.warning(f"Error processing result: {e}")
                continue
        
        # Sort by educational relevance
        filtered_results.sort(
            key=lambda x: x.get("educational_relevance_score", 0),
            reverse=True
        )
        
        logger.info(f"Filtered {len(results)} results to {len(filtered_results)} educational content")
        return filtered_results
    
    def _validate_result_basic(self, result: Dict[str, Any]) -> bool:
        """
        Basic validation of search result.
        
        Args:
            result: Search result
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["title", "url"]
        return all(field in result and result[field] for field in required_fields)
    
    def _filter_educational_content(self, result: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Filter for educational content.
        
        Args:
            result: Search result
            context: Context information
            
        Returns:
            True if educational content, False otherwise
        """
        title = result.get("title", "").lower()
        content = result.get("content", "").lower()
        url = result.get("url", "").lower()
        
        # Prefer educational domains
        educational_domains = [
            ".edu", ".org", "wikipedia.org", "britannica.com",
            "khanacademy.org", "musictheory.net", "teoria.com"
        ]
        
        if any(domain in url for domain in educational_domains):
            return True
        
        # Check for educational keywords
        educational_keywords = [
            "music theory", "musical", "education", "learn", "tutorial",
            "lesson", "guide", "history", "cultural", "traditional",
            "academic", "scholarly", "research", "study"
        ]
        
        text_to_check = f"{title} {content}"
        if any(keyword in text_to_check for keyword in educational_keywords):
            return True
        
        # Check for inappropriate content
        inappropriate_keywords = [
            "adult", "explicit", "inappropriate", "nsfw"
        ]
        
        if any(keyword in text_to_check for keyword in inappropriate_keywords):
            return False
        
        # Default to False for non-educational content
        return False
    
    def _assess_source_quality(self, result: Dict[str, Any]) -> float:
        """
        Assess the quality of a source.
        
        Args:
            result: Search result
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.5  # Base score
        
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        content = result.get("content", "").lower()
        
        # Domain quality assessment
        high_quality_domains = [
            ".edu", ".org", "wikipedia.org", "britannica.com",
            "khanacademy.org", "musictheory.net", "teoria.com"
        ]
        
        if any(domain in url for domain in high_quality_domains):
            score += 0.3
        
        # Content length assessment
        content_length = len(content)
        if content_length > 500:
            score += 0.1
        elif content_length > 200:
            score += 0.05
        
        # Title quality assessment
        if len(title) > 10 and len(title) < 100:
            score += 0.05
        
        # URL structure assessment
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme == "https":
                score += 0.05
        except:
            pass
        
        return min(score, 1.0)
    
    def _assess_context_alignment(self, result: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess how well the result aligns with the context.
        
        Args:
            result: Search result
            context: Context information
            
        Returns:
            Alignment score between 0 and 1
        """
        alignment_score = 0.5  # Base alignment
        
        text_to_check = f"{result.get('title', '')} {result.get('content', '')}".lower()
        
        # Check for skill level alignment
        if context.get("skill_level"):
            skill_level = context["skill_level"].lower()
            if skill_level in ["beginner", "basic"]:
                beginner_keywords = ["basic", "beginner", "introduction", "fundamental"]
                if any(keyword in text_to_check for keyword in beginner_keywords):
                    alignment_score += 0.2
            elif skill_level in ["intermediate", "advanced"]:
                advanced_keywords = ["advanced", "complex", "sophisticated", "expert"]
                if any(keyword in text_to_check for keyword in advanced_keywords):
                    alignment_score += 0.2
        
        # Check for genre alignment
        if context.get("genres"):
            genres = context["genres"]
            if isinstance(genres, list):
                for genre in genres:
                    if genre.lower() in text_to_check:
                        alignment_score += 0.15  # Increased from 0.1
            elif isinstance(genres, str):
                if genres.lower() in text_to_check:
                    alignment_score += 0.15  # Increased from 0.1
        
        # Check for cultural alignment
        if context.get("cultural_elements"):
            cultural_elements = context["cultural_elements"]
            if isinstance(cultural_elements, list):
                for element in cultural_elements:
                    if element.lower() in text_to_check:
                        alignment_score += 0.15  # Increased from 0.1
            elif isinstance(cultural_elements, str):
                if cultural_elements.lower() in text_to_check:
                    alignment_score += 0.15  # Increased from 0.1
        
        return min(alignment_score, 1.0)
    
    def _create_empty_response(self, query: str, enhanced_query: str) -> Dict[str, Any]:
        """Create empty response when service is unavailable."""
        return {
            "query": query,
            "enhanced_query": enhanced_query,
            "results": [],
            "total_results": 0,
            "search_timestamp": datetime.now(timezone.utc),
            "service_available": False,
            "processing_metadata": {
                "query_enhancement_applied": True,
                "educational_filtering_applied": False,
                "source_validation_applied": False,
                "degradation_reason": "Service unavailable"
            }
        }
    
    def _create_error_response(self, query: str, error_message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "query": query,
            "enhanced_query": query,
            "results": [],
            "total_results": 0,
            "search_timestamp": datetime.now(timezone.utc),
            "service_available": False,
            "error": error_message,
            "processing_metadata": {
                "query_enhancement_applied": False,
                "educational_filtering_applied": False,
                "source_validation_applied": False,
                "error_type": "search_error"
            }
        }
    
    def is_service_available(self) -> bool:
        """Check if the web search service is available."""
        return self.is_available
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "service_available": self.is_available,
            "tavily_available": TAVILY_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "max_results": self.settings.WEB_SEARCH_MAX_RESULTS,
            "timeout_seconds": self.settings.WEB_SEARCH_TIMEOUT_SECONDS
        }


# Factory function for dependency injection
async def get_web_search_service() -> AsyncWebSearchService:
    """Get web search service instance for dependency injection."""
    return AsyncWebSearchService() 