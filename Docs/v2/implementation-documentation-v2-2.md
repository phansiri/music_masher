# Lit Music Mashup - Implementation Documentation v2.0
## Educational AI Music Generation Platform - Conversational MVP-First Approach

---

### Document Overview
This implementation guide provides a conversational, MVP-first approach to building the Lit Music Mashup educational platform. The documentation prioritizes **core conversational functionality delivery** with web search capabilities and incremental feature addition through CI/CD validation using modern Python tooling with `uv`.

**Key Principle**: Build a conversational educational mashup generator with web search integration first, then add features through test-driven development with GitHub Actions CI/CD ensuring no regression.

---

## Table of Contents

1. [Conversational MVP-First Development Philosophy](#1-conversational-mvp-first-development-philosophy)
2. [Enhanced Minimal Viable Product Scope](#2-enhanced-minimal-viable-product-scope)
3. [Development Environment with UV and Tool Integration](#3-development-environment-with-uv-and-tool-integration)
4. [Conversational Architecture Implementation](#4-conversational-architecture-implementation)
5. [Enhanced Database Layer](#5-enhanced-database-layer)
6. [Conversational Agent System](#6-conversational-agent-system)
7. [Async API Layer with Chat Endpoints](#7-async-api-layer-with-chat-endpoints)
8. [Web Search Integration](#8-web-search-integration)
9. [CI/CD Pipeline with UV and Tool Testing](#9-cicd-pipeline-with-uv-and-tool-testing)
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
- Modern Python tooling with `uv` for fast dependency management

**Test-Driven Conversational Development**:
- Every conversational flow requires passing tests
- Web search integration tested with mock and real APIs
- GitHub Actions CI/CD prevents regression
- Tool integration validates graceful degradation
- Performance benchmarks for conversation and search

### 1.2 Enhanced Development Phases

#### **Phase 1: Conversational MVP (Week 1-2)**
- ✅ Async chat API endpoints: `POST /api/v1/chat` and `GET /api/v1/session/{id}`
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

### 2.2 Enhanced Technology Stack with UV

```yaml
# Enhanced tech stack for conversational MVP
Package Manager: uv (fast Python package manager)
Backend: FastAPI[standard] (includes uvicorn)
Database: SQLite (with conversation tables)
AI Framework: LangChain/LangGraph for tool orchestration
AI Models: Ollama + Llama 3.1 8B Instruct
Web Search: Tavily API (user-provided key)
Testing: pytest + pytest-asyncio
CI/CD: GitHub Actions with uv integration
Deployment: Docker (with uv optimization)
```

---

## 3. Development Environment with UV and Tool Integration

### 3.1 Enhanced Setup with UV

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create conversational project with uv
mkdir lit-music-mashup-v2
cd lit-music-mashup-v2

# Initialize Python project with uv
uv init --python 3.11

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

# Add core dependencies with uv
uv add "fastapi[standard]"  # Includes uvicorn and other standard dependencies
uv add langchain langgraph langchain-community
uv add tavily-python pydantic python-dotenv
uv add ollama

# Add development dependencies
uv add --dev pytest pytest-asyncio pytest-mock
uv add --dev black isort flake8 mypy
uv add --dev httpx  # For testing FastAPI apps
```

### 3.2 Project Configuration

```toml
# pyproject.toml (generated and enhanced by uv)
[project]
name = "lit-music-mashup-v2"
version = "2.0.0"
description = "Educational AI Music Generation Platform - Conversational MVP"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "fastapi[standard]>=0.104.1",
    "langchain>=0.1.0",
    "langgraph>=0.0.40",
    "langchain-community>=0.0.20",
    "tavily-python>=0.3.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "ollama>=0.1.7",
]
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.7.0",
    "httpx>=0.25.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.7.0",
    "httpx>=0.25.0",
]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 3.3 Environment Configuration

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

# Application settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3.4 Enhanced Docker Setup with UV

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run with uv
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (Enhanced with UV)
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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      
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
│           Async Conversational MVP Architecture         │
├─────────────────────────────────────────────────────────┤
│  FastAPI App (Async Modular Structure)                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ POST /api/v1/chat          - Async conversation    │ │
│  │ GET  /api/v1/session/{id}  - Async session get     │ │
│  │ POST /api/v1/generate      - Async generation      │ │
│  │ GET  /api/v1/mashup/{id}   - Async mashup get      │ │
│  │ GET  /health               - Async health check    │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Async Conversational Agent System (LangGraph)         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Components:                                         │ │
│  │ - Async Conversation Manager (state management)     │ │
│  │ - Async Context Gatherer (multi-turn dialogue)     │ │
│  │ - Async Tool Orchestrator (web search integration) │ │
│  │ - Async Educational Content Generator (enhanced)    │ │
│  │ - Async Validation Engine (conversation & content)  │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Async Tool Integration Layer                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ - Async Web Search Tool (Tavily API integration)   │ │
│  │ - Async Educational Resource Finder                 │ │
│  │ - Async Cultural Context Researcher                 │ │
│  │ - Async Music Theory Validator                      │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Local AI Models (Ollama)                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Llama 3.1 8B Instruct                              │ │
│  │ - Async conversation handling and context           │ │
│  │ - Async tool decision making and orchestration      │ │
│  │ - Async educational content generation              │ │
│  │ - Async web search result synthesis                 │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Async Enhanced SQLite Database                        │
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
├── pyproject.toml                  # UV project configuration
├── uv.lock                         # UV lock file
├── .env.example                    # Environment configuration template
├── Dockerfile                      # Container configuration with UV
├── docker-compose.yml              # Development environment
├── README.md                       # Project documentation
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # Async FastAPI application
│   ├── config.py                   # Configuration management
│   │
│   ├── api/                        # Async API layer
│   │   ├── __init__.py
│   │   ├── chat.py                 # Async conversation endpoints
│   │   ├── generate.py             # Async enhanced generation endpoints
│   │   └── health.py               # Async health checks
│   │
│   ├── agents/                     # Async conversational agents
│   │   ├── __init__.py
│   │   ├── conversation_agent.py   # Async main conversation agent
│   │   ├── context_gatherer.py     # Async context gathering logic
│   │   └── content_generator.py    # Async enhanced content generation
│   │
│   ├── db/                         # Async database layer
│   │   ├── __init__.py
│   │   ├── models.py               # Database models
│   │   ├── conversation_db.py      # Async conversation operations
│   │   └── mashup_db.py            # Async mashup operations
│   │
│   ├── services/                   # Async business logic
│   │   ├── __init__.py
│   │   ├── web_search.py           # Async web search integration
│   │   ├── conversation_service.py # Async conversation management
│   │   └── generation_service.py   # Async enhanced generation
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── validation.py           # Input/output validation
│       └── logging.py              # Logging configuration
│
├── tests/                          # Enhanced test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_conversation.py        # Async conversation flow tests
│   ├── test_web_search.py          # Async web search integration tests
│   ├── test_generation.py          # Async enhanced generation tests
│   └── test_api.py                 # Async API endpoint tests
│
└── .github/
    └── workflows/
        └── conversational-ci.yml   # Enhanced CI/CD with UV
```

---

## 5. Enhanced Database Layer

### 5.1 Async Conversation-Aware Database

```python
# app/db/conversation_db.py
import aiosqlite
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import asyncio

class ConversationPhase(str, Enum):
    INITIAL = "initial"
    GENRE_EXPLORATION = "genre_exploration"
    EDUCATIONAL_CLARIFICATION = "educational_clarification"
    CULTURAL_RESEARCH = "cultural_research"
    READY_FOR_GENERATION = "ready_for_generation"
    COMPLETED = "completed"

class AsyncConversationDB:
    def __init__(self, db_path: str = "./data/conversations.db"):
        self.db_path = db_path
        self._init_lock = asyncio.Lock()
        self._initialized = False
    
    async def init_db(self):
        """Create conversation-aware database schema"""
        async with self._init_lock:
            if self._initialized:
                return
            
            async with aiosqlite.connect(self.db_path) as conn:
                # Conversations table
                await conn.execute("""
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
                await conn.execute("""
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
                await conn.execute("""
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
                await conn.execute("""
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
                await conn.execute("""
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
                
                await conn.commit()
            
            self._initialized = True
    
    async def create_conversation(self, conversation_id: str, user_id: str = None) -> str:
        """Create new conversation session"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                INSERT INTO conversations (id, user_id, gathered_context)
                VALUES (?, ?, ?)
            """, (conversation_id, user_id, json.dumps({})))
            await conn.commit()
            return conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation with messages"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            
            # Get conversation
            async with conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ) as cursor:
                conversation = await cursor.fetchone()
            
            if not conversation:
                return None
            
            # Get messages
            async with conn.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            """, (conversation_id,)) as cursor:
                messages = await cursor.fetchall()
            
            # Parse JSON fields
            conv_data = dict(conversation)
            conv_data['gathered_context'] = json.loads(conv_data['gathered_context'] or '{}')
            
            messages_list = []
            for msg in messages:
                msg_dict = dict(msg)
                msg_dict['tool_calls'] = json.loads(msg_dict['tool_calls'] or '[]')
                messages_list.append(msg_dict)
            
            conv_data['messages'] = messages_list
            return conv_data
    
    async def add_message(self, conversation_id: str, role: str, content: str, tool_calls: List[Dict] = None) -> int:
        """Add message to conversation"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO messages (conversation_id, role, content, tool_calls)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, role, content, json.dumps(tool_calls or [])))
            await conn.commit()
            return cursor.lastrowid
    
    async def update_conversation_context(self, conversation_id: str, context: Dict, phase: str = None):
        """Update conversation context and phase"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            if phase:
                await conn.execute("""
                    UPDATE conversations 
                    SET gathered_context = ?, current_phase = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(context), phase, conversation_id))
            else:
                await conn.execute("""
                    UPDATE conversations 
                    SET gathered_context = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(context), conversation_id))
            await conn.commit()
    
    async def mark_ready_for_generation(self, conversation_id: str):
        """Mark conversation as ready for generation"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                UPDATE conversations 
                SET ready_for_generation = TRUE, current_phase = 'ready_for_generation'
                WHERE id = ?
            """, (conversation_id,))
            await conn.commit()
    
    async def save_tool_call(self, conversation_id: str, message_id: int, tool_name: str, 
                            query: str, results: List[Dict], success: bool) -> int:
        """Save tool call results"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO tool_calls (conversation_id, message_id, tool_name, query, results, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conversation_id, message_id, tool_name, query, json.dumps(results), success))
            await conn.commit()
            return cursor.lastrowid
    
    async def save_mashup(self, mashup_data: Dict) -> int:
        """Save generated mashup"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO mashups (conversation_id, prompt, skill_level, title, lyrics, 
                                   educational_content, web_sources, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mashup_data.get('conversation_id'),
                mashup_data['prompt'],
                mashup_data['skill_level'],
                mashup_data.get('title', ''),
                mashup_data.get('lyrics', ''),
                json.dumps(mashup_data.get('educational_content', {})),
                json.dumps(mashup_data.get('web_sources', [])),
                json.dumps(mashup_data.get('metadata', {}))
            ))
            await conn.commit()
            return cursor.lastrowid
    
    async def get_mashup(self, mashup_id: int) -> Optional[Dict]:
        """Get mashup by ID"""
        await self.init_db()
        
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM mashups WHERE id = ?", (mashup_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    data = dict(row)
                    data['educational_content'] = json.loads(data['educational_content'])
                    data['web_sources'] = json.loads(data['web_sources'])
                    data['metadata'] = json.loads(data['metadata'])
                    return data
        return None
```

---

## 6. Conversational Agent System

### 6.1 Async Enhanced Conversation Agent

```python
# app/agents/conversation_agent.py
import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import HumanMessage, AIMessage

from app.services.web_search import AsyncWebSearchService
from app.db.conversation_db import AsyncConversationDB, ConversationPhase
from app.utils.validation import ConversationValidator

class AsyncConversationalMashupAgent:
    """Enhanced async conversational agent with web search and context management"""
    
    def __init__(self, 
                 model_name: str = "llama3.1:8b-instruct",
                 tavily_api_key: str = None,
                 db_path: str = "./data/conversations.db"):
        
        self.model_name = model_name
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.db = AsyncConversationDB(db_path)
        self.web_search = AsyncWebSearchService(self.tavily_api_key) if self.tavily_api_key else None
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
        conversation = await self.db.get_conversation(session_id)
        if not conversation:
            session_id = session_id or str(uuid.uuid4())
            await self.db.create_conversation(session_id, user_id)
            conversation = await self.db.get_conversation(session_id)
        
        # Add user message to conversation
        message_id = await self.db.add_message(session_id, "user", user_message)
        
        # Determine current phase and process accordingly
        current_phase = ConversationPhase(conversation.get('current_phase', 'initial'))
        
        try:
            # Process message based on current phase
            response_data = await self.phase_handlers[current_phase](
                session_id, user_message, conversation
            )
            
            # Add assistant response to conversation
            await self.db.add_message(
                session_id, 
                "assistant", 
                response_data['agent_response'],
                response_data.get('tool_calls', [])
            )
            
            # Update conversation context if changed
            if response_data.get('context_updated'):
                await self.db.update_conversation_context(
                    session_id,
                    response_data['gathered_context'],
                    response_data.get('next_phase')
                )
            
            # Check if ready for generation
            if response_data.get('ready_for_generation'):
                await self.db.mark_ready_for_generation(session_id)
            
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
            
            await self.db.add_message(session_id, "assistant", error_response)
            
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
            
            # Execute searches concurrently
            search_tasks = []
            for query in search_queries:
                task = self._execute_search_with_error_handling(query, context)
                search_tasks.append(task)
            
            if search_tasks:
                search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                for i, response in enumerate(search_responses):
                    query = search_queries[i]
                    if isinstance(response, Exception):
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "error": str(response),
                            "success": False
                        })
                    else:
                        results, success = response
                        search_results.extend(results)
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "results_count": len(results),
                            "success": success
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
    
    async def _execute_search_with_error_handling(self, query: str, context: Dict) -> tuple[List[Dict], bool]:
        """Execute web search with proper error handling"""
        try:
            results = await self.web_search.search_educational_content(query, context)
            return results, True
        except Exception as e:
            return [], False
    
    async def _handle_genre_exploration(self, session_id: str, user_message: str, conversation: Dict) -> Dict[str, Any]:
        """Handle genre exploration phase with web research"""
        
        current_context = conversation.get('gathered_context', {})
        
        # Extract genre information from user message
        genres = await self._extract_genres(user_message, current_context)
        current_context.setdefault('genres', []).extend(genres)
        
        # Perform concurrent web searches for genres
        tool_calls = []
        if self.web_search and genres:
            search_tasks = []
            search_queries = []
            
            for genre in genres:
                search_query = f"{genre} music trends 2024 characteristics educational"
                search_queries.append(search_query)
                task = self._execute_search_with_error_handling(search_query, current_context)
                search_tasks.append(task)
            
            if search_tasks:
                search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                for i, response in enumerate(search_responses):
                    query = search_queries[i]
                    if isinstance(response, Exception):
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "error": str(response),
                            "success": False
                        })
                    else:
                        results, success = response
                        current_context.setdefault('web_research', []).extend(results)
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "results_count": len(results),
                            "success": success
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
                results, success = await self._execute_search_with_error_handling(search_query, current_context)
                current_context.setdefault('web_research', []).extend(results)
                tool_calls.append({
                    "tool": "web_search",
                    "query": search_query,
                    "results_count": len(results),
                    "success": success
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
        
        # Perform concurrent cultural research
        tool_calls = []
        if self.web_search:
            genres = current_context.get('genres', [])
            search_tasks = []
            search_queries = []
            
            for genre in genres:
                search_query = f"{genre} cultural significance history modern impact"
                search_queries.append(search_query)
                task = self._execute_search_with_error_handling(search_query, current_context)
                search_tasks.append(task)
            
            if search_tasks:
                search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                for i, response in enumerate(search_responses):
                    query = search_queries[i]
                    if isinstance(response, Exception):
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "error": str(response),
                            "success": False
                        })
                    else:
                        results, success = response
                        current_context.setdefault('web_research', []).extend(results)
                        tool_calls.append({
                            "tool": "web_search",
                            "query": query,
                            "results_count": len(results),
                            "success": success
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
    
    # Placeholder methods for context extraction and response generation
    # These would be implemented with actual NLP logic and prompt engineering
    
    async def _extract_initial_context(self, message: str) -> Dict:
        """Extract initial context from user message"""
        # This would use NLP to extract context
        context = {}
        
        # Simple keyword detection (would be more sophisticated in practice)
        if "school" in message.lower():
            context["educational_context"] = "school"
        elif "class" in message.lower():
            context["educational_context"] = "classroom"
        else:
            context["educational_context"] = "general"
        
        return context
    
    def _should_search_for_trends(self, context: Dict) -> bool:
        """Determine if web search is needed for current trends"""
        # Simple logic - in practice would be more sophisticated
        return bool(context.get("educational_context"))
    
    def _build_initial_search_queries(self, context: Dict) -> List[str]:
        """Build initial search queries based on context"""
        queries = []
        educational_context = context.get("educational_context", "")
        
        if educational_context:
            queries.append(f"music education trends 2024 {educational_context}")
        
        return queries
    
    async def _extract_genres(self, message: str, context: Dict) -> List[str]:
        """Extract genres from user message"""
        # Simple keyword detection
        common_genres = ["jazz", "blues", "rock", "pop", "hip-hop", "country", "classical", "folk", "electronic", "reggae", "latin"]
        found_genres = []
        
        message_lower = message.lower()
        for genre in common_genres:
            if genre in message_lower:
                found_genres.append(genre)
        
        return found_genres
    
    async def _extract_educational_objectives(self, message: str, context: Dict) -> List[str]:
        """Extract educational objectives from message"""
        # Simple keyword detection
        objectives = []
        
        objective_keywords = {
            "improvisation": ["improvisation", "improv", "improvise"],
            "rhythm": ["rhythm", "beat", "timing"],
            "harmony": ["harmony", "chord", "progression"],
            "cultural": ["cultural", "culture", "history", "background"]
        }
        
        message_lower = message.lower()
        for objective, keywords in objective_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                objectives.append(objective)
        
        return objectives
    
    async def _extract_skill_level(self, message: str) -> Optional[str]:
        """Extract skill level from message"""
        message_lower = message.lower()
        
        if "beginner" in message_lower or "basic" in message_lower:
            return "beginner"
        elif "advanced" in message_lower:
            return "advanced"
        elif "intermediate" in message_lower:
            return "intermediate"
        
        return None
    
    async def _extract_cultural_elements(self, message: str, context: Dict) -> List[str]:
        """Extract cultural focus areas from message"""
        # Simple keyword detection
        cultural_elements = []
        
        cultural_keywords = [
            "cultural significance", "history", "tradition", "heritage", 
            "social impact", "cultural appropriation", "respect"
        ]
        
        message_lower = message.lower()
        for keyword in cultural_keywords:
            if keyword in message_lower:
                cultural_elements.append(keyword)
        
        return cultural_elements
    
    def _determine_next_phase(self, context: Dict) -> str:
        """Determine next conversation phase based on context"""
        if not context.get("genres"):
            return "genre_exploration"
        elif not context.get("learning_objectives") or not context.get("skill_level"):
            return "educational_clarification"
        elif not context.get("cultural_focus"):
            return "cultural_research"
        else:
            return "ready_for_generation"
    
    async def _generate_phase_response(self, phase: str, context: Dict, user_message: str) -> str:
        """Generate appropriate response for conversation phase"""
        # This would use the local LLM with appropriate prompts
        # For now, return simple responses based on phase
        
        phase_responses = {
            "initial": f"Thank you for sharing that! I understand you're interested in creating educational content. Let me help you develop this further. What musical genres are you most interested in combining?",
            "genre_exploration": f"Great choice of genres! I've researched some current information about these styles. What specific educational goals do you have for your students?",
            "educational_clarification": f"Excellent! Those are important learning objectives. Let me research some cultural context to ensure we create respectful and informative content.",
            "cultural_research": f"I've gathered comprehensive information about the cultural significance of these genres. Are you ready for me to create your educational mashup?"
        }
        
        return phase_responses.get(phase, "Let me help you with that.")
    
    async def _generate_confirmation_response(self, context: Dict) -> str:
        """Generate confirmation response when ready for generation"""
        genres = context.get('genres', [])
        skill_level = context.get('skill_level', 'general')
        
        return f"""Perfect! I now have comprehensive information to create your educational mashup:

📚 Educational Context: {context.get('educational_context', 'general')}
🎵 Genres: {', '.join(genres)}
📊 Skill Level: {skill_level}
🎯 Learning Objectives: {', '.join(context.get('learning_objectives', []))}
🌍 Cultural Focus: {', '.join(context.get('cultural_focus', []))}

I'm ready to create your educational mashup with:
- Engaging lyrics that blend your chosen genres
- Music theory concepts appropriate for {skill_level} level
- Rich cultural context from my research
- Practical teaching notes and activities

Would you like me to generate your educational mashup now?"""
```

---

## 7. Async API Layer with Chat Endpoints

### 7.1 Enhanced Async FastAPI Application

```python
# app/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
import asyncio

from app.agents.conversation_agent import AsyncConversationalMashupAgent
from app.services.generation_service import AsyncEnhancedGenerationService
from app.db.conversation_db import AsyncConversationDB
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

# Global services (initialized on startup)
conversation_agent: Optional[AsyncConversationalMashupAgent] = None
generation_service: Optional[AsyncEnhancedGenerationService] = None
db: Optional[AsyncConversationDB] = None
validator: Optional[ConversationValidator] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global conversation_agent, generation_service, db, validator
    
    logger.info("Initializing services...")
    
    # Initialize database first
    db = AsyncConversationDB(settings.DATABASE_PATH)
    await db.init_db()
    
    # Initialize other services
    conversation_agent = AsyncConversationalMashupAgent(
        tavily_api_key=settings.TAVILY_API_KEY,
        db_path=settings.DATABASE_PATH
    )
    generation_service = AsyncEnhancedGenerationService()
    validator = ConversationValidator()
    
    logger.info("Services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services...")
    # Add any cleanup logic here

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

# Dependency injection
async def get_conversation_agent() -> AsyncConversationalMashupAgent:
    if conversation_agent is None:
        raise HTTPException(500, "Conversation agent not initialized")
    return conversation_agent

async def get_generation_service() -> AsyncEnhancedGenerationService:
    if generation_service is None:
        raise HTTPException(500, "Generation service not initialized")
    return generation_service

async def get_db() -> AsyncConversationDB:
    if db is None:
        raise HTTPException(500, "Database not initialized")
    return db

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Lit Music Mashup Conversational MVP v2.0",
        "features": [
            "Async conversational interface for context gathering",
            "Web search integration for current information",
            "Enhanced educational content generation",
            "Multi-turn dialogue support",
            "Modern Python tooling with UV"
        ],
        "status": "active",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }

@app.get("/health")
async def health_check(db: AsyncConversationDB = Depends(get_db)):
    """Enhanced async health check with service status"""
    
    # Check database connection
    try:
        test_conversation = await db.get_conversation("health-check-test")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check web search availability
    web_search_status = "available" if settings.TAVILY_API_KEY else "disabled (no API key)"
    
    # Check Ollama connection (would be implemented)
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
            "async_processing": True,
            "conversational_interface": True,
            "web_search_integration": bool(settings.TAVILY_API_KEY),
            "tool_orchestration": True,
            "enhanced_generation": True
        }
    }

