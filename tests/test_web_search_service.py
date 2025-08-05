"""
Tests for AsyncWebSearchService.

This module tests the web search service functionality including
educational content filtering, graceful degradation, query enhancement,
and Tavily API integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from typing import Dict, Any

from app.services.web_search import AsyncWebSearchService


class TestAsyncWebSearchService:
    """Test AsyncWebSearchService functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        mock_settings = Mock()
        mock_settings.TAVILY_API_KEY = "test_api_key"
        mock_settings.WEB_SEARCH_MAX_RESULTS = 3
        mock_settings.WEB_SEARCH_TIMEOUT_SECONDS = 10
        return mock_settings
    
    @pytest.fixture
    def web_search_service(self, mock_settings):
        """Create web search service instance."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            return AsyncWebSearchService()
    
    @pytest.fixture
    def mock_tavily_client(self):
        """Create mock Tavily client."""
        mock_client = Mock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Music Theory Basics",
                    "url": "https://musictheory.net/lessons",
                    "content": "Learn the fundamentals of music theory including scales, chords, and rhythm."
                },
                {
                    "title": "Jazz Music History",
                    "url": "https://wikipedia.org/jazz_history",
                    "content": "Explore the rich history of jazz music and its cultural significance."
                }
            ]
        }
        return mock_client
    
    def test_initialization_with_api_key(self, mock_settings):
        """Test service initialization with API key."""
        with patch('app.services.web_search.TAVILY_AVAILABLE', True):
            with patch('app.services.web_search.TavilyClient') as mock_tavily:
                mock_client = Mock()
                mock_tavily.return_value = mock_client
                
                service = AsyncWebSearchService("test_key")
                
                assert service.api_key == "test_key"
                assert service.is_available is True
                mock_tavily.assert_called_once_with(api_key="test_key")
    
    def test_initialization_without_api_key(self, mock_settings):
        """Test service initialization without API key."""
        with patch('app.services.web_search.TAVILY_AVAILABLE', False):
            service = AsyncWebSearchService()
            
            assert service.is_available is False
            assert service.client is None
    
    def test_initialization_without_tavily_package(self, mock_settings):
        """Test service initialization when Tavily package is not available."""
        with patch('app.services.web_search.TAVILY_AVAILABLE', False):
            service = AsyncWebSearchService("test_key")
            
            assert service.is_available is False
            assert service.client is None
    
    @pytest.mark.asyncio
    async def test_search_educational_content_success(self, web_search_service, mock_tavily_client):
        """Test successful educational content search."""
        # Mock the service to be available
        web_search_service.is_available = True
        web_search_service.client = mock_tavily_client
        
        context = {
            "skill_level": "beginner",
            "genres": ["jazz"],
            "cultural_elements": ["improvisation"]
        }
        
        result = await web_search_service.search_educational_content("music theory", context)
        
        assert result["query"] == "music theory"
        assert "enhanced_query" in result
        assert result["service_available"] is True
        assert "results" in result
        assert "processing_metadata" in result
        assert result["processing_metadata"]["query_enhancement_applied"] is True
    
    @pytest.mark.asyncio
    async def test_search_educational_content_service_unavailable(self, web_search_service):
        """Test search when service is unavailable."""
        web_search_service.is_available = False
        
        context = {"skill_level": "beginner"}
        result = await web_search_service.search_educational_content("music theory", context)
        
        assert result["service_available"] is False
        assert result["total_results"] == 0
        assert result["processing_metadata"]["degradation_reason"] == "Service unavailable"
    
    @pytest.mark.asyncio
    async def test_search_educational_content_error(self, web_search_service):
        """Test search error handling."""
        web_search_service.is_available = True
        web_search_service.client = Mock()
        web_search_service.client.search.side_effect = Exception("API Error")
        
        context = {"skill_level": "beginner"}
        result = await web_search_service.search_educational_content("music theory", context)
        
        assert result["service_available"] is False
        assert "error" in result
        assert result["processing_metadata"]["error_type"] == "search_error"
    
    def test_enhance_query_for_education(self, web_search_service):
        """Test query enhancement for educational content."""
        context = {
            "skill_level": "beginner",
            "genres": ["jazz", "blues"],
            "cultural_elements": ["improvisation"]
        }
        
        enhanced_query = web_search_service._enhance_query_for_education("music", context)
        
        assert "music" in enhanced_query
        assert "music theory basics" in enhanced_query
        assert "jazz music history" in enhanced_query
        assert "cultural significance improvisation" in enhanced_query
        assert "educational content" in enhanced_query
        assert "music education" in enhanced_query
    
    def test_enhance_query_for_advanced_level(self, web_search_service):
        """Test query enhancement for advanced skill level."""
        context = {
            "skill_level": "advanced",
            "genres": ["classical"]
        }
        
        enhanced_query = web_search_service._enhance_query_for_education("composition", context)
        
        assert "composition" in enhanced_query
        assert "advanced music theory" in enhanced_query
        assert "classical music history" in enhanced_query
    
    def test_enhance_query_with_list_context(self, web_search_service):
        """Test query enhancement with list-based context."""
        context = {
            "skill_level": "intermediate",
            "genres": ["rock", "pop", "electronic"],
            "cultural_elements": ["rhythm", "melody"]
        }
        
        enhanced_query = web_search_service._enhance_query_for_education("chords", context)
        
        # Should only include first 2 genres and cultural elements
        assert "rock music history" in enhanced_query
        assert "pop music history" in enhanced_query
        assert "cultural significance rhythm" in enhanced_query
        assert "cultural significance melody" in enhanced_query
        # Should not include electronic (third genre)
        assert "electronic music history" not in enhanced_query
    
    @pytest.mark.asyncio
    async def test_filter_and_validate_results(self, web_search_service):
        """Test result filtering and validation."""
        raw_results = [
            {
                "title": "Music Theory Basics",
                "url": "https://musictheory.net/lessons",
                "content": "Learn the fundamentals of music theory including scales, chords, and rhythm."
            },
            {
                "title": "Inappropriate Content",
                "url": "https://inappropriate.com",
                "content": "Adult content that should be filtered out."
            },
            {
                "title": "Jazz History",
                "url": "https://wikipedia.org/jazz",
                "content": "Explore the rich history of jazz music."
            }
        ]
        
        context = {"skill_level": "beginner"}
        filtered_results = await web_search_service._filter_and_validate_results(raw_results, context)
        
        # Should filter out inappropriate content
        assert len(filtered_results) == 2
        
        # Check that educational content is prioritized
        for result in filtered_results:
            assert "educational_relevance_score" in result
            assert "processing_timestamp" in result
            assert "context_alignment" in result
    
    def test_validate_result_basic(self, web_search_service):
        """Test basic result validation."""
        valid_result = {
            "title": "Music Theory",
            "url": "https://example.com"
        }
        assert web_search_service._validate_result_basic(valid_result) is True
        
        invalid_result = {
            "title": "Music Theory"
            # Missing URL
        }
        assert web_search_service._validate_result_basic(invalid_result) is False
    
    def test_filter_educational_content(self, web_search_service):
        """Test educational content filtering."""
        context = {"skill_level": "beginner"}
        
        # Educational domain
        edu_result = {
            "title": "Music Theory",
            "url": "https://musictheory.net/lessons",
            "content": "Learn music theory"
        }
        assert web_search_service._filter_educational_content(edu_result, context) is True
        
        # Educational keywords
        keyword_result = {
            "title": "Learn Music Theory",
            "url": "https://example.com",
            "content": "Educational content about music"
        }
        assert web_search_service._filter_educational_content(keyword_result, context) is True
        
        # Inappropriate content
        inappropriate_result = {
            "title": "Adult Content",
            "url": "https://example.com",
            "content": "Inappropriate adult content"
        }
        assert web_search_service._filter_educational_content(inappropriate_result, context) is False
        
        # Non-educational content
        non_edu_result = {
            "title": "Shopping Site",
            "url": "https://shopping.com",
            "content": "Buy products online"
        }
        assert web_search_service._filter_educational_content(non_edu_result, context) is False
    
    def test_assess_source_quality(self, web_search_service):
        """Test source quality assessment."""
        # High quality educational domain
        high_quality = {
            "title": "Music Theory Fundamentals",
            "url": "https://musictheory.net/lessons",
            "content": "Comprehensive guide to music theory fundamentals including scales, chords, rhythm, and harmony. This educational resource provides detailed explanations and interactive examples for learning music theory."
        }
        score = web_search_service._assess_source_quality(high_quality)
        assert score > 0.8  # Should be high quality
        
        # Medium quality
        medium_quality = {
            "title": "Music Basics",
            "url": "https://example.com/music",
            "content": "Basic music information with some educational content."
        }
        score = web_search_service._assess_source_quality(medium_quality)
        assert 0.5 <= score <= 0.7  # Should be medium quality
        
        # Low quality
        low_quality = {
            "title": "Music",
            "url": "https://example.com",
            "content": "Short content"
        }
        score = web_search_service._assess_source_quality(low_quality)
        assert score < 0.6  # Should be lower quality
    
    def test_assess_context_alignment(self, web_search_service):
        """Test context alignment assessment."""
        result = {
            "title": "Beginner Music Theory",
            "content": "Basic music theory for beginners"
        }
        
        # Beginner context
        beginner_context = {"skill_level": "beginner"}
        alignment = web_search_service._assess_context_alignment(result, beginner_context)
        assert alignment > 0.6  # Should align well with beginner context
        
        # Advanced context
        advanced_context = {"skill_level": "advanced"}
        alignment = web_search_service._assess_context_alignment(result, advanced_context)
        assert alignment < 0.6  # Should not align well with advanced context
    
    def test_assess_context_alignment_with_genres(self, web_search_service):
        """Test context alignment with genre information."""
        result = {
            "title": "Jazz Music History",
            "content": "Explore the rich history of jazz music"
        }
        
        context = {"genres": ["jazz", "blues"]}
        alignment = web_search_service._assess_context_alignment(result, context)
        assert alignment > 0.6  # Should align well with jazz genre
    
    def test_assess_context_alignment_with_cultural_elements(self, web_search_service):
        """Test context alignment with cultural elements."""
        result = {
            "title": "Improvisation in Music",
            "content": "Learn about musical improvisation techniques"
        }
        
        context = {"cultural_elements": ["improvisation"]}
        alignment = web_search_service._assess_context_alignment(result, context)
        assert alignment > 0.6  # Should align well with improvisation
    
    def test_create_empty_response(self, web_search_service):
        """Test empty response creation."""
        response = web_search_service._create_empty_response("test query", "enhanced query")
        
        assert response["query"] == "test query"
        assert response["enhanced_query"] == "enhanced query"
        assert response["service_available"] is False
        assert response["total_results"] == 0
        assert response["processing_metadata"]["degradation_reason"] == "Service unavailable"
    
    def test_create_error_response(self, web_search_service):
        """Test error response creation."""
        response = web_search_service._create_error_response("test query", "API Error")
        
        assert response["query"] == "test query"
        assert response["service_available"] is False
        assert response["error"] == "API Error"
        assert response["processing_metadata"]["error_type"] == "search_error"
    
    def test_is_service_available(self, web_search_service):
        """Test service availability check."""
        web_search_service.is_available = True
        assert web_search_service.is_service_available() is True
        
        web_search_service.is_available = False
        assert web_search_service.is_service_available() is False
    
    def test_get_service_status(self, web_search_service, mock_settings):
        """Test service status information."""
        web_search_service.is_available = True
        status = web_search_service.get_service_status()
        
        assert status["service_available"] is True
        assert status["max_results"] == 3
        assert status["timeout_seconds"] == 10
        assert "api_key_configured" in status
        assert "tavily_available" in status


class TestWebSearchServiceIntegration:
    """Test web search service integration scenarios."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        mock_settings = Mock()
        mock_settings.TAVILY_API_KEY = "test_api_key"
        mock_settings.WEB_SEARCH_MAX_RESULTS = 3
        mock_settings.WEB_SEARCH_TIMEOUT_SECONDS = 10
        return mock_settings
    
    @pytest.mark.asyncio
    async def test_search_with_timeout(self, mock_settings):
        """Test search timeout handling."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            with patch('app.services.web_search.TAVILY_AVAILABLE', True):
                with patch('app.services.web_search.TavilyClient') as mock_tavily:
                    # Mock a slow search that will timeout
                    async def slow_search(*args, **kwargs):
                        await asyncio.sleep(15)  # Longer than timeout
                        return {"results": []}
                    
                    mock_client = Mock()
                    mock_client.search = slow_search
                    mock_tavily.return_value = mock_client
                    
                    service = AsyncWebSearchService()
                    service.is_available = True
                    service.client = mock_client
                    
                    context = {"skill_level": "beginner"}
                    result = await service.search_educational_content("music theory", context)
                    
                    assert result["service_available"] is False
                    assert "error" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self, mock_settings):
        """Test concurrent search operations."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            with patch('app.services.web_search.TAVILY_AVAILABLE', True):
                with patch('app.services.web_search.TavilyClient') as mock_tavily:
                    mock_client = Mock()
                    mock_client.search.return_value = {"results": [{"title": "Test", "url": "https://test.com"}]}
                    mock_tavily.return_value = mock_client
                    
                    service = AsyncWebSearchService()
                    service.is_available = True
                    service.client = mock_client
                    
                    # Perform concurrent searches
                    tasks = [
                        service.search_educational_content("query1", {"skill_level": "beginner"}),
                        service.search_educational_content("query2", {"skill_level": "intermediate"}),
                        service.search_educational_content("query3", {"skill_level": "advanced"})
                    ]
                    
                    results = await asyncio.gather(*tasks)
                    
                    assert len(results) == 3
                    for result in results:
                        assert result["service_available"] is True
                        assert "results" in result


