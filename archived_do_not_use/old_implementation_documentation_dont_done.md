```

## 5. API Implementation

### 5.1 Core API Endpoints (app/api/v1/endpoints/mashup.py)
```python
"""
Educational mashup generation API endpoints
Core functionality for Lit Music Mashup platform
"""

import logging
from typing import Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.models import (
    EducationalMashupRequest, 
    EducationalMashupResult, 
    APIResponse
)
from app.core.workflow import EducationalWorkflowOrchestrator
from app.db.database import get_db
from app.db.repositories.session import SessionRepository
from app.services.mashup_service import MashupGenerationService
from app.services.monitoring_service import MonitoringService
from app.core.security import get_current_user, verify_educational_permissions
from app.utils.validation import validate_educational# Lit Music Mashup - Implementation Documentation

## 1. Executive Summary

This document provides comprehensive implementation guidance for the Lit Music Mashup educational AI platform, building upon the refined PRD and prompt structure to create a production-ready system. The implementation prioritizes educational value, privacy compliance, and scalable architecture while maintaining development velocity and code quality.

## 2. Technical Architecture Overview

### 2.1 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                     Lit Music Mashup Architecture                │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Future)           │  API Gateway (FastAPI)            │
│  ┌─────────────────────────┐ │  ┌─────────────┬─────────────────┐ │
│  │ Teacher Dashboard       │ │  │ Auth        │ Rate Limiting   │ │
│  │ Student Interface       │ │  │ Validation  │ Request Queue   │ │
│  │ Collaboration UI        │ │  └─────────────┴─────────────────┘ │
│  └─────────────────────────┘ │                                   │
├─────────────────────────────────────────────────────────────────┤
│                    Core Application Layer                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              LangGraph Agent Orchestration                  │ │
│  │  ┌───────────────┬───────────────┬───────────────────────┐  │ │
│  │  │ Educational   │ Genre         │ Hook Generator        │  │ │
│  │  │ Context Agent │ Analyzer      │ Agent                 │  │ │
│  │  ├───────────────┼───────────────┼───────────────────────┤  │ │
│  │  │ Lyrics        │ Theory        │ Collaborative         │  │ │
│  │  │ Composer      │ Integration   │ Session Manager       │  │ │
│  │  └───────────────┴───────────────┴───────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      AI Model Layer                              │
│  ┌─────────────────────────┐ │  ┌─────────────────────────────┐ │
│  │    Local Models         │ │  │     Cloud Models            │ │
│  │  ┌─────────────────────┐ │ │  │  ┌─────────────────────────┐ │ │
│  │  │ Ollama Server       │ │ │  │  │ OpenAI API             │ │ │
│  │  │ - Llama 3.1-8B      │ │ │  │  │ Claude API             │ │ │
│  │  │ - Embedding Models  │ │ │  │  │ Other Providers        │ │ │
│  │  └─────────────────────┘ │ │  │  └─────────────────────────┘ │ │
│  └─────────────────────────┘ │  └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     Data & Storage Layer                         │
│  ┌─────────────────────────┐ │  ┌─────────────────────────────┐ │
│  │ Educational Database    │ │  │ Session State Store         │ │
│  │ (PostgreSQL)            │ │  │ (Redis/Memory)              │ │
│  │ - User Profiles         │ │  │ - Active Sessions           │ │
│  │ - Learning Progress     │ │  │ - Collaboration State       │ │
│  │ - Generated Content     │ │  │ - Real-time Data            │ │
│  └─────────────────────────┘ │  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Technology Stack

#### Backend Infrastructure
- **Project Management**: UV (Python package and dependency management)
- **API Framework**: FastAPI with async support
- **AI Orchestration**: LangGraph for multi-agent workflows
- **Database**: PostgreSQL for persistent data, Redis for session state
- **Model Serving**: Ollama for local models, API clients for cloud models
- **Real-time Communication**: WebSockets for collaborative features

