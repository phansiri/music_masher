"""
Tool orchestration service for the Lit Music Mashup platform.

This module provides the AsyncToolOrchestrator class for managing
tool integration with the conversational agent, including concurrent
execution, error handling, and tool call tracking.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

from app.services.web_search import AsyncWebSearchService
from app.db import AsyncConversationDB, ToolCallType
from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class ToolExecutionStatus(str, Enum):
    """Status of tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ToolCallResult:
    """Result of a tool call operation."""
    tool_type: ToolCallType
    input_data: str
    output_data: Optional[str] = None
    status: ToolExecutionStatus = ToolExecutionStatus.PENDING
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AsyncToolOrchestrator:
    """
    Asynchronous tool orchestrator for managing tool integration.
    
    This class provides comprehensive tool orchestration capabilities
    including concurrent execution, error handling, and result processing
    for the conversational agent.
    """
    
    def __init__(
        self,
        web_search_service: Optional[AsyncWebSearchService] = None,
        db: Optional[AsyncConversationDB] = None,
        max_concurrent_tools: int = 3,
        tool_timeout: float = 30.0
    ):
        """
        Initialize the tool orchestrator.
        
        Args:
            web_search_service: Web search service instance
            db: Database instance for tool call tracking
            max_concurrent_tools: Maximum number of concurrent tool executions
            tool_timeout: Timeout for tool execution in seconds
        """
        self.web_search_service = web_search_service
        self.db = db
        self.max_concurrent_tools = max_concurrent_tools
        self.tool_timeout = tool_timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_tools)
        
        # Settings for configuration
        self.settings = get_settings()
        
        logger.info(f"Initialized AsyncToolOrchestrator with {max_concurrent_tools} max concurrent tools")
    
    async def execute_web_search(
        self,
        query: str,
        context: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> ToolCallResult:
        """
        Execute a web search with proper tracking and error handling.
        
        Args:
            query: Search query
            context: Context information for the search
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            ToolCallResult with search results and metadata
        """
        start_time = datetime.now(timezone.utc)
        tool_call_id = None
        
        try:
            # Create tool call record if database is available
            if self.db and conversation_id:
                tool_call_id = await self.db.add_tool_call(
                    conversation_id=conversation_id,
                    tool_type=ToolCallType.WEB_SEARCH,
                    input_data=query,
                    status="running"
                )
            
            # Execute the search with timeout
            async with self.semaphore:
                search_result = await asyncio.wait_for(
                    self._execute_search_with_error_handling(query, context),
                    timeout=self.tool_timeout
                )
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Check if the search result contains an error
            has_error = "error" in search_result and search_result["error"]
            status = ToolExecutionStatus.FAILED if has_error else ToolExecutionStatus.COMPLETED
            error_message = search_result.get("error") if has_error else None
            
            # Update tool call record
            if tool_call_id and self.db:
                await self.db.update_tool_call(
                    tool_call_id=tool_call_id,
                    output_data=str(search_result),
                    status=status.value,
                    error_message=error_message
                )
            
            return ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data=query,
                output_data=str(search_result),
                status=status,
                execution_time=execution_time,
                metadata=search_result,
                error_message=error_message
            )
            
        except asyncio.TimeoutError:
            error_msg = f"Web search timed out after {self.tool_timeout} seconds"
            logger.warning(error_msg)
            
            if tool_call_id and self.db:
                await self.db.update_tool_call(
                    tool_call_id=tool_call_id,
                    status="timeout",
                    error_message=error_msg
                )
            
            return ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data=query,
                status=ToolExecutionStatus.TIMEOUT,
                error_message=error_msg
            )
            
        except Exception as e:
            error_msg = f"Web search failed: {str(e)}"
            logger.error(error_msg)
            
            if tool_call_id and self.db:
                await self.db.update_tool_call(
                    tool_call_id=tool_call_id,
                    status="failed",
                    error_message=error_msg
                )
            
            return ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data=query,
                status=ToolExecutionStatus.FAILED,
                error_message=error_msg
            )
    
    async def execute_concurrent_searches(
        self,
        queries: List[str],
        context: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> List[ToolCallResult]:
        """
        Execute multiple web searches concurrently.
        
        Args:
            queries: List of search queries
            context: Context information for the searches
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            List of ToolCallResult objects
        """
        if not queries:
            return []
        
        logger.info(f"Executing {len(queries)} concurrent web searches")
        
        # Create tasks for all searches
        tasks = [
            self.execute_web_search(query, context, conversation_id)
            for query in queries
        ]
        
        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Search {i} failed with exception: {result}")
                processed_results.append(ToolCallResult(
                    tool_type=ToolCallType.WEB_SEARCH,
                    input_data=queries[i],
                    status=ToolExecutionStatus.FAILED,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_genre_exploration_searches(
        self,
        genres: List[str],
        context: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Dict[str, ToolCallResult]:
        """
        Execute searches for multiple music genres concurrently.
        
        Args:
            genres: List of music genres to search for
            context: Context information for the searches
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Dictionary mapping genres to their search results
        """
        # Create enhanced queries for each genre
        queries = []
        for genre in genres:
            enhanced_query = f"{genre} music history cultural significance educational"
            queries.append(enhanced_query)
        
        # Execute concurrent searches
        results = await self.execute_concurrent_searches(queries, context, conversation_id)
        
        # Map results back to genres
        genre_results = {}
        for i, result in enumerate(results):
            genre_results[genres[i]] = result
        
        return genre_results
    
    async def execute_cultural_research_searches(
        self,
        cultural_elements: List[str],
        context: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Dict[str, ToolCallResult]:
        """
        Execute searches for cultural elements concurrently.
        
        Args:
            cultural_elements: List of cultural elements to research
            context: Context information for the searches
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Dictionary mapping cultural elements to their search results
        """
        # Create enhanced queries for each cultural element
        queries = []
        for element in cultural_elements:
            enhanced_query = f"{element} music culture history significance"
            queries.append(enhanced_query)
        
        # Execute concurrent searches
        results = await self.execute_concurrent_searches(queries, context, conversation_id)
        
        # Map results back to cultural elements
        element_results = {}
        for i, result in enumerate(results):
            element_results[cultural_elements[i]] = result
        
        return element_results
    
    async def _execute_search_with_error_handling(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single web search with comprehensive error handling.
        
        Args:
            query: Search query
            context: Context information
            
        Returns:
            Search results dictionary
        """
        if not self.web_search_service:
            logger.warning("Web search service not available")
            return {
                "query": query,
                "results": [],
                "error": "Web search service not available",
                "enhanced_query": query
            }
        
        try:
            return await self.web_search_service.search_educational_content(query, context)
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "enhanced_query": query
            }
    
    async def process_search_results(
        self,
        results: List[ToolCallResult]
    ) -> Dict[str, Any]:
        """
        Process and synthesize search results.
        
        Args:
            results: List of tool call results
            
        Returns:
            Processed and synthesized results
        """
        successful_results = [r for r in results if r.status == ToolExecutionStatus.COMPLETED]
        failed_results = [r for r in results if r.status != ToolExecutionStatus.COMPLETED]
        
        # Extract and combine successful search results
        combined_results = []
        for result in successful_results:
            if result.metadata and isinstance(result.metadata, dict):
                search_data = result.metadata
                if "results" in search_data:
                    combined_results.extend(search_data["results"])
        
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in combined_results:
            if isinstance(result, dict) and "url" in result:
                if result["url"] not in seen_urls:
                    unique_results.append(result)
                    seen_urls.add(result["url"])
        
        return {
            "successful_searches": len(successful_results),
            "failed_searches": len(failed_results),
            "total_results": len(unique_results),
            "results": unique_results,
            "errors": [r.error_message for r in failed_results if r.error_message]
        }
    
    async def get_tool_statistics(
        self,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about tool usage.
        
        Args:
            conversation_id: Optional conversation ID to filter by
            
        Returns:
            Dictionary with tool usage statistics
        """
        if not self.db:
            return {"error": "Database not available"}
        
        try:
            if conversation_id:
                tool_calls = await self.db.get_conversation_tool_calls(conversation_id)
            else:
                # This would need a method to get all tool calls
                tool_calls = []
            
            total_calls = len(tool_calls)
            successful_calls = len([tc for tc in tool_calls if tc.get("status") == "completed"])
            failed_calls = total_calls - successful_calls
            
            if total_calls > 0:
                success_rate = Decimal(successful_calls) / Decimal(total_calls) * Decimal('100')
                success_rate = float(success_rate.quantize(Decimal('0.00000000000001'), rounding=ROUND_HALF_UP))
            else:
                success_rate = 0.0
            
            return {
                "total_tool_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": success_rate
            }
        except Exception as e:
            logger.error(f"Failed to get tool statistics: {e}")
            return {"error": str(e)}
    
    async def is_web_search_available(self) -> bool:
        """Check if web search service is available."""
        if not self.web_search_service:
            return False
        return self.web_search_service.is_service_available()


async def get_tool_orchestrator(
    web_search_service: Optional[AsyncWebSearchService] = None,
    db: Optional[AsyncConversationDB] = None
) -> AsyncToolOrchestrator:
    """
    Get a configured tool orchestrator instance.
    
    Args:
        web_search_service: Optional web search service instance
        db: Optional database instance
        
    Returns:
        Configured AsyncToolOrchestrator instance
    """
    return AsyncToolOrchestrator(
        web_search_service=web_search_service,
        db=db
    ) 