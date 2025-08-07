from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, Dict, Any, List
import logging
import os
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from collections import defaultdict
import asyncio

# Import database components
from app.db import AsyncConversationDB, ConversationPhase, MessageRole, ToolCallType
from app.db.utils import DatabaseUtils, DatabasePerformanceMonitor
from app.db.validation import ValidationError
from app.config import get_settings
from app.services import AsyncWebSearchService, get_web_search_service, AsyncToolOrchestrator, get_tool_orchestrator
from app.agents.conversation_agent import AsyncConversationalMashupAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database instance for lifespan management
db_instance: Optional[AsyncConversationDB] = None

# Rate limiting storage - reset for each test
rate_limit_storage = defaultdict(list)

def reset_rate_limit_storage():
    """Reset rate limiting storage for testing."""
    global rate_limit_storage
    rate_limit_storage.clear()

# Security
security = HTTPBearer(auto_error=False)

# Rate limiting middleware function
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for API endpoints."""
    requests_per_minute = 60
    
    # Skip rate limiting for exempt paths
    exempt_paths = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
    
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host
    
    # Clean old requests
    current_time = time.time()
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < 60
    ]
    
    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= requests_per_minute:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
        )
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    
    # Process request
    response = await call_next(request)
    return response

# Authentication middleware function
async def authentication_middleware(request: Request, call_next):
    """Authentication middleware for API endpoints."""
    api_key = os.getenv("API_KEY")
    exempt_paths = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
    
    # Skip authentication for exempt paths
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # Check for API key in headers
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authorization header required",
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    # Validate API key
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid authorization header format",
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    api_key_from_header = auth_header.replace("Bearer ", "")
    if api_key and api_key_from_header != api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid API key",
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    return await call_next(request)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Lit Music Mashup Conversational API")
    settings = get_settings()
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database path: {settings.DATABASE_PATH}")
    
    # Initialize database on startup
    global db_instance
    try:
        db_instance = AsyncConversationDB(settings.DATABASE_PATH)
        await db_instance.init_db()
        logger.info("Database initialized successfully on startup")
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Lit Music Mashup Conversational API")
    if db_instance:
        await db_instance.close()

# Create FastAPI app with lifespan
app = FastAPI(
    title="Lit Music Mashup Conversational API",
    description="""
    ## Educational AI Music Generation Platform
    
    This API provides conversational AI-powered educational music mashup generation with comprehensive learning materials.
    
    ### Key Features:
    - **Conversational Interface**: Multi-turn conversations to gather context
    - **Educational Focus**: Every mashup includes music theory and cultural context
    - **Tool Integration**: Web search for current cultural information
    - **Phase-based Management**: Structured conversation flow
    - **Local AI Models**: Privacy-focused with Ollama integration
    
    ### Authentication:
    - API key required via Authorization header: `Bearer YOUR_API_KEY`
    - Set API_KEY environment variable for authentication
    
    ### Rate Limiting:
    - 60 requests per minute per IP address
    - Exempt endpoints: health, docs, root
    
    ### Usage Flow:
    1. Start conversation via `/api/v1/chat`
    2. Agent gathers context through multi-turn dialogue
    3. Web search tools provide current cultural information
    4. Generate educational mashup when context is sufficient
    
    ### Support:
    For questions or issues, consult the project documentation.
    """,
    version="2.0.0-conversational-mvp",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Lit Music Mashup Team",
        "url": "https://github.com/your-repo/lit-music-mashup",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "Core",
            "description": "Core application endpoints (health, info)"
        },
        {
            "name": "Conversation",
            "description": "Conversational AI interaction endpoints"
        },
        {
            "name": "Database",
            "description": "Database operations and management"
        },
        {
            "name": "Tools",
            "description": "Tool integration and web search"
        },
        {
            "name": "Admin",
            "description": "Administrative database utilities"
        }
    ]
)

# Add middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(authentication_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "your-domain.com"]
    )

# Enhanced Pydantic models with validation
class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database status")

class AppInfoResponse(BaseModel):
    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    description: str = Field(..., description="Application description")
    status: str = Field(..., description="Application status")

class ConversationCreateRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100, description="Unique conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if not v.strip():
            raise ValueError('Conversation ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Conversation ID too long')
        # Check for valid characters
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Conversation ID can only contain alphanumeric characters, hyphens, and underscores')
        return v.strip()

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            # Limit metadata size
            if len(str(v)) > 1000:
                raise ValueError('Metadata too large (max 1000 characters)')
        return v

class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    phase: str = Field(..., description="Current conversation phase")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., ge=0, description="Number of messages")

class MessageCreateRequest(BaseModel):
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    @validator('role')
    def validate_role(cls, v):
        valid_roles = [role.value for role in MessageRole]
        if v not in valid_roles:
            raise ValueError(f'Invalid role. Must be one of: {valid_roles}')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        if len(v) > 10000:
            raise ValueError('Message content too long')
        # Check for potentially harmful content
        harmful_patterns = ['<script>', 'javascript:', 'data:text/html']
        v_lower = v.lower()
        for pattern in harmful_patterns:
            if pattern in v_lower:
                raise ValueError('Message content contains potentially harmful content')
        return v.strip()

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            # Limit metadata size
            if len(str(v)) > 1000:
                raise ValueError('Metadata too large (max 1000 characters)')
        return v

class MessageResponse(BaseModel):
    message_id: int = Field(..., description="Message ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class ToolCallCreateRequest(BaseModel):
    tool_type: str = Field(..., description="Type of tool call")
    input_data: str = Field(..., min_length=1, max_length=10000, description="Input data for tool")
    output_data: Optional[str] = Field(None, max_length=50000, description="Output data from tool")
    status: str = Field(default="pending", description="Tool call status")
    error_message: Optional[str] = Field(None, max_length=1000, description="Error message if failed")

    @validator('tool_type')
    def validate_tool_type(cls, v):
        valid_types = [tool_type.value for tool_type in ToolCallType]
        if v not in valid_types:
            raise ValueError(f'Invalid tool type. Must be one of: {valid_types}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["pending", "running", "completed", "failed", "timeout"]
        if v not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {valid_statuses}')
        return v

    @validator('input_data')
    def validate_input_data(cls, v):
        if not v.strip():
            raise ValueError('Input data cannot be empty')
        if len(v) > 10000:
            raise ValueError('Input data too long')
        return v.strip()

    @validator('output_data')
    def validate_output_data(cls, v):
        if v is not None and len(v) > 50000:
            raise ValueError('Output data too long')
        return v

    @validator('error_message')
    def validate_error_message(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Error message too long')
        return v

class ToolCallResponse(BaseModel):
    tool_call_id: int = Field(..., description="Tool call ID")
    conversation_id: str = Field(..., description="Conversation ID")
    tool_type: str = Field(..., description="Tool type")
    input_data: str = Field(..., description="Input data")
    output_data: Optional[str] = Field(None, description="Output data")
    status: str = Field(..., description="Status")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message")

class WebSourceCreateRequest(BaseModel):
    url: str = Field(..., description="Web source URL")
    title: Optional[str] = Field(None, max_length=500, description="Web source title")
    snippet: Optional[str] = Field(None, max_length=2000, description="Web source snippet")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score")

    @validator('url')
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError('URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        if len(v) > 2048:
            raise ValueError('URL too long')
        return v.strip()

    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Title too long')
        return v

    @validator('snippet')
    def validate_snippet(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError('Snippet too long')
        return v

    @validator('relevance_score')
    def validate_relevance_score(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Relevance score must be between 0.0 and 1.0')
        return v

class WebSourceResponse(BaseModel):
    source_id: int = Field(..., description="Source ID")
    tool_call_id: int = Field(..., description="Tool call ID")
    url: str = Field(..., description="Web source URL")
    title: Optional[str] = Field(None, description="Web source title")
    snippet: Optional[str] = Field(None, description="Web source snippet")
    relevance_score: Optional[float] = Field(None, description="Relevance score")
    created_at: datetime = Field(..., description="Creation timestamp")

class MashupCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Mashup title")
    description: Optional[str] = Field(None, max_length=1000, description="Mashup description")
    audio_file_path: Optional[str] = Field(None, description="Audio file path")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title too long')
        # Check for potentially harmful content
        harmful_patterns = ['<script>', 'javascript:', 'data:text/html']
        v_lower = v.lower()
        for pattern in harmful_patterns:
            if pattern in v_lower:
                raise ValueError('Title contains potentially harmful content')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('Description too long')
        return v

    @validator('audio_file_path')
    def validate_audio_file_path(cls, v):
        if v is not None:
            # Check for valid audio file extensions
            valid_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
            if not any(v.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError('Invalid audio file format. Supported formats: mp3, wav, flac, aac, ogg')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            # Limit metadata size
            if len(str(v)) > 1000:
                raise ValueError('Metadata too large (max 1000 characters)')
        return v

class MashupResponse(BaseModel):
    mashup_id: int = Field(..., description="Mashup ID")
    conversation_id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Mashup title")
    description: Optional[str] = Field(None, description="Mashup description")
    audio_file_path: Optional[str] = Field(None, description="Audio file path")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

class ConversationSummaryResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    phase: str = Field(..., description="Current phase")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., ge=0, description="Message count")
    tool_call_count: int = Field(..., ge=0, description="Tool call count")
    mashup_count: int = Field(..., ge=0, description="Mashup count")
    web_source_count: int = Field(..., ge=0, description="Web source count")

class ChatRequest(BaseModel):
    """Chat request model for conversational AI interaction."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message", example="I want to create a jazz and hip-hop mashup for my students")
    session_id: Optional[str] = Field(None, max_length=100, description="Session ID for conversation continuity", example="session_20240101_120000")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the conversation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "I want to create a jazz and hip-hop mashup for my students",
                "session_id": "session_20240101_120000",
                "context": {"skill_level": "intermediate", "class_size": 25}
            }
        }
    )

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long')
        # Check for potentially harmful content
        harmful_patterns = ['<script>', 'javascript:', 'data:text/html']
        v_lower = v.lower()
        for pattern in harmful_patterns:
            if pattern in v_lower:
                raise ValueError('Message contains potentially harmful content')
        return v.strip()

    @validator('session_id')
    def validate_session_id(cls, v):
        if v is not None:
            if len(v) > 100:
                raise ValueError('Session ID too long')
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Session ID can only contain alphanumeric characters, hyphens, and underscores')
        return v

    @validator('context')
    def validate_context(cls, v):
        if v is not None:
            # Limit context size
            if len(str(v)) > 2000:
                raise ValueError('Context too large (max 2000 characters)')
        return v

