"""
Database validation utilities for the Lit Music Mashup AI platform.

This module provides comprehensive validation for database operations
including input sanitization, JSON field validation, and foreign key
constraint validation.
"""

import json
import logging
import re
import html
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from functools import wraps

from app.db.enums import ConversationPhase, MessageRole, ToolCallType

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class DatabaseValidator:
    """Database validation utilities."""
    
    # Validation patterns
    CONVERSATION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
    URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # HTML escape to prevent XSS
        sanitized = html.escape(sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        if len(sanitized) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")
        
        if not sanitized:
            raise ValidationError("String cannot be empty")
        
        return sanitized
    
    @staticmethod
    def validate_conversation_id(conversation_id: str) -> str:
        """
        Validate conversation ID.
        
        Args:
            conversation_id: Conversation ID to validate
            
        Returns:
            Validated conversation ID
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(conversation_id, str):
            raise ValidationError("Conversation ID must be a string")
        
        conversation_id = conversation_id.strip()
        
        if not DatabaseValidator.CONVERSATION_ID_PATTERN.match(conversation_id):
            raise ValidationError(
                "Conversation ID must be 3-50 characters long and contain only "
                "letters, numbers, hyphens, and underscores"
            )
        
        return conversation_id
    
    @staticmethod
    def validate_phase(phase: str) -> ConversationPhase:
        """
        Validate conversation phase.
        
        Args:
            phase: Phase string to validate
            
        Returns:
            Validated ConversationPhase enum
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(phase, str):
            raise ValidationError("Phase must be a string")
        
        try:
            return ConversationPhase(phase)
        except ValueError:
            valid_phases = [p.value for p in ConversationPhase]
            raise ValidationError(f"Invalid phase. Must be one of: {valid_phases}")
    
    @staticmethod
    def validate_message_role(role: str) -> MessageRole:
        """
        Validate message role.
        
        Args:
            role: Role string to validate
            
        Returns:
            Validated MessageRole enum
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(role, str):
            raise ValidationError("Role must be a string")
        
        try:
            return MessageRole(role)
        except ValueError:
            valid_roles = [r.value for r in MessageRole]
            raise ValidationError(f"Invalid role. Must be one of: {valid_roles}")
    
    @staticmethod
    def validate_tool_type(tool_type: str) -> ToolCallType:
        """
        Validate tool call type.
        
        Args:
            tool_type: Tool type string to validate
            
        Returns:
            Validated ToolCallType enum
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(tool_type, str):
            raise ValidationError("Tool type must be a string")
        
        try:
            return ToolCallType(tool_type)
        except ValueError:
            valid_types = [t.value for t in ToolCallType]
            raise ValidationError(f"Invalid tool type. Must be one of: {valid_types}")
    
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(url, str):
            raise ValidationError("URL must be a string")
        
        url = url.strip()
        
        if not DatabaseValidator.URL_PATTERN.match(url):
            raise ValidationError("Invalid URL format")
        
        return url
    
    @staticmethod
    def validate_relevance_score(score: Optional[float]) -> Optional[float]:
        """
        Validate relevance score.
        
        Args:
            score: Score to validate
            
        Returns:
            Validated score
            
        Raises:
            ValidationError: If validation fails
        """
        if score is None:
            return None
        
        if not isinstance(score, (int, float)):
            raise ValidationError("Relevance score must be a number")
        
        if score < 0.0 or score > 1.0:
            raise ValidationError("Relevance score must be between 0.0 and 1.0")
        
        return float(score)
    
    @staticmethod
    def validate_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Validate and serialize metadata.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            JSON string of validated metadata
            
        Raises:
            ValidationError: If validation fails
        """
        if metadata is None:
            return None
        
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
        
        # Validate metadata keys and values
        validated_metadata = {}
        for key, value in metadata.items():
            if not isinstance(key, str):
                raise ValidationError("Metadata keys must be strings")
            
            # Sanitize key
            key = DatabaseValidator.sanitize_string(key, max_length=50)
            
            # Validate value types
            if isinstance(value, (str, int, float, bool, type(None))):
                if isinstance(value, str):
                    value = DatabaseValidator.sanitize_string(value, max_length=500)
                validated_metadata[key] = value
            elif isinstance(value, list):
                # Validate list items
                validated_list = []
                for item in value:
                    if isinstance(item, (str, int, float, bool)):
                        if isinstance(item, str):
                            item = DatabaseValidator.sanitize_string(item, max_length=200)
                        validated_list.append(item)
                    else:
                        raise ValidationError(f"Unsupported metadata value type: {type(item)}")
                validated_metadata[key] = validated_list
            else:
                raise ValidationError(f"Unsupported metadata value type: {type(value)}")
        
        # Limit metadata size
        if len(validated_metadata) > 20:
            raise ValidationError("Too many metadata keys (max 20)")
        
        try:
            return json.dumps(validated_metadata)
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Failed to serialize metadata: {e}")
    
    @staticmethod
    def validate_json_field(json_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Validate JSON field.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        if json_str is None:
            return None
        
        if not isinstance(json_str, str):
            raise ValidationError("JSON field must be a string")
        
        try:
            parsed = json.loads(json_str)
            if not isinstance(parsed, dict):
                raise ValidationError("JSON field must contain a dictionary")
            return parsed
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
    
    @staticmethod
    def validate_timestamp(timestamp: Union[str, datetime]) -> datetime:
        """
        Validate timestamp.
        
        Args:
            timestamp: Timestamp to validate
            
        Returns:
            Validated datetime object
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Try parsing ISO format
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Invalid timestamp format")
        
        raise ValidationError("Timestamp must be a string or datetime object")


def validate_database_input(func: Callable) -> Callable:
    """
    Decorator to validate database input parameters.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Validate conversation_id if present
            if 'conversation_id' in kwargs:
                kwargs['conversation_id'] = DatabaseValidator.validate_conversation_id(
                    kwargs['conversation_id']
                )
            
            # Validate phase if present
            if 'phase' in kwargs and isinstance(kwargs['phase'], str):
                kwargs['phase'] = DatabaseValidator.validate_phase(kwargs['phase'])
            
            # Validate role if present
            if 'role' in kwargs and isinstance(kwargs['role'], str):
                kwargs['role'] = DatabaseValidator.validate_message_role(kwargs['role'])
            
            # Validate tool_type if present
            if 'tool_type' in kwargs and isinstance(kwargs['tool_type'], str):
                kwargs['tool_type'] = DatabaseValidator.validate_tool_type(kwargs['tool_type'])
            
            # Validate content if present
            if 'content' in kwargs:
                kwargs['content'] = DatabaseValidator.sanitize_string(kwargs['content'])
            
            # Validate input_data if present
            if 'input_data' in kwargs:
                kwargs['input_data'] = DatabaseValidator.sanitize_string(kwargs['input_data'])
            
            # Validate output_data if present
            if 'output_data' in kwargs and kwargs['output_data'] is not None:
                kwargs['output_data'] = DatabaseValidator.sanitize_string(kwargs['output_data'])
            
            # Validate url if present
            if 'url' in kwargs:
                kwargs['url'] = DatabaseValidator.validate_url(kwargs['url'])
            
            # Validate title if present
            if 'title' in kwargs and kwargs['title'] is not None:
                kwargs['title'] = DatabaseValidator.sanitize_string(kwargs['title'], max_length=200)
            
            # Validate snippet if present
            if 'snippet' in kwargs and kwargs['snippet'] is not None:
                kwargs['snippet'] = DatabaseValidator.sanitize_string(kwargs['snippet'], max_length=1000)
            
            # Validate relevance_score if present
            if 'relevance_score' in kwargs:
                kwargs['relevance_score'] = DatabaseValidator.validate_relevance_score(
                    kwargs['relevance_score']
                )
            
            # Validate metadata if present
            if 'metadata' in kwargs:
                kwargs['metadata'] = DatabaseValidator.validate_metadata(kwargs['metadata'])
            
            # Validate description if present
            if 'description' in kwargs and kwargs['description'] is not None:
                kwargs['description'] = DatabaseValidator.sanitize_string(kwargs['description'], max_length=500)
            
            # Validate audio_file_path if present
            if 'audio_file_path' in kwargs and kwargs['audio_file_path'] is not None:
                kwargs['audio_file_path'] = DatabaseValidator.sanitize_string(kwargs['audio_file_path'], max_length=200)
            
            return await func(*args, **kwargs)
            
        except ValidationError as e:
            logger.error(f"Validation error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper


def validate_foreign_key_constraints(func: Callable) -> Callable:
    """
    Decorator to validate foreign key constraints.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Get the database instance (first argument after self)
            db = args[1] if len(args) > 1 else None
            
            if db is None:
                return await func(*args, **kwargs)
            
            # Validate conversation_id foreign key if present
            if 'conversation_id' in kwargs:
                conversation = await db.get_conversation(kwargs['conversation_id'])
                if not conversation:
                    raise ValidationError(f"Conversation {kwargs['conversation_id']} does not exist")
            
            # Validate tool_call_id foreign key if present
            if 'tool_call_id' in kwargs:
                tool_call = await db.get_tool_call(kwargs['tool_call_id'])
                if not tool_call:
                    raise ValidationError(f"Tool call {kwargs['tool_call_id']} does not exist")
            
            return await func(*args, **kwargs)
            
        except ValidationError as e:
            logger.error(f"Foreign key validation error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper


def validate_json_fields(func: Callable) -> Callable:
    """
    Decorator to validate JSON fields in database operations.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Validate metadata JSON if present
            if 'metadata' in kwargs and kwargs['metadata'] is not None:
                if isinstance(kwargs['metadata'], str):
                    kwargs['metadata'] = DatabaseValidator.validate_json_field(kwargs['metadata'])
            
            # Validate output_data JSON if present
            if 'output_data' in kwargs and kwargs['output_data'] is not None:
                if isinstance(kwargs['output_data'], str):
                    try:
                        # Try to parse as JSON for tool calls
                        parsed = json.loads(kwargs['output_data'])
                        if not isinstance(parsed, (dict, list)):
                            raise ValidationError("Output data must be valid JSON object or array")
                    except json.JSONDecodeError as e:
                        raise ValidationError(f"Invalid JSON in output_data: {e}")
            
            return await func(*args, **kwargs)
            
        except ValidationError as e:
            logger.error(f"JSON validation error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper


# Combined validation decorator
def validate_database_operation(func: Callable) -> Callable:
    """
    Combined decorator for database operation validation.
    
    This decorator applies input validation, foreign key validation,
    and JSON field validation.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    return validate_json_fields(validate_foreign_key_constraints(validate_database_input(func)))


# Validation utility functions
def sanitize_and_validate_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and validate input data dictionary.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Sanitized and validated data dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    validated_data = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            validated_data[key] = DatabaseValidator.sanitize_string(value)
        elif isinstance(value, dict):
            validated_data[key] = DatabaseValidator.validate_metadata(value)
        elif isinstance(value, (int, float, bool, type(None))):
            validated_data[key] = value
        else:
            raise ValidationError(f"Unsupported data type for key '{key}': {type(value)}")
    
    return validated_data


def validate_conversation_data(conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> tuple:
    """
    Validate conversation creation data.
    
    Args:
        conversation_id: Conversation ID
        metadata: Optional metadata
        
    Returns:
        Tuple of validated data
        
    Raises:
        ValidationError: If validation fails
    """
    validated_id = DatabaseValidator.validate_conversation_id(conversation_id)
    validated_metadata = DatabaseValidator.validate_metadata(metadata)
    
    return validated_id, validated_metadata


def validate_message_data(
    conversation_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Validate message creation data.
    
    Args:
        conversation_id: Conversation ID
        role: Message role
        content: Message content
        metadata: Optional metadata
        
    Returns:
        Tuple of validated data
        
    Raises:
        ValidationError: If validation fails
    """
    validated_id = DatabaseValidator.validate_conversation_id(conversation_id)
    validated_role = DatabaseValidator.validate_message_role(role)
    validated_content = DatabaseValidator.sanitize_string(content)
    validated_metadata = DatabaseValidator.validate_metadata(metadata)
    
    return validated_id, validated_role, validated_content, validated_metadata


def validate_tool_call_data(
    conversation_id: str,
    tool_type: str,
    input_data: str,
    output_data: Optional[str] = None,
    status: str = "pending",
    error_message: Optional[str] = None
) -> tuple:
    """
    Validate tool call creation data.
    
    Args:
        conversation_id: Conversation ID
        tool_type: Tool type
        input_data: Input data
        output_data: Optional output data
        status: Status
        error_message: Optional error message
        
    Returns:
        Tuple of validated data
        
    Raises:
        ValidationError: If validation fails
    """
    validated_id = DatabaseValidator.validate_conversation_id(conversation_id)
    validated_tool_type = DatabaseValidator.validate_tool_type(tool_type)
    validated_input = DatabaseValidator.sanitize_string(input_data)
    validated_output = DatabaseValidator.sanitize_string(output_data) if output_data else None
    validated_status = DatabaseValidator.sanitize_string(status, max_length=20)
    validated_error = DatabaseValidator.sanitize_string(error_message, max_length=500) if error_message else None
    
    return validated_id, validated_tool_type, validated_input, validated_output, validated_status, validated_error 