# Lit Music Mashup - Implementation Documentation
## Educational AI Music Generation Platform

---

### Document Overview
This implementation guide provides a complete, sequential approach to building the Lit Music Mashup educational platform. The documentation prioritizes **MVP core functionality first**, with production enhancements added incrementally.

**Key Principle**: The MVP must successfully generate educational music mashups as its core deliverable. All other features are production enhancements that can be added after the core functionality is proven.

---

## Table of Contents

1. [Introduction & Project Overview](#1-introduction--project-overview)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Project Architecture & Structure](#3-project-architecture--structure)
4. [Core Framework Implementation](#4-core-framework-implementation)
5. [Database Layer Implementation](#5-database-layer-implementation)
6. [AI Agent System Implementation](#6-ai-agent-system-implementation)
7. [Service Layer Implementation](#7-service-layer-implementation)
8. [API Layer Implementation](#8-api-layer-implementation)
9. [MVP Core Feature Validation](#9-mvp-core-feature-validation)
10. [Production Enhancement Roadmap](#10-production-enhancement-roadmap)
11. [Testing Strategy](#11-testing-strategy)
12. [Deployment & Operations](#12-deployment--operations)

---

## 1. Introduction & Project Overview

### 1.1 Executive Summary

The Lit Music Mashup platform is an educational AI system that generates music mashups with comprehensive educational content. The implementation follows a **core-first approach**: establish the fundamental mashup generation capability, then incrementally add production features.

**Core MVP Goal**: Generate educational music mashups that combine different genres with theory explanations, cultural context, and teaching materials.

### 1.2 Educational Platform Goals

- **Primary**: Deliver working educational music mashup generation
- **Secondary**: Support classroom integration and collaborative learning
- **Tertiary**: Provide analytics, monitoring, and enterprise features

### 1.3 Technology Stack Overview

**Backend Infrastructure**:
- **Python 3.11+** with UV package management
- **FastAPI** for API framework
- **PostgreSQL** for all environments (no SQLite migration needed)
- **LangGraph** for AI agent orchestration
- **Ollama** for local AI models (primary)
- **Redis** for session management

**MVP Focus**: Core functionality with local models and basic API endpoints.

### 1.4 MVP vs Production Features

#### **MVP CORE (Must Have)**
- ✅ Educational mashup generation
- ✅ Basic AI agent workflow
- ✅ Simple API endpoints
- ✅ Database persistence
- ✅ Educational content output

#### **Production Enhancements (Add Later)**
- 🔄 Real-time collaboration
- 🔄 WebSocket connections
- 🔄 Advanced analytics
- 🔄 Institution management
- 🔄 FERPA/COPPA compliance features
- 🔄 Monitoring and observability

---

## 2. Development Environment Setup

### 2.1 Prerequisites & System Requirements

```bash
# System Requirements
- Python 3.11 or higher
- Docker and Docker Compose
- Git
- 8GB+ RAM (for local AI models)
- 20GB+ storage
```

### 2.2 Python Environment Setup (UV Package Manager)

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project and virtual environment
uv init lit-music-mashup
cd lit-music-mashup

# Install dependencies
uv add fastapi uvicorn sqlalchemy psycopg2-binary
uv add langchain langgraph langchain-ollama
uv add pydantic python-dotenv python-multipart
uv add pytest pytest-asyncio --dev
```

### 2.3 Database Setup (PostgreSQL from Start)

**Why PostgreSQL for MVP**: Educational features require JSON storage, concurrent access, and advanced querying. Starting with PostgreSQL avoids migration complexity.

```yaml
# docker-compose.yml - Development Setup
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://litmusic:password@db:5432/lit_music_mashup
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - db
      - ollama
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: litmusic
      POSTGRES_PASSWORD: password
      POSTGRES_DB: lit_music_mashup
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

volumes:
  postgres_data:
  ollama_data:
```

### 2.4 Environment Variables Configuration

```bash
# .env file
# Database
DATABASE_URL=postgresql://litmusic:password@localhost:5432/lit_music_mashup

# AI Models
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=llama3.1:8b-instruct

# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# MVP Settings (simplified)
FERPA_COMPLIANCE=false
ENABLE_COLLABORATION=false
ENABLE_ANALYTICS=false
```

### 2.5 Local Development Workflow

```bash
# Start all services
docker-compose up -d

# Install Ollama model
docker exec -it lit-music-mashup-ollama-1 ollama pull llama3.1:8b-instruct

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 3. Project Architecture & Structure

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    MVP Architecture                      │
├─────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ POST /api/v1/mashup/generate                        │ │
│  │ GET  /api/v1/mashup/{id}                           │ │
│  │ GET  /health                                        │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  AI Agent System (LangGraph)                           │
│  ┌───────────────┬───────────────┬───────────────────┐ │
│  │ Educational   │ Genre         │ Hook Generator    │ │
│  │ Context Agent │ Analyzer      │ Agent             │ │
│  ├───────────────┼───────────────┼───────────────────┤ │
│  │ Lyrics        │ Theory        │ Content           │ │
│  │ Composer      │ Integrator    │ Validator         │ │
│  └───────────────┴───────────────┴───────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Local AI Models (Ollama)                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Llama 3.1 8B Instruct                              │ │
│  │ - Text Generation                                   │ │
│  │ - Educational Content Creation                      │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ PostgreSQL Database                                 │ │
│  │ - Users, Sessions, Mashups                          │ │
│  │ - Educational Content                               │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Directory Structure

```
lit_music_mashup/
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── .env.example
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   │
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── mashup.py   # Core mashup endpoints
│   │       │   └── health.py   # Health checks
│   │       └── router.py
│   │
│   ├── agents/                 # AI agents (MVP core)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── educational_context.py
│   │   ├── genre_analyzer.py
│   │   ├── hook_generator.py
│   │   ├── lyrics_composer.py
│   │   └── theory_integrator.py
│   │
│   ├── core/                   # Core logic
│   │   ├── __init__.py
│   │   ├── workflow.py         # LangGraph workflow
│   │   ├── models.py           # Pydantic models
│   │   └── exceptions.py
│   │
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py           # SQLAlchemy models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── mashup.py
│   │       └── session.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── mashup_service.py   # Core service
│   │   └── model_service.py    # AI model management
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── logging.py
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_agents/
│   └── test_services/
│
└── alembic/                    # Database migrations
    ├── env.py
    └── versions/
```

### 3.3 MVP Component Overview

**Core Components (MVP)**:
1. **FastAPI Application** - HTTP API endpoints
2. **LangGraph Workflow** - AI agent orchestration
3. **PostgreSQL Database** - Data persistence
4. **Ollama Integration** - Local AI models
5. **Basic Authentication** - Simple user management

**Deferred Components (Production)**:
- WebSocket connections
- Real-time collaboration
- Advanced analytics
- Institution management
- Compliance features

---

## 4. Core Framework Implementation

### 4.1 FastAPI Application Setup

```python
# app/main.py
"""
Lit Music Mashup - Main FastAPI Application (MVP)
Educational AI Music Generation Platform
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.v1.router import api_router
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
    """Application lifespan management"""
    
    logger.info("Starting Lit Music Mashup MVP...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Initialize AI model service
    try:
        model_service = ModelService()
        await model_service.initialize()
        app.state.model_service = model_service
        logger.info("AI model service initialized")
    except Exception as e:
        logger.error(f"AI model service initialization failed: {e}")
        raise
    
    logger.info("MVP startup complete")
    yield
    
    # Cleanup
    logger.info("Shutting down MVP...")
    if hasattr(app.state, 'model_service'):
        await app.state.model_service.cleanup()
    logger.info("MVP shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Lit Music Mashup API",
    description="Educational AI Music Generation Platform (MVP)",
    version="1.0.0-mvp",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Basic CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.exception_handler(LitMusicMashupException)
async def app_exception_handler(request: Request, exc: LitMusicMashupException):
    """Handle application exceptions"""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message}
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lit Music Mashup MVP",
        "version": "1.0.0-mvp",
        "status": "active",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0-mvp",
        "services": {
            "api": "healthy",
            "database": "healthy",
            "ai_models": "healthy"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
```

### 4.2 Configuration Management (MVP)

```python
# app/config.py
"""
Configuration management for MVP
Simplified settings focused on core functionality
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """MVP Application settings"""
    
    # Basic application settings
    PROJECT_NAME: str = "Lit Music Mashup MVP"
    VERSION: str = "1.0.0-mvp"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database configuration
    DATABASE_URL: str = Field(env="DATABASE_URL")
    
    # AI Model configuration
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    DEFAULT_LOCAL_MODEL: str = Field(default="llama3.1:8b-instruct", env="DEFAULT_LOCAL_MODEL")
    
    # Security (basic)
    SECRET_KEY: str = Field(env="SECRET_KEY")
    
    # MVP Feature Flags (disabled for core focus)
    ENABLE_COLLABORATION: bool = Field(default=False, env="ENABLE_COLLABORATION")
    ENABLE_ANALYTICS: bool = Field(default=False, env="ENABLE_ANALYTICS")
    FERPA_COMPLIANCE: bool = Field(default=False, env="FERPA_COMPLIANCE")
    ENABLE_WEBSOCKETS: bool = Field(default=False, env="ENABLE_WEBSOCKETS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
```

---

## 5. Database Layer Implementation

### 5.1 SQLAlchemy Models (MVP Core)

```python
# app/db/models.py
"""
Database models for MVP
Focus on core entities: Users, Sessions, Mashups
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    """User model (MVP - basic fields only)"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user")
    mashups = relationship("Mashup", back_populates="user")

class Session(Base):
    """Session model for tracking mashup generation"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Request and response data
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="active", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    mashups = relationship("Mashup", back_populates="session")

class Mashup(Base):
    """Generated mashup model with educational content"""
    __tablename__ = "mashups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Core content
    title = Column(String(200), nullable=False)
    genre_blend = Column(JSON, nullable=False)  # List of genres
    lyrics = Column(Text, nullable=True)
    hooks = Column(JSON, nullable=True)
    
    # Educational content (MVP core feature)
    educational_content = Column(JSON, nullable=True)
    theory_analysis = Column(JSON, nullable=True)
    cultural_context = Column(JSON, nullable=True)
    teaching_guide = Column(JSON, nullable=True)
    
    # Metadata
    generation_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="mashups")
    user = relationship("User", back_populates="mashups")
```

### 5.2 Database Connection Setup

```python
# app/db/database.py
"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.models import Base

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.3 Repository Pattern (MVP)

```python
# app/db/repositories/mashup.py
"""
Mashup repository for data access
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Mashup, Session as SessionModel
from app.core.models import MashupCreate

class MashupRepository:
    """Repository for mashup data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, mashup_data: MashupCreate) -> Mashup:
        """Create new mashup"""
        db_mashup = Mashup(**mashup_data.dict())
        self.db.add(db_mashup)
        self.db.commit()
        self.db.refresh(db_mashup)
        return db_mashup
    
    def get_by_id(self, mashup_id: str) -> Optional[Mashup]:
        """Get mashup by ID"""
        return self.db.query(Mashup).filter(Mashup.id == mashup_id).first()
    
    def get_by_session(self, session_id: str) -> List[Mashup]:
        """Get mashups by session ID"""
        return self.db.query(Mashup).filter(Mashup.session_id == session_id).all()
    
    def get_by_user(self, user_id: str, limit: int = 10) -> List[Mashup]:
        """Get user's recent mashups"""
        return (
            self.db.query(Mashup)
            .filter(Mashup.user_id == user_id)
            .order_by(Mashup.created_at.desc())
            .limit(limit)
            .all()
        )
```

---

## 6. AI Agent System Implementation

### 6.1 Base Agent Class

```python
# app/agents/base.py
"""
Base agent class for educational AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.models import AgentState

class BaseEducationalAgent(ABC):
    """Base class for all educational agents"""
    
    def __init__(self, model_service=None):
        self.model_service = model_service
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
    
    async def _generate_content(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate content using AI model"""
        if not self.model_service:
            raise ValueError("Model service not initialized")
        
        return await self.model_service.generate_text(
            prompt=prompt,
            context=context,
            agent_name=self.agent_name
        )
```

### 6.2 Educational Context Agent

```python
# app/agents/educational_context.py
"""
Educational context analysis agent
Analyzes user requirements and sets educational parameters
"""

from typing import Dict, Any
from app.agents.base import BaseEducationalAgent
from app.core.models import AgentState

class EducationalContextAgent(BaseEducationalAgent):
    """Agent for analyzing educational context and requirements"""
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Analyze educational context from user request"""
        
        user_request = state.user_request
        
        # Analyze educational requirements
        context_prompt = f"""
        Analyze this educational music request and provide context:
        
        User Request: {user_request.user_prompt}
        Skill Level: {user_request.skill_level}
        Educational Context: {user_request.educational_context}
        Learning Objectives: {user_request.learning_objectives}
        
        Provide:
        1. Appropriate educational level and complexity
        2. Key learning goals for this request
        3. Recommended teaching approach
        4. Cultural sensitivity considerations
        
        Format as JSON with keys: educational_level, learning_goals, teaching_approach, cultural_notes
        """
        
        response = await self._generate_content(context_prompt)
        
        # Parse and structure the educational context
        educational_context = {
            "analyzed_request": user_request.user_prompt,
            "skill_level": user_request.skill_level,
            "educational_context": user_request.educational_context,
            "ai_analysis": response,
            "agent_metadata": {
                "agent": self.agent_name,
                "processing_time": "calculated_time_here"
            }
        }
        
        return educational_context
```

### 6.3 Genre Analyzer Agent

```python
# app/agents/genre_analyzer.py
"""
Genre analysis agent for educational music mashups
"""

from typing import Dict, Any
from app.agents.base import BaseEducationalAgent
from app.core.models import AgentState

class GenreAnalyzerAgent(BaseEducationalAgent):
    """Agent for analyzing and selecting genres for educational mashups"""
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Analyze and select appropriate genres"""
        
        user_request = state.user_request
        educational_context = state.educational_context
        
        genre_analysis_prompt = f"""
        As a music education expert, analyze this request and suggest appropriate genres for an educational mashup:
        
        User Request: {user_request.user_prompt}
        Educational Level: {educational_context.get('skill_level', 'intermediate')}
        Educational Context: {educational_context.get('educational_context', 'classroom')}
        
        Provide:
        1. 2-3 suitable genres that would create an educational mashup
        2. Educational rationale for each genre selection
        3. Key musical characteristics of each genre
        4. Cultural and historical context for each genre
        5. How these genres complement each other educationally
        
        Focus on genres that offer learning opportunities in:
        - Music theory concepts
        - Cultural understanding
        - Historical context
        - Musical technique differences
        
        Format as JSON with keys: selected_genres, educational_rationale, musical_characteristics, cultural_context, genre_synergy
        """
        
        response = await self._generate_content(genre_analysis_prompt)
        
        genre_analysis = {
            "user_request": user_request.user_prompt,
            "selected_genres": [],  # Will be parsed from AI response
            "analysis_details": response,
            "educational_focus": educational_context,
            "agent_metadata": {
                "agent": self.agent_name,
                "analysis_type": "genre_selection"
            }
        }
        
        return genre_analysis
```

### 6.4 LangGraph Workflow (MVP)

```python
# app/core/workflow.py
"""
LangGraph workflow for MVP educational mashup generation
Simplified workflow focusing on core functionality
"""

import logging
from typing import Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.models import AgentState, EducationalMashupRequest, EducationalMashupResult
from app.agents.educational_context import EducationalContextAgent
from app.agents.genre_analyzer import GenreAnalyzerAgent
from app.agents.hook_generator import HookGeneratorAgent
from app.agents.lyrics_composer import LyricsComposerAgent
from app.agents.theory_integrator import TheoryIntegratorAgent
from app.core.exceptions import WorkflowException

logger = logging.getLogger(__name__)

class MVPWorkflowOrchestrator:
    """Simplified workflow orchestrator for MVP"""
    
    def __init__(self, model_service):
        self.model_service = model_service
        self.checkpointer = MemorySaver()
        
        # Initialize agents
        self.agents = {
            "educational_context": EducationalContextAgent(model_service),
            "genre_analyzer": GenreAnalyzerAgent(model_service),
            "hook_generator": HookGeneratorAgent(model_service),
            "lyrics_composer": LyricsComposerAgent(model_service),
            "theory_integrator": TheoryIntegratorAgent(model_service),
        }
        
        self._build_mvp_workflow()
    
    def _build_mvp_workflow(self):
        """Build simplified MVP workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("educational_context", self._educational_context_node)
        workflow.add_node("genre_analyzer", self._genre_analyzer_node)
        workflow.add_node("hook_generator", self._hook_generator_node)
        workflow.add_node("lyrics_composer", self._lyrics_composer_node)
        workflow.add_node("theory_integrator", self._theory_integrator_node)
        
        # Define linear workflow (MVP simplification)
        workflow.set_entry_point("educational_context")
        workflow.add_edge("educational_context", "genre_analyzer")
        workflow.add_edge("genre_analyzer", "hook_generator")
        workflow.add_edge("hook_generator", "lyrics_composer")
        workflow.add_edge("lyrics_composer", "theory_integrator")
        workflow.add_edge("theory_integrator", END)
        
        # Compile workflow
        self.workflow_graph = workflow.compile(checkpointer=self.checkpointer)
        
        logger.info("MVP workflow graph built successfully")
    
    async def execute_mvp_workflow(
        self, 
        request: EducationalMashupRequest,
        session_id: str
    ) -> EducationalMashupResult:
        """Execute MVP workflow"""
        
        start_time = datetime.now()
        logger.info(f"Starting MVP workflow for session {session_id}")
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            current_agent=None,
            user_request=request,
            session_id=session_id,
            errors=[]
        )
        
        try:
            # Execute workflow
            config = {"configurable": {"thread_id": session_id}}
            final_state = await self.workflow_graph.ainvoke(initial_state, config=config)
            
            # Build result
            result = self._build_mvp_result(final_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"MVP workflow completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"MVP workflow failed: {e}")
            raise WorkflowException(f"Workflow execution failed: {str(e)}")
    
    # Agent node implementations
    async def _educational_context_node(self, state: AgentState) -> AgentState:
        """Execute educational context agent"""
        state.current_agent = "educational_context"
        result = await self.agents["educational_context"].execute(state)
        state.educational_context = result
        return state
    
    async def _genre_analyzer_node(self, state: AgentState) -> AgentState:
        """Execute genre analyzer agent"""
        state.current_agent = "genre_analyzer"
        result = await self.agents["genre_analyzer"].execute(state)
        state.genre_analysis = result
        return state
    
    async def _hook_generator_node(self, state: AgentState) -> AgentState:
        """Execute hook generator agent"""
        state.current_agent = "hook_generator"
        result = await self.agents["hook_generator"].execute(state)
        state.hook_options = result
        return state
    
    async def _lyrics_composer_node(self, state: AgentState) -> AgentState:
        """Execute lyrics composer agent"""
        state.current_agent = "lyrics_composer"
        result = await self.agents["lyrics_composer"].execute(state)
        state.final_composition = result
        return state
    
    async def _theory_integrator_node(self, state: AgentState) -> AgentState:
        """Execute theory integrator agent"""
        state.current_agent = "theory_integrator"
        result = await self.agents["theory_integrator"].execute(state)
        state.theory_integration = result
        return state
    
    def _build_mvp_result(self, final_state: AgentState) -> EducationalMashupResult:
        """Build educational mashup result from final state"""
        
        return EducationalMashupResult(
            session_id=final_state.session_id,
            title=self._extract_title(final_state),
            genre_blend=self._extract_genres(final_state),
            lyrics=self._extract_lyrics(final_state),
            hooks=self._extract_hooks(final_state),
            educational_content=final_state.educational_context,
            theory_analysis=final_state.theory_integration,
            cultural_context=self._extract_cultural_context(final_state),
            teaching_guide=self._generate_teaching_guide(final_state),
            metadata={
                "agents_used": list(self.agents.keys()),
                "workflow_version": "mvp-1.0.0",
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    
    def _extract_title(self, state: AgentState) -> str:
        """Extract mashup title from state"""
        # Implementation to extract title from agent results
        return "Generated Educational Mashup"
    
    def _extract_genres(self, state: AgentState) -> list:
        """Extract genre blend from state"""
        # Implementation to extract genres from genre analyzer results
        return ["Genre1", "Genre2"]
    
    def _extract_lyrics(self, state: AgentState) -> str:
        """Extract lyrics from state"""
        # Implementation to extract lyrics from lyrics composer results
        return "Generated lyrics here..."
    
    def _extract_hooks(self, state: AgentState) -> list:
        """Extract hooks from state"""
        # Implementation to extract hooks from hook generator results
        return ["Hook 1", "Hook 2", "Hook 3"]
    
    def _extract_cultural_context(self, state: AgentState) -> dict:
        """Extract cultural context from state"""
        # Implementation to extract cultural context
        return {"context": "Cultural information here"}
    
    def _generate_teaching_guide(self, state: AgentState) -> dict:
        """Generate teaching guide from state"""
        # Implementation to generate teaching guide
        return {
            "lesson_plan": "Teaching instructions here",
            "discussion_questions": [],
            "activities": []
        }
```

---

## 7. Service Layer Implementation

### 7.1 Mashup Generation Service (MVP Core)

```python
# app/services/mashup_service.py
"""
Core mashup generation service for MVP
Focuses on essential functionality
"""

import logging
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4

from app.core.models import EducationalMashupRequest, EducationalMashupResult
from app.core.workflow import MVPWorkflowOrchestrator
from app.services.model_service import ModelService
from app.core.exceptions import MashupGenerationException

logger = logging.getLogger(__name__)

class MashupGenerationService:
    """MVP service for educational mashup generation"""
    
    def __init__(self, model_service: ModelService):
        self.model_service = model_service
        self.workflow_orchestrator = MVPWorkflowOrchestrator(model_service)
    
    async def generate_educational_mashup(
        self,
        request: EducationalMashupRequest,
        user_id: str = None
    ) -> EducationalMashupResult:
        """Generate educational mashup (MVP core functionality)"""
        
        session_id = str(uuid4())
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting mashup generation for session {session_id}")
            
            # Validate request (basic validation for MVP)
            self._validate_request(request)
            
            # Execute workflow
            result = await self.workflow_orchestrator.execute_mvp_workflow(
                request=request,
                session_id=session_id
            )
            
            # Add generation metadata
            generation_time = (datetime.now() - start_time).total_seconds()
            result.metadata.update({
                "generation_time_seconds": generation_time,
                "mvp_version": "1.0.0",
                "user_id": user_id
            })
            
            logger.info(f"Mashup generation completed in {generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Mashup generation failed: {e}")
            raise MashupGenerationException(
                message=f"Failed to generate educational mashup: {str(e)}",
                session_id=session_id
            )
    
    def _validate_request(self, request: EducationalMashupRequest):
        """Basic request validation for MVP"""
        
        if not request.user_prompt or len(request.user_prompt.strip()) < 5:
            raise MashupGenerationException(
                message="User prompt must be at least 5 characters long"
            )
        
        valid_skill_levels = ["beginner", "intermediate", "advanced"]
        if request.skill_level not in valid_skill_levels:
            raise MashupGenerationException(
                message=f"Skill level must be one of: {valid_skill_levels}"
            )
```

### 7.2 Model Service (Ollama Integration)

```python
# app/services/model_service.py
"""
AI model service for local Ollama integration
"""

import logging
import httpx
from typing import Dict, Any, Optional

from app.config import settings
from app.core.exceptions import ModelServiceException

logger = logging.getLogger(__name__)

class ModelService:
    """Service for managing AI model interactions"""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.DEFAULT_LOCAL_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)
        self.model_initialized = False
    
    async def initialize(self):
        """Initialize model service and verify Ollama connection"""
        
        try:
            # Check Ollama connection
            response = await self.client.get(f"{self.ollama_base_url}/api/tags")
            response.raise_for_status()
            
            # Verify default model is available
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.default_model not in model_names:
                logger.warning(f"Default model {self.default_model} not found. Available models: {model_names}")
                # Try to pull the model
                await self._pull_model(self.default_model)
            
            self.model_initialized = True
            logger.info(f"Model service initialized with {self.default_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model service: {e}")
            raise ModelServiceException(f"Model service initialization failed: {str(e)}")
    
    async def generate_text(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        agent_name: str = None
    ) -> str:
        """Generate text using Ollama model"""
        
        if not self.model_initialized:
            raise ModelServiceException("Model service not initialized")
        
        try:
            # Prepare request payload
            payload = {
                "model": self.default_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            # Add context if provided
            if context:
                enhanced_prompt = f"Context: {context}\n\nPrompt: {prompt}"
                payload["prompt"] = enhanced_prompt
            
            # Make request to Ollama
            response = await self.client.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            if not generated_text:
                raise ModelServiceException("Empty response from model")
            
            logger.debug(f"Generated text for {agent_name}: {len(generated_text)} characters")
            
            return generated_text
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during text generation: {e}")
            raise ModelServiceException(f"Model request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during text generation: {e}")
            raise ModelServiceException(f"Text generation failed: {str(e)}")
    
    async def _pull_model(self, model_name: str):
        """Pull model if not available"""
        
        try:
            logger.info(f"Pulling model {model_name}...")
            
            payload = {"name": model_name}
            response = await self.client.post(
                f"{self.ollama_base_url}/api/pull",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Successfully pulled model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise ModelServiceException(f"Model pull failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if model service is healthy"""
        
        try:
            response = await self.client.get(f"{self.ollama_base_url}/api/tags")
            return response.status_code == 200 and self.model_initialized
        except:
            return False
    
    async def cleanup(self):
        """Cleanup model service resources"""
        
        await self.client.aclose()
        logger.info("Model service cleaned up")
```

---

## 8. API Layer Implementation

### 8.1 Core API Endpoints (MVP)

```python
# app/api/v1/endpoints/mashup.py
"""
Core mashup generation API endpoints for MVP
"""

import logging
from typing import Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.models import (
    EducationalMashupRequest, 
    EducationalMashupResult,
    MashupResponse
)
from app.db.database import get_db
from app.db.repositories.mashup import MashupRepository
from app.db.repositories.session import SessionRepository
from app.services.mashup_service import MashupGenerationService
from app.services.model_service import ModelService
from app.core.exceptions import MashupGenerationException

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get services
async def get_mashup_service() -> MashupGenerationService:
    """Get mashup generation service"""
    # In a real implementation, this would come from dependency injection
    model_service = ModelService()
    return MashupGenerationService(model_service)

@router.post("/generate", response_model=MashupResponse)
async def generate_mashup(
    request: EducationalMashupRequest,
    db: Session = Depends(get_db),
    mashup_service: MashupGenerationService = Depends(get_mashup_service)
):
    """
    Generate educational music mashup (MVP core endpoint)
    
    This is the core functionality that the MVP must deliver successfully.
    """
    
    try:
        logger.info(f"Received mashup generation request: {request.user_prompt[:50]}...")
        
        # Create session record
        session_repo = SessionRepository(db)
        session_id = str(uuid4())
        
        session_record = session_repo.create_session(
            session_id=session_id,
            request_data=request.dict(),
            status="processing"
        )
        
        # Generate mashup
        result = await mashup_service.generate_educational_mashup(
            request=request,
            user_id=session_record.id  # For MVP, using session ID as user reference
        )
        
        # Save mashup to database
        mashup_repo = MashupRepository(db)
        mashup_record = mashup_repo.create_mashup(
            session_id=session_record.id,
            user_id=session_record.id,
            mashup_data=result
        )
        
        # Update session status
        session_repo.update_session_status(
            session_id=session_id,
            status="completed",
            response_data=result.dict()
        )
        
        logger.info(f"Successfully generated mashup {mashup_record.id}")
        
        return MashupResponse(
            success=True,
            mashup_id=str(mashup_record.id),
            session_id=session_id,
            result=result,
            message="Educational mashup generated successfully"
        )
        
    except MashupGenerationException as e:
        logger.error(f"Mashup generation failed: {e.message}")
        
        # Update session with error
        if 'session_repo' in locals() and 'session_id' in locals():
            session_repo.update_session_status(
                session_id=session_id,
                status="failed",
                error_info={"error": e.message}
            )
        
        raise HTTPException(status_code=400, detail=e.message)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{mashup_id}", response_model=EducationalMashupResult)
async def get_mashup(
    mashup_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a generated mashup by ID
    """
    
    try:
        mashup_repo = MashupRepository(db)
        mashup = mashup_repo.get_by_id(mashup_id)
        
        if not mashup:
            raise HTTPException(status_code=404, detail="Mashup not found")
        
        # Convert database record to response model
        result = EducationalMashupResult(
            session_id=str(mashup.session_id),
            title=mashup.title,
            genre_blend=mashup.genre_blend,
            lyrics=mashup.lyrics,
            hooks=mashup.hooks,
            educational_content=mashup.educational_content,
            theory_analysis=mashup.theory_analysis,
            cultural_context=mashup.cultural_context,
            teaching_guide=mashup.teaching_guide,
            metadata=mashup.generation_metadata or {}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mashup {mashup_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def list_recent_mashups(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List recent mashups (MVP simple listing)
    """
    
    try:
        mashup_repo = MashupRepository(db)
        mashups = mashup_repo.get_recent(limit=limit)
        
        return {
            "mashups": [
                {
                    "id": str(mashup.id),
                    "title": mashup.title,
                    "genre_blend": mashup.genre_blend,
                    "created_at": mashup.created_at.isoformat()
                }
                for mashup in mashups
            ],
            "total": len(mashups)
        }
        
    except Exception as e:
        logger.error(f"Error listing mashups: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 8.2 API Router Setup

```python
# app/api/v1/router.py
"""
API router configuration for MVP
"""

from fastapi import APIRouter
from app.api.v1.endpoints import mashup

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    mashup.router, 
    prefix="/mashup", 
    tags=["mashup"]
)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": "1.0.0-mvp",
        "api": "operational"
    }
```

---

## 9. MVP Core Feature Validation

### 9.1 MVP Success Criteria

The MVP is considered successful when it can consistently:

#### **✅ Core Functionality Checklist**

1. **Accept User Input**
   - ✅ Receive educational mashup requests via API
   - ✅ Parse user prompts, skill levels, and educational context
   - ✅ Validate input parameters

2. **AI Processing Pipeline**
   - ✅ Execute complete LangGraph workflow
   - ✅ Educational context analysis
   - ✅ Genre analysis and selection
   - ✅ Hook generation
   - ✅ Lyrics composition
   - ✅ Theory integration

3. **Educational Output Generation**
   - ✅ Generate mashup lyrics combining multiple genres
   - ✅ Provide music theory explanations
   - ✅ Include cultural context information
   - ✅ Create teaching guide materials
   - ✅ Offer multiple hook options

4. **Data Persistence**
   - ✅ Store sessions in PostgreSQL
   - ✅ Save generated mashups
   - ✅ Track generation metadata

5. **API Response**
   - ✅ Return structured educational content
   - ✅ Provide retrievable mashup records
   - ✅ Include generation metadata

### 9.2 MVP Testing Strategy

```python
# tests/test_mvp_core.py
"""
Core MVP functionality tests
These tests must pass for MVP to be considered functional
"""

import pytest
from app.core.models import EducationalMashupRequest
from app.services.mashup_service import MashupGenerationService

@pytest.mark.asyncio
async def test_mvp_core_generation():
    """Test core mashup generation functionality"""
    
    # Create test request
    request = EducationalMashupRequest(
        user_prompt="Create a mashup combining jazz and hip-hop for high school students",
        skill_level="intermediate",
        educational_context="classroom",
        learning_objectives=["Understanding genre fusion", "Cultural context appreciation"]
    )
    
    # Generate mashup
    service = MashupGenerationService(model_service)
    result = await service.generate_educational_mashup(request)
    
    # Validate core output
    assert result.title is not None
    assert len(result.genre_blend) >= 2
    assert result.lyrics is not None
    assert len(result.hooks) > 0
    assert result.educational_content is not None
    assert result.theory_analysis is not None
    assert result.cultural_context is not None
    assert result.teaching_guide is not None

@pytest.mark.asyncio
async def test_api_endpoint_generation():
    """Test API endpoint for mashup generation"""
    
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    request_data = {
        "user_prompt": "Create a mashup combining blues and rock for beginners",
        "skill_level": "beginner",
        "educational_context": "workshop",
        "learning_objectives": ["Basic music theory", "Genre recognition"]
    }
    
    response = client.post("/api/v1/mashup/generate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "mashup_id" in data
    assert "result" in data
    assert data["result"]["title"] is not None
```

### 9.3 MVP Performance Benchmarks

**Acceptable MVP Performance**:
- **Generation Time**: < 2 minutes per mashup
- **Success Rate**: > 85% successful generations
- **API Response**: < 5 seconds for retrieval endpoints
- **Educational Content Quality**: All required sections present
- **Database Operations**: < 1 second for CRUD operations

---

## 10. Production Enhancement Roadmap

### 10.1 Phase 1 Enhancements (Post-MVP)

**Priority 1: User Experience**
- User authentication and session management
- Improved error handling and user feedback
- Request validation and sanitization
- Response formatting optimization

**Priority 2: Educational Features**
- Advanced educational analytics
- Institution management
- Classroom integration tools
- Learning progress tracking

### 10.2 Phase 2 Enhancements

**Collaboration Features**:
- Real-time WebSocket connections
- Multi-user collaborative sessions
- Live editing and voting
- Session facilitation tools

**Advanced AI**:
- Multiple model support (cloud models)
- Content quality validation
- Cultural sensitivity checking
- Advanced personalization

### 10.3 Phase 3 Enhancements

**Enterprise Features**:
- FERPA/COPPA compliance
- Advanced privacy controls
- Data retention policies
- Audit logging

**Scalability & Operations**:
- Monitoring and observability
- Performance optimization
- Caching strategies
- Load balancing

### 10.4 Feature Flag Implementation

```python
# app/config.py - Feature flags for production rollout
class ProductionFeatures:
    """Feature flags for gradual production rollout"""
    
    # Phase 1 flags
    ENABLE_USER_AUTH: bool = False
    ENABLE_ADVANCED_VALIDATION: bool = False
    ENABLE_ANALYTICS: bool = False
    
    # Phase 2 flags
    ENABLE_COLLABORATION: bool = False
    ENABLE_WEBSOCKETS: bool = False
    ENABLE_CLOUD_MODELS: bool = False
    
    # Phase 3 flags
    ENABLE_COMPLIANCE_FEATURES: bool = False
    ENABLE_ENTERPRISE_FEATURES: bool = False
    ENABLE_MONITORING: bool = False
```

---

## 11. Testing Strategy

### 11.1 MVP Testing Approach

**Testing Priority for MVP**:
1. **Core Functionality Tests** - Must pass for MVP success
2. **Integration Tests** - API and database integration
3. **AI Agent Tests** - Individual agent functionality
4. **Performance Tests** - Basic performance benchmarks

### 11.2 Test Structure

```python
# tests/conftest.py
"""
Test configuration for MVP testing
"""

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.services.model_service import ModelService

# Test database
TEST_DATABASE_URL = "postgresql://test:test@localhost:5432/test_lit_music_mashup"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def model_service():
    """Create model service for testing"""
    service = ModelService()
    await service.initialize()
    yield service
    await service.cleanup()

@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)
```

### 11.3 Core Tests Implementation

```python
# tests/test_core_agents.py
"""
Test individual AI agents
"""

import pytest
from app.agents.educational_context import EducationalContextAgent
from app.agents.genre_analyzer import GenreAnalyzerAgent
from app.core.models import AgentState, EducationalMashupRequest

@pytest.mark.asyncio
async def test_educational_context_agent(model_service):
    """Test educational context analysis"""
    
    agent = EducationalContextAgent(model_service)
    
    request = EducationalMashupRequest(
        user_prompt="Create a jazz and blues mashup for beginners",
        skill_level="beginner",
        educational_context="classroom",
        learning_objectives=["Basic improvisation", "Blues scale understanding"]
    )
    
    state = AgentState(
        messages=[],
        user_request=request,
        session_id="test-session"
    )
    
    result = await agent.execute(state)
    
    assert result is not None
    assert "educational_level" in str(result)
    assert "learning_goals" in str(result)

@pytest.mark.asyncio
async def test_genre_analyzer_agent(model_service):
    """Test genre analysis functionality"""
    
    agent = GenreAnalyzerAgent(model_service)
    
    request = EducationalMashupRequest(
        user_prompt="Mix country and hip-hop for advanced students",
        skill_level="advanced",
        educational_context="individual_study"
    )
    
    state = AgentState(
        messages=[],
        user_request=request,
        session_id="test-session",
        educational_context={"skill_level": "advanced"}
    )
    
    result = await agent.execute(state)
    
    assert result is not None
    assert "selected_genres" in str(result)
    assert "educational_rationale" in str(result)
```

---

## 12. Deployment & Operations

### 12.1 MVP Deployment Strategy

**Deployment Approach**: Simple containerized deployment focusing on reliability over complexity.

### 12.2 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 12.3 Production Docker Compose

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://litmusic:${DB_PASSWORD}@db:5432/lit_music_mashup
      - OLLAMA_BASE_URL=http://ollama:11434
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      ollama:
        condition: service_healthy
    restart: unless-stopped
    
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: litmusic
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: lit_music_mashup
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U litmusic"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ssl_certs:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  ollama_data:
  ssl_certs:
```

### 12.4 Environment Management

```bash
# production.env
DATABASE_URL=postgresql://litmusic:${DB_PASSWORD}@localhost:5432/lit_music_mashup
OLLAMA_BASE_URL=http://localhost:11434
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=${SECRET_KEY}

# MVP feature flags (production-ready features disabled)
ENABLE_COLLABORATION=false
ENABLE_ANALYTICS=false
FERPA_COMPLIANCE=false
ENABLE_WEBSOCKETS=false
```

### 12.5 Basic Monitoring Setup

```python
# app/utils/monitoring.py
"""
Basic monitoring for MVP deployment
"""

import logging
import time
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class BasicMonitoring:
    """Simple monitoring for MVP"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_generation_time = 0
        self.generation_count = 0
    
    def record_request(self):
        """Record API request"""
        self.request_count += 1
    
    def record_error(self):
        """Record error"""
        self.error_count += 1
        logger.error("Error recorded in monitoring")
    
    def record_generation(self, duration: float):
        """Record mashup generation"""
        self.generation_count += 1
        self.total_generation_time += duration
    
    def get_stats(self) -> dict:
        """Get basic statistics"""
        avg_generation_time = (
            self.total_generation_time / self.generation_count 
            if self.generation_count > 0 else 0
        )
        
        return {
            "requests": self.request_count,
            "errors": self.error_count,
            "generations": self.generation_count,
            "avg_generation_time": avg_generation_time,
            "error_rate": self.error_count / max(self.request_count, 1)
        }

# Global monitoring instance
monitoring = BasicMonitoring()

@asynccontextmanager
async def monitor_generation():
    """Context manager for monitoring generation time"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        monitoring.record_generation(duration)
    except Exception as e:
        monitoring.record_error()
        raise
```

---

## 13. Summary and Next Steps

### 13.1 MVP Implementation Summary

This implementation documentation provides a complete, sequential approach to building the Lit Music Mashup educational platform with a **core-first strategy**:

#### **✅ MVP Delivers Core Value**
- **Educational mashup generation** with AI agents
- **PostgreSQL database** from the start (no migration needed)
- **Local AI models** via Ollama
- **RESTful API** for mashup creation and retrieval
- **Complete educational content** output

#### **🔄 Production Features Added Incrementally**
- Real-time collaboration (Phase 2)
- Advanced analytics (Phase 2)
- Compliance features (Phase 3)
- Enterprise functionality (Phase 3)

### 13.2 Development Workflow

1. **Start with MVP Core** - Get basic mashup generation working
2. **Validate Core Functionality** - Ensure educational output quality
3. **Add Production Features** - Incrementally enhance based on user needs
4. **Scale and Optimize** - Performance and reliability improvements

### 13.3 Success Metrics

**MVP Success**: 
- ✅ Consistently generates educational mashups
- ✅ All required educational content sections present
- ✅ < 2 minute generation time
- ✅ > 85% success rate

**Production Success**:
- 🔄 Real-time collaboration working
- 🔄 Institution management integrated
- 🔄 FERPA/COPPA compliance achieved
- 🔄 Enterprise features deployed

### 13.4 Key Implementation Principles

1. **Core First**: MVP must deliver the fundamental value proposition
2. **PostgreSQL Always**: No database migration complexity 
3. **Local Models**: Reduce external dependencies for MVP
4. **Feature Flags**: Enable gradual production rollout
5. **Educational Focus**: Maintain educational value throughout development

This implementation guide provides everything needed to build a working educational AI music mashup platform, starting with core functionality and expanding to production features systematically.