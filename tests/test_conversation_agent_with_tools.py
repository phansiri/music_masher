"""
Tests for the enhanced AsyncConversationalMashupAgent with tool integration.

This module provides comprehensive tests for the conversation agent with
tool orchestration, phase-based conversation management, and web search integration.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from app.agents.conversation_agent import AsyncConversationalMashupAgent, ConversationPhase, SkillLevel
from app.services.tool_orchestrator import AsyncToolOrchestrator, ToolCallResult, ToolExecutionStatus
from app.services.web_search import AsyncWebSearchService
from app.db import AsyncConversationDB, ToolCallType


class TestConversationAgentWithTools:
    """Test the enhanced conversation agent with tool integration."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database."""
        mock_db = AsyncMock(spec=AsyncConversationDB)
        mock_db.get_conversation.return_value = {
            "conversation_id": "test-session",
            "phase": ConversationPhase.INITIAL.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        mock_db.add_message.return_value = True
        mock_db.update_conversation_phase.return_value = True
        return mock_db
    
    @pytest_asyncio.fixture
    async def mock_web_search_service(self):
        """Create a mock web search service."""
        mock_service = AsyncMock(spec=AsyncWebSearchService)
        mock_service.is_service_available.return_value = True
        return mock_service
    
    @pytest_asyncio.fixture
    async def mock_tool_orchestrator(self):
        """Create a mock tool orchestrator."""
        mock_orchestrator = AsyncMock(spec=AsyncToolOrchestrator)
        mock_orchestrator.is_web_search_available.return_value = True
        return mock_orchestrator
    
    @pytest_asyncio.fixture
    async def conversation_agent(self, mock_db, mock_web_search_service, mock_tool_orchestrator):
        """Create a conversation agent instance for testing."""
        with patch('app.agents.conversation_agent.AsyncWebSearchService', return_value=mock_web_search_service), \
             patch('app.agents.conversation_agent.AsyncToolOrchestrator', return_value=mock_tool_orchestrator):
            
            agent = AsyncConversationalMashupAgent(
                model_name="test-model",
                enable_tools=True,
                db_path=":memory:"
            )
            agent.db = mock_db
            agent.tool_orchestrator = mock_tool_orchestrator
            
            # Mock the AI model
            mock_model = AsyncMock()
            agent.model = mock_model
            
            return agent
    
    @pytest.mark.asyncio
    async def test_initialization_with_tools(self, mock_web_search_service, mock_tool_orchestrator):
        """Test conversation agent initialization with tools enabled."""
        with patch('app.agents.conversation_agent.AsyncWebSearchService', return_value=mock_web_search_service), \
             patch('app.agents.conversation_agent.AsyncToolOrchestrator', return_value=mock_tool_orchestrator):
            
            agent = AsyncConversationalMashupAgent(enable_tools=True)
            
            assert agent.enable_tools is True
            assert agent.tool_orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_initialization_without_tools(self):
        """Test conversation agent initialization with tools disabled."""
        agent = AsyncConversationalMashupAgent(enable_tools=False)
        
        assert agent.enable_tools is False
        assert agent.tool_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_process_message_with_tools(self, conversation_agent, mock_db, mock_tool_orchestrator):
        """Test message processing with tool integration."""
        # Mock AI model response
        mock_response = MagicMock()
        mock_response.content = "Hello! I'm here to help you create an educational music mashup."
        conversation_agent.model.ainvoke.return_value = mock_response
        
        # Mock tool execution results
        mock_tool_orchestrator.execute_genre_exploration_searches.return_value = {}
        mock_tool_orchestrator.process_search_results.return_value = {
            "successful_searches": 0,
            "failed_searches": 0,
            "total_results": 0,
            "results": []
        }
        
        # Process message
        result = await conversation_agent.process_message(
            session_id="test-session",
            user_message="I want to create a jazz and rock mashup"
        )
        
        # Verify result
        assert "response" in result
        assert "phase" in result
        assert "phase_transition" in result
        assert "context" in result
        assert "tool_results" in result
        
        # Verify database calls
        mock_db.add_message.assert_called()
        mock_db.update_conversation_phase.assert_called()
    
    @pytest.mark.asyncio
    async def test_genre_exploration_with_tools(self, conversation_agent, mock_tool_orchestrator):
        """Test genre exploration phase with tool execution."""
        # Set up conversation for genre exploration
        conversation_agent.db.get_conversation.return_value = {
            "conversation_id": "test-session",
            "phase": ConversationPhase.GENRE_EXPLORATION.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Mock AI model response
        mock_response = MagicMock()
        mock_response.content = "Great! Let me research jazz and rock for you."
        conversation_agent.model.ainvoke.return_value = mock_response
        
        # Mock tool execution
        mock_tool_results = {
            "jazz": ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data="jazz music history cultural significance educational",
                status=ToolExecutionStatus.COMPLETED,
                metadata={"results": [{"title": "Jazz History", "url": "http://example.com"}]}
            ),
            "rock": ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data="rock music history cultural significance educational",
                status=ToolExecutionStatus.COMPLETED,
                metadata={"results": [{"title": "Rock History", "url": "http://example.com"}]}
            )
        }
        mock_tool_orchestrator.execute_genre_exploration_searches.return_value = mock_tool_results
        mock_tool_orchestrator.process_search_results.return_value = {
            "successful_searches": 2,
            "failed_searches": 0,
            "total_results": 2,
            "results": [{"title": "Jazz History"}, {"title": "Rock History"}]
        }
        
        # Process message
        result = await conversation_agent.process_message(
            session_id="test-session",
            user_message="I want to explore jazz and rock genres"
        )
        
        # Verify tool execution
        mock_tool_orchestrator.execute_genre_exploration_searches.assert_called_once()
        assert "tool_results" in result
        assert result["tool_results"]["synthesized"]["total_results"] == 2
    
    @pytest.mark.asyncio
    async def test_cultural_research_with_tools(self, conversation_agent, mock_tool_orchestrator):
        """Test cultural research phase with tool execution."""
        # Set up conversation for cultural research
        conversation_agent.db.get_conversation.return_value = {
            "conversation_id": "test-session",
            "phase": ConversationPhase.CULTURAL_RESEARCH.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Mock AI model response
        mock_response = MagicMock()
        mock_response.content = "Let me research the cultural context of these genres."
        conversation_agent.model.ainvoke.return_value = mock_response
        
        # Mock tool execution
        mock_cultural_results = {
            "history": ToolCallResult(
                tool_type=ToolCallType.WEB_SEARCH,
                input_data="history music culture history significance",
                status=ToolExecutionStatus.COMPLETED,
                metadata={"results": [{"title": "Cultural History", "url": "http://example.com"}]}
            )
        }
        mock_tool_orchestrator.execute_cultural_research_searches.return_value = mock_cultural_results
        mock_tool_orchestrator.process_search_results.return_value = {
            "successful_searches": 1,
            "failed_searches": 0,
            "total_results": 1,
            "results": [{"title": "Cultural History"}]
        }
        
        # Process message
        result = await conversation_agent.process_message(
            session_id="test-session",
            user_message="I want to learn about the cultural history"
        )
        
        # Verify tool execution
        mock_tool_orchestrator.execute_cultural_research_searches.assert_called_once()
        assert "tool_results" in result
    
    @pytest.mark.asyncio
    async def test_tool_execution_error_handling(self, conversation_agent, mock_tool_orchestrator):
        """Test error handling when tool execution fails."""
        # Mock AI model response
        mock_response = MagicMock()
        mock_response.content = "I'll help you explore genres."
        conversation_agent.model.ainvoke.return_value = mock_response
        
        # Mock tool execution error
        mock_tool_orchestrator.execute_genre_exploration_searches.side_effect = Exception("Tool execution failed")
        
        # Process message
        result = await conversation_agent.process_message(
            session_id="test-session",
            user_message="I want to explore jazz and rock"
        )
        

        
        # Verify error handling
        assert "tool_results" in result
        assert "error" in result["tool_results"]
        assert "Tool execution failed" in result["tool_results"]["error"]
    
    @pytest.mark.asyncio
    async def test_context_extraction_with_genres(self, conversation_agent):
        """Test context extraction for genre-related messages."""
        # Test genre extraction
        context = await conversation_agent._extract_genre_context("I love jazz and rock music")
        
        assert "mentioned_genres" in context
        assert "jazz" in context["mentioned_genres"]
        assert "rock" in context["mentioned_genres"]
    
    @pytest.mark.asyncio
    async def test_context_extraction_with_skill_level(self, conversation_agent):
        """Test context extraction for skill level."""
        # Test beginner skill level
        context = await conversation_agent._extract_initial_context("I'm a beginner in music")
        
        assert context["skill_level"] == SkillLevel.BEGINNER
        
        # Test advanced skill level
        context = await conversation_agent._extract_initial_context("I'm an advanced musician")
        
        assert context["skill_level"] == SkillLevel.ADVANCED
    
    @pytest.mark.asyncio
    async def test_context_extraction_with_theory_concepts(self, conversation_agent):
        """Test context extraction for music theory concepts."""
        context = await conversation_agent._extract_educational_context("I want to learn about rhythm and harmony")
        
        assert "theory_concepts" in context
        assert "rhythm" in context["theory_concepts"]
        assert "harmony" in context["theory_concepts"]
    
    @pytest.mark.asyncio
    async def test_context_extraction_with_cultural_elements(self, conversation_agent):
        """Test context extraction for cultural elements."""
        context = await conversation_agent._extract_cultural_context("I'm interested in the history and tradition")
        
        assert "cultural_elements" in context
        assert "history" in context["cultural_elements"]
        assert "tradition" in context["cultural_elements"]
    
    @pytest.mark.asyncio
    async def test_phase_transition_logic(self, conversation_agent):
        """Test phase transition logic."""
        # Test initial to genre exploration
        transition = await conversation_agent._determine_phase_transition(
            ConversationPhase.INITIAL,
            "I want to explore different music genres",
            "Let's explore genres!",
            {"mentioned_genres": ["jazz"]}
        )
        
        assert transition["should_transition"] is True
        assert transition["new_phase"] == ConversationPhase.GENRE_EXPLORATION
        
        # Test genre exploration to educational clarification
        transition = await conversation_agent._determine_phase_transition(
            ConversationPhase.GENRE_EXPLORATION,
            "I want to learn music theory",
            "Great! Let's clarify your educational goals.",
            {"mentioned_genres": ["jazz"], "has_educational_goals": True}
        )
        
        assert transition["should_transition"] is True
        assert transition["new_phase"] == ConversationPhase.EDUCATIONAL_CLARIFICATION
    
    @pytest.mark.asyncio
    async def test_prepare_messages_with_tools(self, conversation_agent):
        """Test message preparation with tool results."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        tool_results = {
            "synthesized": {
                "total_results": 3,
                "results": [{"title": "Result 1"}, {"title": "Result 2"}, {"title": "Result 3"}]
            }
        }
        
        ai_messages = await conversation_agent._prepare_messages_for_ai_with_tools(
            messages, ConversationPhase.GENRE_EXPLORATION, {}, tool_results
        )
        
        # Verify system message includes tool context
        system_message = ai_messages[0].content
        assert "3 relevant sources" in system_message
    
    @pytest.mark.asyncio
    async def test_fallback_response(self, conversation_agent):
        """Test fallback response generation."""
        response = conversation_agent._get_fallback_response(ConversationPhase.INITIAL)
        assert "help you create" in response
        
        response = conversation_agent._get_fallback_response(ConversationPhase.GENRE_EXPLORATION)
        assert "genres" in response
    
    @pytest.mark.asyncio
    async def test_agent_cleanup(self, conversation_agent, mock_db):
        """Test agent cleanup."""
        await conversation_agent.close()
        mock_db.close.assert_called_once()


class TestConversationAgentIntegration:
    """Integration tests for conversation agent with real components."""
    
    @pytest_asyncio.fixture
    async def mock_db_for_integration(self):
        """Create a mock database for integration tests."""
        mock_db = AsyncMock(spec=AsyncConversationDB)
        
        # Track conversation state
        conversation_state = {
            "conversation_id": "test-session-1",
            "phase": ConversationPhase.INITIAL.value,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        async def get_conversation(session_id):
            return conversation_state
        
        async def update_conversation_phase(session_id, new_phase):
            conversation_state["phase"] = new_phase.value
            return True
        
        mock_db.get_conversation = get_conversation
        mock_db.update_conversation_phase = update_conversation_phase
        mock_db.add_message.return_value = True
        mock_db.create_conversation.return_value = True
        return mock_db
    
    @pytest.mark.asyncio
    async def test_conversation_agent_with_real_web_search(self, mock_db_for_integration):
        """Test conversation agent with real web search service (no API key)."""
        from app.services.web_search import AsyncWebSearchService
        
        # Create agent with real web search service (no API key)
        web_search = AsyncWebSearchService()
        agent = AsyncConversationalMashupAgent(
            enable_tools=True,
            tavily_api_key=None  # No API key for graceful degradation
        )
        
        # Mock the database
        agent.db = mock_db_for_integration
        
        # Mock the AI model
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Hello! I'm here to help you explore jazz music."
        mock_model.ainvoke.return_value = mock_response
        agent.model = mock_model
        
        # Test message processing
        result = await agent.process_message(
            session_id="test-session",
            user_message="I want to explore jazz music"
        )
        
        # Should complete successfully even without API key
        assert "response" in result
        assert "phase" in result
        assert "tool_results" in result
    
    @pytest.mark.asyncio
    async def test_conversation_agent_phase_progression(self, mock_db_for_integration):
        """Test conversation agent phase progression."""
        agent = AsyncConversationalMashupAgent(enable_tools=False)  # Disable tools for simpler testing
        
        # Mock the database
        agent.db = mock_db_for_integration
        
        # Mock the AI model
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Great! Let's explore some genres."
        mock_model.ainvoke.return_value = mock_response
        agent.model = mock_model
        
        # Test initial phase
        result1 = await agent.process_message(
            session_id="test-session-1",
            user_message="I want to create a music mashup"
        )
        
        # Test genre exploration phase (using same session to test phase transition)
        result2 = await agent.process_message(
            session_id="test-session-1",
            user_message="I want to explore jazz and rock genres"
        )
        
        # Both should complete successfully
        assert result1["phase"] == ConversationPhase.INITIAL
        assert result2["phase"] == ConversationPhase.GENRE_EXPLORATION 