class TestWebSearchServiceEdgeCases:
    """Test web search service edge cases and error conditions."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        mock_settings = Mock()
        mock_settings.TAVILY_API_KEY = None  # No API key
        mock_settings.WEB_SEARCH_MAX_RESULTS = 3
        mock_settings.WEB_SEARCH_TIMEOUT_SECONDS = 10
        return mock_settings
    
    def test_initialization_without_api_key(self, mock_settings):
        """Test initialization without API key."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            with patch('app.services.web_search.TAVILY_AVAILABLE', True):
                service = AsyncWebSearchService()
                
                assert service.is_available is False
                assert service.api_key is None
    
    @pytest.mark.asyncio
    async def test_search_with_empty_context(self, mock_settings):
        """Test search with empty context."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            service = AsyncWebSearchService()
            service.is_available = False  # Service unavailable
            
            result = await service.search_educational_content("music", {})
            
            assert result["query"] == "music"
            assert result["service_available"] is False
            assert result["total_results"] == 0
    
    @pytest.mark.asyncio
    async def test_search_with_none_context(self, mock_settings):
        """Test search with None context."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            service = AsyncWebSearchService()
            service.is_available = False  # Service unavailable
            
            result = await service.search_educational_content("music", None)
            
            assert result["query"] == "music"
            assert result["service_available"] is False
    
    def test_enhance_query_with_empty_context(self, mock_settings):
        """Test query enhancement with empty context."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            service = AsyncWebSearchService()
            
            enhanced_query = service._enhance_query_for_education("music", {})
            
            assert "music" in enhanced_query
            assert "educational content" in enhanced_query
            assert "music education" in enhanced_query
    
    def test_enhance_query_with_none_context(self, mock_settings):
        """Test query enhancement with None context."""
        with patch('app.services.web_search.get_settings', return_value=mock_settings):
            service = AsyncWebSearchService()
            
            enhanced_query = service._enhance_query_for_education("music", None)
            
            assert "music" in enhanced_query
            assert "educational content" in enhanced_query


if __name__ == "__main__":
    pytest.main([__file__]) 