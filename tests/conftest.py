import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import httpx
from fastapi.testclient import TestClient

# Import app components (will be created in later tasks)
# from app.main import app
# from app.config import Settings
# from app.db.conversation_db import AsyncConversationDB


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_path() -> str:
    """Create a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def test_settings(temp_db_path: str) -> dict:
    """Create test settings with temporary database."""
    return {
        "DATABASE_PATH": temp_db_path,
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.1:8b-instruct",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "TAVILY_API_KEY": "test_key",
        "MAX_CONVERSATION_TURNS": 5,
        "CONVERSATION_TIMEOUT_MINUTES": 10,
        "WEB_SEARCH_MAX_RESULTS": 2,
        "WEB_SEARCH_TIMEOUT_SECONDS": 5,
        "MIN_CULTURAL_CONTEXT_LENGTH": 50,
        "MIN_THEORY_CONCEPTS": 1,
        "REQUIRED_TEACHING_NOTES": True,
    }


@pytest.fixture
async def async_app_client(test_settings: dict) -> AsyncGenerator[TestClient, None]:
    """Create an async test client for the FastAPI application."""
    # This will be implemented when the app is created
    # from app.main import create_app
    # app = create_app(test_settings)
    # async with TestClient(app) as client:
    #     yield client
    pass


@pytest.fixture
async def mock_web_search_results() -> list:
    """Mock web search results for testing."""
    return [
        {
            "title": "Jazz and Hip-Hop Fusion in Modern Music Education",
            "content": "Contemporary music education explores the connections between jazz improvisation and hip-hop rhythmic patterns. Both genres share common elements of syncopation and rhythmic complexity.",
            "url": "https://musiceducation.org/jazz-hiphop-fusion",
            "source_quality": "high"
        },
        {
            "title": "Cultural Significance of Jazz in American Music",
            "content": "Jazz emerged from African American communities in New Orleans, representing a rich cultural tradition of musical innovation and social expression.",
            "url": "https://musichistory.edu/jazz-culture",
            "source_quality": "high"
        }
    ]


@pytest.fixture
def sample_conversation_context() -> dict:
    """Sample conversation context for testing."""
    return {
        "educational_context": "high school classroom",
        "genres": ["jazz", "hip-hop"],
        "skill_level": "intermediate",
        "learning_objectives": ["improvisation", "rhythm analysis"],
        "cultural_focus": ["historical context", "modern fusion"],
        "web_research": []
    }


@pytest.fixture
def sample_mashup_request() -> dict:
    """Sample mashup generation request for testing."""
    return {
        "prompt": "Create a jazz and hip-hop mashup for intermediate students",
        "skill_level": "intermediate",
        "gathered_context": {
            "educational_context": "high school classroom",
            "genres": ["jazz", "hip-hop"],
            "learning_objectives": ["improvisation", "rhythm analysis"]
        }
    }


@pytest.fixture
def sample_chat_request() -> dict:
    """Sample chat request for testing."""
    return {
        "session_id": "test-session-123",
        "message": "I want to create a mashup for my high school music class",
        "context": {
            "educational_context": "classroom",
            "skill_level": "intermediate"
        }
    }


@pytest.fixture
async def mock_ollama_response() -> str:
    """Mock Ollama response for testing."""
    return """
{
    "title": "Jazz-Hop Fusion: Improvisation Meets Rhythm",
    "lyrics": "In the classroom where jazz meets hip-hop beat\nImprovisation flows with rhythm so sweet\nFrom New Orleans to the Bronx we connect\nCultural fusion with deep respect",
    "educational_content": {
        "theory_concepts": [
            "Syncopation in both jazz and hip-hop",
            "Improvisation techniques across genres",
            "Rhythmic complexity and polyrhythms"
        ],
        "cultural_context": "Jazz emerged from African American communities in New Orleans, while hip-hop originated in the Bronx. Both represent powerful forms of cultural expression through rhythm and innovation.",
        "teaching_notes": "Use this mashup to explore: 1) Compare swing rhythms with hip-hop beats, 2) Discuss cultural connections between genres, 3) Practice improvisation over different rhythmic patterns."
    },
    "metadata": {
        "genres_analyzed": ["jazz", "hip-hop"],
        "complexity_level": "intermediate",
        "learning_focus": ["improvisation", "rhythm analysis"],
        "cultural_elements": ["historical context", "cultural fusion"],
        "estimated_teaching_time": "45 minutes"
    }
}
"""


# Utility functions for testing
def create_test_conversation_session(session_id: str = "test-session") -> dict:
    """Create a test conversation session."""
    return {
        "session_id": session_id,
        "messages": [],
        "gathered_context": {
            "educational_context": None,
            "genres": [],
            "skill_level": None,
            "learning_objectives": [],
            "cultural_focus": [],
            "web_research": []
        },
        "tool_calls": [],
        "current_phase": "initial"
    }


def validate_educational_content(content: dict) -> bool:
    """Validate that educational content meets requirements."""
    required_fields = ["theory_concepts", "cultural_context", "teaching_notes"]
    
    # Check all required fields exist
    if not all(field in content for field in required_fields):
        return False
    
    # Check theory concepts
    if not isinstance(content["theory_concepts"], list) or len(content["theory_concepts"]) < 1:
        return False
    
    # Check cultural context length
    if len(content["cultural_context"]) < 50:
        return False
    
    # Check teaching notes
    if len(content["teaching_notes"]) < 20:
        return False
    
    return True


def validate_cultural_sensitivity(content: dict) -> bool:
    """Validate cultural sensitivity of content."""
    cultural_context = content.get("cultural_context", "").lower()
    
    # Check for respectful language
    respectful_indicators = [
        "cultural", "tradition", "community", "significance",
        "respect", "authentic", "historical", "evolution"
    ]
    
    disrespectful_indicators = [
        "primitive", "exotic", "tribal", "savage"
    ]
    
    # Should have respectful indicators
    has_respectful = any(indicator in cultural_context for indicator in respectful_indicators)
    
    # Should not have disrespectful indicators
    has_disrespectful = any(indicator in cultural_context for indicator in disrespectful_indicators)
    
    return has_respectful and not has_disrespectful
