from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager

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
    description="Educational AI Music Generation with Conversational Interface",
    version="2.0.0-conversational-mvp",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_status: str

class AppInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    status: str

class ConversationCreateRequest(BaseModel):
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    phase: str
    created_at: datetime
    updated_at: datetime
    message_count: int

class MessageCreateRequest(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    message_id: int
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ToolCallCreateRequest(BaseModel):
    tool_type: str
    input_data: str
    output_data: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None

class ToolCallResponse(BaseModel):
    tool_call_id: int
    conversation_id: str
    tool_type: str
    input_data: str
    output_data: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class WebSourceCreateRequest(BaseModel):
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None

class WebSourceResponse(BaseModel):
    source_id: int
    tool_call_id: int
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None
    created_at: datetime

class MashupCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    audio_file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MashupResponse(BaseModel):
    mashup_id: int
    conversation_id: str
    title: str
    description: Optional[str] = None
    audio_file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class ConversationSummaryResponse(BaseModel):
    conversation_id: str
    phase: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    tool_call_count: int
    mashup_count: int
    web_source_count: int

# Conversational API models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    phase: str
    phase_transition: bool
    new_phase: Optional[str] = None
    context: Dict[str, Any]
    tool_results: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ToolStatisticsResponse(BaseModel):
    total_tool_calls: int
    successful_calls: int
    failed_calls: int
    success_rate: float

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

# Root endpoint
@app.get("/", response_model=AppInfoResponse)
async def root():
    """Root endpoint with app information"""
    return AppInfoResponse(
        name="Lit Music Mashup Conversational API",
        version="2.0.0-conversational-mvp",
        description="Educational AI Music Generation with Conversational Interface",
        status="running"
    )

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
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

# Basic conversation endpoints
@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Create a new conversation"""
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
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get conversation details"""
    try:
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

# Message operations
@app.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    request: MessageCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a message to a conversation"""
    try:
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
    limit: Optional[int] = None,
    offset: int = 0,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get messages for a conversation"""
    try:
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
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Tool call operations
@app.post("/conversations/{conversation_id}/tool-calls", response_model=ToolCallResponse)
async def add_tool_call(
    conversation_id: str,
    request: ToolCallCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a tool call to a conversation"""
    try:
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

# Web source operations
@app.post("/tool-calls/{tool_call_id}/web-sources", response_model=WebSourceResponse)
async def add_web_source(
    tool_call_id: int,
    request: WebSourceCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Add a web source to a tool call"""
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

# Mashup operations
@app.post("/conversations/{conversation_id}/mashups", response_model=MashupResponse)
async def create_mashup(
    conversation_id: str,
    request: MashupCreateRequest,
    db: AsyncConversationDB = Depends(get_db)
):
    """Create a mashup for a conversation"""
    try:
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

# Conversation summary
@app.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get a comprehensive summary of a conversation"""
    try:
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

# Phase management
@app.put("/conversations/{conversation_id}/phase")
async def update_conversation_phase(
    conversation_id: str,
    phase: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Update the phase of a conversation"""
    try:
        # Validate phase
        if phase not in [phase.value for phase in ConversationPhase]:
            raise HTTPException(status_code=400, detail="Invalid conversation phase")
        
        success = await db.update_conversation_phase(
            conversation_id,
            ConversationPhase(phase)
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update conversation phase")
        
        return {"message": "Conversation phase updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation phase: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Web search endpoints
@app.get("/api/v1/web-search/status")
async def get_web_search_status(
    web_search: AsyncWebSearchService = Depends(get_web_search_service)
):
    """Get web search service status"""
    try:
        status = web_search.get_service_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting web search status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/web-search/search")
async def search_educational_content(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    web_search: AsyncWebSearchService = Depends(get_web_search_service)
):
    """Search for educational content"""
    try:
        if context is None:
            context = {}
        
        result = await web_search.search_educational_content(query, context)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Conversational API endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
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

@app.get("/api/v1/session/{session_id}")
async def get_conversation_session(
    session_id: str,
    db: AsyncConversationDB = Depends(get_db)
):
    """Get conversation session information."""
    try:
        conversation = await db.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get recent messages
        messages = await db.get_messages(session_id, limit=10)
        
        # Get tool statistics
        tool_stats = await db.get_conversation_tool_calls(session_id, limit=5)
        
        return {
            "session_id": session_id,
            "conversation": conversation,
            "recent_messages": messages,
            "tool_calls": tool_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/tools/statistics", response_model=ToolStatisticsResponse)
async def get_tool_statistics(
    session_id: Optional[str] = None,
    tool_orchestrator: AsyncToolOrchestrator = Depends(get_tool_orchestrator_dep)
):
    """Get tool usage statistics."""
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

@app.get("/api/v1/tools/status")
async def get_tools_status(
    tool_orchestrator: AsyncToolOrchestrator = Depends(get_tool_orchestrator_dep)
):
    """Get status of all available tools."""
    try:
        web_search_available = await tool_orchestrator.is_web_search_available()
        
        return {
            "web_search": {
                "available": web_search_available,
                "service": "Tavily API"
            },
            "tool_orchestrator": {
                "available": True,
                "max_concurrent_tools": tool_orchestrator.max_concurrent_tools,
                "tool_timeout": tool_orchestrator.tool_timeout
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting tools status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Database utility endpoints
@app.post("/admin/database/backup")
async def create_database_backup(
    backup_name: Optional[str] = None,
    settings: Any = Depends(get_settings_dep)
):
    """Create a database backup"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        backup_path = await utils.create_backup(backup_name)
        return {
            "message": "Database backup created successfully",
            "backup_path": backup_path
        }
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create database backup")

@app.get("/admin/database/backups")
async def list_database_backups(settings: Any = Depends(get_settings_dep)):
    """List available database backups"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        backups = await utils.list_backups()
        return {"backups": backups}
    except Exception as e:
        logger.error(f"Failed to list database backups: {e}")
        raise HTTPException(status_code=500, detail="Failed to list database backups")

@app.post("/admin/database/restore")
async def restore_database_backup(
    backup_path: str,
    settings: Any = Depends(get_settings_dep)
):
    """Restore database from backup"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        success = await utils.restore_backup(backup_path)
        if success:
            return {"message": "Database restored successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to restore database")
    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore database")

@app.get("/admin/database/info")
async def get_database_info(settings: Any = Depends(get_settings_dep)):
    """Get database information and statistics"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        info = await utils.get_database_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database info")

@app.get("/admin/database/integrity")
async def validate_database_integrity(settings: Any = Depends(get_settings_dep)):
    """Validate database integrity"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        integrity = await utils.validate_database_integrity()
        return integrity
    except Exception as e:
        logger.error(f"Failed to validate database integrity: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate database integrity")

@app.post("/admin/database/optimize")
async def optimize_database(settings: Any = Depends(get_settings_dep)):
    """Optimize database performance"""
    try:
        utils = DatabaseUtils(settings.DATABASE_PATH)
        success = await utils.optimize_database()
        if success:
            return {"message": "Database optimization completed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to optimize database")
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize database")

@app.get("/admin/database/metrics")
async def get_database_metrics(settings: Any = Depends(get_settings_dep)):
    """Get database performance metrics"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        metrics = await monitor.collect_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to collect database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect database metrics")

@app.get("/admin/database/metrics/history")
async def get_database_metrics_history(
    limit: Optional[int] = None,
    settings: Any = Depends(get_settings_dep)
):
    """Get database metrics history"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        history = monitor.get_metrics_history(limit)
        return {"metrics_history": history}
    except Exception as e:
        logger.error(f"Failed to get database metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database metrics history")

@app.get("/admin/database/metrics/summary")
async def get_database_performance_summary(settings: Any = Depends(get_settings_dep)):
    """Get database performance summary"""
    try:
        monitor = DatabasePerformanceMonitor(settings.DATABASE_PATH)
        summary = monitor.get_performance_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get database performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database performance summary")

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Validation error handler"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
