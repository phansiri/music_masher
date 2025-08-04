"""
Database enums for the Lit Music Mashup AI platform.

This module contains enums used throughout the database layer
for conversation management and data consistency.
"""

from enum import Enum


class ConversationPhase(str, Enum):
    """
    Conversation phases for the educational music generation process.
    
    These phases represent the different stages of a conversation
    as the AI guides users through music theory and cultural exploration.
    """
    
    INITIAL = "initial"
    """Initial conversation state when user first starts."""
    
    GENRE_EXPLORATION = "genre_exploration"
    """Exploring different music genres and styles."""
    
    EDUCATIONAL_CLARIFICATION = "educational_clarification"
    """Clarifying educational goals and learning objectives."""
    
    CULTURAL_RESEARCH = "cultural_research"
    """Researching cultural context and historical background."""
    
    READY_FOR_GENERATION = "ready_for_generation"
    """Ready to generate the final music mashup."""
    
    GENERATION_COMPLETE = "generation_complete"
    """Mashup generation has been completed."""
    
    ERROR = "error"
    """Error state when something goes wrong."""
    
    @classmethod
    def get_initial_phase(cls) -> "ConversationPhase":
        """Get the initial conversation phase."""
        return cls.INITIAL
    
    @classmethod
    def get_final_phase(cls) -> "ConversationPhase":
        """Get the final conversation phase."""
        return cls.GENERATION_COMPLETE
    
    @classmethod
    def is_terminal(cls, phase: "ConversationPhase") -> bool:
        """Check if a phase is terminal (conversation ends here)."""
        return phase in [cls.GENERATION_COMPLETE, cls.ERROR]
    
    @classmethod
    def get_next_phase(cls, current_phase: "ConversationPhase") -> "ConversationPhase":
        """Get the next logical phase in the conversation flow."""
        phase_flow = {
            cls.INITIAL: cls.GENRE_EXPLORATION,
            cls.GENRE_EXPLORATION: cls.EDUCATIONAL_CLARIFICATION,
            cls.EDUCATIONAL_CLARIFICATION: cls.CULTURAL_RESEARCH,
            cls.CULTURAL_RESEARCH: cls.READY_FOR_GENERATION,
            cls.READY_FOR_GENERATION: cls.GENERATION_COMPLETE,
        }
        return phase_flow.get(current_phase, cls.ERROR)


class MessageRole(str, Enum):
    """
    Message roles for conversation tracking.
    
    These roles identify the source and type of messages
    in the conversation history.
    """
    
    USER = "user"
    """Message from the user."""
    
    ASSISTANT = "assistant"
    """Message from the AI assistant."""
    
    SYSTEM = "system"
    """System message (instructions, context, etc.)."""
    
    TOOL = "tool"
    """Message from a tool (web search, etc.)."""
    
    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if a role string is valid."""
        return role in [member.value for member in cls]


class ToolCallType(str, Enum):
    """
    Types of tool calls for tracking web search and other operations.
    
    These types help categorize different tool operations
    for analytics and debugging purposes.
    """
    
    WEB_SEARCH = "web_search"
    """Web search operation."""
    
    MUSIC_ANALYSIS = "music_analysis"
    """Music analysis operation."""
    
    CULTURAL_RESEARCH = "cultural_research"
    """Cultural research operation."""
    
    THEORY_EXPLANATION = "theory_explanation"
    """Music theory explanation."""
    
    @classmethod
    def is_valid_type(cls, tool_type: str) -> bool:
        """Check if a tool type string is valid."""
        return tool_type in [member.value for member in cls] 