class ChatResponse(BaseModel):
    """Chat response model from conversational AI agent."""
    response: str = Field(..., description="AI agent response", example="Great! Let's explore jazz and hip-hop fusion. What specific learning objectives do you have?")
    session_id: str = Field(..., description="Session ID for conversation continuity", example="session_20240101_120000")
    phase: str = Field(..., description="Current conversation phase", example="genre_exploration")
    phase_transition: bool = Field(..., description="Whether phase transition occurred", example=True)
    new_phase: Optional[str] = Field(None, description="New phase if transition occurred", example="educational_clarification")
    context: Dict[str, Any] = Field(..., description="Current conversation context")
    tool_results: Optional[Dict[str, Any]] = Field(None, description="Results from tool executions (web search, etc.)")
    timestamp: datetime = Field(..., description="Response timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Great! Let's explore jazz and hip-hop fusion. What specific learning objectives do you have?",
                "session_id": "session_20240101_120000",
                "phase": "genre_exploration",
                "phase_transition": True,
                "new_phase": "educational_clarification",
                "context": {"genres": ["jazz", "hip-hop"], "skill_level": "intermediate"},
                "tool_results": {"web_search": {"sources_found": 5}},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )

class ToolStatisticsResponse(BaseModel):
    total_tool_calls: int = Field(..., ge=0, description="Total tool calls")
    successful_calls: int = Field(..., ge=0, description="Successful tool calls")
    failed_calls: int = Field(..., ge=0, description="Failed tool calls")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    average_response_time: Optional[float] = Field(None, ge=0.0, description="Average response time in seconds")

