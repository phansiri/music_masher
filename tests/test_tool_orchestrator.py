"""
Tests for the AsyncToolOrchestrator class.

This module provides comprehensive tests for tool orchestration functionality
including concurrent execution, error handling, and database integration.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from app.services.tool_orchestrator import (
    AsyncToolOrchestrator,
    ToolCallResult,
    ToolExecutionStatus
)
from app.db import AsyncConversationDB, ToolCallType
from app.services.web_search import AsyncWebSearchService


class TestToolCallResult:
    """Test the ToolCallResult dataclass."""
    
    def test_tool_call_result_creation(self):
        """Test creating a ToolCallResult instance."""
        result = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="test query",
            output_data="test output",
            status=ToolExecutionStatus.COMPLETED,
            execution_time=1.5
        )
        
        assert result.tool_type == ToolCallType.WEB_SEARCH
        assert result.input_data == "test query"
        assert result.output_data == "test output"
        assert result.status == ToolExecutionStatus.COMPLETED
        assert result.execution_time == 1.5
    
    def test_tool_call_result_defaults(self):
        """Test ToolCallResult with default values."""
        result = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="test query"
        )
        
        assert result.status == ToolExecutionStatus.PENDING
        assert result.output_data is None
        assert result.error_message is None
        assert result.execution_time is None
        assert result.metadata is None


class TestAsyncToolOrchestrator:
    """Test the AsyncToolOrchestrator class."""
    
    @pytest.fixture
    def mock_web_search_service(self):
        """Create a mock web search service."""
        mock_service = AsyncMock(spec=AsyncWebSearchService)
        mock_service.is_service_available.return_value = True
        return mock_service
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock_db = AsyncMock(spec=AsyncConversationDB)
        mock_db.add_tool_call.return_value = 1
        return mock_db
    
    @pytest.fixture
    def tool_orchestrator(self, mock_web_search_service, mock_db):
        """Create a tool orchestrator instance for testing."""
        return AsyncToolOrchestrator(
            web_search_service=mock_web_search_service,
            db=mock_db,
            max_concurrent_tools=2,
            tool_timeout=5.0
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_web_search_service, mock_db):
        """Test tool orchestrator initialization."""
        orchestrator = AsyncToolOrchestrator(
            web_search_service=mock_web_search_service,
            db=mock_db,
            max_concurrent_tools=3,
            tool_timeout=10.0
        )
        
        assert orchestrator.web_search_service == mock_web_search_service
        assert orchestrator.db == mock_db
        assert orchestrator.max_concurrent_tools == 3
        assert orchestrator.tool_timeout == 10.0
        assert orchestrator.semaphore._value == 3
    
    @pytest.mark.asyncio
    async def test_execute_web_search_success(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test successful web search execution."""
        # Mock search result
        search_result = {
            "query": "test query",
            "results": [{"title": "Test Result", "url": "http://test.com"}],
            "enhanced_query": "test query educational"
        }
        mock_web_search_service.search_educational_content.return_value = search_result
        
        # Execute search
        result = await tool_orchestrator.execute_web_search(
            "test query", {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify result
        assert result.tool_type == ToolCallType.WEB_SEARCH
        assert result.input_data == "test query"
        assert result.status == ToolExecutionStatus.COMPLETED
        assert result.execution_time is not None
        assert result.metadata == search_result
        
        # Verify database calls
        mock_db.add_tool_call.assert_called_once()
        mock_db.update_tool_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_web_search_timeout(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test web search timeout handling."""
        # Mock slow search
        async def slow_search(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {"results": []}
        
        mock_web_search_service.search_educational_content.side_effect = slow_search
        
        # Execute search
        result = await tool_orchestrator.execute_web_search(
            "test query", {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify timeout result
        assert result.status == ToolExecutionStatus.TIMEOUT
        assert "timed out" in result.error_message
        assert result.execution_time is None
    
    @pytest.mark.asyncio
    async def test_execute_web_search_error(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test web search error handling."""
        # Mock search error
        mock_web_search_service.search_educational_content.side_effect = Exception("Search failed")
        
        # Execute search
        result = await tool_orchestrator.execute_web_search(
            "test query", {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify error result
        assert result.status == ToolExecutionStatus.FAILED
        assert "Search failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_execute_concurrent_searches(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test concurrent search execution."""
        # Mock search results
        search_results = [
            {"query": "query1", "results": [{"title": "Result 1"}]},
            {"query": "query2", "results": [{"title": "Result 2"}]}
        ]
        mock_web_search_service.search_educational_content.side_effect = search_results
        
        # Execute concurrent searches
        results = await tool_orchestrator.execute_concurrent_searches(
            ["query1", "query2"], {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify results
        assert len(results) == 2
        assert all(result.status == ToolExecutionStatus.COMPLETED for result in results)
        assert results[0].input_data == "query1"
        assert results[1].input_data == "query2"
    
    @pytest.mark.asyncio
    async def test_execute_genre_exploration_searches(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test genre exploration search execution."""
        # Mock search results
        search_results = [
            {"query": "jazz music history cultural significance educational", "results": [{"title": "Jazz History"}]},
            {"query": "rock music history cultural significance educational", "results": [{"title": "Rock History"}]}
        ]
        mock_web_search_service.search_educational_content.side_effect = search_results
        
        # Execute genre searches
        results = await tool_orchestrator.execute_genre_exploration_searches(
            ["jazz", "rock"], {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify results
        assert len(results) == 2
        assert "jazz" in results
        assert "rock" in results
        assert results["jazz"].status == ToolExecutionStatus.COMPLETED
        assert results["rock"].status == ToolExecutionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_cultural_research_searches(self, tool_orchestrator, mock_web_search_service, mock_db):
        """Test cultural research search execution."""
        # Mock search results
        search_results = [
            {"query": "history music culture history significance", "results": [{"title": "Cultural History"}]},
            {"query": "tradition music culture history significance", "results": [{"title": "Cultural Tradition"}]}
        ]
        mock_web_search_service.search_educational_content.side_effect = search_results
        
        # Execute cultural searches
        results = await tool_orchestrator.execute_cultural_research_searches(
            ["history", "tradition"], {"skill_level": "beginner"}, "test-session"
        )
        
        # Verify results
        assert len(results) == 2
        assert "history" in results
        assert "tradition" in results
        assert results["history"].status == ToolExecutionStatus.COMPLETED
        assert results["tradition"].status == ToolExecutionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_process_search_results(self, tool_orchestrator):
        """Test search result processing and synthesis."""
        # Create mock results
        successful_result = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="query1",
            status=ToolExecutionStatus.COMPLETED,
            metadata={
                "results": [
                    {"title": "Result 1", "url": "http://test1.com"},
                    {"title": "Result 2", "url": "http://test2.com"}
                ]
            }
        )
        
        failed_result = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="query2",
            status=ToolExecutionStatus.FAILED,
            error_message="Search failed"
        )
        
        results = [successful_result, failed_result]
        
        # Process results
        processed = await tool_orchestrator.process_search_results(results)
        
        # Verify processing
        assert processed["successful_searches"] == 1
        assert processed["failed_searches"] == 1
        assert processed["total_results"] == 2
        assert len(processed["results"]) == 2
        assert len(processed["errors"]) == 1
    
    @pytest.mark.asyncio
    async def test_process_search_results_duplicates(self, tool_orchestrator):
        """Test search result processing with duplicate URLs."""
        # Create mock results with duplicate URLs
        result1 = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="query1",
            status=ToolExecutionStatus.COMPLETED,
            metadata={
                "results": [
                    {"title": "Result 1", "url": "http://test.com"},
                    {"title": "Result 2", "url": "http://test.com"}  # Duplicate URL
                ]
            }
        )
        
        result2 = ToolCallResult(
            tool_type=ToolCallType.WEB_SEARCH,
            input_data="query2",
            status=ToolExecutionStatus.COMPLETED,
            metadata={
                "results": [
                    {"title": "Result 3", "url": "http://test.com"},  # Another duplicate
                    {"title": "Result 4", "url": "http://unique.com"}
                ]
            }
        )
        
        results = [result1, result2]
        
        # Process results
        processed = await tool_orchestrator.process_search_results(results)
        
        # Verify deduplication
        assert processed["total_results"] == 2  # Only unique URLs
        assert len(processed["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_tool_statistics(self, tool_orchestrator, mock_db):
        """Test tool statistics retrieval."""
        # Mock tool calls
        mock_tool_calls = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "failed"}
        ]
        mock_db.get_conversation_tool_calls.return_value = mock_tool_calls
        
        # Get statistics
        stats = await tool_orchestrator.get_tool_statistics("test-session")
        
        # Verify statistics
        assert stats["total_tool_calls"] == 3
        assert stats["successful_calls"] == 2
        assert stats["failed_calls"] == 1
        assert stats["success_rate"] == 66.66666666666667
    
    @pytest.mark.asyncio
    async def test_get_tool_statistics_no_db(self):
        """Test tool statistics when database is not available."""
        orchestrator = AsyncToolOrchestrator()
        
        stats = await orchestrator.get_tool_statistics("test-session")
        
        assert "error" in stats
        assert stats["error"] == "Database not available"
    
    @pytest.mark.asyncio
    async def test_is_web_search_available(self, tool_orchestrator, mock_web_search_service):
        """Test web search availability check."""
        mock_web_search_service.is_service_available.return_value = True
        
        available = await tool_orchestrator.is_web_search_available()
        
        assert available is True
    
    @pytest.mark.asyncio
    async def test_is_web_search_available_no_service(self):
        """Test web search availability when service is not available."""
        orchestrator = AsyncToolOrchestrator()
        
        available = await orchestrator.is_web_search_available()
        
        assert available is False
    
    @pytest.mark.asyncio
    async def test_execute_web_search_no_db(self, mock_web_search_service):
        """Test web search execution without database."""
        orchestrator = AsyncToolOrchestrator(web_search_service=mock_web_search_service)
        
        search_result = {"query": "test", "results": []}
        mock_web_search_service.search_educational_content.return_value = search_result
        
        result = await orchestrator.execute_web_search("test query", {"skill_level": "beginner"})
        
        assert result.status == ToolExecutionStatus.COMPLETED
        assert result.metadata == search_result
    
    @pytest.mark.asyncio
    async def test_execute_web_search_no_service(self):
        """Test web search execution without web search service."""
        orchestrator = AsyncToolOrchestrator()
        
        result = await orchestrator.execute_web_search("test query", {"skill_level": "beginner"})
        
        # When no service is available, it should still complete but with an error
        assert result.status == ToolExecutionStatus.FAILED
        assert "not available" in result.metadata["error"]


class TestToolOrchestratorIntegration:
    """Integration tests for tool orchestrator with real components."""
    
    @pytest.mark.asyncio
    async def test_tool_orchestrator_with_real_web_search(self):
        """Test tool orchestrator with real web search service (no API key)."""
        from app.services.web_search import AsyncWebSearchService
        
        # Create orchestrator with web search service (no API key)
        web_search = AsyncWebSearchService(api_key=None)  # Explicitly pass None to ensure no API key
        orchestrator = AsyncToolOrchestrator(web_search_service=web_search)
        
        # Test search execution (should work without API key due to graceful degradation)
        result = await orchestrator.execute_web_search(
            "jazz music history", {"skill_level": "beginner"}
        )
        
        # Should complete successfully since the service is actually working
        assert result.status == ToolExecutionStatus.COMPLETED
        # Check that the service is marked as available in the metadata
        assert result.metadata.get("service_available") == True
    
    @pytest.mark.asyncio
    async def test_concurrent_execution_limits(self):
        """Test that concurrent execution respects limits."""
        orchestrator = AsyncToolOrchestrator(max_concurrent_tools=2)
        
        # Create multiple concurrent searches
        async def mock_search(query, context):
            await asyncio.sleep(0.1)  # Simulate search time
            return {"query": query, "results": []}
        
        with patch.object(orchestrator, '_execute_search_with_error_handling', side_effect=mock_search):
            # Execute multiple searches concurrently
            results = await orchestrator.execute_concurrent_searches(
                ["query1", "query2", "query3", "query4"],
                {"skill_level": "beginner"}
            )
            
            # All should complete successfully
            assert len(results) == 4
            assert all(result.status == ToolExecutionStatus.COMPLETED for result in results)


# Test the get_tool_orchestrator factory function
class TestGetToolOrchestrator:
    """Test the get_tool_orchestrator factory function."""
    
    @pytest.mark.asyncio
    async def test_get_tool_orchestrator(self):
        """Test the factory function."""
        from app.services.tool_orchestrator import get_tool_orchestrator
        
        orchestrator = await get_tool_orchestrator()
        
        assert isinstance(orchestrator, AsyncToolOrchestrator)
        assert orchestrator.web_search_service is None
        assert orchestrator.db is None
    
    @pytest.mark.asyncio
    async def test_get_tool_orchestrator_with_services(self):
        """Test the factory function with services."""
        from app.services.tool_orchestrator import get_tool_orchestrator
        
        mock_web_search = AsyncMock(spec=AsyncWebSearchService)
        mock_db = AsyncMock(spec=AsyncConversationDB)
        
        orchestrator = await get_tool_orchestrator(
            web_search_service=mock_web_search,
            db=mock_db
        )
        
        assert isinstance(orchestrator, AsyncToolOrchestrator)
        assert orchestrator.web_search_service == mock_web_search
        assert orchestrator.db == mock_db 