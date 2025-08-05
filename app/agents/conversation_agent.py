"""
Async conversational AI agent for the Lit Music Mashup platform.

This module provides the AsyncConversationalMashupAgent class for managing
conversations with phase-based progression and context extraction.
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


class SkillLevel(str, Enum):
    """Educational skill levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AsyncConversationalMashupAgent:
    """
    Async conversational AI agent with phase-based conversation management.
    
    This agent handles educational music mashup conversations with context
    extraction and state management across different conversation phases.
    """
    
    def __init__(
        self, 
        model_name: str = "llama3.1:8b-instruct",
        model_type: str = "ollama",  # "ollama" or "openai"
        tavily_api_key: Optional[str] = None,
        db_path: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the conversational agent.
        
        Args:
            model_name: Name of the AI model to use
            model_type: Type of model ("ollama" or "openai")
            tavily_api_key: Optional Tavily API key for web search
            db_path: Path to the database
            openai_api_key: Optional OpenAI API key
        """
        self.model_name = model_name
        self.model_type = model_type
        self.tavily_api_key = tavily_api_key
        self.openai_api_key = openai_api_key
        
        # Initialize database
        settings = get_settings()
        self.db = AsyncConversationDB(db_path or settings.DATABASE_PATH)
        
        # Initialize AI model
        self._initialize_model()
        
        # System prompts for different phases
        self._initialize_system_prompts()
        
        logger.info(f"Initialized AsyncConversationalMashupAgent with {model_type} model: {model_name}")
    
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
                
            logger.info(f"Successfully initialized {self.model_type} model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise
    
    def _initialize_system_prompts(self):
        """Initialize system prompts for different conversation phases."""
        self.system_prompts = {
            ConversationPhase.INITIAL: """You are an educational AI assistant specializing in music theory and cultural music education. 
Your goal is to help users create educational music mashups that combine different genres and cultural elements.

In the initial phase, your role is to:
1. Welcome the user warmly and explain your capabilities
2. Ask about their educational goals and target audience
3. Gather basic information about their interests in music
4. Set expectations for the conversation flow

Be encouraging, educational, and culturally sensitive. Ask open-ended questions to understand their needs.""",

            ConversationPhase.GENRE_EXPLORATION: """You are now in the genre exploration phase. Your role is to:
1. Help users identify and explore different music genres
2. Discuss the cultural origins and significance of genres
3. Understand how genres can be combined educationally
4. Gather specific genre preferences and learning objectives

Focus on educational value and cultural context. Ask about:
- What genres interest them most
- Their experience level with different genres
- Cultural elements they want to explore
- Educational goals for their students/audience""",

            ConversationPhase.EDUCATIONAL_CLARIFICATION: """You are in the educational clarification phase. Your role is to:
1. Determine the appropriate skill level (beginner, intermediate, advanced)
2. Clarify specific educational objectives
3. Understand the target audience (age, experience, context)
4. Identify key music theory concepts to include
5. Plan the educational approach and methodology

Ask specific questions about:
- Student age and experience level
- Key music theory concepts to teach
- Cultural learning objectives
- Assessment and evaluation methods""",

            ConversationPhase.CULTURAL_RESEARCH: """You are in the cultural research phase. Your role is to:
1. Deepen understanding of cultural elements in chosen genres
2. Research historical and contemporary significance
3. Identify educational opportunities for cultural learning
4. Plan how to incorporate cultural context into the mashup
5. Consider cultural sensitivity and representation

Focus on:
- Historical context of genres
- Cultural significance and meaning
- Modern interpretations and adaptations
- Educational value of cultural elements""",

            ConversationPhase.READY_FOR_GENERATION: """You are in the ready for generation phase. Your role is to:
1. Summarize all gathered information
2. Confirm the educational approach and objectives
3. Outline what will be generated
4. Set expectations for the final output
5. Ask for any final clarifications or adjustments

Provide a comprehensive summary including:
- Selected genres and their cultural significance
- Educational objectives and skill level
- Key music theory concepts to include
- Cultural learning elements
- Expected output format and content"""
        }
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return the agent's response.
        
        Args:
            session_id: Unique session identifier
            user_message: The user's message
            context: Optional additional context
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(session_id)
            current_phase = ConversationPhase(conversation.get('phase', ConversationPhase.INITIAL))
            
            # Add user message to database
            await self.db.add_message(session_id, MessageRole.USER, user_message)
            
            # Extract context from user message
            extracted_context = await self._extract_context(user_message, current_phase)
            
            # Handle conversation based on current phase
            response_data = await self._handle_conversation_phase(
                session_id, user_message, conversation, current_phase, extracted_context
            )
            
            # Add agent response to database
            await self.db.add_message(session_id, MessageRole.ASSISTANT, response_data['response'])
            
            # Update conversation phase if needed
            if response_data.get('phase_transition'):
                await self.db.update_conversation_phase(session_id, response_data['new_phase'])
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I apologize, but I encountered an error processing your message. Please try again.",
                'error': str(e),
                'phase': conversation.get('phase', ConversationPhase.INITIAL) if 'conversation' in locals() else ConversationPhase.INITIAL
            }
    
    async def _get_or_create_conversation(self, session_id: str) -> Dict[str, Any]:
        """Get existing conversation or create a new one."""
        conversation = await self.db.get_conversation(session_id)
        if not conversation:
            # Create new conversation
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
            user_message: The user's message
            current_phase: Current conversation phase
            
        Returns:
            Dictionary of extracted context
        """
        context = {
            'message': user_message,
            'phase': current_phase,
            'extracted_info': {}
        }
        
        # Extract information based on phase
        if current_phase == ConversationPhase.INITIAL:
            context['extracted_info'] = await self._extract_initial_context(user_message)
        elif current_phase == ConversationPhase.GENRE_EXPLORATION:
            context['extracted_info'] = await self._extract_genre_context(user_message)
        elif current_phase == ConversationPhase.EDUCATIONAL_CLARIFICATION:
            context['extracted_info'] = await self._extract_educational_context(user_message)
        elif current_phase == ConversationPhase.CULTURAL_RESEARCH:
            context['extracted_info'] = await self._extract_cultural_context(user_message)
        elif current_phase == ConversationPhase.READY_FOR_GENERATION:
            context['extracted_info'] = await self._extract_generation_context(user_message)
        
        return context
    
    async def _extract_initial_context(self, message: str) -> Dict[str, Any]:
        """Extract context from initial phase messages."""
        context = {
            'educational_goals': [],
            'target_audience': None,
            'music_interests': [],
            'experience_level': None
        }
        
        # Simple keyword-based extraction (can be enhanced with AI)
        message_lower = message.lower()
        
        # Extract educational goals
        if any(word in message_lower for word in ['teach', 'learn', 'education', 'class', 'student']):
            context['educational_goals'].append('teaching')
        
        if any(word in message_lower for word in ['theory', 'concept', 'fundamental']):
            context['educational_goals'].append('music_theory')
        
        # Extract target audience
        if any(word in message_lower for word in ['high school', 'college', 'university']):
            context['target_audience'] = 'higher_education'
        elif any(word in message_lower for word in ['elementary', 'middle school', 'kids']):
            context['target_audience'] = 'k12'
        
        # Extract music interests
        genres = ['jazz', 'classical', 'rock', 'pop', 'hip hop', 'blues', 'folk', 'electronic']
        for genre in genres:
            if genre in message_lower:
                context['music_interests'].append(genre)
        
        return context
    
    async def _extract_genre_context(self, message: str) -> Dict[str, Any]:
        """Extract genre-related context from messages."""
        context = {
            'mentioned_genres': [],
            'cultural_elements': [],
            'combination_ideas': []
        }
        
        message_lower = message.lower()
        
        # Extract mentioned genres
        genres = ['jazz', 'classical', 'rock', 'pop', 'hip hop', 'blues', 'folk', 'electronic', 
                 'reggae', 'country', 'r&b', 'soul', 'funk', 'disco', 'punk', 'metal']
        
        for genre in genres:
            if genre in message_lower:
                context['mentioned_genres'].append(genre)
        
        # Extract cultural elements
        cultural_keywords = ['culture', 'tradition', 'heritage', 'history', 'origin', 'background']
        for keyword in cultural_keywords:
            if keyword in message_lower:
                context['cultural_elements'].append(keyword)
        
        return context
    
    async def _extract_educational_context(self, message: str) -> Dict[str, Any]:
        """Extract educational context from messages."""
        context = {
            'skill_level': None,
            'theory_concepts': [],
            'learning_objectives': [],
            'assessment_methods': []
        }
        
        message_lower = message.lower()
        
        # Determine skill level
        if any(word in message_lower for word in ['beginner', 'basic', 'start', 'new']):
            context['skill_level'] = SkillLevel.BEGINNER
        elif any(word in message_lower for word in ['intermediate', 'moderate', 'some']):
            context['skill_level'] = SkillLevel.INTERMEDIATE
        elif any(word in message_lower for word in ['advanced', 'expert', 'complex']):
            context['skill_level'] = SkillLevel.ADVANCED
        
        # Extract theory concepts
        theory_concepts = ['rhythm', 'melody', 'harmony', 'chord', 'scale', 'tempo', 'dynamics']
        for concept in theory_concepts:
            if concept in message_lower:
                context['theory_concepts'].append(concept)
        
        return context
    
    async def _extract_cultural_context(self, message: str) -> Dict[str, Any]:
        """Extract cultural context from messages."""
        context = {
            'cultural_significance': [],
            'historical_elements': [],
            'modern_interpretations': []
        }
        
        message_lower = message.lower()
        
        # Extract cultural significance
        cultural_keywords = ['tradition', 'heritage', 'culture', 'history', 'origin']
        for keyword in cultural_keywords:
            if keyword in message_lower:
                context['cultural_significance'].append(keyword)
        
        return context
    
    async def _extract_generation_context(self, message: str) -> Dict[str, Any]:
        """Extract context for generation phase."""
        context = {
            'confirmation': False,
            'adjustments': [],
            'final_preferences': []
        }
        
        message_lower = message.lower()
        
        # Check for confirmation
        if any(word in message_lower for word in ['yes', 'confirm', 'proceed', 'ready']):
            context['confirmation'] = True
        
        return context
    
    async def _handle_conversation_phase(
        self,
        session_id: str,
        user_message: str,
        conversation: Dict[str, Any],
        current_phase: ConversationPhase,
        extracted_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle conversation based on current phase.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            conversation: Current conversation data
            current_phase: Current conversation phase
            extracted_context: Extracted context from user message
            
        Returns:
            Response data with potential phase transition
        """
        # Get conversation history
        messages = await self.db.get_messages(session_id, limit=10)
        
        # Prepare messages for AI model
        ai_messages = await self._prepare_messages_for_ai(
            messages, current_phase, extracted_context
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
            'session_id': session_id
        }
    
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
            if any(word in message_lower for word in ['genre', 'music', 'style', 'type']):
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.GENRE_EXPLORATION
                }
        
        elif current_phase == ConversationPhase.GENRE_EXPLORATION:
            # Transition to educational clarification if user mentions educational goals
            if any(word in message_lower for word in ['teach', 'learn', 'education', 'student', 'class']):
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.EDUCATIONAL_CLARIFICATION
                }
        
        elif current_phase == ConversationPhase.EDUCATIONAL_CLARIFICATION:
            # Transition to cultural research if user mentions cultural elements
            if any(word in message_lower for word in ['culture', 'tradition', 'history', 'background']):
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.CULTURAL_RESEARCH
                }
        
        elif current_phase == ConversationPhase.CULTURAL_RESEARCH:
            # Transition to ready phase if user seems ready
            if any(word in message_lower for word in ['ready', 'proceed', 'generate', 'create']):
                return {
                    'should_transition': True,
                    'new_phase': ConversationPhase.READY_FOR_GENERATION
                }
        
        # No transition
        return {
            'should_transition': False,
            'new_phase': current_phase
        }
    
    def _get_fallback_response(self, phase: ConversationPhase) -> str:
        """Get fallback response if AI model fails."""
        fallback_responses = {
            ConversationPhase.INITIAL: "I'd love to help you create an educational music mashup! Could you tell me a bit about your goals and what kind of music interests you?",
            ConversationPhase.GENRE_EXPLORATION: "That's interesting! What genres of music are you most interested in exploring? We can combine different styles to create something educational and engaging.",
            ConversationPhase.EDUCATIONAL_CLARIFICATION: "Great! What's the skill level of your students or audience? Are they beginners, intermediate, or more advanced?",
            ConversationPhase.CULTURAL_RESEARCH: "Excellent! What cultural elements would you like to explore? We can research the history and significance of different musical traditions.",
            ConversationPhase.READY_FOR_GENERATION: "Perfect! Are you ready to proceed with creating the educational mashup based on what we've discussed?"
        }
        
        return fallback_responses.get(phase, "I'm here to help you create an educational music mashup!")
    
    async def close(self):
        """Close the agent and clean up resources."""
        if hasattr(self, 'db'):
            await self.db.close()
        logger.info("AsyncConversationalMashupAgent closed") 