#### Python Dependencies (pyproject.toml)
```toml
[project]
name = "lit-music-mashup"
version = "0.1.0"
description = "Educational AI Music Mashup Platform"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "langchain>=0.1.0",
    "langgraph>=0.0.40",
    "langchain-ollama>=0.1.0",
    "langchain-openai>=0.1.0",
    "pydantic>=2.5.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "redis>=5.0.0",
    "websockets>=12.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-dotenv>=1.0.0",
    "httpx>=0.25.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.9.0",
    "isort>=5.12.0",
    "mypy>=1.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=4.1.0",
    "pre-commit>=3.5.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
strict = true
```

## 3. Project Structure and Organization

### 3.1 Directory Structure
```
lit_music_mashup/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── api/                    # API routes and endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mashup.py           # Mashup generation endpoints
│   │   │   │   ├── collaboration.py   # Collaborative session endpoints
│   │   │   │   ├── education.py       # Educational features endpoints
│   │   │   │   └── health.py          # Health check endpoints
│   │   │   └── api.py          # API router configuration
│   │   └── websocket/          # WebSocket handlers
│   │       ├── __init__.py
│   │       └── collaboration.py
│   │
│   ├── agents/                 # LangGraph AI agents
│   │   ├── __init__.py
│   │   ├── base.py            # Base agent class
│   │   ├── educational_context.py
│   │   ├── genre_analyzer.py
│   │   ├── hook_generator.py
│   │   ├── lyrics_composer.py
│   │   ├── theory_integrator.py
│   │   └── session_manager.py
│   │
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── workflow.py        # LangGraph workflow orchestration
│   │   ├── models.py          # Pydantic models and schemas
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── security.py        # Authentication and authorization
│   │
│   ├── db/                    # Database layer
│   │   ├── __init__.py
│   │   ├── database.py        # Database connection and session management
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── mashup.py
│   │   └── migrations/        # Alembic migrations
│   │       └── versions/
│   │
│   ├── services/              # Business service layer
│   │   ├── __init__.py
│   │   ├── model_service.py   # AI model management
│   │   ├── mashup_service.py  # Mashup generation service
│   │   ├── collaboration_service.py # Collaborative features
│   │   ├── educational_service.py   # Educational content management
│   │   └── monitoring_service.py    # Performance monitoring
│   │
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── logging.py         # Logging configuration
│   │   ├── validation.py      # Content validation utilities
│   │   └── privacy.py         # Privacy compliance utilities
│   │
│   └── templates/             # Prompt templates
│       ├── __init__.py
│       ├── educational_context.py
│       ├── genre_analysis.py
│       ├── hook_generation.py
│       ├── lyrics_composition.py
│       ├── theory_integration.py
│       └── collaboration.py
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── test_agents/          # Agent tests
│   ├── test_api/             # API endpoint tests
│   ├── test_services/        # Service layer tests
│   └── test_integration/     # Integration tests
│
├── scripts/                  # Utility scripts
│   ├── setup_dev.py         # Development environment setup
│   ├── migrate.py           # Database migration runner
│   └── seed_data.py         # Test data seeding
│
└── docs/                    # Documentation
    ├── api.md              # API documentation
    ├── deployment.md       # Deployment guide
    └── development.md      # Development guide
```

## 4. Core Implementation Components