class StandardResponse(BaseModel):
    """Standard API response format for consistency across all endpoints."""
    status: str = Field(..., description="Response status (success/error)", example="success")
    message: str = Field(..., description="Human-readable response message", example="Operation completed successfully")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data payload")
    timestamp: datetime = Field(..., description="Response timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {"example_key": "example_value"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )

class ErrorResponse(BaseModel):
    """Standard error response format for consistency across all endpoints."""
    status: str = Field(default="error", description="Error status", example="error")
    message: str = Field(..., description="Error message", example="Validation failed")
    detail: Optional[str] = Field(None, description="Error detail", example="Input validation failed for field 'message'")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Validation failed",
                "detail": "Input validation failed for field 'message'",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )

# Dependency injection functions
async def get_db():
    """Get database instance."""
    if db_instance is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_instance

async def get_settings_dep():
    """Get settings instance."""
    return get_settings()

async def get_tool_orchestrator_dep():
    """Get tool orchestrator instance."""
    db = await get_db()
    web_search = get_web_search_service()
    return await get_tool_orchestrator(web_search_service=web_search, db=db)

async def get_conversation_agent():
    """Get conversation agent instance."""
    settings = get_settings()
    return AsyncConversationalMashupAgent(
        model_name=settings.OLLAMA_MODEL,
        tavily_api_key=settings.TAVILY_API_KEY,
        db_path=settings.DATABASE_PATH,
        enable_tools=True
    )

