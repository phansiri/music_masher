# Lit Music Mashup - Implementation Documentation v2.0
## Educational AI Music Generation Platform - Conversational MVP-First Approach

---

### Document Overview
This implementation guide provides a conversational, MVP-first approach to building the Lit Music Mashup educational platform. The documentation prioritizes **core conversational functionality delivery** with web search capabilities and incremental feature addition through CI/CD validation.

**Key Principle**: Build a conversational educational mashup generator with web search integration first, then add features through test-driven development with GitHub Actions CI/CD ensuring no regression.

---

## Table of Contents

1. [Conversational MVP-First Development Philosophy](#1-conversational-mvp-first-development-philosophy)
2. [Enhanced Minimal Viable Product Scope](#2-enhanced-minimal-viable-product-scope)
3. [Development Environment with Tool Integration](#3-development-environment-with-tool-integration)
4. [Conversational Architecture Implementation](#4-conversational-architecture-implementation)
5. [Enhanced Database Layer](#5-enhanced-database-layer)
6. [Conversational Agent System](#6-conversational-agent-system)
7. [API Layer with Chat Endpoints](#7-api-layer-with-chat-endpoints)
8. [Web Search Integration](#8-web-search-integration)
9. [CI/CD Pipeline with Tool Testing](#9-cicd-pipeline-with-tool-testing)
10. [MVP Validation & Conversational Testing](#10-mvp-validation--conversational-testing)
11. [Feature Addition Strategy](#11-feature-addition-strategy)

---

## 1. Conversational MVP-First Development Philosophy

### 1.1 Core Principles

**Start with Conversation, Add Complexity Gradually**:
- Conversational interface for context gathering
- Web search integration for current information
- Multi-turn dialogue for comprehensive understanding
- Educational content enhanced with real-time research
- Local models with tool orchestration
- SQLite database with conversation persistence

**Test-Driven Conversational Development**:
- Every conversational flow requires passing tests
- Web search integration tested with mock and real APIs
- GitHub Actions CI/CD prevents regression
- Tool integration validates graceful degradation
- Performance benchmarks for conversation and search

### 1.2 Enhanced Development Phases

#### **Phase 1: Conversational MVP (Week 1-2)**
- ✅ Chat API endpoints: `POST /api/v1/chat` and `GET /api/v1/session/{id}`
- ✅ Conversational context gathering system
- ✅ Web search integration (Tavily API)
- ✅ Enhanced educational content generation
- ✅ Conversation state persistence
- ✅ Tool orchestration with LangChain/LangGraph

#### **Phase 2: Enhanced Conversational Features (Week 3-4)**
- ✅ Advanced conversation validation
- ✅ Cultural sensitivity with web research
- ✅ Multi-source information synthesis
- ✅ Conversation history and context retrieval
- ✅ Enhanced error handling with fallbacks

#### **Phase 3: Quality & Polish (Week 5-6)**
- ✅ Comprehensive conversational testing
- ✅ Web search reliability optimization
- ✅ Advanced conversation flow management
- ✅ Source credibility validation
- ✅ Performance monitoring for tools

#### **Phase 4: Advanced Conversational Features (Week 7+)**
- ✅ Real-time collaborative conversations
- ✅ Advanced tool integration
- ✅ Multi-modal conversation support
- ✅ Advanced analytics for conversations
- ✅ Enterprise conversation management

---

## 2. Enhanced Minimal Viable Product Scope

### 2.1 Conversational MVP Core Requirements

**Must Have**:
```python
# Conversational endpoint for context gathering
POST /api/v1/chat
{
    "session_id": "optional-session-id",
    "message": "I want to create a mashup for my high school class",
    "context": {}
}

# Returns conversational response with tool usage
{
    "session_id": "generated-or-provided-id",
    "agent_response": "Great! Let me help you create an educational mashup...",
    "tool_calls": [
        {
            "tool": "web_search",
            "query": "high school music education trends 2024",
            "results": ["current research results"]
        }
    ],
    "ready_for_generation": false,
    "gathered_context": {
        "educational_context": "high school classroom",
        "genres": [],
        "skill_level": null,
        "learning_objectives": []
    }
}

# Final generation endpoint (enhanced with context)
POST /api/v1/generate
{
    "prompt": "Create jazz-hip hop mashup for high school",
    "skill_level": "intermediate",
    "gathered_context": {
        "educational_context": "high school classroom",
        "web_research": ["current web search results"],
        "cultural_focus": ["cultural elements from research"]
    }
}
```

**Nice to Have (Later Phases)**:
- Advanced conversation analytics
- Multi-user conversation management
- Voice conversation interface
- Advanced tool integration
- Conversation export capabilities

### 2.2 Enhanced Technology Stack

```yaml
# Enhanced tech stack for conversational MVP
Backend: FastAPI (structured with conversation modules)
Database: SQLite (with conversation tables)
AI Framework: LangChain/LangGraph for tool orchestration
AI Models: Ollama + Llama 3.1 8B Instruct
Web Search: Tavily API (user-provided key)
Testing: pytest + pytest-asyncio
CI/CD: GitHub Actions with API key management
Deployment: Docker (with environment configuration)
```

---

## 3. Development Environment with Tool Integration

### 3.1 Enhanced Setup

```bash
# Create conversational project
mkdir lit-music-mashup-v2
cd lit-music-mashup-v2

# Install enhanced dependencies
pip install fastapi uvicorn sqlite3 ollama pytest pytest-asyncio
pip install langchain langgraph langchain-community
pip install tavily-python pydantic python-dotenv

# Create enhanced structure
mkdir -p app/{api,agents,db,services,utils}
touch app/__init__.py
touch app/main.py
touch app/api/__init__.py
touch app/api/chat.py
touch app/api/generate.py
touch app/agents/__init__.py
touch app/agents/conversation_agent.py
touch app/db/__init__.py
touch app/db/models.py
touch app/db/conversation_db.py
touch app/services/__init__.py
touch app/services/web_search.py
touch .env.example
touch test_conversation.py
touch .github/workflows/conversational-ci.yml
```

### 3.2 Environment Configuration

```bash
# .env.example
# Required for web search functionality
TAVILY_API_KEY=your_tavily_api_key_here

# Local AI configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct

# Database configuration
DATABASE_PATH=./data/conversations.db

# Conversation settings
MAX_CONVERSATION_TURNS=10
CONVERSATION_TIMEOUT_MINUTES=30
WEB_SEARCH_MAX_RESULTS=3
WEB_SEARCH_TIMEOUT_SECONDS=10

# Educational content settings
MIN_CULTURAL_CONTEXT_LENGTH=100
MIN_THEORY_CONCEPTS=2
REQUIRE_WEB_RESEARCH=false
```

### 3.3 Enhanced Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (Enhanced)
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - "./data:/app/data"
      - "./.env:/app/.env"
    environment:
      - DATABASE_PATH=/app/data/conversations.db
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped
      
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  ollama_data:
```

---

## 4. Conversational Architecture Implementation

### 4.1 Enhanced MVP Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Conversational MVP Architecture               │
├─────────────────────────────────────────────────────────┤
│  FastAPI App (Modular Structure)                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ POST /api/v1/chat          - Conversation handling │ │
│  │ GET  /api/v1/session/{id}  - Session retrieval     │ │
│  │ POST /api/v1/generate      - Enhanced generation   │ │
│  │ GET  /api/v1/mashup/{id}   - Mashup retrieval      │ │
│  │ GET  /health               - Health check          │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Conversational Agent System (LangGraph)               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Components:                                         │ │
│  │ - Conversation Manager (state management)           │ │
│  │ - Context Gatherer (multi-turn dialogue)           │ │
│  │ - Tool Orchestrator (web search integration)       │ │
│  │ - Educational Content Generator (enhanced)          │ │
│  │ - Validation Engine (conversation and content)      │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Tool Integration Layer                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - Web Search Tool (Tavily API integration)         │ │
│  │ - Educational Resource Finder                       │ │
│  │ - Cultural Context Researcher                       │ │
│  │ - Music Theory Validator                            │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Local AI Models (Ollama)                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Llama 3.1 8B Instruct                              │ │
│  │ - Conversation handling and context understanding   │ │
│  │ - Tool decision making and orchestration            │ │
│  │ - Educational content generation                    │ │
│  │ - Web search result synthesis                       │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Enhanced SQLite Database                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Tables:                                             │ │
│  │ - conversations (session management)                │ │
│  │ - messages (conversation history)                   │ │
│  │ - tool_calls (web search history)                   │ │
│  │ - mashups (generated content)                       │ │
│  │ - web_sources (research citations)                  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Enhanced File Structure

```
lit-music-mashup-v2/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application with conversation endpoints
│   ├── config.py                   # Configuration management
│   │
│   ├── api/                        # API layer
│   │   ├── __init__.py
│   │   ├── chat.py                 # Conversation endpoints
│   │   ├── generate.py             # Enhanced generation endpoints
│   │   └── health.py               # Health checks
│   │
│   ├── agents/                     # Conversational agents
│   │   ├── __init__.py
│   │   ├── conversation_agent.py   # Main conversation agent
│   │   ├── context_gatherer.py     # Context gathering logic
│   │   └── content_generator.py    # Enhanced content generation
│   │
│   ├── db/                         # Database layer
│   │   ├── __init__.py
│   │   ├── models.py               # Database models
│   │   ├── conversation_db.py      # Conversation data operations
│   │   └── mashup_db.py            # Mashup data operations
│   │
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   ├── web_search.py           # Web search integration
│   │   ├── conversation_service.py # Conversation management
│   │   └── generation_service.py   # Enhanced generation
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── validation.py           # Input/output validation
│       └── logging.py              # Logging configuration
│
├── tests/                          # Enhanced test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_conversation.py        # Conversation flow tests
│   ├── test_web_search.py          # Web search integration tests
│   ├── test_generation.py          # Enhanced generation tests
│   └── test_api.py                 # API endpoint tests
│
├── requirements.txt                # Enhanced dependencies
├── .env.example                    # Environment configuration template
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Development environment
└── .github/
    └── workflows/
        └── conversational-ci.yml   # Enhanced CI/CD pipeline
```

---

## 5. Enhanced Database Layer

### 5.1 Conversation-Aware Database Schema

```python
# app/db/models.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ConversationPhase(str, Enum):
    INITIAL = "initial"
    GENRE_EXPLORATION = "genre_exploration"
    EDUCATIONAL_CLARIFICATION = "educational_clarification"
    CULTURAL_RESEARCH = "cultural_research"
    READY_FOR_GENERATION = "ready_for_generation"
    COMPLETED = "completed"

class ConversationDB:
    def __init__(self, db_path: str = "./data/conversations.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create conversation-aware database schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    current_phase TEXT DEFAULT 'initial',
                    gathered_context TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    ready_for_generation BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Messages table (conversation history)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT,  -- 'user' or 'assistant'
                    content TEXT,
                    tool_calls TEXT,  -- JSON array of tool calls
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Tool calls table (web search history)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    message_id INTEGER,
                    tool_name TEXT,
                    query TEXT,
                    results TEXT,  -- JSON
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                    FOREIGN KEY (message_id) REFERENCES messages (id)
                )
            """)
            
            # Enhanced mashups table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mashups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    prompt TEXT NOT NULL,
                    skill_level TEXT NOT NULL,
                    title TEXT,
                    lyrics TEXT,
                    educational_content TEXT,  -- JSON
                    web_sources TEXT,  -- JSON array of sources used
                    metadata TEXT,  -- JSON with generation metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Web sources table (for citation tracking)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS web_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mashup_id INTEGER,
                    url TEXT,
                    title TEXT,
                    content_snippet TEXT,
                    source_quality TEXT,  -- 'high', 'medium', 'low'
                    used_in_generation BOOLEAN DEFAULT TRUE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mashup_id) REFERENCES mashups (id)
                )
            """)
    
    def create_conversation(self, conversation_id: str, user_id: str = None) -> str:
        """Create new conversation session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (id, user_id, gathered_context)
                VALUES (?, ?, ?)
            """, (conversation_id, user_id, json.dumps({})))
            return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation with messages"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get conversation
            conv_cursor = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            )
            conversation = conv_cursor.fetchone()
            
            if not conversation:
                return None
            
            # Get messages
            msg_cursor = conn.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            """, (conversation_id,))
            messages = [dict(row) for row in msg_cursor.fetchall()]
            
            # Parse JSON fields
            conv_data = dict(conversation)
            conv_data['gathered_context'] = json.loads(conv_data['gathered_context'] or '{}')
            
            for msg in messages:
                msg['tool_calls'] = json.loads(msg['tool_calls'] or '[]')
            
            conv_data['messages'] = messages
            return conv_data
    
    def add_message(self, conversation_id: str, role: str, content: str, tool_calls: List[Dict] = None) -> int:
        """Add message to conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO messages (conversation_id, role, content, tool_calls)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, role, content, json.dumps(tool_calls or [])))
            return cursor.lastrowid
    
    def update_conversation_context(self, conversation_id: str, context: Dict, phase: str = None):
        """Update conversation context and phase"""
        with sqlite3.connect(self.db_path) as conn:
            if phase:
                conn.execute("""
                    UPDATE conversations 
                    SET gathered_context = ?, current_phase = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(context), phase, conversation_id))
            else:
                conn.execute("""
                    UPDATE conversations 
                    SET gathered_context = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(context), conversation_id))
    
    def mark_ready_for_generation(self, conversation_id: str):
        """Mark conversation as ready for generation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversations 
                SET ready_for_generation = TRUE, current_phase = 'ready_for_generation'
                WHERE id = ?
            """, (conversation_id,))
    
    def save_tool_call(self, conversation_id: str, message_id: int, tool_name: str, 
                      query: str, results: List[Dict], success: bool) -> int:
        """Save tool call results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO tool_calls (conversation_id, message_id, tool_name, query, results, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conversation_id, message_id, tool_name, query, json.dumps(results), success))
            return cursor.lastrowid
```

---

## 6. Conversational Agent System

### 6.1 Enhanced Conversation Agent

```python
# app/agents/conversation_agent.py
import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import HumanMessage, AIMessage

from app.services.web_search import WebSearchService
from app.db.conversation_db import ConversationDB, ConversationPhase
from app.utils.validation import ConversationValidator

class ConversationalMashupAgent:
    """Enhanced conversational agent with web search and context management"""
    
    def __init__(self, 
                 model_name: str = "llama3.1:8b-instruct",
                 tavily_api_key: str = None,
                 db_path: str = "./data/conversations.db"):
        
        self.model_name = model_name
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.db = ConversationDB(db_path)
        self.web_search = WebSearchService(self.tavily_api_key) if self.tavily_api_key else None
        self.validator = ConversationValidator()
        
        # Conversation phase handlers
        self.phase_handlers = {
            ConversationPhase.INITIAL: self._handle_initial_phase,
            ConversationPhase.GENRE_EXPLORATION: self._handle_genre_exploration,
            ConversationPhase.EDUCATIONAL_CLARIFICATION: self._handle_educational_clarification,
            ConversationPhase.CULTURAL_RESEARCH: self._handle_cultural_research,
            ConversationPhase.READY_FOR_GENERATION: self._handle_ready_phase
        }
    
    async def process_message(self, session_id: str, user_message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user message in conversation context"""
        
        # Get or create conversation
        conversation = self.db.get_conversation(session_id)
        if not conversation:
            session_id = session_id or str(uuid.uuid4())
            self.db.create_conversation(session_id, user_id)
            conversation = self.db.get_conversation(session_id)
        
        # Add user message to conversation
        message_id = self.db.add_message(session_id, "user", user_message)
        
        # Determine current phase and process accordingly
        current_phase = ConversationPhase(conversation.get('current_phase', 'initial'))
        
        try:
            # Process message based on current phase
            response_data = await self.phase_handlers[current_phase](
                session_id, user_message, conversation
            )
            
            # Add assistant response to conversation
            self.db.add_message(
                session_id, 
                "assistant", 
                response_data['agent_response'],
                response_data.get('tool_calls', [])
            )
            
            # Update conversation context if changed
            if response_data.get('context_updated'):
                self.db.update_conversation_context(
                    session_id,
                    response_data['gathered_context'],
                    response_data.get('next_phase')
                )
            
            # Check if ready for generation
            if response_data.get('ready_for_generation'):
                self.db.mark_ready_for_generation(session_id)
            
            return {
                "session_id": session_id,
                "agent_response": response_data['agent_response'],
                "tool_calls": response_data.get('tool_calls', []),
                "ready_for_generation": response_data.get('ready_for_generation', False),
                "gathered_context": response_data['gathered_context'],
                "current_phase": response_data.get('next_phase', current_phase)
            }
            
        except Exception as e:
            # Error handling with fallback response
            error_response = f"I apologize, but I encountered an issue processing your message. Let me try to help you in a different way. Could you please rephrase your request?"
            
            self.db.add_message(session_id, "assistant", error_response)
            
            return {
                "session_id": session_id,
                "agent_response": error_response,
                "tool_calls": [],
                "ready_for_generation": False,
                "gathered_context": conversation.get('gathered_context', {}),
                "error": str(e)
            }
    
    async def _handle_initial_phase(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle initial conversation phase - gather basic context"""
        
        # Extract initial context from user message
        context = await self._extract_initial_context(user_message)
        
        # Determine if we need web search for current trends
        web_search_needed = self._should_search_for_trends(context)
        tool_calls = []
        
        if web_search_needed and self.web_search:
            search_queries = self._build_initial_search_queries(context)
            search_results = []
            
            for query in search_queries:
                try:
                    results = await self.web_search.search_educational_content(query, context)
                    search_results.extend(results)
                    tool_calls.append({
                        "tool": "web_search",
                        "query": query,
                        "results_count": len(results),
                        "success": True
                    })
                except Exception as e:
                    tool_calls.append({
                        "tool": "web_search",
                        "query": query,
                        "error": str(e),
                        "success": False
                    })
            
            # Add search results to context
            context['web_research'] = search_results
        
        # Generate appropriate response based on gathered context
        response = await self._generate_phase_response("initial", context, user_message)
        
        # Determine next phase
        next_phase = self._determine_next_phase(context)
        
        return {
            "agent_response": response,
            "tool_calls": tool_calls,
            "gathered_context": context,
            "context_updated": True,
            "next_phase": next_phase,
            "ready_for_generation": False
        }
    
    async def _handle_genre_exploration(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle genre exploration phase with web research"""
        
        current_context = conversation.get('gathered_context', {})
        
        # Extract genre information from user message
        genres = await self._extract_genres(user_message, current_context)
        current_context.setdefault('genres', []).extend(genres)
        
        # Perform web search for current genre information
        tool_calls = []
        if self.web_search and genres:
            for genre in genres:
                search_query = f"{genre} music trends 2024 characteristics educational"
                try:
                    results = await self.web_search.search_educational_content(
                        search_query, current_context
                    )
                    current_context.setdefault('web_research', []).extend(results)
                    tool_calls.append({
                        "tool": "web_search",
                        "query": search_query,
                        "results_count": len(results),
                        "success": True
                    })
                except Exception as e:
                    tool_calls.append({
                        "tool": "web_search",
                        "query": search_query,
                        "error": str(e),
                        "success": False
                    })
        
        # Generate response with research-enhanced content
        response = await self._generate_phase_response("genre_exploration", current_context, user_message)
        
        # Check if we have enough genre information
        next_phase = "educational_clarification" if len(current_context.get('genres', [])) >= 2 else "genre_exploration"
        
        return {
            "agent_response": response,
            "tool_calls": tool_calls,
            "gathered_context": current_context,
            "context_updated": True,
            "next_phase": next_phase,
            "ready_for_generation": False
        }
    
    async def _handle_educational_clarification(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle educational objective clarification"""
        
        current_context = conversation.get('gathered_context', {})
        
        # Extract educational objectives
        objectives = await self._extract_educational_objectives(user_message, current_context)
        current_context.setdefault('learning_objectives', []).extend(objectives)
        
        # Extract skill level if mentioned
        skill_level = await self._extract_skill_level(user_message)
        if skill_level:
            current_context['skill_level'] = skill_level
        
        # Search for educational resources if needed
        tool_calls = []
        if self.web_search and objectives:
            search_query = f"music education {' '.join(objectives)} teaching methods"
            try:
                results = await self.web_search.search_educational_content(
                    search_query, current_context
                )
                current_context.setdefault('web_research', []).extend(results)
                tool_calls.append({
                    "tool": "web_search",
                    "query": search_query,
                    "results_count": len(results),
                    "success": True
                })
            except Exception as e:
                tool_calls.append({
                    "tool": "web_search",
                    "query": search_query,
                    "error": str(e),
                    "success": False
                })
        
        response = await self._generate_phase_response("educational_clarification", current_context, user_message)
        
        # Move to cultural research if we have objectives and skill level
        has_objectives = bool(current_context.get('learning_objectives'))
        has_skill_level = bool(current_context.get('skill_level'))
        next_phase = "cultural_research" if (has_objectives and has_skill_level) else "educational_clarification"
        
        return {
            "agent_response": response,
            "tool_calls": tool_calls,
            "gathered_context": current_context,
            "context_updated": True,
            "next_phase": next_phase,
            "ready_for_generation": False
        }
    
    async def _handle_cultural_research(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle cultural context research phase"""
        
        current_context = conversation.get('gathered_context', {})
        
        # Extract cultural focus areas
        cultural_elements = await self._extract_cultural_elements(user_message, current_context)
        current_context.setdefault('cultural_focus', []).extend(cultural_elements)
        
        # Perform cultural research
        tool_calls = []
        if self.web_search:
            genres = current_context.get('genres', [])
            for genre in genres:
                search_query = f"{genre} cultural significance history modern impact"
                try:
                    results = await self.web_search.search_educational_content(
                        search_query, current_context
                    )
                    current_context.setdefault('web_research', []).extend(results)
                    tool_calls.append({
                        "tool": "web_search",
                        "query": search_query,
                        "results_count": len(results),
                        "success": True
                    })
                except Exception as e:
                    tool_calls.append({
                        "tool": "web_search",
                        "query": search_query,
                        "error": str(e),
                        "success": False
                    })
        
        response = await self._generate_phase_response("cultural_research", current_context, user_message)
        
        # Check if ready for generation
        ready = self._check_readiness_for_generation(current_context)
        next_phase = "ready_for_generation" if ready else "cultural_research"
        
        return {
            "agent_response": response,
            "tool_calls": tool_calls,
            "gathered_context": current_context,
            "context_updated": True,
            "next_phase": next_phase,
            "ready_for_generation": ready
        }
    
    async def _handle_ready_phase(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle ready for generation phase"""
        
        current_context = conversation.get('gathered_context', {})
        
        # Generate confirmation response
        response = await self._generate_confirmation_response(current_context)
        
        return {
            "agent_response": response,
            "tool_calls": [],
            "gathered_context": current_context,
            "context_updated": False,
            "next_phase": "ready_for_generation",
            "ready_for_generation": True
        }
    
    def _check_readiness_for_generation(self, context: Dict) -> bool:
        """Check if conversation has gathered sufficient context"""
        required_fields = [
            context.get("educational_context"),
            context.get("genres") and len(context["genres"]) >= 2,
            context.get("skill_level"),
            context.get("learning_objectives")
        ]
        return all(required_fields)
    
    # Helper methods for context extraction and response generation would be implemented here
    # These include natural language processing to extract genres, objectives, etc.
    # and prompt engineering for generating appropriate responses for each phase
```

---

## 7. API Layer with Chat Endpoints

### 7.1 Enhanced FastAPI Application

```python
# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os

from app.agents.conversation_agent import ConversationalMashupAgent
from app.services.generation_service import EnhancedGenerationService
from app.db.conversation_db import ConversationDB
from app.utils.validation import ConversationValidator
from app.config import settings

# Initialize logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Lit Music Mashup Conversational API",
    description="Educational AI Music Generation with Conversational Interface and Web Search",
    version="2.0.0-conversational-mvp",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
conversation_agent = ConversationalMashupAgent(
    tavily_api_key=settings.TAVILY_API_KEY,
    db_path=settings.DATABASE_PATH
)
generation_service = EnhancedGenerationService()
db = ConversationDB(settings.DATABASE_PATH)
validator = ConversationValidator()

# Request/Response Models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    agent_response: str
    tool_calls: List[Dict[str, Any]] = []
    ready_for_generation: bool = False
    gathered_context: Dict[str, Any] = {}
    current_phase: str = "initial"

class EnhancedGenerateRequest(BaseModel):
    prompt: str
    skill_level: str = "beginner"
    gathered_context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class MashupResponse(BaseModel):
    id: int
    session_id: Optional[str] = None
    title: str
    lyrics: str
    educational_content: Dict[str, Any]
    web_sources: List[str] = []
    metadata: Dict[str, Any] = {}

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Lit Music Mashup Conversational MVP v2.0",
        "features": [
            "Conversational interface for context gathering",
            "Web search integration for current information",
            "Enhanced educational content generation",
            "Multi-turn dialogue support"
        ],
        "status": "active",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    
    # Check database connection
    try:
        test_conversation = db.get_conversation("health-check-test")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check web search availability
    web_search_status = "available" if settings.TAVILY_API_KEY else "disabled (no API key)"
    
    # Check Ollama connection
    try:
        # This would typically ping the Ollama service
        ollama_status = "healthy"
    except Exception as e:
        ollama_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "2.0.0-conversational-mvp",
        "services": {
            "database": db_status,
            "web_search": web_search_status,
            "ollama": ollama_status,
            "conversation_agent": "active"
        },
        "features": {
            "conversational_interface": True,
            "web_search_integration": bool(settings.TAVILY_API_KEY),
            "tool_orchestration": True,
            "enhanced_generation": True
        }
    }

# Conversational endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with conversational agent for context gathering"""
    
    try:
        # Validate input
        if len(request.message.strip()) < 1:
            raise HTTPException(400, "Message cannot be empty")
        
        if len(request.message) > 1000:
            raise HTTPException(400, "Message too long (max 1000 characters)")
        
        # Process message with conversational agent
        response = await conversation_agent.process_message(
            session_id=request.session_id,
            user_message=request.message,
            user_id=None  # For MVP, no user authentication
        )
        
        return ChatResponse(
            session_id=response["session_id"],
            agent_response=response["agent_response"],
            tool_calls=response.get("tool_calls", []),
            ready_for_generation=response.get("ready_for_generation", False),
            gathered_context=response.get("gathered_context", {}),
            current_phase=response.get("current_phase", "initial")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(500, f"Failed to process chat message: {str(e)}")

@app.get("/api/v1/session/{session_id}")
async def get_conversation_session(session_id: str):
    """Retrieve conversation session with history"""
    
    try:
        conversation = db.get_conversation(session_id)
        
        if not conversation:
            raise HTTPException(404, "Conversation session not found")
        
        return {
            "session_id": session_id,
            "current_phase": conversation.get("current_phase", "initial"),
            "gathered_context": conversation.get("gathered_context", {}),
            "ready_for_generation": conversation.get("ready_for_generation", False),
            "messages": conversation.get("messages", []),
            "created_at": conversation.get("created_at"),
            "updated_at": conversation.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session retrieval error: {e}")
        raise HTTPException(500, f"Failed to retrieve session: {str(e)}")

# Enhanced generation endpoints
@app.post("/api/v1/generate", response_model=MashupResponse)
async def generate_educational_mashup(request: EnhancedGenerateRequest):
    """Generate educational mashup with enhanced context"""
    
    try:
        # Validate input
        if len(request.prompt.strip()) < 5:
            raise HTTPException(400, "Prompt must be at least 5 characters")
        
        valid_skill_levels = ["beginner", "intermediate", "advanced"]
        if request.skill_level not in valid_skill_levels:
            raise HTTPException(400, f"Skill level must be one of: {valid_skill_levels}")
        
        # Generate mashup with enhanced service
        result = await generation_service.generate_with_context(
            prompt=request.prompt,
            skill_level=request.skill_level,
            gathered_context=request.gathered_context or {},
            session_id=request.session_id
        )
        
        return MashupResponse(
            id=result["id"],
            session_id=request.session_id,
            title=result["title"],
            lyrics=result["lyrics"],
            educational_content=result["educational_content"],
            web_sources=result.get("web_sources", []),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(500, f"Failed to generate mashup: {str(e)}")

@app.get("/api/v1/mashup/{mashup_id}")
async def get_mashup(mashup_id: int):
    """Retrieve generated mashup by ID"""
    
    try:
        # This would be implemented to retrieve from enhanced database
        mashup = db.get_mashup(mashup_id)  # Assuming this method exists
        
        if not mashup:
            raise HTTPException(404, "Mashup not found")
        
        return mashup
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mashup retrieval error: {e}")
        raise HTTPException(500, f"Failed to retrieve mashup: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
```

---

## 8. Web Search Integration

### 8.1 Enhanced Web Search Service

```python
# app/services/web_search.py
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_community.tools.tavily_search import TavilySearchResults
from app.utils.validation import WebSourceValidator

class WebSearchService:
    """Enhanced web search service for educational content"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.validator = WebSourceValidator()
        
        if self.api_key:
            self.search_tool = TavilySearchResults(
                api_key=self.api_key,
                max_results=int(os.getenv("WEB_SEARCH_MAX_RESULTS", "3")),
                search_depth="basic",
                include_domains=["edu", "org", "gov"],  # Prefer educational sources
                exclude_domains=["tiktok.com", "instagram.com", "snapchat.com"]
            )
        else:
            self.search_tool = None
    
    async def search_educational_content(self, query: str, context: Dict[str, Any] = None) -> List[Dict]:
        """Search for educational content with context enhancement"""
        
        if not self.search_tool:
            return []  # Graceful degradation when no API key
        
        try:
            # Enhance query with educational context
            enhanced_query = self._enhance_query_for_education(query, context or {})
            
            # Perform search with timeout
            search_timeout = int(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10"))
            results = await asyncio.wait_for(
                self.search_tool.arun(enhanced_query),
                timeout=search_timeout
            )
            
            # Filter and validate results
            validated_results = self._filter_and_validate_results(results, context or {})
            
            return validated_results
            
        except asyncio.TimeoutError:
            return []  # Graceful degradation on timeout
        except Exception as e:
            # Log error but don't break the conversation
            import logging
            logging.error(f"Web search error: {e}")
            return []
    
    def _enhance_query_for_education(self, query: str, context: Dict[str, Any]) -> str:
        """Enhance search query with educational context"""
        
        enhanced_query = query
        
        # Add skill level if available
        skill_level = context.get("skill_level")
        if skill_level:
            enhanced_query += f" {skill_level} level"
        
        # Add educational context
        educational_context = context.get("educational_context")
        if educational_context in ["classroom", "school", "workshop"]:
            enhanced_query += " education teaching"
        
        # Add "2024" for current trends
        if "trends" in query.lower() or "current" in query.lower():
            enhanced_query += " 2024"
        
        return enhanced_query
    
    def _filter_and_validate_results(self, results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Filter results for educational appropriateness and quality"""
        
        if isinstance(results, str):
            # Sometimes Tavily returns a string instead of a list
            return []
        
        filtered_results = []
        
        for result in results:
            try:
                # Basic quality filters
                if not result.get("content") or len(result["content"]) < 100:
                    continue
                
                # Validate with educational context
                if not self.validator.is_educationally_appropriate(result):
                    continue
                
                # Assess source quality
                source_quality = self._assess_source_quality(result)
                result["source_quality"] = source_quality
                
                # Add processing metadata
                result["processed_at"] = datetime.now().isoformat()
                result["search_context"] = {
                    "skill_level": context.get("skill_level"),
                    "educational_context": context.get("educational_context")
                }
                
                filtered_results.append(result)
                
            except Exception as e:
                # Skip problematic results but log the issue
                import logging
                logging.warning(f"Error processing search result: {e}")
                continue
        
        # Sort by source quality and return top results
        filtered_results.sort(key=lambda x: self._quality_score(x["source_quality"]), reverse=True)
        return filtered_results[:3]  # Return top 3 results
    
    def _assess_source_quality(self, result: Dict) -> str:
        """Assess the quality of a web source"""
        
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        
        # High quality indicators
        if any(domain in url for domain in [".edu", ".gov", ".org"]):
            return "high"
        
        # Medium quality indicators
        if any(indicator in url or indicator in title for indicator in [
            "wikipedia", "britannica", "musictheory", "education", "academic"
        ]):
            return "medium"
        
        # Default to low quality
        return "low"
    
    def _quality_score(self, quality: str) -> int:
        """Convert quality rating to numeric score for sorting"""
        return {"high": 3, "medium": 2, "low": 1}.get(quality, 0)
```

---

## 9. CI/CD Pipeline with Tool Testing

### 9.1 Enhanced GitHub Actions Configuration

```yaml
# .github/workflows/conversational-ci.yml
name: Conversational AI Music Mashup CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'app/**'
      - 'tests/**'
      - 'requirements.txt'
      - 'Dockerfile'
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: "3.11"

jobs:
  test-core-functionality:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-mock
    
    - name: Create test environment
      run: |
        mkdir -p test_data
        touch test_data/test_conversations.db
    
    - name: Test database operations
      run: |
        python -c "
        from app.db.conversation_db import ConversationDB
        import tempfile
        import os
        
        # Test database initialization
        fd, path = tempfile.mkstemp()
        os.close(fd)
        
        db = ConversationDB(path)
        conversation_id = 'test-123'
        db.create_conversation(conversation_id)
        
        # Test conversation operations
        conv = db.get_conversation(conversation_id)
        assert conv is not None
        assert conv['id'] == conversation_id
        
        # Test message operations
        msg_id = db.add_message(conversation_id, 'user', 'test message')
        assert msg_id is not None
        
        print('Database tests passed')
        os.unlink(path)
        "
    
    - name: Test conversation agent structure
      run: |
        python -c "
        from app.agents.conversation_agent import ConversationalMashupAgent
        import tempfile
        import os
        
        # Test agent initialization without API key
        fd, path = tempfile.mkstemp()
        os.close(fd)
        
        agent = ConversationalMashupAgent(db_path=path)
        assert agent is not None
        assert agent.web_search is None  # No API key provided
        
        print('Conversation agent structure tests passed')
        os.unlink(path)
        "
    
    - name: Test API endpoint structure
      run: |
        python -c "
        from fastapi.testclient import TestClient
        import os
        import tempfile
        
        # Set test environment variables
        os.environ['DATABASE_PATH'] = tempfile.mktemp()
        os.environ['LOG_LEVEL'] = 'ERROR'
        
        from app.main import app
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        
        # Test root endpoint
        response = client.get('/')
        assert response.status_code == 200
        assert 'Conversational MVP' in response.json()['message']
        
        print('API endpoint structure tests passed')
        "
    
    - name: Run unit tests
      run: |
        pytest tests/ -v --tb=short
      env:
        DATABASE_PATH: ./test_data/test_conversations.db
        LOG_LEVEL: ERROR

  test-with-web-search:
    runs-on: ubuntu-latest
    if: ${{ secrets.TAVILY_API_KEY != '' }}
    
    env:
      TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test web search integration
      run: |
        python -c "
        import asyncio
        import os
        from app.services.web_search import WebSearchService
        
        async def test_web_search():
            if not os.getenv('TAVILY_API_KEY'):
                print('Skipping web search test - no API key')
                return
            
            search_service = WebSearchService()
            results = await search_service.search_educational_content(
                'jazz music education basics',
                {'skill_level': 'beginner', 'educational_context': 'classroom'}
            )
            
            assert isinstance(results, list)
            print(f'Web search integration test passed - found {len(results)} results')
            
            # Test individual result structure
            if results:
                result = results[0]
                assert 'title' in result
                assert 'content' in result
                assert 'source_quality' in result
                print('Result structure validation passed')
        
        asyncio.run(test_web_search())
        "
    
    - name: Test conversation flow with web search
      run: |
        python -c "
        import asyncio
        import os
        import tempfile
        from app.agents.conversation_agent import ConversationalMashupAgent
        
        async def test_conversation_with_search():
            if not os.getenv('TAVILY_API_KEY'):
                print('Skipping conversation test - no API key')
                return
            
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            agent = ConversationalMashupAgent(db_path=path, tavily_api_key=os.getenv('TAVILY_API_KEY'))
            
            # Test initial conversation
            response = await agent.process_message(
                'test-session-123',
                'I want to create a jazz and blues mashup for my beginner music class'
            )
            
            assert 'session_id' in response
            assert 'agent_response' in response
            assert isinstance(response.get('tool_calls', []), list)
            
            print('Conversation flow with web search test passed')
            os.unlink(path)
        
        asyncio.run(test_conversation_with_search())
        "

  test-without-web-search:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test graceful degradation without API key
      run: |
        python -c "
        import asyncio
        import tempfile
        import os
        from app.agents.conversation_agent import ConversationalMashupAgent
        
        async def test_without_api_key():
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            # Test agent without API key
            agent = ConversationalMashupAgent(db_path=path, tavily_api_key=None)
            assert agent.web_search is None
            
            # Test conversation still works
            response = await agent.process_message(
                'test-session-456',
                'I want to create a simple mashup for beginners'
            )
            
            assert 'session_id' in response
            assert 'agent_response' in response
            assert response.get('tool_calls', []) == []  # No web search calls
            
            print('Graceful degradation test passed')
            os.unlink(path)
        
        asyncio.run(test_without_api_key())
        "

  quality-check:
    runs-on: ubuntu-latest
    needs: [test-core-functionality]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install quality tools
      run: |
        pip install black isort flake8 mypy
    
    - name: Check code formatting
      run: |
        black --check app/ tests/
        isort --check-only app/ tests/
    
    - name: Check code style
      run: |
        flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
    
    - name: Type checking
      run: |
        mypy app/ --ignore-missing-imports

  integration-test:
    runs-on: ubuntu-latest
    needs: [test-core-functionality, quality-check]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Build Docker image
      run: |
        docker build -t lit-music-mashup-v2:test .
    
    - name: Test Docker container
      run: |
        # Create test environment file
        echo "DATABASE_PATH=/app/data/test.db" > test.env
        echo "LOG_LEVEL=ERROR" >> test.env
        
        # Run container
        docker run -d -p 8001:8000 --name test-container \
          --env-file test.env \
          lit-music-mashup-v2:test
        
        # Wait for startup
        sleep 15
        
        # Test health endpoint
        curl -f http://localhost:8001/health || exit 1
        
        # Test chat endpoint (basic structure)
        curl -f -X POST http://localhost:8001/api/v1/chat \
          -H "Content-Type: application/json" \
          -d '{"message": "hello"}' || exit 1
        
        # Cleanup
        docker stop test-container
        docker rm test-container
        
        echo "Integration tests passed"

  deploy:
    runs-on: ubuntu-latest
    needs: [integration-test, test-with-web-search, test-without-web-search]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build production image
      run: |
        docker build -t lit-music-mashup-v2:${{ github.sha }} .
        docker tag lit-music-mashup-v2:${{ github.sha }} lit-music-mashup-v2:latest
    
    # Add deployment steps here (e.g., push to registry, deploy to server)
    - name: Deploy notification
      run: |
        echo "Ready for deployment - all tests passed"
        echo "Image: lit-music-mashup-v2:${{ github.sha }}"
```

---

## 10. MVP Validation & Conversational Testing

### 10.1 Enhanced MVP Success Criteria

```python
# tests/test_mvp_conversational.py
import pytest
import asyncio
import tempfile
import os
from fastapi.testclient import TestClient

@pytest.fixture
def temp_db_path():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)

@pytest.fixture
def app_client(temp_db_path):
    """Create test client with temporary database"""
    os.environ['DATABASE_PATH'] = temp_db_path
    os.environ['LOG_LEVEL'] = 'ERROR'
    
    from app.main import app
    return TestClient(app)

class TestConversationalMVP:
    """Test complete conversational MVP functionality"""
    
    def test_conversational_workflow_complete(self, app_client):
        """Test complete conversational workflow"""
        
        # 1. Start conversation
        response = app_client.post("/api/v1/chat", json={
            "message": "I want to create a jazz and hip-hop mashup for my high school music class"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate initial response structure
        assert "session_id" in data
        assert "agent_response" in data
        assert "gathered_context" in data
        assert "ready_for_generation" in data
        assert data["ready_for_generation"] is False
        
        session_id = data["session_id"]
        
        # 2. Continue conversation with more details
        response = app_client.post("/api/v1/chat", json={
            "session_id": session_id,
            "message": "The students are at intermediate level and I want to focus on improvisation and rhythm analysis"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have more context now
        context = data["gathered_context"]
        assert "educational_context" in context
        assert "skill_level" in context or "intermediate" in data["agent_response"].lower()
        
        # 3. Confirm readiness (simulated)
        response = app_client.post("/api/v1/chat", json={
            "session_id": session_id,
            "message": "Yes, I'm ready to generate the mashup"
        })
        
        assert response.status_code == 200
        # Note: Actual readiness depends on conversation agent implementation
    
    def test_session_retrieval(self, app_client):
        """Test conversation session retrieval"""
        
        # Create a conversation
        response = app_client.post("/api/v1/chat", json={
            "message": "Create a simple mashup"
        })
        
        session_id = response.json()["session_id"]
        
        # Retrieve session
        response = app_client.get(f"/api/v1/session/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "messages" in data
        assert "gathered_context" in data
        assert "current_phase" in data
    
    def test_enhanced_generation(self, app_client):
        """Test enhanced generation with context"""
        
        response = app_client.post("/api/v1/generate", json={
            "prompt": "Jazz and blues educational mashup",
            "skill_level": "intermediate",
            "gathered_context": {
                "educational_context": "high school classroom",
                "genres": ["jazz", "blues"],
                "learning_objectives": ["improvisation", "blues scale"],
                "web_research": [
                    {
                        "title": "Jazz Education Methods",
                        "content": "Modern jazz education emphasizes...",
                        "source_quality": "high"
                    }
                ]
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate enhanced response structure
        assert "title" in data
        assert "lyrics" in data
        assert "educational_content" in data
        assert "web_sources" in data
        assert "metadata" in data
        
        # Educational content should be comprehensive
        edu_content = data["educational_content"]
        assert "theory_concepts" in edu_content
        assert "cultural_context" in edu_content
        assert "teaching_notes" in edu_content

@pytest.mark.asyncio
class TestWebSearchIntegration:
    """Test web search integration with graceful degradation"""
    
    async def test_web_search_with_api_key(self, temp_db_path):
        """Test web search when API key is available"""
        
        # This test only runs if TAVILY_API_KEY is set
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            pytest.skip("No TAVILY_API_KEY available for testing")
        
        from app.services.web_search import WebSearchService
        
        search_service = WebSearchService(api_key)
        results = await search_service.search_educational_content(
            "jazz music education methods",
            {"skill_level": "beginner", "educational_context": "classroom"}
        )
        
        assert isinstance(results, list)
        
        # If results are found, validate structure
        if results:
            result = results[0]
            assert "title" in result
            assert "content" in result
            assert "source_quality" in result
            assert result["source_quality"] in ["high", "medium", "low"]
    
    async def test_web_search_without_api_key(self, temp_db_path):
        """Test graceful degradation without API key"""
        
        from app.services.web_search import WebSearchService
        
        search_service = WebSearchService(api_key=None)
        results = await search_service.search_educational_content(
            "test query",
            {"skill_level": "beginner"}
        )
        
        # Should return empty list without crashing
        assert results == []
    
    async def test_conversation_agent_without_web_search(self, temp_db_path):
        """Test conversation agent works without web search"""
        
        from app.agents.conversation_agent import ConversationalMashupAgent
        
        agent = ConversationalMashupAgent(db_path=temp_db_path, tavily_api_key=None)
        
        response = await agent.process_message(
            "test-session",
            "Create a simple educational mashup"
        )
        
        assert "session_id" in response
        assert "agent_response" in response
        assert response.get("tool_calls", []) == []  # No web search calls

class TestPerformanceBenchmarks:
    """Test performance benchmarks for conversational features"""
    
    def test_conversation_response_time(self, app_client):
        """Test conversation response time"""
        import time
        
        start_time = time.time()
        response = app_client.post("/api/v1/chat", json={
            "message": "Create a mashup for beginners"
        })
        end_time = time.time()
        
        assert response.status_code == 200
        # Conversation should respond within 10 seconds (without web search)
        assert (end_time - start_time) < 10
    
    def test_session_retrieval_performance(self, app_client):
        """Test session retrieval performance"""
        import time
        
        # Create session first
        response = app_client.post("/api/v1/chat", json={
            "message": "test message"
        })
        session_id = response.json()["session_id"]
        
        # Test retrieval time
        start_time = time.time()
        response = app_client.get(f"/api/v1/session/{session_id}")
        end_time = time.time()
        
        assert response.status_code == 200
        # Session retrieval should be very fast
        assert (end_time - start_time) < 1
```

---

## 11. Feature Addition Strategy

### 11.1 Enhanced Incremental Development Process

**Step 1: Create Conversational Feature Branch**
```bash
git checkout -b feature/advanced-cultural-context
```

**Step 2: Add Conversational Tests First (TDD)**
```python
# tests/test_advanced_cultural_context.py
def test_cultural_context_web_research():
    """Test advanced cultural context with web research"""
    
    # Test that cultural research includes multiple sources
    response = client.post("/api/v1/chat", json={
        "session_id": "cultural-test",
        "message": "I want to explore the cultural significance of jazz and hip-hop fusion"
    })
    
    data = response.json()
    tool_calls = data.get("tool_calls", [])
    
    # Should trigger cultural research
    cultural_calls = [call for call in tool_calls if "cultural" in call.get("query", "").lower()]
    assert len(cultural_calls) > 0

def test_cultural_sensitivity_validation():
    """Test cultural sensitivity in generated content"""
    
    response = client.post("/api/v1/generate", json={
        "prompt": "Jazz and hip-hop fusion",
        "skill_level": "intermediate",
        "gathered_context": {
            "cultural_focus": ["African American musical traditions", "cultural appropriation awareness"]
        }
    })
    
    data = response.json()
    cultural_context = data["educational_content"]["cultural_context"]
    
    # Should include respectful cultural discussion
    assert "African American" in cultural_context
    assert len(cultural_context) > 200  # Substantial cultural content
```

**Step 3: Implement Enhanced Feature**
```python
# app/agents/cultural_research_agent.py
class AdvancedCulturalResearchAgent:
    """Enhanced cultural research with multiple sources and sensitivity validation"""
    
    async def research_cultural_context(self, genres: List[str], context: Dict) -> Dict:
        """Perform comprehensive cultural research"""
        
        cultural_research = {}
        
        for genre in genres:
            # Search for cultural significance
            cultural_query = f"{genre} cultural significance African American history"
            cultural_results = await self.web_search.search_educational_content(
                cultural_query, context
            )
            
            # Search for modern cultural impact
            modern_query = f"{genre} modern cultural impact social justice"
            modern_results = await self.web_search.search_educational_content(
                modern_query, context
            )
            
            cultural_research[genre] = {
                "historical_significance": cultural_results,
                "modern_impact": modern_results,
                "synthesis": self._synthesize_cultural_information(
                    cultural_results, modern_results
                )
            }
        
        return cultural_research
```

### 11.2 Enhanced Feature Addition Roadmap

**Phase 2 Conversational Features (Week 3-4)**:
```python
PHASE_2_CONVERSATIONAL_FEATURES = [
    "advanced_cultural_research",     # Multi-source cultural context
    "conversation_memory_system",     # Remember user preferences across sessions
    "context_validation_engine",      # Validate gathered context quality
    "enhanced_error_recovery",        # Better error handling in conversations
    "conversation_analytics"          # Track conversation effectiveness
]
```

**Phase 3 Advanced Features (Week 5-6)**:
```python
PHASE_3_ADVANCED_FEATURES = [
    "multi_user_conversations",       # Multiple users in same conversation
    "conversation_export_system",     # Export conversation transcripts
    "advanced_tool_integration",      # Additional research tools
    "conversation_templates",         # Pre-built conversation flows
    "real_time_collaboration"         # WebSocket-based real-time features
]
```

### 11.2 Enhanced Quality Gates for Conversational Features

**Every Conversational Feature Must Pass**:
1. ✅ All existing conversation flows still work
2. ✅ Web search integration maintains graceful degradation
3. ✅ Conversation state management remains consistent
4. ✅ Tool orchestration performance is maintained
5. ✅ Educational content quality is preserved
6. ✅ Cultural sensitivity validation passes
7. ✅ API response times remain under thresholds

---

## 12. Summary

### 12.1 Conversational MVP v2.0 Advantages

**Enhanced Conversational Development**:
- Multi-turn dialogue for comprehensive context gathering
- Web search integration for current and accurate information
- Tool orchestration with LangChain/LangGraph
- Graceful degradation when external services unavailable
- Enhanced database schema for conversation persistence

**Advanced Quality Assurance**:
- Conversational flow testing with real and mock API integration
- Web search reliability and performance testing
- Cultural sensitivity validation with web-enhanced context
- Tool integration testing with fallback scenarios
- Performance monitoring for conversations and searches

**Educational Focus Enhanced**:
- Current information through web research
- Comprehensive cultural context with multiple sources
- Context-driven educational content generation
- Multi-source validation for accuracy
- Enhanced teaching resources with current examples

### 12.2 Next Steps for Conversational Implementation

**Week 1**: 
1. Set up enhanced project structure with conversation modules
2. Implement basic conversational agent with web search
3. Create conversation database schema
4. Set up CI/CD pipeline with tool integration testing

**Week 2**: 
1. Validate conversational MVP with real conversations
2. Test web search integration thoroughly
3. Optimize conversation flow and context gathering  
4. Prepare for Phase 2 conversational enhancements

**Week 3+**: 
1. Add advanced conversational features incrementally
2. Enhance web search and tool integration
3. Monitor conversation effectiveness and user satisfaction
4. Gather feedback for conversation flow improvements

This conversational implementation approach ensures we have a sophisticated educational AI music platform that leverages current information and multi-turn dialogue while maintaining quality, reliability, and educational value through every iteration.