### 4.1 FastAPI Application Setup (app/main.py)
```python
"""
Lit Music Mashup - Main FastAPI Application
Educational AI Music Generation Platform
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.v1.api import api_router
from app.api.websocket.collaboration import websocket_router
from app.config import settings
from app.core.exceptions import LitMusicMashupException
from app.db.database import init_db
from app.services.model_service import ModelService
from app.utils.logging import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management with proper startup/shutdown"""
    
    logger.info("Starting Lit Music Mashup application...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Initialize AI model service
    try:
        model_service = ModelService()
        await model_service.initialize()
        app.state.model_service = model_service
        logger.info("AI model service initialized successfully")
    except Exception as e:
        logger.error(f"AI model service initialization failed: {e}")
        raise
    
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    
    if hasattr(app.state, 'model_service'):
        await app.state.model_service.cleanup()
        logger.info("AI model service cleaned up")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Lit Music Mashup API",
    description="Educational AI Music Generation Platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware for educational environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(LitMusicMashupException)
async def lit_music_mashup_exception_handler(
    request: Request, 
    exc: LitMusicMashupException
) -> JSONResponse:
    """Handle custom application exceptions"""
    
    logger.error(f"Application error: {exc.message}", extra={
        'error_code': exc.error_code,
        'request_url': str(request.url)
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle internal server errors with educational context"""
    
    logger.error(f"Internal server error: {str(exc)}", extra={
        'request_url': str(request.url),
        'exception_type': type(exc).__name__
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal error occurred. The educational session may need to be restarted.",
            "support_message": "Please contact your instructor or system administrator."
        }
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")


@app.get("/")
async def root():
    """Root endpoint with educational platform information"""
    return {
        "message": "Lit Music Mashup - Educational AI Music Generation Platform",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs" if settings.ENVIRONMENT == "development" else "Contact administrator"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment"""
    
    try:
        # Check model service health
        model_service = getattr(app.state, 'model_service', None)
        model_status = "healthy" if model_service and await model_service.health_check() else "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",  # This would be dynamic
            "services": {
                "api": "healthy",
                "models": model_status,
                "database": "healthy"  # This would be checked dynamically
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
```

### 4.2 Configuration Management (app/config.py)
```python
"""
Configuration management for Lit Music Mashup
Handles environment variables and application settings
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with educational environment considerations"""
    
    # Basic application settings
    PROJECT_NAME: str = "Lit Music Mashup"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Database configuration
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis configuration for session state
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DECODE_RESPONSES: bool = True
    
    # AI Model configuration
    LOCAL_MODEL_ENABLED: bool = Field(default=True, env="LOCAL_MODEL_ENABLED")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    DEFAULT_LOCAL_MODEL: str = Field(default="llama3.1:8b-instruct", env="DEFAULT_LOCAL_MODEL")
    
    # Cloud model configuration (optional)
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    CLOUD_MODELS_ENABLED: bool = Field(default=False, env="CLOUD_MODELS_ENABLED")
    
    # Educational privacy settings
    FERPA_COMPLIANCE: bool = Field(default=True, env="FERPA_COMPLIANCE")
    COPPA_COMPLIANCE: bool = Field(default=True, env="COPPA_COMPLIANCE")
    DATA_RETENTION_DAYS: int = Field(default=2555, env="DATA_RETENTION_DAYS")  # 7 years
    STUDENT_DATA_ENCRYPTION: bool = Field(default=True, env="STUDENT_DATA_ENCRYPTION")
    
    # Session and collaboration settings
    MAX_SESSION_DURATION_HOURS: int = Field(default=4, env="MAX_SESSION_DURATION_HOURS")
    MAX_CONCURRENT_SESSIONS: int = Field(default=100, env="MAX_CONCURRENT_SESSIONS")
    MAX_PARTICIPANTS_PER_SESSION: int = Field(default=30, env="MAX_PARTICIPANTS_PER_SESSION")
    
    # Security settings
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 8 hours for classroom use
    ALGORITHM: str = "HS256"
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Educational content validation
    ENABLE_CONTENT_VALIDATION: bool = Field(default=True, env="ENABLE_CONTENT_VALIDATION")
    CULTURAL_SENSITIVITY_THRESHOLD: float = Field(default=0.8, env="CULTURAL_SENSITIVITY_THRESHOLD")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")
        return v
    
    @validator("DATA_RETENTION_DAYS")
    def validate_retention_period(cls, v):
        if v < 365:  # Minimum 1 year for educational records
            raise ValueError("DATA_RETENTION_DAYS must be at least 365 for educational compliance")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Educational environment specific configurations
class EducationalEnvironmentConfig:
    """Specialized configuration for educational environments"""
    
    @staticmethod
    def get_institutional_config(institution_type: str) -> dict:
        """Get configuration optimized for different institution types"""
        
        configs = {
            "k12": {
                "coppa_compliance": True,
                "enhanced_privacy": True,
                "content_filtering": "strict",
                "max_session_duration": 45,  # minutes
                "parental_consent_required": True
            },
            "higher_ed": {
                "ferpa_compliance": True,
                "research_features": True,
                "extended_sessions": True,
                "max_session_duration": 180,  # minutes
                "advanced_analytics": True
            },
            "professional": {
                "enterprise_features": True,
                "advanced_collaboration": True,
                "api_access": True,
                "custom_branding": True,
                "priority_support": True
            }
        }
        
        return configs.get(institution_type, configs["higher_ed"])
    
    @staticmethod
    def get_privacy_config(compliance_level: str) -> dict:
        """Get privacy configuration based on compliance requirements"""
        
        privacy_configs = {
            "strict": {
                "local_models_only": True,
                "no_cloud_storage": True,
                "enhanced_encryption": True,
                "audit_logging": "detailed",
                "data_minimization": True
            },
            "standard": {
                "hybrid_models": True,
                "secure_cloud_storage": True,
                "standard_encryption": True,
                "audit_logging": "standard",
                "gdpr_compliance": True
            },
            "relaxed": {
                "cloud_models_preferred": True,
                "cloud_storage": True,
                "basic_encryption": True,
                "audit_logging": "basic",
                "performance_optimized": True
            }
        }
        
        return privacy_configs.get(compliance_level, privacy_configs["standard"])


# Initialize educational environment configuration
educational_config = EducationalEnvironmentConfig()
```

