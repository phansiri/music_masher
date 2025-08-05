"""
Async conversational AI agent for the Lit Music Mashup platform.

This module provides the AsyncConversationalMashupAgent class for managing
conversations with phase-based progression, context extraction, and tool integration.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.db import AsyncConversationDB, ConversationPhase, MessageRole
from app.services import AsyncWebSearchService, AsyncToolOrchestrator
from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class ConversationPhase(str, Enum):
    """Conversation phases for the educational mashup generation process."""
    INITIAL = "initial"
    GENRE_EXPLORATION = "genre_exploration"
    EDUCATIONAL_CLARIFICATION = "educational_clarification"
    CULTURAL_RESEARCH = "cultural_research"
    READY_FOR_GENERATION = "ready_for_generation"
    ERROR = "error"


class SkillLevel(str, Enum):
    """Educational skill levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AsyncConversationalMashupAgent:
    """
    Async conversational AI agent with phase-based conversation management and tool integration.
    
    This agent handles educational music mashup conversations with context
    extraction, state management, and tool orchestration across different conversation phases.
    """
    
    def __init__(
        self, 
        model_name: str = "llama3.1:8b-instruct",
        model_type: str = "ollama",  # "ollama" or "openai"
        tavily_api_key: Optional[str] = None,
        db_path: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        enable_tools: bool = True
    ):
        """
        Initialize the conversational agent.
        
        Args:
            model_name: Name of the AI model to use
            model_type: Type of model ("ollama" or "openai")
            tavily_api_key: Optional Tavily API key for web search
            db_path: Path to the database
            openai_api_key: Optional OpenAI API key
            enable_tools: Whether to enable tool integration
        """
        self.model_name = model_name
        self.model_type = model_type
        self.tavily_api_key = tavily_api_key
        self.openai_api_key = openai_api_key
        self.enable_tools = enable_tools
        
        # Initialize database
        settings = get_settings()
        self.db = AsyncConversationDB(db_path or settings.DATABASE_PATH)
        
        # Initialize AI model
        self._initialize_model()
        
        # Initialize tool orchestrator if enabled
        self.tool_orchestrator = None
        if self.enable_tools:
            self._initialize_tool_orchestrator()
        
        # System prompts for different phases
        self._initialize_system_prompts()
        
        logger.info(f"Initialized AsyncConversationalMashupAgent with {model_type} model: {model_name}, tools: {enable_tools}")
    
    def _initialize_model(self):
        """Initialize the AI model based on model_type."""
        try:
            if self.model_type == "ollama":
                self.model = ChatOllama(
                    model=self.model_name,
                    temperature=0.7
                )
            elif self.model_type == "openai":
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key required for OpenAI model type")
                self.model = ChatOpenAI(
                    model=self.model_name,
                    temperature=0.7,
                    api_key=self.openai_api_key
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise
    
    def _initialize_tool_orchestrator(self):
        """Initialize the tool orchestrator."""
        try:
            # Initialize web search service
            web_search_service = AsyncWebSearchService(self.tavily_api_key)
            
            # Initialize tool orchestrator
            self.tool_orchestrator = AsyncToolOrchestrator(
                web_search_service=web_search_service,
                db=self.db
            )
            logger.info("Tool orchestrator initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize tool orchestrator: {e}")
            self.tool_orchestrator = None
    
    def _initialize_system_prompts(self):
        """Initialize system prompts for different conversation phases."""
        self.system_prompts = {
            ConversationPhase.INITIAL: """You are an educational AI assistant for music mashup creation. 
            Your goal is to help users create educational music mashups that combine different genres 
            while teaching music theory and cultural context. Start by understanding the user's goals 
            and experience level. Be friendly, encouraging, and educational.""",
            
            ConversationPhase.GENRE_EXPLORATION: """You are helping the user explore different music genres 
            for their mashup. Ask about their musical preferences, favorite genres, and what they want to learn. 
            Help them understand the characteristics of different genres and how they might work together. 
            Be educational and encourage exploration.""",
            
            ConversationPhase.EDUCATIONAL_CLARIFICATION: """You are clarifying the educational objectives 
            for the music mashup. Understand the user's skill level (beginner, intermediate, advanced) 
            and what music theory concepts they want to learn. Help them set clear learning goals 
            and explain how the mashup will help them understand these concepts.""",
            
            ConversationPhase.CULTURAL_RESEARCH: """You are researching the cultural context and historical 
            background of the music genres for the mashup. Help the user understand the cultural significance, 
            historical development, and social context of the genres they've chosen. This will enrich 
            their educational experience and create more meaningful content.""",
            
            ConversationPhase.READY_FOR_GENERATION: """You are preparing to generate the final music mashup. 
            Summarize what you've learned about the user's preferences, educational goals, and cultural context. 
            Confirm that you have all the information needed to create an educational mashup that combines 
            the chosen genres while teaching the specified music theory concepts and cultural context."""
        }
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response with tool integration.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            context: Optional additional context
            
        Returns:
            Response data with potential tool results and phase transition
        """
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(session_id)
            current_phase = ConversationPhase(conversation['phase'])
            
            # Extract context from user message
            extracted_context = await self._extract_context(user_message, current_phase)
            
            # Handle conversation phase with tool integration
            response_data = await self._handle_conversation_phase_with_tools(
                session_id, user_message, conversation, current_phase, extracted_context
            )
            
            # Add user message to database
            await self.db.add_message(session_id, MessageRole.USER, user_message)
            
            # Add AI response to database
            await self.db.add_message(session_id, MessageRole.ASSISTANT, response_data['response'])
            
            # Update conversation phase if needed
            if response_data['phase_transition']:
                await self.db.update_conversation_phase(session_id, response_data['new_phase'])
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I apologize, but I encountered an error processing your message. Please try again.",
                'phase': ConversationPhase.ERROR,
                'phase_transition': False,
                'error': str(e)
            }
    
    async def _get_or_create_conversation(self, session_id: str) -> Dict[str, Any]:
        """Get existing conversation or create a new one."""
        conversation = await self.db.get_conversation(session_id)
        if not conversation:
            await self.db.create_conversation(session_id)
            conversation = await self.db.get_conversation(session_id)
        return conversation
    
    async def _extract_context(
        self, 
        user_message: str, 
        current_phase: ConversationPhase
    ) -> Dict[str, Any]:
        """
        Extract context from user message based on current phase.
        
        Args:
            user_message: User's message
            current_phase: Current conversation phase
            
        Returns:
            Extracted context dictionary
        """
        context = {
            'message': user_message,
            'phase': current_phase,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Phase-specific context extraction
        if current_phase == ConversationPhase.INITIAL:
            context.update(await self._extract_initial_context(user_message))
        elif current_phase == ConversationPhase.GENRE_EXPLORATION:
            context.update(await self._extract_genre_context(user_message))
        elif current_phase == ConversationPhase.EDUCATIONAL_CLARIFICATION:
            context.update(await self._extract_educational_context(user_message))
        elif current_phase == ConversationPhase.CULTURAL_RESEARCH:
            context.update(await self._extract_cultural_context(user_message))
        elif current_phase == ConversationPhase.READY_FOR_GENERATION:
            context.update(await self._extract_generation_context(user_message))
        
        return context
    
    async def _extract_initial_context(self, message: str) -> Dict[str, Any]:
        """Extract context from initial phase messages."""
        message_lower = message.lower()
        context = {
            'educational_goals': [],
            'target_audience': None,
            'music_interests': [],
            'skill_level': SkillLevel.INTERMEDIATE
        }
        
        # Extract skill level
        if any(word in message_lower for word in ['beginner', 'new', 'start', 'basic']):
            context['skill_level'] = SkillLevel.BEGINNER
        elif any(word in message_lower for word in ['advanced', 'expert', 'professional']):
            context['skill_level'] = SkillLevel.ADVANCED
        
        # Extract educational goals
        if any(word in message_lower for word in ['teach', 'teaching', 'education', 'learn', 'learning']):
            context['educational_goals'].append('teaching')
        if any(word in message_lower for word in ['learn', 'learning', 'study', 'understand']):
            context['educational_goals'].append('learning')
        
        # Extract target audience
        if any(word in message_lower for word in ['high school', 'college', 'university', 'student', 'students']):
            context['target_audience'] = 'higher_education'
        elif any(word in message_lower for word in ['elementary', 'middle school', 'grade']):
            context['target_audience'] = 'k12_education'
        
        # Extract music interests and mentioned genres
        genres = ['jazz', 'classical', 'rock', 'pop', 'hip hop', 'blues', 'folk', 'electronic', 'country', 'reggae', 'soul', 'r&b', 'metal', 'punk', 'funk', 'disco', 'latin', 'world', 'ambient', 'experimental']
        for genre in genres:
            if genre in message_lower:
                context['music_interests'].append(genre)
                context['mentioned_genres'] = context.get('mentioned_genres', []) + [genre]
        
        return context
    
    async def _extract_genre_context(self, message: str) -> Dict[str, Any]:
        """Extract genre-related context."""
        message_lower = message.lower()
        context = {
            'mentioned_genres': [],
            'cultural_elements': [],
            'combination_ideas': []
        }
        
        # Common music genres
        genres = [
            'jazz', 'rock', 'pop', 'hip hop', 'classical', 'blues', 'country',
            'electronic', 'folk', 'reggae', 'soul', 'r&b', 'metal', 'punk',
            'funk', 'disco', 'latin', 'world', 'ambient', 'experimental'
        ]
        
        for genre in genres:
            if genre in message_lower:
                context['mentioned_genres'].append(genre)
        
        # Extract cultural elements
        cultural_elements = [
            'history', 'tradition', 'culture', 'society', 'community',
            'ceremony', 'celebration', 'ritual', 'spiritual', 'religious',
            'heritage', 'custom', 'practice', 'belief', 'ceremony'
        ]
        
        for element in cultural_elements:
            if element in message_lower:
                context['cultural_elements'].append(element)
        
        return context
    
    async def _extract_educational_context(self, message: str) -> Dict[str, Any]:
        """Extract educational context."""
        message_lower = message.lower()
        context = {
            'skill_level': SkillLevel.INTERMEDIATE,
            'theory_concepts': [],
            'learning_objectives': [],
            'assessment_methods': []
        }
        
        # Extract skill level
        if any(word in message_lower for word in ['beginner', 'new', 'start', 'basic']):
            context['skill_level'] = SkillLevel.BEGINNER
        elif any(word in message_lower for word in ['advanced', 'expert', 'professional']):
            context['skill_level'] = SkillLevel.ADVANCED
        
        # Music theory concepts
        theory_concepts = [
            'rhythm', 'melody', 'harmony', 'chord', 'scale', 'key', 'tempo',
            'beat', 'syncopation', 'polyrhythm', 'modulation', 'transposition'
        ]
        
        for concept in theory_concepts:
            if concept in message_lower:
                context['theory_concepts'].append(concept)
        
        return context
    
    async def _extract_cultural_context(self, message: str) -> Dict[str, Any]:
        """Extract cultural context."""
        message_lower = message.lower()
        context = {
            'cultural_elements': [],
            'historical_context': [],
            'social_significance': []
        }
        
        # Cultural elements
        cultural_elements = [
            'history', 'tradition', 'culture', 'society', 'community',
            'ceremony', 'celebration', 'ritual', 'spiritual', 'religious',
            'heritage', 'custom', 'practice', 'belief', 'ceremony'
        ]
        
        for element in cultural_elements:
            if element in message_lower:
                context['cultural_elements'].append(element)
        
        return context
    
    async def _extract_generation_context(self, message: str) -> Dict[str, Any]:
        """Extract generation context."""
        message_lower = message.lower()
        context = {}
        
        # Check for confirmation words
        if any(word in message_lower for word in ['yes', 'ready', 'go', 'create', 'generate']):
            context['ready_for_generation'] = True
        
        return context
    
    async def _handle_conversation_phase_with_tools(
        self,
        session_id: str,
        user_message: str,
        conversation: Dict[str, Any],
        current_phase: ConversationPhase,
        extracted_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle conversation phase with tool integration.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            conversation: Current conversation data
            current_phase: Current conversation phase
            extracted_context: Extracted context from user message
            
        Returns:
            Response data with tool results and potential phase transition
        """
        # Execute tools based on phase and context
        tool_results = await self._execute_phase_tools(
            session_id, current_phase, extracted_context
        )
        
        # Get conversation history
        messages = await self.db.get_messages(session_id, limit=10)
        
        # Prepare messages for AI model with tool results
        ai_messages = await self._prepare_messages_for_ai_with_tools(
            messages, current_phase, extracted_context, tool_results
        )
        
        # Get AI response
        try:
            response = await self.model.ainvoke(ai_messages)
            ai_response = response.content
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            ai_response = self._get_fallback_response(current_phase)
        
        # Determine phase transition
        phase_transition = await self._determine_phase_transition(
            current_phase, user_message, ai_response, extracted_context
        )
        
        return {
            'response': ai_response,
            'phase': current_phase,
            'phase_transition': phase_transition['should_transition'],
            'new_phase': phase_transition['new_phase'] if phase_transition['should_transition'] else current_phase,
            'context': extracted_context,
            'tool_results': tool_results,
            'session_id': session_id
        }
    
    async def _execute_phase_tools(
        self,
        session_id: str,
        current_phase: ConversationPhase,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tools based on conversation phase and context.
        
        Args:
            session_id: Session identifier
            current_phase: Current conversation phase
            context: Extracted context
            
        Returns:
            Tool execution results
        """
        if not self.tool_orchestrator:
            return {}
        
        tool_results = {}
        
        try:
            if current_phase == ConversationPhase.INITIAL:
                # Execute genre exploration searches if genres are mentioned
                if 'mentioned_genres' in context and context['mentioned_genres']:
                    genre_results = await self.tool_orchestrator.execute_genre_exploration_searches(
                        context['mentioned_genres'], context, session_id
                    )
                    tool_results['genre_research'] = genre_results
            
            elif current_phase == ConversationPhase.GENRE_EXPLORATION:
                # Execute genre exploration searches
                if 'mentioned_genres' in context:
                    genre_results = await self.tool_orchestrator.execute_genre_exploration_searches(
                        context['mentioned_genres'], context, session_id
                    )
                    tool_results['genre_research'] = genre_results
            
            elif current_phase == ConversationPhase.CULTURAL_RESEARCH:
                # Execute cultural research searches
                if 'cultural_elements' in context:
                    cultural_results = await self.tool_orchestrator.execute_cultural_research_searches(
                        context['cultural_elements'], context, session_id
                    )
                    tool_results['cultural_research'] = cultural_results
                
                # Also search for genre cultural context if available
                if 'mentioned_genres' in context:
                    genre_cultural_results = await self.tool_orchestrator.execute_genre_exploration_searches(
                        context['mentioned_genres'], context, session_id
                    )
                    tool_results['genre_cultural_research'] = genre_cultural_results
            
            # Process and synthesize tool results
            if tool_results:
                processed_results = await self.tool_orchestrator.process_search_results(
                    [result for results in tool_results.values() for result in results.values()]
                )
                tool_results['synthesized'] = processed_results
            
        except Exception as e:
            logger.error(f"Error executing phase tools: {e}")
            tool_results['error'] = str(e)
        
        return tool_results
    
    async def _prepare_messages_for_ai_with_tools(
        self,
        messages: List[Dict[str, Any]],
        current_phase: ConversationPhase,
        extracted_context: Dict[str, Any],
        tool_results: Dict[str, Any]
    ) -> List:
        """Prepare messages for AI model with tool results."""
        ai_messages = []
        
        # Add system message with tool context
        system_prompt = self.system_prompts[current_phase]
        
        # Add tool results to system prompt if available
        if tool_results and 'synthesized' in tool_results:
            synthesized = tool_results['synthesized']
            if synthesized.get('total_results', 0) > 0:
                system_prompt += f"\n\nI have found {synthesized['total_results']} relevant sources that may help inform our conversation. Use this information to provide more accurate and educational responses."
        
        ai_messages.append(SystemMessage(content=system_prompt))
        
        # Add conversation history
        for message in messages[-6:]:  # Last 6 messages for context
            if message['role'] == MessageRole.USER:
                ai_messages.append(HumanMessage(content=message['content']))
            elif message['role'] == MessageRole.ASSISTANT:
                ai_messages.append(AIMessage(content=message['content']))
        
        return ai_messages
    
    async def _prepare_messages_for_ai(
        self,
        messages: List[Dict[str, Any]],
        current_phase: ConversationPhase,
        extracted_context: Dict[str, Any]
    ) -> List:
        """Prepare messages for AI model."""
        ai_messages = []
        
        # Add system message
        system_prompt = self.system_prompts[current_phase]
        ai_messages.append(SystemMessage(content=system_prompt))
        
        # Add conversation history
        for message in messages[-6:]:  # Last 6 messages for context
            if message['role'] == MessageRole.USER:
                ai_messages.append(HumanMessage(content=message['content']))
            elif message['role'] == MessageRole.ASSISTANT:
                ai_messages.append(AIMessage(content=message['content']))
        
        return ai_messages
    
    async def _determine_phase_transition(
        self,
        current_phase: ConversationPhase,
        user_message: str,
        ai_response: str,
        extracted_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine if conversation should transition to next phase.
        
        Args:
            current_phase: Current conversation phase
            user_message: User's message
            ai_response: AI's response
            extracted_context: Extracted context
            
        Returns:
            Dictionary with transition decision
        """
        # Simple phase transition logic (can be enhanced with AI)
        message_lower = user_message.lower()
        
        if current_phase == ConversationPhase.INITIAL:
            # Transition to genre exploration if user shows interest in specific genres
            if any(word in message_lower for word in ['genre', 'music', 'style', 'type', 'explore', 'jazz', 'rock', 'pop', 'classical', 'blues', 'country', 'electronic', 'folk', 'reggae', 'soul', 'r&b', 'metal', 'punk', 'funk', 'disco', 'latin', 'world', 'ambient', 'experimental']):
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.GENRE_EXPLORATION
                }
        
        elif current_phase == ConversationPhase.GENRE_EXPLORATION:
            # Transition to educational clarification if genres are mentioned
            if 'mentioned_genres' in extracted_context and extracted_context['mentioned_genres']:
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.EDUCATIONAL_CLARIFICATION
                }
        
        elif current_phase == ConversationPhase.EDUCATIONAL_CLARIFICATION:
            # Transition to cultural research if educational goals are clear
            if 'theory_concepts' in extracted_context or 'has_educational_goals' in extracted_context:
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.CULTURAL_RESEARCH
                }
        
        elif current_phase == ConversationPhase.CULTURAL_RESEARCH:
            # Transition to ready for generation if cultural context is explored
            if 'cultural_elements' in extracted_context or 'mentioned_genres' in extracted_context:
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.READY_FOR_GENERATION
                }
        
        elif current_phase == ConversationPhase.READY_FOR_GENERATION:
            # Stay in ready phase until user confirms
            if 'ready_for_generation' in extracted_context:
                return {
                    'should_transition': False,
                    'new_phase': current_phase
                }
        
        return {
            'should_transition': False,
            'new_phase': current_phase
        }
    
    def _get_fallback_response(self, phase: ConversationPhase) -> str:
        """Get fallback response for a given phase."""
        fallback_responses = {
            ConversationPhase.INITIAL: "I'm here to help you create an educational music mashup! What kind of music are you interested in exploring?",
            ConversationPhase.GENRE_EXPLORATION: "That's interesting! What other genres would you like to explore or combine?",
            ConversationPhase.EDUCATIONAL_CLARIFICATION: "Great! What music theory concepts would you like to learn about?",
            ConversationPhase.CULTURAL_RESEARCH: "Excellent! Let's explore the cultural context of these genres. What aspects interest you most?",
            ConversationPhase.READY_FOR_GENERATION: "Perfect! Are you ready to create your educational music mashup?"
        }
        return fallback_responses.get(phase, "I'm here to help you with your music mashup project!")
    
    async def close(self):
        """Close the agent and cleanup resources."""
        if self.db:
            await self.db.close()
        logger.info("AsyncConversationalMashupAgent closed") 