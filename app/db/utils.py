"""
Database utilities for the Lit Music Mashup AI platform.

This module provides database utility functions including backup, restore,
migration, and performance monitoring capabilities.
"""

import asyncio
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import aiosqlite

from app.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseUtils:
    """Database utility functions for backup, restore, and maintenance."""
    
    def __init__(self, db_path: str):
        """Initialize database utilities."""
        self.db_path = Path(db_path)
        self.backup_dir = self.db_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a database backup.
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            str: Path to the backup file
        """
        if not backup_name:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup using SQLite's backup API
            async with aiosqlite.connect(self.db_path) as source:
                async with aiosqlite.connect(backup_path) as backup:
                    await source.backup(backup)
            
            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise
    
    async def restore_backup(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if restore was successful
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create a temporary backup of current database
            temp_backup = await self.create_backup("temp_before_restore.db")
            
            # Restore from backup
            async with aiosqlite.connect(backup_file) as source:
                async with aiosqlite.connect(self.db_path) as target:
                    await source.backup(target)
            
            # Remove temporary backup
            Path(temp_backup).unlink(missing_ok=True)
            
            logger.info(f"Database restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database from backup: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available database backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.db"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                })
            except Exception as e:
                logger.warning(f"Failed to get backup info for {backup_file}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    
    async def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            int: Number of backups removed
        """
        backups = await self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        removed_count = 0
        for backup in backups[keep_count:]:
            try:
                Path(backup["path"]).unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup['name']}")
            except Exception as e:
                logger.error(f"Failed to remove backup {backup['name']}: {e}")
        
        return removed_count
    
    async def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics.
        
        Returns:
            Dictionary with database information
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get database size
                db_path = Path(self.db_path)
                size_bytes = db_path.stat().st_size if db_path.exists() else 0
                
                # Get table information
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] async for row in cursor]
                
                # Get row counts for each table
                table_counts = {}
                for table in tables:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    table_counts[table] = count[0] if count else 0
                
                # Get database schema version (if exists)
                schema_version = None
                try:
                    cursor = await db.execute("SELECT version FROM schema_version LIMIT 1")
                    result = await cursor.fetchone()
                    schema_version = result[0] if result else None
                except:
                    pass
                
                return {
                    "path": str(self.db_path),
                    "size_bytes": size_bytes,
                    "tables": tables,
                    "table_counts": table_counts,
                    "schema_version": schema_version,
                    "backup_count": len(await self.list_backups())
                }
                
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}
    
    async def validate_database_integrity(self) -> Dict[str, Any]:
        """
        Validate database integrity.
        
        Returns:
            Dictionary with validation results
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Run integrity check
                cursor = await db.execute("PRAGMA integrity_check")
                integrity_result = await cursor.fetchone()
                
                # Check foreign key constraints
                cursor = await db.execute("PRAGMA foreign_key_check")
                foreign_key_errors = await cursor.fetchall()
                
                # Get database statistics
                cursor = await db.execute("PRAGMA stats")
                stats = await cursor.fetchall()
                
                return {
                    "integrity_ok": integrity_result[0] == "ok" if integrity_result else False,
                    "integrity_message": integrity_result[0] if integrity_result else "Unknown",
                    "foreign_key_errors": len(foreign_key_errors),
                    "foreign_key_details": foreign_key_errors,
                    "statistics": stats
                }
                
        except Exception as e:
            logger.error(f"Failed to validate database integrity: {e}")
            return {"error": str(e)}
    
    async def optimize_database(self) -> bool:
        """
        Optimize database performance.
        
        Returns:
            bool: True if optimization was successful
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Run VACUUM to optimize database
                await db.execute("VACUUM")
                
                # Update statistics
                await db.execute("ANALYZE")
                
                # Optimize indexes
                await db.execute("REINDEX")
                
                await db.commit()
                logger.info("Database optimization completed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            return False
    
    async def export_data(self, table_name: str, output_path: str) -> bool:
        """
        Export table data to JSON file.
        
        Args:
            table_name: Name of the table to export
            output_path: Path to the output JSON file
            
        Returns:
            bool: True if export was successful
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(f"SELECT * FROM {table_name}")
                rows = await cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = row[i]
                    data.append(row_dict)
                
                # Write to JSON file
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                logger.info(f"Exported {len(data)} rows from {table_name} to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to export data from {table_name}: {e}")
            return False
    
    async def import_data(self, table_name: str, input_path: str) -> bool:
        """
        Import data from JSON file to table.
        
        Args:
            table_name: Name of the table to import into
            input_path: Path to the input JSON file
            
        Returns:
            bool: True if import was successful
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            if not data:
                logger.warning(f"No data found in {input_path}")
                return False
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get column names from first row
                columns = list(data[0].keys())
                placeholders = ', '.join(['?' for _ in columns])
                column_names = ', '.join(columns)
                
                # Insert data
                for row in data:
                    values = [row.get(col) for col in columns]
                    await db.execute(
                        f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
                        values
                    )
                
                await db.commit()
                logger.info(f"Imported {len(data)} rows into {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to import data into {table_name}: {e}")
            return False


class DatabasePerformanceMonitor:
    """Database performance monitoring and metrics collection."""
    
    def __init__(self, db_path: str):
        """Initialize performance monitor."""
        self.db_path = db_path
        self.metrics: List[Dict[str, Any]] = []
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect database performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get database size
                db_path = Path(self.db_path)
                size_bytes = db_path.stat().st_size if db_path.exists() else 0
                
                # Get table sizes
                cursor = await db.execute("""
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = await cursor.fetchall()
                
                table_metrics = {}
                for table_name, _ in tables:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = await cursor.fetchone()
                    table_metrics[table_name] = count[0] if count else 0
                
                # Get index information
                cursor = await db.execute("""
                    SELECT name, tbl_name FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                indexes = await cursor.fetchall()
                
                # Get database statistics
                cursor = await db.execute("PRAGMA stats")
                stats = await cursor.fetchall()
                
                metrics = {
                    "timestamp": datetime.now(timezone.utc),
                    "size_bytes": size_bytes,
                    "table_count": len(tables),
                    "index_count": len(indexes),
                    "table_metrics": table_metrics,
                    "statistics": stats
                }
                
                # Store metrics
                self.metrics.append(metrics)
                
                # Keep only last 100 metrics
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
            return {}
    
    def get_metrics_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get metrics history.
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of metrics dictionaries
        """
        if limit:
            return self.metrics[-limit:]
        return self.metrics.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary from collected metrics.
        
        Returns:
            Dictionary with performance summary
        """
        if not self.metrics:
            return {}
        
        # Calculate size growth
        size_growth = 0
        if len(self.metrics) >= 2:
            size_growth = self.metrics[-1]["size_bytes"] - self.metrics[0]["size_bytes"]
        
        # Calculate average table counts
        total_table_counts = {}
        for metric in self.metrics:
            for table, count in metric.get("table_metrics", {}).items():
                if table not in total_table_counts:
                    total_table_counts[table] = []
                total_table_counts[table].append(count)
        
        avg_table_counts = {
            table: sum(counts) / len(counts) 
            for table, counts in total_table_counts.items()
        }
        
        return {
            "metrics_count": len(self.metrics),
            "time_span": {
                "start": self.metrics[0]["timestamp"],
                "end": self.metrics[-1]["timestamp"]
            },
            "size_growth_bytes": size_growth,
            "current_size_bytes": self.metrics[-1]["size_bytes"],
            "average_table_counts": avg_table_counts,
            "current_table_counts": self.metrics[-1].get("table_metrics", {})
        }


# Utility functions
async def create_database_backup(db_path: str, backup_name: Optional[str] = None) -> str:
    """Create a database backup."""
    utils = DatabaseUtils(db_path)
    return await utils.create_backup(backup_name)


async def restore_database_backup(db_path: str, backup_path: str) -> bool:
    """Restore database from backup."""
    utils = DatabaseUtils(db_path)
    return await utils.restore_backup(backup_path)


async def get_database_info(db_path: str) -> Dict[str, Any]:
    """Get database information and statistics."""
    utils = DatabaseUtils(db_path)
    return await utils.get_database_info()


async def validate_database_integrity(db_path: str) -> Dict[str, Any]:
    """Validate database integrity."""
    utils = DatabaseUtils(db_path)
    return await utils.validate_database_integrity()


async def optimize_database(db_path: str) -> bool:
    """Optimize database performance."""
    utils = DatabaseUtils(db_path)
    return await utils.optimize_database() 