import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Lit Music Mashup Conversational API"
    assert data["version"] == "2.0.0-conversational-mvp"
    assert data["status"] == "running"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0-conversational-mvp"
    assert "timestamp" in data
    assert "database_status" in data

def test_create_conversation():
    """Test creating a new conversation"""
    import uuid
    conversation_data = {
        "conversation_id": f"test_conv_{uuid.uuid4().hex[:8]}",
        "metadata": {"test": "data"}
    }
    response = client.post("/conversations", json=conversation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_data["conversation_id"]
    assert data["phase"] == "initial"
    assert data["message_count"] == 0

def test_get_conversation():
    """Test getting a conversation"""
    import uuid
    # First create a conversation
    conversation_id = f"test_conv_{uuid.uuid4().hex[:8]}"
    conversation_data = {
        "conversation_id": conversation_id,
        "metadata": {"test": "data"}
    }
    client.post("/conversations", json=conversation_data)
    
    # Then get it
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_id
    assert data["phase"] == "initial"

def test_get_nonexistent_conversation():
    """Test getting a conversation that doesn't exist"""
    response = client.get("/conversations/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Conversation not found"

def test_openapi_docs():
    """Test that OpenAPI documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_docs():
    """Test that ReDoc documentation is available"""
    response = client.get("/redoc")
    assert response.status_code == 200 