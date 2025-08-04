"""
Tests for database utilities and validation.

This module tests the database utility functions, validation,
and performance monitoring capabilities.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from app.db.utils import DatabaseUtils, DatabasePerformanceMonitor
from app.db.validation import DatabaseValidator, ValidationError, validate_database_operation


class TestDatabaseValidator:
    """Test database validation functionality."""
    
    def test_sanitize_string_valid(self):
        """Test string sanitization with valid input."""
        result = DatabaseValidator.sanitize_string("Hello World", max_length=20)
        assert result == "Hello World"
    
    def test_sanitize_string_with_html(self):
        """Test string sanitization with HTML content."""
        result = DatabaseValidator.sanitize_string("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result
    
    def test_sanitize_string_too_long(self):
        """Test string sanitization with too long input."""
        with pytest.raises(ValidationError):
            DatabaseValidator.sanitize_string("a" * 1001)
    
    def test_sanitize_string_empty(self):
        """Test string sanitization with empty input."""
        with pytest.raises(ValidationError):
            DatabaseValidator.sanitize_string("")
    
    def test_validate_conversation_id_valid(self):
        """Test conversation ID validation with valid input."""
        result = DatabaseValidator.validate_conversation_id("conv_123")
        assert result == "conv_123"
    
    def test_validate_conversation_id_invalid(self):
        """Test conversation ID validation with invalid input."""
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_conversation_id("conv@123")
    
    def test_validate_conversation_id_too_short(self):
        """Test conversation ID validation with too short input."""
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_conversation_id("ab")
    
    def test_validate_url_valid(self):
        """Test URL validation with valid input."""
        result = DatabaseValidator.validate_url("https://example.com")
        assert result == "https://example.com"
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid input."""
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_url("not-a-url")
    
    def test_validate_relevance_score_valid(self):
        """Test relevance score validation with valid input."""
        result = DatabaseValidator.validate_relevance_score(0.5)
        assert result == 0.5
    
    def test_validate_relevance_score_invalid_range(self):
        """Test relevance score validation with invalid range."""
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_relevance_score(1.5)
    
    def test_validate_metadata_valid(self):
        """Test metadata validation with valid input."""
        metadata = {"key": "value", "number": 42}
        result = DatabaseValidator.validate_metadata(metadata)
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result
    
    def test_validate_metadata_too_many_keys(self):
        """Test metadata validation with too many keys."""
        metadata = {f"key_{i}": f"value_{i}" for i in range(25)}
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_metadata(metadata)


class TestDatabaseUtils:
    """Test database utility functions."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        try:
            Path(temp_path).unlink(missing_ok=True)
        except:
            pass
    
    @pytest.fixture
    def db_utils(self, temp_db_path):
        """Create database utils instance."""
        return DatabaseUtils(temp_db_path)
    
    @pytest.mark.asyncio
    async def test_create_backup(self, db_utils, temp_db_path):
        """Test database backup creation."""
        # Create a simple database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("test",))
            await db.commit()
        
        # Create backup
        backup_path = await db_utils.create_backup()
        assert Path(backup_path).exists()
        
        # Verify backup contains data
        async with aiosqlite.connect(backup_path) as db:
            cursor = await db.execute("SELECT name FROM test")
            result = await cursor.fetchone()
            assert result[0] == "test"
    
    @pytest.mark.asyncio
    async def test_restore_backup(self, db_utils, temp_db_path):
        """Test database backup restoration."""
        # Create original database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("original",))
            await db.commit()
        
        # Create backup
        backup_path = await db_utils.create_backup()
        
        # Modify original database
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("DELETE FROM test")
            await db.commit()
        
        # Restore from backup
        success = await db_utils.restore_backup(backup_path)
        assert success
        
        # Verify restoration
        async with aiosqlite.connect(temp_db_path) as db:
            cursor = await db.execute("SELECT name FROM test")
            result = await cursor.fetchone()
            assert result[0] == "original"
    
    @pytest.mark.asyncio
    async def test_list_backups(self, db_utils):
        """Test listing database backups."""
        # Create some backups
        await db_utils.create_backup("backup1.db")
        await db_utils.create_backup("backup2.db")
        
        backups = await db_utils.list_backups()
        assert len(backups) >= 2
        
        # Check backup info
        for backup in backups:
            assert "name" in backup
            assert "path" in backup
            assert "size_bytes" in backup
            assert "created_at" in backup
    
    @pytest.mark.asyncio
    async def test_get_database_info(self, db_utils, temp_db_path):
        """Test getting database information."""
        # Create a simple database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("test",))
            await db.commit()
        
        info = await db_utils.get_database_info()
        assert "path" in info
        assert "size_bytes" in info
        assert "tables" in info
        assert "test" in info["tables"]
        assert info["table_counts"]["test"] == 1
    
    @pytest.mark.asyncio
    async def test_validate_database_integrity(self, db_utils, temp_db_path):
        """Test database integrity validation."""
        # Create a simple database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.commit()
        
        integrity = await db_utils.validate_database_integrity()
        assert "integrity_ok" in integrity
        assert integrity["integrity_ok"] is True
    
    @pytest.mark.asyncio
    async def test_optimize_database(self, db_utils, temp_db_path):
        """Test database optimization."""
        # Create a simple database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.commit()
        
        success = await db_utils.optimize_database()
        assert success is True


class TestDatabasePerformanceMonitor:
    """Test database performance monitoring."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        try:
            Path(temp_path).unlink(missing_ok=True)
        except:
            pass
    
    @pytest.fixture
    def monitor(self, temp_db_path):
        """Create performance monitor instance."""
        return DatabasePerformanceMonitor(temp_db_path)
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, monitor, temp_db_path):
        """Test metrics collection."""
        # Create a simple database
        import aiosqlite
        async with aiosqlite.connect(temp_db_path) as db:
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("test",))
            await db.commit()
        
        metrics = await monitor.collect_metrics()
        assert "timestamp" in metrics
        assert "size_bytes" in metrics
        assert "table_count" in metrics
        assert "index_count" in metrics
        assert "table_metrics" in metrics
        assert metrics["table_metrics"]["test"] == 1
    
    @pytest.mark.asyncio
    async def test_metrics_history(self, monitor):
        """Test metrics history tracking."""
        # Collect some metrics
        await monitor.collect_metrics()
        await monitor.collect_metrics()
        
        history = monitor.get_metrics_history()
        assert len(history) == 2
        
        # Test limit
        history_limited = monitor.get_metrics_history(limit=1)
        assert len(history_limited) == 1
    
    @pytest.mark.asyncio
    async def test_performance_summary(self, monitor):
        """Test performance summary generation."""
        # Collect some metrics
        await monitor.collect_metrics()
        await monitor.collect_metrics()
        
        summary = monitor.get_performance_summary()
        assert "metrics_count" in summary
        assert "time_span" in summary
        assert summary["metrics_count"] == 2


