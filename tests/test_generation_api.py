"""
API endpoint tests for the generation service.

This module tests the FastAPI endpoints related to content generation,
validation, and quality scoring.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.services.generation_service import (
    AsyncEnhancedGenerationService,
    GenerationRequest,
    ContentType,
    SkillLevel,
    ContentValidationResult,
    QualityMetrics
)


class TestGenerationAPIEndpoints:
    """Test suite for generation service API endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from app.main import app
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_generation_request_data(self):
        """Sample request data for content generation."""
        return {
            "prompt": "Create a beginner lesson about jazz music",
            "content_type": "theory_lesson",
            "skill_level": "beginner",
            "context": {
                "genre": "jazz",
                "learning_objectives": ["basic theory", "cultural context"],
                "target_audience": "music students"
            }
        }

    @pytest.fixture
    def sample_validation_request_data(self):
        """Sample request data for content validation."""
        return {
            "content": """
            Jazz Theory Lesson: Understanding Basic Concepts
            
            Jazz music is a rich cultural tradition that emerged from African American 
            communities in New Orleans. This lesson will teach you the fundamentals 
            of jazz theory including chord progressions, scales, and improvisation.
            
            Key Concepts:
            1. The ii-V-I progression
            2. Jazz scales and modes
            3. Improvisation techniques
            4. Cultural significance
            """,
            "skill_level": "intermediate"
        }

    @pytest.mark.asyncio
    async def test_generate_content_endpoint_success(self, client, sample_generation_request_data):
        """Test successful content generation endpoint."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock the generation service
            mock_service = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = "Generated jazz theory lesson content"
            mock_response.content_type = ContentType.THEORY_LESSON
            mock_response.skill_level = SkillLevel.BEGINNER
            mock_response.quality_score = 7.5
            mock_response.quality_level = "good"
            mock_response.confidence_score = 0.8
            mock_response.generation_time = 25.5
            mock_response.model_used = "mistral-small3.2:latest"
            mock_response.context_used = {"genre": "jazz"}
            mock_response.suggestions = ["Add more examples", "Include cultural context"]
            mock_response.metadata = {"word_count": 150, "complexity": "beginner"}
            
            mock_service.generate_with_context.return_value = mock_response
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.post(
                "/api/v1/generate/content",
                json=sample_generation_request_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "Generated jazz theory lesson content"
            assert data["content_type"] == "theory_lesson"
            assert data["skill_level"] == "beginner"
            assert data["quality_score"] == 7.5
            assert data["quality_level"] == "good"
            assert data["generation_time"] == 25.5
            assert data["model_used"] == "mistral-small3.2:latest"

    @pytest.mark.asyncio
    async def test_generate_content_endpoint_failure(self, client, sample_generation_request_data):
        """Test content generation endpoint failure."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock service failure
            mock_service = AsyncMock()
            mock_service.generate_with_context.side_effect = Exception("Generation failed")
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.post(
                "/api/v1/generate/content",
                json=sample_generation_request_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert error response
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Generation failed" in data["error"]

    @pytest.mark.asyncio
    async def test_validate_content_endpoint_success(self, client, sample_validation_request_data):
        """Test successful content validation endpoint."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock the validation service
            mock_service = AsyncMock()
            mock_validator = AsyncMock()
            mock_validator.validate_content.return_value = ContentValidationResult(
                is_appropriate=True,
                cultural_sensitivity_score=0.85,
                educational_value_score=0.78,
                age_appropriateness=True,
                issues=[],
                suggestions=["Add more practical examples", "Include cultural context"]
            )
            mock_service.content_validator = mock_validator
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.post(
                "/api/v1/validate/content",
                json=sample_validation_request_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert data["is_appropriate"] is True
            assert data["cultural_sensitivity_score"] == 0.85
            assert data["educational_value_score"] == 0.78
            assert data["age_appropriateness"] is True
            assert len(data["suggestions"]) == 2

    @pytest.mark.asyncio
    async def test_generation_status_endpoint(self, client):
        """Test generation service status endpoint."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock the service
            mock_service = AsyncMock()
            mock_service.health_check.return_value = {
                "status": "healthy",
                "ollama_available": True,
                "available_models": ["mistral-small3.2:latest", "llama3.1:8b:latest"],
                "stats": {
                    "total_requests": 10,
                    "successful_requests": 8,
                    "failed_requests": 2,
                    "average_generation_time": 25.5
                }
            }
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.get(
                "/api/v1/generation/status",
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["ollama_available"] is True
            assert len(data["available_models"]) == 2
            assert data["stats"]["total_requests"] == 10

    @pytest.mark.asyncio
    async def test_generation_metrics_endpoint(self, client, sample_validation_request_data):
        """Test generation quality metrics endpoint."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock the quality scorer
            mock_service = AsyncMock()
            mock_scorer = AsyncMock()
            mock_scorer.score_content.return_value = QualityMetrics(
                educational_value=7.8,
                cultural_accuracy=8.2,
                engagement_level=6.9,
                content_relevance=7.5,
                overall_score=7.6,
                confidence_level=0.82
            )
            mock_service.quality_scorer = mock_scorer
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.post(
                "/api/v1/generation/metrics",
                json=sample_validation_request_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert data["educational_value"] == 7.8
            assert data["cultural_accuracy"] == 8.2
            assert data["engagement_level"] == 6.9
            assert data["content_relevance"] == 7.5
            assert data["overall_score"] == 7.6
            assert data["confidence_level"] == 0.82

    @pytest.mark.asyncio
    async def test_available_models_endpoint(self, client):
        """Test available models endpoint."""
        with patch('app.services.generation_service.get_generation_service') as mock_get_service:
            # Mock the service
            mock_service = AsyncMock()
            mock_service.get_available_models.return_value = [
                "mistral-small3.2:latest",
                "llama3.1:8b:latest",
                "command-r:latest"
            ]
            mock_get_service.return_value = mock_service
            
            # Make request
            response = client.get(
                "/api/v1/generation/models",
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            assert len(data["models"]) == 3
            assert "mistral-small3.2:latest" in data["models"]
            assert "llama3.1:8b:latest" in data["models"]
            assert "command-r:latest" in data["models"]

    @pytest.mark.asyncio
    async def test_api_authentication(self, client, sample_generation_request_data):
        """Test API authentication."""
        # Test without API key
        response = client.post(
            "/api/v1/generate/content",
            json=sample_generation_request_data
        )
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.post(
            "/api/v1/generate/content",
            json=sample_generation_request_data,
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_request_validation(self, client):
        """Test request validation."""
        # Test missing required fields
        invalid_request = {
            "prompt": "Create a lesson",
            # Missing content_type and skill_level
        }
        
        response = client.post(
            "/api/v1/generate/content",
            json=invalid_request,
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_content_type_validation(self, client):
        """Test content type validation."""
        invalid_request = {
            "prompt": "Create a lesson",
            "content_type": "invalid_type",
            "skill_level": "beginner",
            "context": {"genre": "jazz"}
        }
        
        response = client.post(
            "/api/v1/generate/content",
            json=invalid_request,
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_skill_level_validation(self, client):
        """Test skill level validation."""
        invalid_request = {
            "prompt": "Create a lesson",
            "content_type": "theory_lesson",
            "skill_level": "invalid_level",
            "context": {"genre": "jazz"}
        }
        
        response = client.post(
            "/api/v1/generate/content",
            json=invalid_request,
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 422


class TestGenerationAPIIntegration:
    """Integration tests for generation API endpoints."""

    @pytest.mark.asyncio
    async def test_full_generation_workflow_api(self, client):
        """Test complete generation workflow through API."""
        # Test health check first
        response = client.get(
            "/api/v1/generation/status",
            headers={"X-API-Key": "test-api-key"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ollama_available", False):
                # Test content generation
                generation_request = {
                    "prompt": "Create a simple music theory lesson",
                    "content_type": "theory_lesson",
                    "skill_level": "beginner",
                    "context": {
                        "genre": "general",
                        "learning_objectives": ["basics"]
                    }
                }
                
                response = client.post(
                    "/api/v1/generate/content",
                    json=generation_request,
                    headers={"X-API-Key": "test-api-key"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "content" in data
                    assert "quality_score" in data
                    assert "generation_time" in data
                    
                    # Test content validation
                    validation_request = {
                        "content": data["content"],
                        "skill_level": "beginner"
                    }
                    
                    response = client.post(
                        "/api/v1/validate/content",
                        json=validation_request,
                        headers={"X-API-Key": "test-api-key"}
                    )
                    
                    if response.status_code == 200:
                        validation_data = response.json()
                        assert "is_appropriate" in validation_data
                        assert "cultural_sensitivity_score" in validation_data

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, client):
        """Test handling of concurrent API requests."""
        import asyncio
        
        generation_request = {
            "prompt": "Create a music lesson",
            "content_type": "theory_lesson",
            "skill_level": "beginner",
            "context": {"genre": "general"}
        }
        
        # Create multiple concurrent requests
        async def make_request():
            response = client.post(
                "/api/v1/generate/content",
                json=generation_request,
                headers={"X-API-Key": "test-api-key"}
            )
            return response.status_code
        
        # Note: This is a simplified test since TestClient is synchronous
        # In a real async environment, you'd use httpx.AsyncClient
        responses = []
        for _ in range(3):
            response = client.post(
                "/api/v1/generate/content",
                json=generation_request,
                headers={"X-API-Key": "test-api-key"}
            )
            responses.append(response.status_code)
        
        # Check that all requests were processed
        assert len(responses) == 3
        # Some may fail if Ollama is not available, but they should be processed
        assert all(status in [200, 500] for status in responses)


# Test fixtures for API testing
@pytest.fixture
def mock_generation_service():
    """Mock generation service for API testing."""
    service = AsyncMock()
    
    # Mock successful generation response
    mock_response = MagicMock()
    mock_response.content = "Generated content"
    mock_response.content_type = ContentType.THEORY_LESSON
    mock_response.skill_level = SkillLevel.BEGINNER
    mock_response.quality_score = 7.5
    mock_response.quality_level = "good"
    mock_response.confidence_score = 0.8
    mock_response.generation_time = 25.5
    mock_response.model_used = "mistral-small3.2:latest"
    mock_response.context_used = {"genre": "jazz"}
    mock_response.suggestions = ["Add examples"]
    mock_response.metadata = {"word_count": 100}
    
    service.generate_with_context.return_value = mock_response
    
    # Mock health check
    service.health_check.return_value = {
        "status": "healthy",
        "ollama_available": True,
        "available_models": ["mistral-small3.2:latest"],
        "stats": {"total_requests": 5}
    }
    
    # Mock model listing
    service.get_available_models.return_value = ["mistral-small3.2:latest"]
    
    return service


@pytest.fixture
def mock_validation_service():
    """Mock validation service for API testing."""
    service = AsyncMock()
    
    # Mock content validator
    mock_validator = AsyncMock()
    mock_validator.validate_content.return_value = ContentValidationResult(
        is_appropriate=True,
        cultural_sensitivity_score=0.85,
        educational_value_score=0.78,
        age_appropriateness=True,
        issues=[],
        suggestions=["Add examples"]
    )
    service.content_validator = mock_validator
    
    # Mock quality scorer
    mock_scorer = AsyncMock()
    mock_scorer.score_content.return_value = QualityMetrics(
        educational_value=7.8,
        cultural_accuracy=8.2,
        engagement_level=6.9,
        content_relevance=7.5,
        overall_score=7.6,
        confidence_level=0.82
    )
    service.quality_scorer = mock_scorer
    
    return service