### 4.3 LangGraph Workflow Implementation (app/core/workflow.py)
```python
"""
LangGraph workflow orchestration for educational music mashup generation
Implements the complete educational agent pipeline
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphError

from app.core.models import (
    AgentState, 
    EducationalMashupRequest, 
    EducationalMashupResult,
    AgentError
)
from app.agents.educational_context import EducationalContextAgent
from app.agents.genre_analyzer import GenreAnalyzerAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.lyrics_composer import LyricsComposerAgent
from app.agents.theory_integrator import TheoryIntegratorAgent
from app.agents.session_manager import CollaborativeSessionManagerAgent
from app.core.exceptions import WorkflowException, AgentException
from app.services.monitoring_service import MonitoringService


logger = logging.getLogger(__name__)


class EducationalWorkflowOrchestrator:
    """Main orchestrator for educational music mashup generation workflow"""
    
    def __init__(self, monitoring_service: MonitoringService):
        self.monitoring_service = monitoring_service
        self.workflow_graph = None
        self.checkpointer = MemorySaver()  # TODO: Replace with PostgreSQL checkpointer for production
        
        # Initialize agents
        self.agents = {
            "educational_context": EducationalContextAgent(),
            "genre_analyzer": GenreAnalyzerAgent(),
            "hook_generator": HookGeneratorAgent(),
            "lyrics_composer": LyricsComposerAgent(),
            "theory_integrator": TheoryIntegratorAgent(),
            "session_manager": CollaborativeSessionManagerAgent()
        }
        
        self._build_workflow()
    
    def _build_workflow(self) -> None:
        """Build the complete educational workflow using LangGraph"""
        
        logger.info("Building educational workflow graph")
        
        # Create StateGraph with educational state model
        workflow = StateGraph(AgentState)
        
        # Add all educational agent nodes
        workflow.add_node("educational_context", self._educational_context_node)
        workflow.add_node("genre_analyzer", self._genre_analyzer_node)
        workflow.add_node("hook_generator", self._hook_generator_node)
        workflow.add_node("lyrics_composer", self._lyrics_composer_node)
        workflow.add_node("theory_integrator", self._theory_integrator_node)
        workflow.add_node("session_manager", self._session_manager_node)
        workflow.add_node("quality_validator", self._quality_validator_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define educational workflow progression
        workflow.set_entry_point("educational_context")
        
        # Sequential educational pipeline
        workflow.add_edge("educational_context", "genre_analyzer")
        workflow.add_edge("genre_analyzer", "hook_generator")
        workflow.add_edge("hook_generator", "lyrics_composer")
        workflow.add_edge("lyrics_composer", "theory_integrator")
        workflow.add_edge("theory_integrator", "quality_validator")
        
        # Conditional routing after quality validation
        workflow.add_conditional_edges(
            "quality_validator",
            self._route_after_validation,
            {
                "collaboration": "session_manager",
                "complete": END,
                "retry": "genre_analyzer",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("session_manager", END)
        workflow.add_edge("error_handler", END)
        
        # Compile workflow with checkpointing
        self.workflow_graph = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["session_manager"],  # Allow teacher intervention
            debug=True
        )
        
        logger.info("Educational workflow graph built successfully")
    
    async def execute_educational_workflow(
        self, 
        request: EducationalMashupRequest,
        session_id: str
    ) -> EducationalMashupResult:
        """Execute the complete educational workflow"""
        
        start_time = datetime.now()
        
        logger.info(f"Starting educational workflow for session {session_id}")
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            current_agent=None,
            user_request=request,
            session_id=session_id,
            iteration_count=0,
            errors=[]
        )
        
        try:
            # Execute workflow
            config = {
                "configurable": {
                    "thread_id": session_id,
                    "educational_mode": True,
                    "privacy_level": "high" if request.educational_context == "classroom" else "medium"
                }
            }
            
            # Monitor workflow execution
            self.monitoring_service.start_workflow_monitoring(session_id, request)
            
            # Run the educational workflow
            final_state = await self.workflow_graph.ainvoke(initial_state, config=config)
            
            # Validate final results
            if final_state.errors:
                logger.warning(f"Workflow completed with errors: {final_state.errors}")
            
            # Build final educational result
            result = self._build_educational_result(final_state)
            
            # Record metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.monitoring_service.record_workflow_completion(
                session_id, 
                execution_time, 
                len(final_state.errors) == 0
            )
            
            logger.info(f"Educational workflow completed for session {session_id} in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Educational workflow failed for session {session_id}: {e}")
            
            # Record failure metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.monitoring_service.record_workflow_failure(session_id, str(e), execution_time)
            
            raise WorkflowException(
                message=f"Educational workflow execution failed: {str(e)}",
                session_id=session_id,
                execution_time=execution_time
            )
    
    # Agent Node Implementations
    
    async def _educational_context_node(self, state: AgentState) -> AgentState:
        """Execute educational context analysis agent"""
        
        try:
            logger.debug(f"Executing educational context agent for session {state.session_id}")
            
            state.current_agent = "educational_context"
            result = await self.agents["educational_context"].execute(state)
            
            state.educational_context = result
            state.messages.append("Educational context analysis completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "educational_context")
    
    async def _genre_analyzer_node(self, state: AgentState) -> AgentState:
        """Execute genre analyzer agent with educational focus"""
        
        try:
            logger.debug(f"Executing genre analyzer agent for session {state.session_id}")
            
            state.current_agent = "genre_analyzer"
            result = await self.agents["genre_analyzer"].execute(state)
            
            state.genre_analysis = result
            state.messages.append("Educational genre analysis completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "genre_analyzer")
    
    async def _hook_generator_node(self, state: AgentState) -> AgentState:
        """Execute educational hook generator agent"""
        
        try:
            logger.debug(f"Executing hook generator agent for session {state.session_id}")
            
            state.current_agent = "hook_generator"
            result = await self.agents["hook_generator"].execute(state)
            
            state.hook_options = result.hook_options
            state.messages.append("Educational hook generation completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "hook_generator")
    
    async def _lyrics_composer_node(self, state: AgentState) -> AgentState:
        """Execute educational lyrics composer agent"""
        
        try:
            logger.debug(f"Executing lyrics composer agent for session {state.session_id}")
            
            state.current_agent = "lyrics_composer"
            result = await self.agents["lyrics_composer"].execute(state)
            
            state.final_composition = result
            state.messages.append("Educational lyrics composition completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "lyrics_composer")
    
    async def _theory_integrator_node(self, state: AgentState) -> AgentState:
        """Execute theory integration agent"""
        
        try:
            logger.debug(f"Executing theory integrator agent for session {state.session_id}")
            
            state.current_agent = "theory_integrator"
            result = await self.agents["theory_integrator"].execute(state)
            
            state.theory_integration = result
            state.messages.append("Music theory integration completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "theory_integrator")
    
    async def _session_manager_node(self, state: AgentState) -> AgentState:
        """Execute collaborative session manager agent"""
        
        try:
            logger.debug(f"Executing session manager agent for session {state.session_id}")
            
            state.current_agent = "session_manager"
            result = await self.agents["session_manager"].execute(state)
            
            state.collaboration_state = result
            state.messages.append("Collaborative session management completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "session_manager")
    
    async def _quality_validator_node(self, state: AgentState) -> AgentState:
        """Validate educational content quality"""
        
        try:
            logger.debug(f"Validating educational content quality for session {state.session_id}")
            
            state.current_agent = "quality_validator"
            
            # Perform comprehensive quality validation
            validation_results = await self._validate_educational_quality(state)
            
            if validation_results["overall_quality"] < 0.7:
                logger.warning(f"Quality validation failed for session {state.session_id}")
                state.errors.append({
                    "agent": "quality_validator",
                    "type": "quality_validation_failed",
                    "message": "Educational content quality below threshold",
                    "details": validation_results
                })
            
            state.messages.append("Educational quality validation completed")
            
            return state
            
        except Exception as e:
            return self._handle_agent_error(state, e, "quality_validator")
    
    async def _error_handler_node(self, state: AgentState) -> AgentState:
        """Handle workflow errors and provide fallback content"""
        
        logger.info(f"Handling workflow errors for session {state.session_id}")
        
        state.current_agent = "error_handler"
        
        # Attempt to provide fallback educational content
        try:
            fallback_result = await self._generate_fallback_content(state)
            state.messages.append("Fallback educational content generated")
            return state
            
        except Exception as e:
            logger.error(f"Fallback content generation failed: {e}")
            state.errors.append({
                "agent": "error_handler",
                "type": "fallback_failed",
                "message": "Unable to generate fallback educational content",
                "details": str(e)
            })
            return state
    
    # Utility Methods
    
    def _route_after_validation(self, state: AgentState) -> str:
        """Route workflow after quality validation"""
        
        # Check for critical errors
        if any(error.get("type") == "critical" for error in state.errors):
            return "error"
        
        # Check if quality validation failed
        quality_errors = [e for e in state.errors if e.get("agent") == "quality_validator"]
        if quality_errors and state.iteration_count < 2:  # Allow 2 retry attempts
            state.iteration_count += 1
            return "retry"
        elif quality_errors:
            return "error"
        
        # Check for collaboration mode
        if state.user_request and state.user_request.collaboration_mode:
            return "collaboration"
        
        return "complete"
    
    def _handle_agent_error(self, state: AgentState, error: Exception, agent_name: str) -> AgentState:
        """Handle individual agent errors with educational context"""
        
        logger.error(f"Agent error in {agent_name}: {error}")
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "type": type(error).__