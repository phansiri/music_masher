from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
from datetime import datetime

# Import database components
from app.db import AsyncConversationDB, ConversationPhase, MessageRole
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lit Music Mashup Conversational API",
    description="Educational AI Music Generation with Conversational Interface",
    version="2.0.0-conversational-mvp",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Dependency injection
async def get_db():
    """Database dependency"""
    settings = get_settings()
    db = AsyncConversationDB(settings.DATABASE_PATH)
    try:
        await db.init_db()
        yield db
    finally:
        await db.close()

async def get_settings_dep():
    """Settings dependency"""
    return get_settings()

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
        timestamp=datetime.utcnow(),
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

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Lit Music Mashup Conversational API")
    settings = get_settings()
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database path: {settings.DATABASE_PATH}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Lit Music Mashup Conversational API")
