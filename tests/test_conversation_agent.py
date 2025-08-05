"""
Tests for the AsyncConversationalMashupAgent.

This module contains tests for the conversation agent functionality.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.agents import AsyncConversationalMashupAgent, ConversationPhase, SkillLevel


class TestAsyncConversationalMashupAgent:
    """Test cases for AsyncConversationalMashupAgent."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database for testing."""
        mock_db = Mock()
        mock_db.get_conversation = AsyncMock(return_value={
            'conversation_id': 'test-session',
            'phase': ConversationPhase.INITIAL,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        mock_db.create_conversation = AsyncMock(return_value=True)
        mock_db.add_message = AsyncMock(return_value=True)
        mock_db.update_conversation_phase = AsyncMock(return_value=True)
        mock_db.get_messages = AsyncMock(return_value=[])
        mock_db.close = AsyncMock()
        return mock_db
    
    @pytest_asyncio.fixture
    async def agent(self, mock_db):
        """Create an agent instance for testing."""
        with patch('app.agents.conversation_agent.AsyncConversationDB', return_value=mock_db):
            with patch('app.agents.conversation_agent.get_settings') as mock_settings:
                mock_settings.return_value.DATABASE_PATH = '/tmp/test.db'
                
                # Mock the model initialization
                with patch('app.agents.conversation_agent.ChatOllama') as mock_chat_ollama:
                    mock_model = Mock()
                    mock_model.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
                    mock_chat_ollama.return_value = mock_model
                    
                    agent = AsyncConversationalMashupAgent(
                        model_name="test-model",
                        model_type="ollama",
                        db_path="/tmp/test.db"
                    )
                    agent.db = mock_db
                    yield agent
                    await agent.close()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent.model_name == "test-model"
        assert agent.model_type == "ollama"
        assert agent.system_prompts is not None
        assert len(agent.system_prompts) == 5  # All phases
    
    @pytest.mark.asyncio
    async def test_extract_initial_context(self, agent):
        """Test context extraction for initial phase."""
        message = "I want to teach my high school students about jazz and classical music"
        context = await agent._extract_initial_context(message)
        
        assert 'teaching' in context['educational_goals']
        assert context['target_audience'] == 'higher_education'
        assert 'jazz' in context['music_interests']
        assert 'classical' in context['music_interests']
    
    @pytest.mark.asyncio
    async def test_extract_genre_context(self, agent):
        """Test context extraction for genre exploration phase."""
        message = "I'm interested in jazz and blues music with cultural traditions"
        context = await agent._extract_genre_context(message)
        
        assert 'jazz' in context['mentioned_genres']
        assert 'blues' in context['mentioned_genres']
        assert 'tradition' in context['cultural_elements']
    
    @pytest.mark.asyncio
    async def test_extract_educational_context(self, agent):
        """Test context extraction for educational clarification phase."""
        message = "My students are beginners and I want to teach them about rhythm and melody"
        context = await agent._extract_educational_context(message)
        
        assert context['skill_level'] == SkillLevel.BEGINNER
        assert 'rhythm' in context['theory_concepts']
        assert 'melody' in context['theory_concepts']
    
    @pytest.mark.asyncio
    async def test_determine_phase_transition(self, agent):
        """Test phase transition logic."""
        # Test transition from initial to genre exploration
        transition = await agent._determine_phase_transition(
            ConversationPhase.INITIAL,
            "I want to explore different music genres",
            "Test response",
            {}
        )
        assert transition['should_transition'] is True
        assert transition['new_phase'] == ConversationPhase.GENRE_EXPLORATION
        
        # Test no transition
        transition = await agent._determine_phase_transition(
            ConversationPhase.INITIAL,
            "Hello, how are you?",
            "Test response",
            {}
        )
        assert transition['should_transition'] is False
    
    @pytest.mark.asyncio
    async def test_process_message(self, agent):
        """Test processing a user message."""
        response = await agent.process_message(
            session_id="test-session",
            user_message="I want to create an educational mashup for my students"
        )
        
        assert 'response' in response
        assert 'phase' in response
        assert 'session_id' in response
        assert response['session_id'] == "test-session"
    
    @pytest.mark.asyncio
    async def test_fallback_response(self, agent):
        """Test fallback response generation."""
        fallback = agent._get_fallback_response(ConversationPhase.INITIAL)
        assert "educational music mashup" in fallback.lower()
        
        fallback = agent._get_fallback_response(ConversationPhase.GENRE_EXPLORATION)
        assert "genres" in fallback.lower()
    
    @pytest.mark.asyncio
    async def test_model_initialization_ollama(self):
        """Test Ollama model initialization."""
        with patch('app.agents.conversation_agent.ChatOllama') as mock_chat_ollama:
            mock_chat_ollama.return_value = Mock()
            
            with patch('app.agents.conversation_agent.AsyncConversationDB') as mock_db_class:
                mock_db_class.return_value = Mock()
                
                with patch('app.agents.conversation_agent.get_settings') as mock_settings:
                    mock_settings.return_value.DATABASE_PATH = '/tmp/test.db'
                    
                    agent = AsyncConversationalMashupAgent(
                        model_name="llama3.1:8b-instruct",
                        model_type="ollama"
                    )
                    
                    assert agent.model_type == "ollama"
                    mock_chat_ollama.assert_called_once_with(
                        model="llama3.1:8b-instruct",
                        temperature=0.7
                    )
    
    @pytest.mark.asyncio
    async def test_model_initialization_openai(self):
        """Test OpenAI model initialization."""
        with patch('app.agents.conversation_agent.ChatOpenAI') as mock_chat_openai:
            mock_chat_openai.return_value = Mock()
            
            with patch('app.agents.conversation_agent.AsyncConversationDB') as mock_db_class:
                mock_db_class.return_value = Mock()
                
                with patch('app.agents.conversation_agent.get_settings') as mock_settings:
                    mock_settings.return_value.DATABASE_PATH = '/tmp/test.db'
                    
                    agent = AsyncConversationalMashupAgent(
                        model_name="gpt-4",
                        model_type="openai",
                        openai_api_key="test-key"
                    )
                    
                    assert agent.model_type == "openai"
                    mock_chat_openai.assert_called_once_with(
                        model="gpt-4",
                        temperature=0.7,
                        api_key="test-key"
                    )
    
    @pytest.mark.asyncio
    async def test_invalid_model_type(self):
        """Test that invalid model type raises error."""
        with pytest.raises(ValueError, match="Unsupported model type"):
            with patch('app.agents.conversation_agent.AsyncConversationDB') as mock_db_class:
                mock_db_class.return_value = Mock()
                
                with patch('app.agents.conversation_agent.get_settings') as mock_settings:
                    mock_settings.return_value.DATABASE_PATH = '/tmp/test.db'
                    
                    AsyncConversationalMashupAgent(
                        model_name="test-model",
                        model_type="invalid"
                    ) 