class TestValidationDecorators:
    """Test validation decorators."""
    
    @pytest.mark.asyncio
    async def test_validate_database_input_decorator(self):
        """Test database input validation decorator."""
        @validate_database_operation
        async def test_function(conversation_id: str, content: str):
            return {"conversation_id": conversation_id, "content": content}
        
        # Test valid input
        result = await test_function(conversation_id="valid_123", content="Hello World")
        assert result["conversation_id"] == "valid_123"
        assert result["content"] == "Hello World"
        
        # Test invalid conversation ID
        with pytest.raises(ValidationError):
            await test_function(conversation_id="invalid@123", content="Hello World")
    
    @pytest.mark.asyncio
    async def test_validate_metadata_decorator(self):
        """Test metadata validation decorator."""
        @validate_database_operation
        async def test_function(metadata: dict):
            return {"metadata": metadata}
        
        # Test valid metadata
        valid_metadata = {"key": "value", "number": 42}
        result = await test_function(metadata=valid_metadata)
        assert "metadata" in result
        
        # Test invalid metadata (too many keys)
        invalid_metadata = {f"key_{i}": f"value_{i}" for i in range(25)}
        with pytest.raises(ValidationError):
            await test_function(metadata=invalid_metadata)


class TestValidationUtilityFunctions:
    """Test validation utility functions."""
    
    def test_sanitize_and_validate_input(self):
        """Test input sanitization and validation."""
        from app.db.validation import sanitize_and_validate_input
        
        input_data = {
            "string": "Hello <script>alert('xss')</script>",
            "number": 42,
            "boolean": True,
            "metadata": {"key": "value"}
        }
        
        result = sanitize_and_validate_input(input_data)
        assert "string" in result
        assert "&lt;" in result["string"]  # HTML escaped
        assert result["number"] == 42
        assert result["boolean"] is True
    
    def test_validate_conversation_data(self):
        """Test conversation data validation."""
        from app.db.validation import validate_conversation_data
        
        conversation_id, metadata = validate_conversation_data(
            "valid_123", {"key": "value"}
        )
        assert conversation_id == "valid_123"
        assert metadata is not None
        
        with pytest.raises(ValidationError):
            validate_conversation_data("invalid@123", {"key": "value"})
    
    def test_validate_message_data(self):
        """Test message data validation."""
        from app.db.validation import validate_message_data
        
        conv_id, role, content, metadata = validate_message_data(
            "valid_123", "user", "Hello World", {"key": "value"}
        )
        assert conv_id == "valid_123"
        assert role.value == "user"
        assert content == "Hello World"
        
        with pytest.raises(ValidationError):
            validate_message_data("invalid@123", "user", "Hello World")
    
    def test_validate_tool_call_data(self):
        """Test tool call data validation."""
        from app.db.validation import validate_tool_call_data
        
        conv_id, tool_type, input_data, output_data, status, error = validate_tool_call_data(
            "valid_123", "web_search", "query", "result", "completed"
        )
        assert conv_id == "valid_123"
        assert tool_type.value == "web_search"
        assert input_data == "query"
        assert output_data == "result"
        assert status == "completed"
        
        with pytest.raises(ValidationError):
            validate_tool_call_data("invalid@123", "web_search", "query")


if __name__ == "__main__":
    pytest.main([__file__]) 