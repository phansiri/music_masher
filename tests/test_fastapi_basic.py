import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.db import AsyncConversationDB

# Mock database for testing
@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    mock_db = AsyncMock(spec=AsyncConversationDB)
    
    # Mock conversation data
    mock_conversation = {
        "conversation_id": "test_conv_123",
        "phase": "initial",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    mock_db.get_conversation.return_value = mock_conversation
    mock_db.create_conversation.return_value = True
    mock_db.get_messages.return_value = []
    mock_db.init_db.return_value = None
    
    return mock_db

# Create test client with mocked database
@pytest.fixture
def test_client(mock_db):
    """Create a test client with mocked database."""
    with patch('app.main.get_db', return_value=mock_db):
        with TestClient(app) as client:
            yield client

def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Lit Music Mashup Conversational API"
    assert data["version"] == "2.0.0-conversational-mvp"
    assert data["status"] == "running"

def test_health_endpoint(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0-conversational-mvp"
    assert "timestamp" in data
    assert "database_status" in data

def test_create_conversation(test_client):
    """Test creating a new conversation"""
    import uuid
    conversation_data = {
        "conversation_id": f"test_conv_{uuid.uuid4().hex[:8]}",
        "metadata": {"test": "data"}
    }
    response = test_client.post("/conversations", json=conversation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_data["conversation_id"]
    assert data["phase"] == "initial"
    assert data["message_count"] == 0

def test_get_conversation(test_client):
    """Test getting a conversation"""
    import uuid
    # First create a conversation
    conversation_id = f"test_conv_{uuid.uuid4().hex[:8]}"
    conversation_data = {
        "conversation_id": conversation_id,
        "metadata": {"test": "data"}
    }
    test_client.post("/conversations", json=conversation_data)
    
    # Then get it
    response = test_client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_id
    assert data["phase"] == "initial"

def test_get_nonexistent_conversation(test_client):
    """Test getting a conversation that doesn't exist"""
    response = test_client.get("/conversations/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Conversation not found"

def test_openapi_docs(test_client):
    """Test that OpenAPI documentation is available"""
    response = test_client.get("/docs")
    assert response.status_code == 200

def test_redoc_docs(test_client):
    """Test that ReDoc documentation is available"""
    response = test_client.get("/redoc")
    assert response.status_code == 200 