# Root endpoint with enhanced response
@app.get("/", response_model=AppInfoResponse, tags=["Core"])
async def root():
    """Root endpoint with app information"""
    return AppInfoResponse(
        name="Lit Music Mashup Conversational API",
        version="2.0.0-conversational-mvp",
        description="Educational AI Music Generation with Conversational Interface",
        status="running"
    )

# Enhanced health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Core"])
async def health_check(db: AsyncConversationDB = Depends(get_db)):
    """Health check endpoint with database status"""
    try:
        # Test database connection
        await db.init_db()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="2.0.0-conversational-mvp",
        database_status=db_status
    )

# Enhanced conversation endpoints with validation
@app.post("/conversations", response_model=ConversationResponse, tags=["Database"])
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Create a new conversation with enhanced validation"""
    try:
        success = await db.create_conversation(
            request.conversation_id,
            metadata=request.metadata
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create conversation")
        
        # Get the created conversation
        conversation = await db.get_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=500, detail="Conversation not found after creation")
        
        # Get message count
        messages = await db.get_messages(request.conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation["conversation_id"],
            phase=conversation["phase"],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
            message_count=len(messages)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse, tags=["Database"])
async def get_conversation(
    conversation_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get conversation details with validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get message count
        messages = await db.get_messages(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation["conversation_id"],
            phase=conversation["phase"],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
            message_count=len(messages)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced message operations with validation
@app.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    request: MessageCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a message to a conversation with enhanced validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        # Validate role
        if request.role not in [role.value for role in MessageRole]:
            raise HTTPException(status_code=400, detail="Invalid message role")
        
        success = await db.add_message(
            conversation_id,
            MessageRole(request.role),
            request.content,
            metadata=request.metadata
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add message")
        
        # Get the latest message
        messages = await db.get_messages(conversation_id, limit=1)
        if not messages:
            raise HTTPException(status_code=500, detail="Message not found after creation")
        
        latest_message = messages[0]
        return MessageResponse(
            message_id=latest_message["message_id"],
            conversation_id=latest_message["conversation_id"],
            role=latest_message["role"],
            content=latest_message["content"],
            timestamp=latest_message["timestamp"],
            metadata=latest_message.get("metadata")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    db: AsyncConversationDB = Depends(get_db)
):
    """Get messages for a conversation with pagination"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        messages = await db.get_messages(conversation_id, limit=limit, offset=offset)
        return [
            MessageResponse(
                message_id=msg["message_id"],
                conversation_id=msg["conversation_id"],
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                metadata=msg.get("metadata")
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced tool call operations
@app.post("/conversations/{conversation_id}/tool-calls", response_model=ToolCallResponse)
async def add_tool_call(
    conversation_id: str,
    request: ToolCallCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a tool call to a conversation with enhanced validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        # Validate tool type
        if request.tool_type not in [tool_type.value for tool_type in ToolCallType]:
            raise HTTPException(status_code=400, detail="Invalid tool type")
        
        tool_call_id = await db.add_tool_call(
            conversation_id,
            ToolCallType(request.tool_type),
            request.input_data,
            output_data=request.output_data,
            status=request.status,
            error_message=request.error_message
        )
        if not tool_call_id:
            raise HTTPException(status_code=400, detail="Failed to add tool call")
        
        # Get the created tool call
        tool_call = await db.get_tool_call(tool_call_id)
        if not tool_call:
            raise HTTPException(status_code=500, detail="Tool call not found after creation")
        
        return ToolCallResponse(
            tool_call_id=tool_call["tool_call_id"],
            conversation_id=tool_call["conversation_id"],
            tool_type=tool_call["tool_type"],
            input_data=tool_call["input_data"],
            output_data=tool_call["output_data"],
            status=tool_call["status"],
            created_at=tool_call["created_at"],
            completed_at=tool_call.get("completed_at"),
            error_message=tool_call.get("error_message")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tool call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced web source operations
@app.post("/tool-calls/{tool_call_id}/web-sources", response_model=WebSourceResponse)
async def add_web_source(
    tool_call_id: int,
    request: WebSourceCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a web source to a tool call with enhanced validation"""
    try:
        success = await db.add_web_source(
            tool_call_id,
            request.url,
            title=request.title,
            snippet=request.snippet,
            relevance_score=request.relevance_score
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add web source")
        
        # Return a basic response (we'll need to add a get_web_source method)
        return WebSourceResponse(
            source_id=0,  # Placeholder
            tool_call_id=tool_call_id,
            url=request.url,
            title=request.title,
            snippet=request.snippet,
            relevance_score=request.relevance_score,
            created_at=datetime.now(timezone.utc)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding web source: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced mashup operations
@app.post("/conversations/{conversation_id}/mashups", response_model=MashupResponse)
async def create_mashup(
    conversation_id: str,
    request: MashupCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Create a mashup for a conversation with enhanced validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        mashup_id = await db.create_mashup(
            conversation_id,
            request.title,
            description=request.description,
            audio_file_path=request.audio_file_path,
            metadata=request.metadata
        )
        if not mashup_id:
            raise HTTPException(status_code=400, detail="Failed to create mashup")
        
        # Return a basic response (we'll need to add a get_mashup method)
        return MashupResponse(
            mashup_id=mashup_id,
            conversation_id=conversation_id,
            title=request.title,
            description=request.description,
            audio_file_path=request.audio_file_path,
            metadata=request.metadata,
            created_at=datetime.now(timezone.utc)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating mashup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced conversation summary
@app.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get a comprehensive summary of a conversation with validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        summary = await db.get_conversation_summary(conversation_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationSummaryResponse(
            conversation_id=summary["conversation_id"],
            phase=summary["phase"],
            created_at=summary["created_at"],
            updated_at=summary["updated_at"],
            message_count=summary["message_count"],
            tool_call_count=summary.get("tool_call_count", 0),
            mashup_count=summary.get("mashup_count", 0),
            web_source_count=summary.get("web_source_count", 0)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced phase management
@app.put("/conversations/{conversation_id}/phase")
async def update_conversation_phase(
    conversation_id: str,
    phase: str = Query(..., description="New conversation phase"),
    db: AsyncConversationDB = Depends(get_db)
):
    """Update the phase of a conversation with validation"""
    try:
        # Validate conversation_id
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
        
        # Validate phase
        if phase not in [phase.value for phase in ConversationPhase]:
            raise HTTPException(status_code=400, detail="Invalid conversation phase")
        
        success = await db.update_conversation_phase(
            conversation_id,
            ConversationPhase(phase)
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update conversation phase")
        
        return StandardResponse(
            status="success",
            message="Conversation phase updated successfully",
            timestamp=datetime.now(timezone.utc)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation phase: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced web search endpoints
@app.get("/api/v1/web-search/status")
async def get_web_search_status(
    web_search: AsyncWebSearchService = Depends(get_web_search_service)
):
    """Get web search service status with enhanced response"""
    try:
        status = web_search.get_service_status()
        return StandardResponse(
            status="success",
            message="Web search status retrieved successfully",
            data=status,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error getting web search status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

class WebSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    context: Optional[Dict[str, Any]] = Field(None, description="Search context")

@app.post("/api/v1/web-search/search", tags=["Tools"])
async def search_educational_content(
    request: WebSearchRequest,
    web_search: AsyncWebSearchService = Depends(get_web_search_service)
):
    """Search for educational content with enhanced validation"""
    try:
        if request.context is None:
            context = {}
        else:
            context = request.context
        
        result = await web_search.search_educational_content(request.query, context)
        return StandardResponse(
            status="success",
            message="Educational content search completed successfully",
            data=result,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced conversational API endpoints
@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Conversation"])
async def chat_with_agent(
    request: ChatRequest,
    agent: AsyncConversationalMashupAgent = Depends(get_conversation_agent)
):
    """
    Chat with the conversational AI agent.
    
    This endpoint provides the main conversational interface for the educational
    music mashup platform with tool integration and phase-based conversation management.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Process message with agent
        result = await agent.process_message(
            session_id=session_id,
            user_message=request.message,
            context=request.context
        )
        
        # Prepare response
        response = ChatResponse(
            response=result['response'],
            session_id=session_id,
            phase=result['phase'].value,
            phase_transition=result['phase_transition'],
            new_phase=result['new_phase'].value if result['new_phase'] else None,
            context=result['context'],
            tool_results=result.get('tool_results'),
            timestamp=datetime.now(timezone.utc)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/session/{session_id}", tags=["Conversation"])
async def get_conversation_session(
    session_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get conversation session information with validation"""
    try:
        # Validate session_id
        if not session_id.strip():
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")
        
        conversation = await db.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get recent messages
        messages = await db.get_messages(session_id, limit=10)
        
        # Get tool statistics
        tool_stats = await db.get_conversation_tool_calls(session_id, limit=5)
        
        return StandardResponse(
            status="success",
            message="Session information retrieved successfully",
            data={
                "session_id": session_id,
                "conversation": conversation,
                "recent_messages": messages,
                "tool_calls": tool_stats
            },
            timestamp=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/tools/statistics", response_model=ToolStatisticsResponse, tags=["Tools"])
async def get_tool_statistics(
    session_id: Optional[str] = Query(None, description="Optional session ID for filtering"),
    tool_orchestrator: AsyncToolOrchestrator = Depends(get_tool_orchestrator_dep)
):
    """Get tool usage statistics with validation"""
    try:
        stats = await tool_orchestrator.get_tool_statistics(session_id)
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return ToolStatisticsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/tools/status", tags=["Tools"])
async def get_tools_status(
    tool_orchestrator: AsyncToolOrchestrator = Depends(get_tool_orchestrator_dep)
):
    """Get status of all available tools with enhanced response"""
    try:
        web_search_available = await tool_orchestrator.is_web_search_available()
        
        return StandardResponse(
            status="success",
            message="Tools status retrieved successfully",
            data={
                "web_search": {
                    "available": web_search_available,
                    "service": "Tavily API"
                },
                "tool_orchestrator": {
                    "available": True,
                    "max_concurrent_tools": tool_orchestrator.max_concurrent_tools,
                    "tool_timeout": tool_orchestrator.tool_timeout
                }
            },
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error getting tools status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced database utility endpoints
@app.post("/admin/database/backup", tags=["Admin"])
async def create_database_backup(
    backup_name: Optional[str] = Query(None, max_length=100, description="Optional backup name"),
    settings: Any = Depends(get_settings_dep)
):
    """Create a database backup with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        backup_path = await utils.create_backup(backup_name)
        return StandardResponse(
            status="success",
            message="Database backup created successfully",
            data={"backup_path": backup_path},
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create database backup")

@app.get("/admin/database/backups")
async def list_database_backups(settings: Any = Depends(get_settings_dep)):
    """List available database backups with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        backups = await utils.list_backups()
        return StandardResponse(
            status="success",
            message="Database backups retrieved successfully",
            data={"backups": backups},
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to list database backups: {e}")
        raise HTTPException(status_code=500, detail="Failed to list database backups")

@app.post("/admin/database/restore")
async def restore_database_backup(
    backup_path: str = Query(..., description="Path to backup file"),
    settings: Any = Depends(get_settings_dep)
):
    """Restore database from backup with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        success = await utils.restore_backup(backup_path)
        if success:
            return StandardResponse(
                status="success",
                message="Database restored successfully",
                timestamp=datetime.now(timezone.utc)
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to restore database")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore database")

@app.get("/admin/database/info")
async def get_database_info(settings: Any = Depends(get_settings_dep)):
    """Get database information and statistics with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        info = await utils.get_database_info()
        return StandardResponse(
            status="success",
            message="Database information retrieved successfully",
            data=info,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database info")

@app.get("/admin/database/integrity")
async def validate_database_integrity(settings: Any = Depends(get_settings_dep)):
    """Validate database integrity with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        integrity = await utils.validate_database_integrity()
        return StandardResponse(
            status="success",
            message="Database integrity validation completed",
            data=integrity,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to validate database integrity: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate database integrity")

@app.post("/admin/database/optimize")
async def optimize_database(settings: Any = Depends(get_settings_dep)):
    """Optimize database performance with enhanced response"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        success = await utils.optimize_database()
        if success:
            return StandardResponse(
                status="success",
                message="Database optimization completed successfully",
                timestamp=datetime.now(timezone.utc)
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to optimize database")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize database")

@app.get("/admin/database/metrics")
async def get_database_metrics(settings: Any = Depends(get_settings_dep)):
    """Get database performance metrics with enhanced response"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        metrics = await monitor.collect_metrics()
        return StandardResponse(
            status="success",
            message="Database metrics retrieved successfully",
            data=metrics,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to collect database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect database metrics")

@app.get("/admin/database/metrics/history")
async def get_database_metrics_history(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Number of history entries to retrieve"),
    settings: Any = Depends(get_settings_dep)
):
    """Get database metrics history with enhanced response"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        history = monitor.get_metrics_history(limit)
        return StandardResponse(
            status="success",
            message="Database metrics history retrieved successfully",
            data={"metrics_history": history},
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to get database metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database metrics history")

@app.get("/admin/database/metrics/summary")
async def get_database_performance_summary(settings: Any = Depends(get_settings_dep)):
    """Get database performance summary with enhanced response"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        summary = monitor.get_performance_summary()
        return StandardResponse(
            status="success",
            message="Database performance summary retrieved successfully",
            data=summary,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Failed to get database performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database performance summary")

# Enhanced error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with enhanced error response"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Validation error handler with enhanced error response"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Validation error",
            "detail": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler with enhanced error response"""
    logger.error(f"HTTP exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
