"""
Async database layer for the Lit Music Mashup AI platform.

This module provides the AsyncConversationDB class for managing
conversations, messages, tool calls, and generated content with
proper async/await patterns and error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiosqlite

from app.config import get_settings
from app.db.enums import ConversationPhase, MessageRole, ToolCallType

# Configure logging
logger = logging.getLogger(__name__)


class AsyncConversationDB:
    """
    Async database manager for conversation data.
    
    This class provides comprehensive async database operations
    for managing conversations, messages, tool calls, and generated content.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses config default.
        """
        settings = get_settings()
        self.db_path = db_path or settings.DATABASE_PATH
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None:
            # Ensure database directory exists
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
            logger.info(f"Connected to database: {self.db_path}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    async def init_db(self) -> None:
        """
        Initialize database schema.
        
        Creates all required tables if they don't exist:
        - conversations: Session management
        - messages: Conversation history
        - tool_calls: Web search and tool operation history
        - mashups: Generated content
        - web_sources: Citation tracking
        """
        async with self._lock:
            await self.connect()
            
            # Create conversations table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    phase TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (phase) REFERENCES conversation_phases(phase)
                )
            """)
            
            # Create messages table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (role) REFERENCES message_roles(role)
                )
            """)
            
            # Create tool_calls table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    tool_call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    tool_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (tool_type) REFERENCES tool_call_types(tool_type)
                )
            """)
            
            # Create mashups table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS mashups (
                    mashup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    audio_file_path TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            # Create web_sources table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS web_sources (
                    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_call_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    snippet TEXT,
                    relevance_score REAL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (tool_call_id) REFERENCES tool_calls(tool_call_id)
                )
            """)
            
            # Create indexes for better performance
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                ON messages(conversation_id)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages(timestamp)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_calls_conversation_id 
                ON tool_calls(conversation_id)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_calls_type 
                ON tool_calls(tool_type)
            """)
            
            await self._connection.commit()
            logger.info("Database schema initialized successfully")
    
    async def create_conversation(
        self, 
        conversation_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            metadata: Optional metadata dictionary
            
        Returns:
            bool: True if conversation was created successfully
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                metadata_json = self._dict_to_json(metadata) if metadata else None
                
                await self._connection.execute("""
                    INSERT INTO conversations (conversation_id, phase, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (conversation_id, ConversationPhase.INITIAL.value, now, now, metadata_json))
                
                await self._connection.commit()
                logger.info(f"Created conversation: {conversation_id}")
                return True
                
            except aiosqlite.IntegrityError as e:
                logger.warning(f"Conversation {conversation_id} already exists: {e}")
                return False
            except Exception as e:
                logger.error(f"Error creating conversation {conversation_id}: {e}")
                return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation details.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Optional[Dict]: Conversation data or None if not found
        """
        async with self._lock:
            try:
                cursor = await self._connection.execute("""
                    SELECT * FROM conversations WHERE conversation_id = ?
                """, (conversation_id,))
                
                row = await cursor.fetchone()
                if row:
                    return {
                        'conversation_id': row['conversation_id'],
                        'phase': row['phase'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'metadata': self._json_to_dict(row['metadata'])
                    }
                return None
                
            except Exception as e:
                logger.error(f"Error getting conversation {conversation_id}: {e}")
                return None
    
    async def update_conversation_phase(
        self, 
        conversation_id: str, 
        phase: ConversationPhase
    ) -> bool:
        """
        Update conversation phase.
        
        Args:
            conversation_id: Unique identifier for the conversation
            phase: New conversation phase
            
        Returns:
            bool: True if update was successful
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                await self._connection.execute("""
                    UPDATE conversations 
                    SET phase = ?, updated_at = ?
                    WHERE conversation_id = ?
                """, (phase.value, now, conversation_id))
                
                await self._connection.commit()
                logger.info(f"Updated conversation {conversation_id} to phase: {phase.value}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating conversation phase {conversation_id}: {e}")
                return False
    
    async def add_message(
        self, 
        conversation_id: str, 
        role: MessageRole, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to the conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Optional metadata dictionary
            
        Returns:
            bool: True if message was added successfully
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                metadata_json = self._dict_to_json(metadata) if metadata else None
                
                await self._connection.execute("""
                    INSERT INTO messages (conversation_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (conversation_id, role.value, content, now, metadata_json))
                
                await self._connection.commit()
                logger.debug(f"Added message to conversation {conversation_id}: {role.value}")
                return True
                
            except Exception as e:
                logger.error(f"Error adding message to conversation {conversation_id}: {e}")
                return False
    
    async def get_messages(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List[Dict]: List of message dictionaries
        """
        async with self._lock:
            try:
                query = """
                    SELECT * FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """
                params = [conversation_id]
                
                if limit:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                
                cursor = await self._connection.execute(query, params)
                rows = await cursor.fetchall()
                
                return [
                    {
                        'message_id': row['message_id'],
                        'conversation_id': row['conversation_id'],
                        'role': row['role'],
                        'content': row['content'],
                        'timestamp': row['timestamp'],
                        'metadata': self._json_to_dict(row['metadata'])
                    }
                    for row in rows
                ]
                
            except Exception as e:
                logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
                return []
    
    async def add_tool_call(
        self,
        conversation_id: str,
        tool_type: ToolCallType,
        input_data: str,
        output_data: Optional[str] = None,
        status: str = "pending",
        error_message: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a tool call record.
        
        Args:
            conversation_id: Unique identifier for the conversation
            tool_type: Type of tool call
            input_data: Input data for the tool call
            output_data: Output data from the tool call
            status: Status of the tool call
            error_message: Error message if failed
            
        Returns:
            Optional[int]: Tool call ID if successful, None otherwise
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                completed_at = now if status in ["completed", "failed"] else None
                
                cursor = await self._connection.execute("""
                    INSERT INTO tool_calls 
                    (conversation_id, tool_type, input_data, output_data, status, 
                     created_at, completed_at, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (conversation_id, tool_type.value, input_data, output_data, 
                      status, now, completed_at, error_message))
                
                await self._connection.commit()
                tool_call_id = cursor.lastrowid
                logger.debug(f"Added tool call {tool_call_id} to conversation {conversation_id}")
                return tool_call_id
                
            except Exception as e:
                logger.error(f"Error adding tool call to conversation {conversation_id}: {e}")
                return None
    
    async def update_tool_call(
        self,
        tool_call_id: int,
        output_data: Optional[str] = None,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update a tool call record.
        
        Args:
            tool_call_id: ID of the tool call to update
            output_data: Output data from the tool call
            status: New status of the tool call
            error_message: Error message if failed
            
        Returns:
            bool: True if update was successful
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                completed_at = now if status in ["completed", "failed"] else None
                
                await self._connection.execute("""
                    UPDATE tool_calls 
                    SET output_data = ?, status = ?, completed_at = ?, error_message = ?
                    WHERE tool_call_id = ?
                """, (output_data, status, completed_at, error_message, tool_call_id))
                
                await self._connection.commit()
                logger.debug(f"Updated tool call {tool_call_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating tool call {tool_call_id}: {e}")
                return False
    
    async def add_web_source(
        self,
        tool_call_id: int,
        url: str,
        title: Optional[str] = None,
        snippet: Optional[str] = None,
        relevance_score: Optional[float] = None
    ) -> bool:
        """
        Add a web source for citation tracking.
        
        Args:
            tool_call_id: ID of the associated tool call
            url: URL of the web source
            title: Title of the web page
            snippet: Text snippet from the page
            relevance_score: Relevance score (0.0 to 1.0)
            
        Returns:
            bool: True if web source was added successfully
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                
                await self._connection.execute("""
                    INSERT INTO web_sources 
                    (tool_call_id, url, title, snippet, relevance_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tool_call_id, url, title, snippet, relevance_score, now))
                
                await self._connection.commit()
                logger.debug(f"Added web source for tool call {tool_call_id}: {url}")
                return True
                
            except Exception as e:
                logger.error(f"Error adding web source for tool call {tool_call_id}: {e}")
                return False
    
    async def create_mashup(
        self,
        conversation_id: str,
        title: str,
        description: Optional[str] = None,
        audio_file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Create a new mashup record.
        
        Args:
            conversation_id: Unique identifier for the conversation
            title: Title of the mashup
            description: Description of the mashup
            audio_file_path: Path to the audio file
            metadata: Optional metadata dictionary
            
        Returns:
            Optional[int]: Mashup ID if successful, None otherwise
        """
        async with self._lock:
            try:
                now = datetime.now(timezone.utc)
                metadata_json = self._dict_to_json(metadata) if metadata else None
                
                cursor = await self._connection.execute("""
                    INSERT INTO mashups 
                    (conversation_id, title, description, audio_file_path, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (conversation_id, title, description, audio_file_path, metadata_json, now))
                
                await self._connection.commit()
                mashup_id = cursor.lastrowid
                logger.info(f"Created mashup {mashup_id} for conversation {conversation_id}")
                return mashup_id
                
            except Exception as e:
                logger.error(f"Error creating mashup for conversation {conversation_id}: {e}")
                return None
    
    async def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive summary of a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Optional[Dict]: Conversation summary or None if not found
        """
        async with self._lock:
            try:
                # Get conversation details directly (avoid nested lock)
                cursor = await self._connection.execute("""
                    SELECT * FROM conversations WHERE conversation_id = ?
                """, (conversation_id,))
                
                row = await cursor.fetchone()
                if not row:
                    return None
                
                conversation = {
                    'conversation_id': row['conversation_id'],
                    'phase': row['phase'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'metadata': self._json_to_dict(row['metadata'])
                }
                
                # Get message count
                cursor = await self._connection.execute("""
                    SELECT COUNT(*) as message_count FROM messages 
                    WHERE conversation_id = ?
                """, (conversation_id,))
                message_count = (await cursor.fetchone())['message_count']
                
                # Get tool call count
                cursor = await self._connection.execute("""
                    SELECT COUNT(*) as tool_call_count FROM tool_calls 
                    WHERE conversation_id = ?
                """, (conversation_id,))
                tool_call_count = (await cursor.fetchone())['tool_call_count']
                
                # Get mashup count
                cursor = await self._connection.execute("""
                    SELECT COUNT(*) as mashup_count FROM mashups 
                    WHERE conversation_id = ?
                """, (conversation_id,))
                mashup_count = (await cursor.fetchone())['mashup_count']
                
                return {
                    **conversation,
                    'message_count': message_count,
                    'tool_call_count': tool_call_count,
                    'mashup_count': mashup_count
                }
                
            except Exception as e:
                logger.error(f"Error getting conversation summary {conversation_id}: {e}")
                return None
    
    def _dict_to_json(self, data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Convert dictionary to JSON string."""
        if data is None:
            return None
        import json
        return json.dumps(data)
    
    def _json_to_dict(self, json_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """Convert JSON string to dictionary."""
        if json_str is None:
            return None
        import json
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON: {json_str}")
            return None 