# Conversational endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent: AsyncConversationalMashupAgent = Depends(get_conversation_agent)
):
    """Async chat with conversational agent for context gathering"""
    
    try:
        # Validate input
        if len(request.message.strip()) < 1:
            raise HTTPException(400, "Message cannot be empty")
        
        if len(request.message) > 1000:
            raise HTTPException(400, "Message too long (max 1000 characters)")
        
        # Process message with conversational agent (async)
        response = await agent.process_message(
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
async def get_conversation_session(
    session_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Retrieve conversation session with history"""
    
    try:
        conversation = await db.get_conversation(session_id)
        
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
async def generate_educational_mashup(
    request: EnhancedGenerateRequest,
    background_tasks: BackgroundTasks,
    generation_service: AsyncEnhancedGenerationService = Depends(get_generation_service)
):
    """Generate educational mashup with enhanced context"""
    
    try:
        # Validate input
        if len(request.prompt.strip()) < 5:
            raise HTTPException(400, "Prompt must be at least 5 characters")
        
        valid_skill_levels = ["beginner", "intermediate", "advanced"]
        if request.skill_level not in valid_skill_levels:
            raise HTTPException(400, f"Skill level must be one of: {valid_skill_levels}")
        
        # Generate mashup with enhanced service (async)
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
async def get_mashup(
    mashup_id: int,
    db: AsyncConversationDB = Depends(get_db)
):
    """Retrieve generated mashup by ID"""
    
    try:
        mashup = await db.get_mashup(mashup_id)
        
        if not mashup:
            raise HTTPException(404, "Mashup not found")
        
        return mashup
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mashup retrieval error: {e}")
        raise HTTPException(500, f"Failed to retrieve mashup: {str(e)}")

# Additional async utility endpoints
@app.get("/api/v1/sessions")
async def list_recent_sessions(
    limit: int = 10,
    db: AsyncConversationDB = Depends(get_db)
):
    """List recent conversation sessions"""
    
    try:
        # This would be implemented in the database layer
        # For now, return empty list
        return {
            "sessions": [],
            "total": 0,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Session listing error: {e}")
        raise HTTPException(500, f"Failed to list sessions: {str(e)}")

# Development-only endpoints
if settings.ENVIRONMENT == "development":
    @app.post("/api/v1/dev/reset-session/{session_id}")
    async def reset_session(
        session_id: str,
        db: AsyncConversationDB = Depends(get_db)
    ):
        """Reset conversation session (development only)"""
        try:
            # This would clear the session and reset state
            return {"message": f"Session {session_id} reset", "success": True}
        except Exception as e:
            raise HTTPException(500, f"Failed to reset session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
```

### 7.2 Configuration Management

```python
# app/config.py
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/conversations.db")
    
    # AI Models
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")
    
    # External APIs
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Conversation settings
    MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "10"))
    CONVERSATION_TIMEOUT_MINUTES: int = int(os.getenv("CONVERSATION_TIMEOUT_MINUTES", "30"))
    WEB_SEARCH_MAX_RESULTS: int = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "3"))
    WEB_SEARCH_TIMEOUT_SECONDS: int = int(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10"))
    
    # Educational content settings
    MIN_CULTURAL_CONTEXT_LENGTH: int = int(os.getenv("MIN_CULTURAL_CONTEXT_LENGTH", "100"))
    MIN_THEORY_CONCEPTS: int = int(os.getenv("MIN_THEORY_CONCEPTS", "2"))
    REQUIRE_WEB_RESEARCH: bool = os.getenv("REQUIRE_WEB_RESEARCH", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 8. Web Search Integration

### 8.1 Enhanced Async Web Search Service

```python
# app/services/web_search.py
import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_community.tools.tavily_search import TavilySearchResults
from app.utils.validation import WebSourceValidator

class AsyncWebSearchService:
    """Enhanced async web search service for educational content"""
    
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
            
            # Use asyncio timeout for the search
            results = await asyncio.wait_for(
                self._execute_search(enhanced_query),
                timeout=search_timeout
            )
            
            # Filter and validate results
            validated_results = await self._filter_and_validate_results(results, context or {})
            
            return validated_results
            
        except asyncio.TimeoutError:
            return []  # Graceful degradation on timeout
        except Exception as e:
            # Log error but don't break the conversation
            import logging
            logging.error(f"Web search error: {e}")
            return []
    
    async def _execute_search(self, query: str) -> List[Dict]:
        """Execute the actual search operation"""
        # Note: TavilySearchResults might not be fully async
        # In a real implementation, you might need to run it in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.search_tool.arun, query)
    
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
    
    async def _filter_and_validate_results(self, results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
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
                
                # Validate with educational context (async if needed)
                if not await self._validate_educational_appropriateness(result):
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
    
    async def _validate_educational_appropriateness(self, result: Dict) -> bool:
        """Validate educational appropriateness (can be async if needed)"""
        # For now, use synchronous validation
        return self.validator.is_educationally_appropriate(result)
    
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
    
    async def search_multiple_queries(self, queries: List[str], context: Dict[str, Any] = None) -> List[Dict]:
        """Search multiple queries concurrently"""
        
        if not queries:
            return []
        
        # Execute searches concurrently
        search_tasks = [
            self.search_educational_content(query, context)
            for query in queries
        ]
        
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results from all searches
        combined_results = []
        for results in search_results:
            if isinstance(results, list):
                combined_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in combined_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
```

---

## 9. CI/CD Pipeline with UV and Tool Testing

### 9.1 Enhanced GitHub Actions Configuration with UV

```yaml
# .github/workflows/conversational-ci.yml
name: Conversational AI Music Mashup CI/CD with UV

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'app/**'
      - 'tests/**'
      - 'pyproject.toml'
      - 'uv.lock'
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
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      run: uv python install ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies with uv
      run: |
        uv sync --frozen --no-cache
    
    - name: Create test environment
      run: |
        mkdir -p test_data
        touch test_data/test_conversations.db
    
    - name: Test database operations
      run: |
        uv run python -c "
        import asyncio
        from app.db.conversation_db import AsyncConversationDB
        import tempfile
        import os
        
        async def test_db():
            # Test database initialization
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            db = AsyncConversationDB(path)
            await db.init_db()
            
            conversation_id = 'test-123'
            await db.create_conversation(conversation_id)
            
            # Test conversation operations
            conv = await db.get_conversation(conversation_id)
            assert conv is not None
            assert conv['id'] == conversation_id
            
            # Test message operations
            msg_id = await db.add_message(conversation_id, 'user', 'test message')
            assert msg_id is not None
            
            print('Async database tests passed')
            os.unlink(path)
        
        asyncio.run(test_db())
        "
    
    - name: Test conversation agent structure
      run: |
        uv run python -c "
        import asyncio
        from app.agents.conversation_agent import AsyncConversationalMashupAgent
        import tempfile
        import os
        
        async def test_agent():
            # Test agent initialization without API key
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            agent = AsyncConversationalMashupAgent(db_path=path)
            assert agent is not None
            assert agent.web_search is None  # No API key provided
            
            print('Async conversation agent structure tests passed')
            os.unlink(path)
        
        asyncio.run(test_agent())
        "
    
    - name: Test async API endpoint structure
      run: |
        uv run python -c "
        import asyncio
        from httpx import AsyncClient
        import os
        import tempfile
        
        async def test_api():
            # Set test environment variables
            os.environ['DATABASE_PATH'] = tempfile.mktemp()
            os.environ['LOG_LEVEL'] = 'ERROR'
            
            from app.main import app
            
            async with AsyncClient(app=app, base_url='http://test') as client:
                # Test health endpoint
                response = await client.get('/health')
                assert response.status_code == 200
                
                # Test root endpoint
                response = await client.get('/')
                assert response.status_code == 200
                assert 'Conversational MVP' in response.json()['message']
                
                print('Async API endpoint structure tests passed')
        
        asyncio.run(test_api())
        "
    
    - name: Run async unit tests
      run: |
        uv run pytest tests/ -v --tb=short -x
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
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      run: uv python install ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies with uv
      run: |
        uv sync --frozen --no-cache
    
    - name: Test async web search integration
      run: |
        uv run python -c "
        import asyncio
        import os
        from app.services.web_search import AsyncWebSearchService
        
        async def test_web_search():
            if not os.getenv('TAVILY_API_KEY'):
                print('Skipping web search test - no API key')
                return
            
            search_service = AsyncWebSearchService()
            results = await search_service.search_educational_content(
                'jazz music education basics',
                {'skill_level': 'beginner', 'educational_context': 'classroom'}
            )
            
            assert isinstance(results, list)
            print(f'Async web search integration test passed - found {len(results)} results')
            
            # Test individual result structure
            if results:
                result = results[0]
                assert 'title' in result
                assert 'content' in result
                assert 'source_quality' in result
                print('Result structure validation passed')
        
        asyncio.run(test_web_search())
        "
    
    - name: Test async conversation flow with web search
      run: |
        uv run python -c "
        import asyncio
        import os
        import tempfile
        from app.agents.conversation_agent import AsyncConversationalMashupAgent
        
        async def test_conversation_with_search():
            if not os.getenv('TAVILY_API_KEY'):
                print('Skipping conversation test - no API key')
                return
            
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            agent = AsyncConversationalMashupAgent(
                db_path=path, 
                tavily_api_key=os.getenv('TAVILY_API_KEY')
            )
            
            # Test initial conversation
            response = await agent.process_message(
                'test-session-123',
                'I want to create a jazz and blues mashup for my beginner music class'
            )
            
            assert 'session_id' in response
            assert 'agent_response' in response
            assert isinstance(response.get('tool_calls', []), list)
            
            print('Async conversation flow with web search test passed')
            os.unlink(path)
        
        asyncio.run(test_conversation_with_search())
        "

  test-without-web-search:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      run: uv python install ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies with uv
      run: |
        uv sync --frozen --no-cache
    
    - name: Test graceful degradation without API key
      run: |
        uv run python -c "
        import asyncio
        import tempfile
        import os
        from app.agents.conversation_agent import AsyncConversationalMashupAgent
        
        async def test_without_api_key():
            fd, path = tempfile.mkstemp()
            os.close(fd)
            
            # Test agent without API key
            agent = AsyncConversationalMashupAgent(db_path=path, tavily_api_key=None)
            assert agent.web_search is None
            
            # Test conversation still works
            response = await agent.process_message(
                'test-session-456',
                'I want to create a simple mashup for beginners'
            )
            
            assert 'session_id' in response
            assert 'agent_response' in response
            assert response.get('tool_calls', []) == []  # No web search calls
            
            print('Async graceful degradation test passed')
            os.unlink(path)
        
        asyncio.run(test_without_api_key())
        "

  quality-check:
    runs-on: ubuntu-latest
    needs: [test-core-functionality]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      run: uv python install ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies with uv
      run: |
        uv sync --frozen --no-cache
    
    - name: Check code formatting
      run: |
        uv run black --check app/ tests/
        uv run isort --check-only app/ tests/
    
    - name: Check code style
      run: |
        uv run flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
    
    - name: Type checking
      run: |
        uv run mypy app/ --ignore-missing-imports

  integration-test:
    runs-on: ubuntu-latest
    needs: [test-core-functionality, quality-check]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image with UV
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

  performance-test:
    runs-on: ubuntu-latest
    needs: [integration-test]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      run: uv python install ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies with uv
      run: |
        uv sync --frozen --no-cache
    
    - name: Run performance benchmarks
      run: |
        uv run python -c "
        import asyncio
        import time
        from httpx import AsyncClient
        import os
        import tempfile
        
        async def test_performance():
            # Set test environment variables
            os.environ['DATABASE_PATH'] = tempfile.mktemp()
            os.environ['LOG_LEVEL'] = 'ERROR'
            
            from app.main import app
            
            async with AsyncClient(app=app, base_url='http://test') as client:
                # Test chat response time
                start_time = time.time()
                response = await client.post('/api/v1/chat', json={
                    'message': 'Create a simple mashup for beginners'
                })
                end_time = time.time()
                
                assert response.status_code == 200
                response_time = end_time - start_time
                
                print(f'Chat response time: {response_time:.2f}s')
                # Should respond within 10 seconds without web search
                assert response_time < 10, f'Response too slow: {response_time}s'
                
                # Test concurrent requests
                start_time = time.time()
                tasks = []
                for i in range(5):
                    task = client.post('/api/v1/chat', json={
                        'message': f'Test message {i}'
                    })
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks)
                end_time = time.time()
                
                concurrent_time = end_time - start_time
                print(f'5 concurrent requests time: {concurrent_time:.2f}s')
                
                # All should succeed
                for resp in responses:
                    assert resp.status_code == 200
                
                print('Performance tests passed')
        
        asyncio.run(test_performance())
        "

  deploy:
    runs-on: ubuntu-latest
    needs: [integration-test, test-with-web-search, test-without-web-search, performance-test]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build production image with UV
      run: |
        docker build -t lit-music-mashup-v2:${{ github.sha }} .
        docker tag lit-music-mashup-v2:${{ github.sha }} lit-music-mashup-v2:latest
    
    # Add deployment steps here (e.g., push to registry, deploy to server)
    - name: Deploy notification
      run: |
        echo "Ready for deployment - all tests passed"
        echo "Image: lit-music-mashup-v2:${{ github.sha }}"
        echo "Built with UV for fast dependency management"
```

---

## 10. MVP Validation & Conversational Testing

### 10.1 Enhanced Async MVP Success Criteria

```python
# tests/test_mvp_conversational_async.py
import pytest
import asyncio
import tempfile
import os
from httpx import AsyncClient

@pytest.fixture
def temp_db_path():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)

@pytest.fixture
async def async_app_client(temp_db_path):
    """Create async test client with temporary database"""
    os.environ['DATABASE_PATH'] = temp_db_path
    os.environ['LOG_LEVEL'] = 'ERROR'
    
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestAsyncConversationalMVP:
    """Test complete async conversational MVP functionality"""
    
    @pytest.mark.asyncio
    async def test_conversational_workflow_complete(self, async_app_client):
        """Test complete async conversational workflow"""
        
        # 1. Start conversation
        response = await async_app_client.post("/api/v1/chat", json={
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
        response = await async_app_client.post("/api/v1/chat", json={
            "session_id": session_id,
            "message": "The students are at intermediate level and I want to focus on improvisation and rhythm analysis"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have more context now
        context = data["gathered_context"]
        assert "educational_context" in context or "school" in data["agent_response"].lower()
        
        # 3. Test session retrieval
        response = await async_app_client.get(f"/api/v1/session/{session_id}")
        assert response.status_code == 200
        
        session_data = response.json()
        assert session_data["session_id"] == session_id
        assert "messages" in session_data
        assert len(session_data["messages"]) >= 2  # User and assistant messages
    
    @pytest.mark.asyncio
    async def test_enhanced_generation(self, async_app_client):
        """Test enhanced async generation with context"""
        
        response = await async_app_client.post("/api/v1/generate", json={
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
    async def test_concurrent_conversations(self, async_app_client):
        """Test handling concurrent conversations"""
        
        # Create multiple conversation tasks
        conversation_tasks = []
        for i in range(3):
            task = async_app_client.post("/api/v1/chat", json={
                "message": f"Create a mashup for session {i}"
            })
            conversation_tasks.append(task)
        
        # Execute concurrently
        responses = await asyncio.gather(*conversation_tasks)
        
        # All should succeed with different session IDs
        session_ids = set()
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            session_id = data["session_id"]
            assert session_id not in session_ids  # Each should be unique
            session_ids.add(session_id)
        
        assert len(session_ids) == 3

@pytest.mark.asyncio
class TestAsyncWebSearchIntegration:
    """Test async web search integration with graceful degradation"""
    
    async def test_async_web_search_with_api_key(self, temp_db_path):
        """Test async web search when API key is available"""
        
        # This test only runs if TAVILY_API_KEY is set
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            pytest.skip("No TAVILY_API_KEY available for testing")
        
        from app.services.web_search import AsyncWebSearchService
        
        search_service = AsyncWebSearchService(api_key)
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
    
    async def test_async_web_search_without_api_key(self, temp_db_path):
        """Test async graceful degradation without API key"""
        
        from app.services.web_search import AsyncWebSearchService
        
        search_service = AsyncWebSearchService(api_key=None)
        results = await search_service.search_educational_content(
            "test query",
            {"skill_level": "beginner"}
        )
        
        # Should return empty list without crashing
        assert results == []
    
    async def test_concurrent_web_searches(self, temp_db_path):
        """Test concurrent web searches"""
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            pytest.skip("No TAVILY_API_KEY available for testing")
        
        from app.services.web_search import AsyncWebSearchService
        
        search_service = AsyncWebSearchService(api_key)
        
        # Test multiple concurrent searches
        queries = [
            "jazz music education",
            "hip hop cultural significance",
            "music theory for beginners"
        ]
        
        search_tasks = [
            search_service.search_educational_content(query, {"skill_level": "beginner"})
            for query in queries
        ]
        
        results_list = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # All should complete (either with results or empty lists)
        for results in results_list:
            if isinstance(results, Exception):
                # Search failed, but should not crash
                continue
            assert isinstance(results, list)

class TestAsyncPerformanceBenchmarks:
    """Test async performance benchmarks for conversational features"""
    
    @pytest.mark.asyncio
    async def test_conversation_response_time(self, async_app_client):
        """Test async conversation response time"""
        import time
        
        start_time = time.time()
        response = await async_app_client.post("/api/v1/chat", json={
            "message": "Create a mashup for beginners"
        })
        end_time = time.time()
        
        assert response.status_code == 200
        # Async conversation should respond within 10 seconds (without web search)
        response_time = end_time - start_time
        assert response_time < 10, f"Response too slow: {response_time}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self, async_app_client):
        """Test performance with concurrent requests"""
        import time
        
        start_time = time.time()
        
        # Create 5 concurrent conversation requests
        tasks = []
        for i in range(5):
            task = async_app_client.post("/api/v1/chat", json={
                "message": f"Test conversation {i}"
            })
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should handle 5 concurrent requests in reasonable time
        total_time = end_time - start_time
        assert total_time < 30, f"Concurrent requests too slow: {total_time}s"
    
    @pytest.mark.asyncio
    async def test_session_retrieval_performance(self, async_app_client):
        """Test async session retrieval performance"""
        import time
        
        # Create session first
        response = await async_app_client.post("/api/v1/chat", json={
            "message": "test message"
        })
        session_id = response.json()["session_id"]
        
        # Test retrieval time
        start_time = time.time()
        response = await async_app_client.get(f"/api/v1/session/{session_id}")
        end_time = time.time()
        
        assert response.status_code == 200
        # Session retrieval should be very fast
        retrieval_time = end_time - start_time
        assert retrieval_time < 1, f"Session retrieval too slow: {retrieval_time}s"
```

---

## 11. Feature Addition Strategy

### 11.1 Enhanced Async Incremental Development Process

**Step 1: Create Async Feature Branch**
```bash
git checkout -b feature/async-advanced-cultural-context
```

**Step 2: Add Async Tests First (TDD)**
```python
# tests/test_async_advanced_cultural_context.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_cultural_context_web_research():
    """Test async advanced cultural context with web research"""
    
    # Test that cultural research includes multiple concurrent sources
    from httpx import AsyncClient
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/chat", json={
            "session_id": "cultural-test",
            "message": "I want to explore the cultural significance of jazz and hip-hop fusion"
        })
        
        data = response.json()
        tool_calls = data.get("tool_calls", [])
        
        # Should trigger concurrent cultural research
        cultural_calls = [call for call in tool_calls if "cultural" in call.get("query", "").lower()]
        assert len(cultural_calls) > 0

@pytest.mark.asyncio
async def test_async_cultural_sensitivity_validation():
    """Test async cultural sensitivity in generated content"""
    
    from httpx import AsyncClient
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/generate", json={
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

**Step 3: Implement Enhanced Async Feature**
```python
# app/agents/async_cultural_research_agent.py
import asyncio
from typing import List, Dict

class AsyncAdvancedCulturalResearchAgent:
    """Enhanced async cultural research with multiple sources and sensitivity validation"""
    
    async def research_cultural_context(self, genres: List[str], context: Dict) -> Dict:
        """Perform comprehensive concurrent cultural research"""
        
        cultural_research = {}
        
        # Create concurrent research tasks for all genres
        research_tasks = []
        for genre in genres:
            # Search for cultural significance
            cultural_task = self._research_cultural_significance(genre, context)
            modern_task = self._research_modern_impact(genre, context)
            
            research_tasks.extend([cultural_task, modern_task])
        
        # Execute all research concurrently
        research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Process results for each genre
        for i, genre in enumerate(genres):
            cultural_idx = i * 2
            modern_idx = i * 2 + 1
            
            cultural_results = research_results[cultural_idx] if cultural_idx < len(research_results) else []
            modern_results = research_results[modern_idx] if modern_idx < len(research_results) else []
            
            # Handle exceptions gracefully
            if isinstance(cultural_results, Exception):
                cultural_results = []
            if isinstance(modern_results, Exception):
                modern_results = []
            
            cultural_research[genre] = {
                "historical_significance": cultural_results,
                "modern_impact": modern_results,
                "synthesis": await self._synthesize_cultural_information(
                    cultural_results, modern_results
                )
            }
        
        return cultural_research
    
    async def _research_cultural_significance(self, genre: str, context: Dict) -> List[Dict]:
        """Research cultural significance of a genre"""
        cultural_query = f"{genre} cultural significance African American history"
        return await self.web_search.search_educational_content(cultural_query, context)
    
    async def _research_modern_impact(self, genre: str, context: Dict) -> List[Dict]:
        """Research modern cultural impact of a genre"""
        modern_query = f"{genre} modern cultural impact social justice"
        return await self.web_search.search_educational_content(modern_query, context)
    
    async def _synthesize_cultural_information(self, historical: List[Dict], modern: List[Dict]) -> str:
        """Synthesize cultural information from multiple sources"""
        # This would use AI to synthesize the information
        return "Synthesized cultural context from multiple sources..."
```

### 11.2 Enhanced Async Feature Addition Roadmap

**Phase 2 Async Conversational Features (Week 3-4)**:
```python
PHASE_2_ASYNC_CONVERSATIONAL_FEATURES = [
    "async_advanced_cultural_research",     # Concurrent multi-source cultural context
    "async_conversation_memory_system",     # Async user preference persistence
    "async_context_validation_engine",      # Concurrent context quality validation
    "async_enhanced_error_recovery",        # Async error handling with fallbacks
    "async_conversation_analytics"          # Real-time conversation effectiveness tracking
]
```

**Phase 3 Advanced Async Features (Week 5-6)**:
```python
PHASE_3_ADVANCED_ASYNC_FEATURES = [
    "websocket_multi_user_conversations",   # Real-time multi-user conversations
    "async_conversation_export_system",     # Concurrent export processing
    "async_advanced_tool_integration",      # Multiple concurrent research tools
    "async_conversation_templates",         # Dynamic conversation flow templates
    "async_real_time_collaboration"         # WebSocket-based real-time features
]
```

### 11.3 Enhanced Quality Gates for Async Conversational Features

**Every Async Conversational Feature Must Pass**:
1. ✅ All existing async conversation flows still work
2. ✅ Concurrent web search integration maintains graceful degradation
3. ✅ Async conversation state management remains consistent
4. ✅ Tool orchestration performance with concurrency is maintained
5. ✅ Educational content quality is preserved under concurrent load
6. ✅ Cultural sensitivity validation passes with async processing
7. ✅ API response times remain under thresholds with concurrent requests
8. ✅ Memory usage remains stable under concurrent operations

---

## 12. Summary

### 12.1 Async Conversational MVP v2.0 with UV Advantages

**Modern Development Environment**:
- UV for fast, reliable Python package management
- FastAPI[standard] with built-in uvicorn for simplified dependencies
- Async-first architecture for better performance and scalability
- Concurrent processing for web search and tool integration
- Enhanced Docker setup optimized for UV

**Enhanced Async Conversational Development**:
- Fully async multi-turn dialogue for comprehensive context gathering
- Concurrent web search integration for current and accurate information
- Async tool orchestration with LangChain/LangGraph
- Graceful degradation with async error handling
- Async database operations with proper connection management

**Advanced Async Quality Assurance**:
- Async conversational flow testing with concurrent scenarios
- Web search reliability and performance testing under load
- Cultural sensitivity validation with async processing
- Concurrent tool integration testing with fallback scenarios
- Performance monitoring for async conversations and concurrent searches

**Educational Focus Enhanced with Async Processing**:
- Concurrent information gathering through web research
- Comprehensive cultural context with multiple concurrent sources
- Async context-driven educational content generation
- Multi-source validation for accuracy with concurrent processing
- Enhanced teaching resources with real-time current examples

### 12.2 Next Steps for Async Conversational Implementation

**Week 1**: 
1. Set up UV-based project structure with async conversation modules
2. Implement async conversational agent with concurrent web search
3. Create async conversation database operations
4. Set up CI/CD pipeline with UV integration and async testing

**Week 2**: 
1. Validate async conversational MVP with real concurrent conversations
2. Test web search integration thoroughly under concurrent load
3. Optimize async conversation flow and context gathering  
4. Prepare for Phase 2 async conversational enhancements

**Week 3+**: 
1. Add advanced async conversational features incrementally
2. Enhance concurrent web search and tool integration
3. Monitor async conversation effectiveness and performance under load
4. Gather feedback for async conversation flow improvements

This async conversational implementation approach with UV ensures we have a modern, high-performance educational AI music platform that leverages concurrent processing, current information, and efficient dependency management while maintaining quality, reliability, and educational value through every iteration.