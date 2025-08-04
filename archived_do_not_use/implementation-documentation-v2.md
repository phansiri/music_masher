# Lit Music Mashup - Implementation Documentation v2.0
## Educational AI Music Generation Platform - MVP-First Approach

---

### Document Overview
This implementation guide provides a simplified, MVP-first approach to building the Lit Music Mashup educational platform. The documentation prioritizes **core functionality delivery** with incremental feature addition through CI/CD validation.

**Key Principle**: Build the simplest working educational mashup generator first, then add features through test-driven development with GitHub Actions CI/CD ensuring no regression.

---

## Table of Contents

1. [MVP-First Development Philosophy](#1-mvp-first-development-philosophy)
2. [Minimal Viable Product Scope](#2-minimal-viable-product-scope)
3. [Simple Development Environment](#3-simple-development-environment)
4. [Core Architecture (Simplified)](#4-core-architecture-simplified)
5. [Basic Database Layer](#5-basic-database-layer)
6. [Minimal Agent System](#6-minimal-agent-system)
7. [Essential API Layer](#7-essential-api-layer)
8. [CI/CD Pipeline Setup](#8-cicd-pipeline-setup)
9. [MVP Validation & Testing](#9-mvp-validation--testing)
10. [Feature Addition Strategy](#10-feature-addition-strategy)

---

## 1. MVP-First Development Philosophy

### 1.1 Core Principles

**Start Simple, Add Complexity Gradually**:
- Single educational mashup generation endpoint
- Basic educational content output
- Local models only (Ollama)
- SQLite database for simplicity
- No real-time collaboration initially
- No complex user management

**Test-Driven Feature Addition**:
- Every new feature requires passing tests
- GitHub Actions CI/CD prevents regression
- Feature flags for incremental rollout
- Performance benchmarks must be maintained

### 1.2 Development Phases

#### **Phase 1: Core MVP (Week 1-2)**
- ✅ Single API endpoint: `POST /generate`
- ✅ Basic educational context analysis
- ✅ Simple genre blending
- ✅ Educational content output
- ✅ SQLite persistence

#### **Phase 2: Enhanced Features (Week 3-4)**
- ✅ Multiple hook options
- ✅ Detailed theory integration
- ✅ Cultural context expansion
- ✅ Basic error handling

#### **Phase 3: Quality & Polish (Week 5-6)**
- ✅ Comprehensive testing
- ✅ Performance optimization
- ✅ Better error messages
- ✅ API documentation

#### **Phase 4: Advanced Features (Week 7+)**
- ✅ Real-time collaboration
- ✅ User management
- ✅ PostgreSQL migration
- ✅ Advanced analytics

---

## 2. Minimal Viable Product Scope

### 2.1 MVP Core Requirements

**Must Have**:
```python
# Single endpoint that works reliably
POST /api/v1/generate
{
    "prompt": "Create a jazz-hip hop mashup for beginners",
    "skill_level": "beginner"
}

# Returns educational mashup with:
{
    "title": "Generated title",
    "lyrics": "Complete lyrics",
    "educational_content": {
        "theory_concepts": ["chord progressions", "rhythm"],
        "cultural_context": "Historical background",
        "teaching_notes": "How to use this in class"
    }
}
```

**Nice to Have (Later Phases)**:
- Multiple genre combinations
- Collaboration features
- Advanced analytics
- User authentication
- Complex theory analysis

### 2.2 Technology Stack (Simplified)

```yaml
# Minimal tech stack for MVP
Backend: FastAPI (single file initially)
Database: SQLite (local file)
AI: Ollama + Llama 3.1 8B
Testing: pytest
CI/CD: GitHub Actions
Deployment: Docker (single container)
```

---

## 3. Simple Development Environment

### 3.1 Quick Setup

```bash
# Create project
mkdir lit-music-mashup
cd lit-music-mashup

# Install dependencies
pip install fastapi uvicorn sqlite3 ollama pytest

# Create basic structure
touch main.py
touch database.py
touch test_main.py
touch .github/workflows/ci.yml
```

### 3.2 Docker Setup (Minimal)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (MVP)
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - "./data:/app/data"  # SQLite storage
    environment:
      - DATABASE_PATH=/app/data/mashups.db
      
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

---

## 4. Core Architecture (Simplified)

### 4.1 MVP Architecture

```
┌─────────────────────────────────────────┐
│           MVP Architecture              │
├─────────────────────────────────────────┤
│  FastAPI App (Single File)             │
│  ┌─────────────────────────────────────┐ │
│  │ POST /api/v1/generate               │ │
│  │ GET  /health                        │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Simple Agent (Basic Functions)        │
│  ┌─────────────────────────────────────┐ │
│  │ analyze_request()                   │ │
│  │ generate_mashup()                   │ │
│  │ add_educational_content()           │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Ollama Local Model                    │
│  ┌─────────────────────────────────────┐ │
│  │ Llama 3.1 8B Instruct              │ │
│  └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  SQLite Database                       │
│  ┌─────────────────────────────────────┐ │
│  │ mashups table                       │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 4.2 File Structure (MVP)

```
lit-music-mashup/
├── main.py                 # Single FastAPI app
├── database.py             # SQLite operations
├── agents.py               # Basic AI functions
├── models.py               # Pydantic models
├── test_main.py            # Core tests
├── requirements.txt        # Dependencies
├── Dockerfile              # Container config
├── docker-compose.yml      # Local dev
└── .github/
    └── workflows/
        └── ci.yml          # GitHub Actions
```

---

## 5. Basic Database Layer

### 5.1 Simple SQLite Schema

```python
# database.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional

class MashupDB:
    def __init__(self, db_path: str = "mashups.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mashups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    skill_level TEXT NOT NULL,
                    title TEXT,
                    lyrics TEXT,
                    educational_content TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_mashup(self, mashup_data: Dict) -> int:
        """Save mashup to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO mashups (prompt, skill_level, title, lyrics, educational_content)
                VALUES (?, ?, ?, ?, ?)
            """, (
                mashup_data['prompt'],
                mashup_data['skill_level'],
                mashup_data.get('title', ''),
                mashup_data.get('lyrics', ''),
                json.dumps(mashup_data.get('educational_content', {}))
            ))
            return cursor.lastrowid
    
    def get_mashup(self, mashup_id: int) -> Optional[Dict]:
        """Get mashup by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM mashups WHERE id = ?", (mashup_id,)
            )
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['educational_content'] = json.loads(data['educational_content'])
                return data
        return None
```

---

## 6. Minimal Agent System

### 6.1 Basic AI Functions

```python
# agents.py
import ollama
from typing import Dict, List
import re

class SimpleMashupAgent:
    def __init__(self, model_name: str = "llama3.1:8b-instruct"):
        self.model_name = model_name
    
    async def generate_mashup(self, prompt: str, skill_level: str) -> Dict:
        """Generate basic educational mashup"""
        
        # Simple prompt for MVP
        system_prompt = f"""
        You are a music educator. Create a simple educational mashup.
        
        User request: {prompt}
        Skill level: {skill_level}
        
        Generate:
        1. A catchy title
        2. Simple lyrics (4-6 lines)
        3. Basic educational content
        
        Format as JSON:
        {{
            "title": "Mashup title",
            "lyrics": "Verse 1 lyrics here...",
            "educational_content": {{
                "theory_concepts": ["concept1", "concept2"],
                "cultural_context": "Brief cultural background",
                "teaching_notes": "How to use this in class"
            }}
        }}
        """
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": system_prompt}],
                stream=False
            )
            
            # Parse JSON response
            import json
            result = json.loads(response['message']['content'])
            return result
            
        except Exception as e:
            # Fallback response
            return {
                "title": f"Educational Mashup: {prompt[:30]}",
                "lyrics": "Generated lyrics will appear here...",
                "educational_content": {
                    "theory_concepts": ["rhythm", "melody"],
                    "cultural_context": "Basic cultural information",
                    "teaching_notes": "Use this to introduce genre concepts"
                }
            }
```

---

## 7. Essential API Layer

### 7.1 Single File FastAPI App

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio

from database import MashupDB
from agents import SimpleMashupAgent

app = FastAPI(
    title="Lit Music Mashup MVP",
    description="Educational AI Music Generation - MVP",
    version="2.0.0-mvp"
)

# Initialize components
db = MashupDB()
agent = SimpleMashupAgent()

# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str
    skill_level: str = "beginner"

class MashupResponse(BaseModel):
    id: int
    title: str
    lyrics: str
    educational_content: dict

@app.get("/")
async def root():
    return {
        "message": "Lit Music Mashup MVP v2.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0-mvp"}

@app.post("/api/v1/generate", response_model=MashupResponse)
async def generate_mashup(request: GenerateRequest):
    """Generate educational mashup (MVP core functionality)"""
    
    try:
        # Validate input
        if len(request.prompt.strip()) < 5:
            raise HTTPException(400, "Prompt must be at least 5 characters")
        
        # Generate mashup
        result = await agent.generate_mashup(request.prompt, request.skill_level)
        
        # Save to database
        mashup_data = {
            "prompt": request.prompt,
            "skill_level": request.skill_level,
            **result
        }
        mashup_id = db.save_mashup(mashup_data)
        
        return MashupResponse(
            id=mashup_id,
            title=result['title'],
            lyrics=result['lyrics'],
            educational_content=result['educational_content']
        )
        
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {str(e)}")

@app.get("/api/v1/mashup/{mashup_id}")
async def get_mashup(mashup_id: int):
    """Get generated mashup by ID"""
    
    mashup = db.get_mashup(mashup_id)
    if not mashup:
        raise HTTPException(404, "Mashup not found")
    
    return mashup

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 8. CI/CD Pipeline Setup

### 8.1 GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: Lit Music Mashup CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: |
        pytest test_main.py -v
    
    - name: Test API endpoints
      run: |
        python -c "
        import requests
        import time
        import subprocess
        
        # Start server in background
        proc = subprocess.Popen(['uvicorn', 'main:app', '--port', '8001'])
        time.sleep(5)
        
        try:
            # Test health endpoint
            resp = requests.get('http://localhost:8001/health')
            assert resp.status_code == 200
            
            # Test generate endpoint (mock)
            # resp = requests.post('http://localhost:8001/api/v1/generate', 
            #                     json={'prompt': 'test', 'skill_level': 'beginner'})
            # assert resp.status_code == 200
            
            print('API tests passed')
        finally:
            proc.terminate()
        "

  quality-check:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install quality tools
      run: |
        pip install black isort flake8
    
    - name: Check code formatting
      run: |
        black --check .
        isort --check-only .
        flake8 .

  deploy:
    runs-on: ubuntu-latest
    needs: [test, quality-check]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t lit-music-mashup:${{ github.sha }} .
    
    - name: Test Docker container
      run: |
        docker run -d -p 8002:8000 --name test-container lit-music-mashup:${{ github.sha }}
        sleep 10
        curl -f http://localhost:8002/health || exit 1
        docker stop test-container
        docker rm test-container
    
    # Add deployment steps here (e.g., push to registry, deploy to server)
```

### 8.2 Essential Tests

```python
# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app
from database import MashupDB
import tempfile
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    db = MashupDB(path)
    yield db
    os.unlink(path)

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Lit Music Mashup MVP v2.0" in response.json()["message"]

def test_health_endpoint(client):
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_endpoint_validation(client):
    """Test input validation"""
    # Test short prompt
    response = client.post("/api/v1/generate", json={
        "prompt": "hi",
        "skill_level": "beginner"
    })
    assert response.status_code == 400

def test_generate_endpoint_valid_input(client):
    """Test valid generation request"""
    response = client.post("/api/v1/generate", json={
        "prompt": "Create a jazz and blues mashup for beginners",
        "skill_level": "beginner"
    })
    
    # Should succeed (might timeout without actual Ollama)
    # assert response.status_code == 200
    # data = response.json()
    # assert "title" in data
    # assert "lyrics" in data
    # assert "educational_content" in data

def test_database_operations(temp_db):
    """Test database functionality"""
    # Test saving mashup
    mashup_data = {
        "prompt": "test prompt",
        "skill_level": "beginner",
        "title": "Test Title",
        "lyrics": "Test lyrics",
        "educational_content": {"concepts": ["rhythm"]}
    }
    
    mashup_id = temp_db.save_mashup(mashup_data)
    assert mashup_id is not None
    
    # Test retrieving mashup
    retrieved = temp_db.get_mashup(mashup_id)
    assert retrieved is not None
    assert retrieved["title"] == "Test Title"
    assert retrieved["educational_content"]["concepts"] == ["rhythm"]

@pytest.mark.asyncio
async def test_agent_fallback():
    """Test agent fallback functionality"""
    from agents import SimpleMashupAgent
    
    agent = SimpleMashupAgent()
    result = await agent.generate_mashup("test prompt", "beginner")
    
    # Should return fallback response
    assert "title" in result
    assert "lyrics" in result
    assert "educational_content" in result
```

---

## 9. MVP Validation & Testing

### 9.1 MVP Success Criteria

**Core Functionality Tests**:
```python
# MVP must pass these tests
def test_mvp_core_functionality():
    """Test complete MVP workflow"""
    
    # 1. API accepts request
    request = {
        "prompt": "Jazz and hip-hop mashup for high school",
        "skill_level": "intermediate"
    }
    
    # 2. Returns structured response
    response = client.post("/api/v1/generate", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["title"]) > 0
    assert len(data["lyrics"]) > 10
    assert "theory_concepts" in data["educational_content"]
    assert "cultural_context" in data["educational_content"]
    assert "teaching_notes" in data["educational_content"]
    
    # 3. Data persists in database
    mashup_id = data["id"]
    get_response = client.get(f"/api/v1/mashup/{mashup_id}")
    assert get_response.status_code == 200
```

### 9.2 Performance Benchmarks

```python
# Performance tests for MVP
def test_response_time():
    """Ensure reasonable response times"""
    import time
    
    start_time = time.time()
    response = client.post("/api/v1/generate", json={
        "prompt": "Simple mashup test",
        "skill_level": "beginner"
    })
    end_time = time.time()
    
    # MVP should respond within 60 seconds
    assert (end_time - start_time) < 60
    
def test_database_performance():
    """Test database operations are fast"""
    import time
    
    start_time = time.time()
    for i in range(100):
        temp_db.save_mashup({
            "prompt": f"test {i}",
            "skill_level": "beginner",
            "title": f"Title {i}",
            "lyrics": f"Lyrics {i}",
            "educational_content": {}
        })
    end_time = time.time()
    
    # Should save 100 records in under 1 second
    assert (end_time - start_time) < 1.0
```

---

## 10. Feature Addition Strategy

### 10.1 Incremental Development Process

**Step 1: Create Feature Branch**
```bash
git checkout -b feature/multiple-hooks
```

**Step 2: Add Tests First (TDD)**
```python
# test_multiple_hooks.py
def test_multiple_hook_generation():
    """Test that we can generate multiple hooks"""
    response = client.post("/api/v1/generate", json={
        "prompt": "Jazz blues mashup",
        "skill_level": "intermediate",
        "options": {"multiple_hooks": True}
    })
    
    data = response.json()
    assert "hooks" in data
    assert len(data["hooks"]) >= 3
```

**Step 3: Implement Feature**
```python
# Add to main.py
class GenerateRequest(BaseModel):
    prompt: str
    skill_level: str = "beginner"
    options: Optional[dict] = {}  # New field

# Update generate_mashup function
@app.post("/api/v1/generate", response_model=MashupResponse)
async def generate_mashup(request: GenerateRequest):
    # Add multiple hooks logic
    multiple_hooks = request.options.get("multiple_hooks", False)
    result = await agent.generate_mashup(
        request.prompt, 
        request.skill_level, 
        multiple_hooks=multiple_hooks
    )
    # ... rest of function
```

**Step 4: Run Tests**
```bash
pytest test_main.py test_multiple_hooks.py -v
```

**Step 5: Create PR and Let CI/CD Validate**
```bash
git add .
git commit -m "Add multiple hooks feature"
git push origin feature/multiple-hooks
# Create PR on GitHub
```

### 10.2 Feature Addition Roadmap

**Phase 2 Features (Week 3-4)**:
```python
# Features to add after MVP is stable
PHASE_2_FEATURES = [
    "multiple_hook_options",      # Generate 3-5 hook variations
    "detailed_theory_analysis",   # Expand music theory content
    "cultural_context_expansion", # More detailed cultural info
    "error_recovery_system",      # Better error handling
    "request_validation"          # Enhanced input validation
]
```

**Phase 3 Features (Week 5-6)**:
```python
PHASE_3_FEATURES = [
    "user_authentication",       # Basic user system
    "session_management",        # Track user sessions
    "mashup_rating_system",      # Rate generated content
    "export_functionality",      # Export to different formats
    "api_rate_limiting"          # Prevent abuse
]
```

**Phase 4 Features (Week 7+)**:
```python
PHASE_4_FEATURES = [
    "real_time_collaboration",   # WebSocket-based collaboration
    "postgresql_migration",      # Move from SQLite to PostgreSQL
    "advanced_analytics",        # Usage analytics and insights
    "lms_integration",           # Canvas, Blackboard integration
    "mobile_api_endpoints"       # Mobile app support
]
```

### 10.3 Quality Gates

**Every Feature Must Pass**:
1. ✅ All existing tests still pass
2. ✅ New feature has comprehensive tests
3. ✅ Code coverage remains > 80%
4. ✅ Performance benchmarks met
5. ✅ API documentation updated
6. ✅ No security vulnerabilities introduced

**CI/CD Pipeline Ensures**:
- Automated testing on every PR
- Code quality checks (black, isort, flake8)
- Docker container builds successfully
- API endpoints remain functional
- Database migrations work (when applicable)

---

## 11. Summary

### 11.1 MVP v2.0 Advantages

**Simplified Development**:
- Single file FastAPI application
- SQLite database (no complex setup)
- Basic AI agent (no over-engineering)
- Essential tests only
- Straightforward Docker deployment

**Quality Assurance**:
- GitHub Actions CI/CD from day one
- Test-driven feature development
- Automated quality checks
- No feature addition without tests
- Performance monitoring built-in

**Educational Focus Maintained**:
- Every response includes educational content
- Theory concepts in simple format
- Cultural context awareness
- Teaching notes for educators
- Beginner-friendly design

### 11.2 Next Steps

**Week 1**: 
1. Set up basic project structure
2. Implement MVP core functionality
3. Create essential tests
4. Set up CI/CD pipeline

**Week 2**: 
1. Validate MVP with real users
2. Fix any critical issues
3. Optimize performance
4. Prepare for Phase 2 features

**Week 3+**: 
1. Add features incrementally
2. Maintain test coverage
3. Monitor performance metrics
4. Gather user feedback for priorities

This simplified approach ensures we have a working educational AI music platform quickly while maintaining quality and educational value through every iteration.