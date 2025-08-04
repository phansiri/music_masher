"""
Configuration management for Lit Music Mashup AI platform.

This module provides environment-based configuration with validation,
warning systems for missing optional configurations, and proper
secret handling for the conversational AI music generation platform.
"""

import os
import warnings
from pathlib import Path
from typing import Optional, List

from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with validation and warning systems.
    
    This class manages all configuration for the Lit Music Mashup AI platform,
    including environment variables, API keys, database settings, and AI model
    configuration with proper validation and warning systems.
    """
    
    # Pydantic configuration using ConfigDict
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Environment settings
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development, production, test)"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Database configuration
    DATABASE_PATH: str = Field(
        default="./data/conversations.db",
        description="Path to SQLite database file"
    )
    
    # Local AI configuration
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.1:8b-instruct",
        description="Ollama model to use for AI generation"
    )
    
    # Web search configuration (optional)
    TAVILY_API_KEY: Optional[str] = Field(
        default=None,
        description="Tavily API key for web search functionality"
    )
    
    # Conversation settings
    MAX_CONVERSATION_TURNS: int = Field(
        default=10,
        description="Maximum number of conversation turns"
    )
    CONVERSATION_TIMEOUT_MINUTES: int = Field(
        default=30,
        description="Conversation timeout in minutes"
    )
    WEB_SEARCH_MAX_RESULTS: int = Field(
        default=3,
        description="Maximum number of web search results"
    )
    WEB_SEARCH_TIMEOUT_SECONDS: int = Field(
        default=10,
        description="Web search timeout in seconds"
    )
    
    # Educational content validation
    MIN_CULTURAL_CONTEXT_LENGTH: int = Field(
        default=100,
        description="Minimum length for cultural context in characters"
    )
    MIN_THEORY_CONCEPTS: int = Field(
        default=2,
        description="Minimum number of music theory concepts required"
    )
    REQUIRED_TEACHING_NOTES: bool = Field(
        default=True,
        description="Whether teaching notes are required"
    )
    
    # Validation methods
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "production", "test"]
        if v not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level setting."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("MAX_CONVERSATION_TURNS")
    @classmethod
    def validate_max_conversation_turns(cls, v):
        """Validate maximum conversation turns."""
        if v < 3 or v > 20:
            raise ValueError("MAX_CONVERSATION_TURNS must be between 3 and 20")
        return v
    
    @field_validator("CONVERSATION_TIMEOUT_MINUTES")
    @classmethod
    def validate_conversation_timeout(cls, v):
        """Validate conversation timeout."""
        if v < 5 or v > 120:
            raise ValueError("CONVERSATION_TIMEOUT_MINUTES must be between 5 and 120")
        return v
    
    @field_validator("WEB_SEARCH_MAX_RESULTS")
    @classmethod
    def validate_web_search_max_results(cls, v):
        """Validate web search max results."""
        if v < 1 or v > 10:
            raise ValueError("WEB_SEARCH_MAX_RESULTS must be between 1 and 10")
        return v
    
    @field_validator("MIN_CULTURAL_CONTEXT_LENGTH")
    @classmethod
    def validate_min_cultural_context_length(cls, v):
        """Validate minimum cultural context length."""
        if v < 50 or v > 1000:
            raise ValueError("MIN_CULTURAL_CONTEXT_LENGTH must be between 50 and 1000")
        return v
    
    @field_validator("MIN_THEORY_CONCEPTS")
    @classmethod
    def validate_min_theory_concepts(cls, v):
        """Validate minimum theory concepts."""
        if v < 1 or v > 10:
            raise ValueError("MIN_THEORY_CONCEPTS must be between 1 and 10")
        return v


class ConfigurationValidator:
    """
    Configuration validator with warning system for missing optional configs.
    
    This class provides methods to validate configuration and generate
    appropriate warnings for missing optional configurations.
    """
    
    def __init__(self, settings: Settings):
        """Initialize validator with settings."""
        self.settings = settings
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def validate_configuration(self) -> bool:
        """
        Validate the complete configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        self.warnings.clear()
        self.errors.clear()
        
        # Validate required settings
        self._validate_required_settings()
        
        # Check optional settings and generate warnings
        self._check_optional_settings()
        
        # Validate file paths
        self._validate_file_paths()
        
        # Print warnings and errors
        self._print_validation_results()
        
        return len(self.errors) == 0
    
    def _validate_required_settings(self):
        """Validate required configuration settings."""
        # Check if database directory exists or can be created
        db_path = Path(self.settings.DATABASE_PATH)
        db_dir = db_path.parent
        
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.errors.append(f"Cannot create database directory {db_dir}: {e}")
    
    def _check_optional_settings(self):
        """Check optional settings and generate warnings."""
        # Check for Tavily API key
        if not self.settings.TAVILY_API_KEY:
            self.warnings.append(
                "TAVILY_API_KEY not configured - web search functionality will be disabled. "
                "Add your Tavily API key to .env file for full functionality."
            )
        
        # Check Ollama connection
        if self.settings.ENVIRONMENT == "production":
            if self.settings.OLLAMA_BASE_URL == "http://localhost:11434":
                self.warnings.append(
                    "Using localhost for Ollama in production environment. "
                    "Consider using a proper Ollama server URL."
                )
    
    def _validate_file_paths(self):
        """Validate file paths and permissions."""
        # Check database path
        db_path = Path(self.settings.DATABASE_PATH)
        db_dir = db_path.parent
        
        if db_dir.exists() and not os.access(db_dir, os.W_OK):
            self.errors.append(f"No write permission for database directory: {db_dir}")
    
    def _print_validation_results(self):
        """Print validation warnings and errors."""
        if self.warnings:
            print("\n⚠️  Configuration Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print("\n❌ Configuration Errors:")
            for error in self.errors:
                print(f"   • {error}")
        
        if not self.warnings and not self.errors:
            print("\n✅ Configuration validation passed!")
    
    def get_web_search_available(self) -> bool:
        """Check if web search is available."""
        return bool(self.settings.TAVILY_API_KEY)
    
    def get_configuration_summary(self) -> dict:
        """Get a summary of the current configuration."""
        return {
            "environment": self.settings.ENVIRONMENT,
            "log_level": self.settings.LOG_LEVEL,
            "database_path": self.settings.DATABASE_PATH,
            "ollama_url": self.settings.OLLAMA_BASE_URL,
            "ollama_model": self.settings.OLLAMA_MODEL,
            "web_search_available": self.get_web_search_available(),
            "max_conversation_turns": self.settings.MAX_CONVERSATION_TURNS,
            "conversation_timeout_minutes": self.settings.CONVERSATION_TIMEOUT_MINUTES,
            "web_search_max_results": self.settings.WEB_SEARCH_MAX_RESULTS,
            "web_search_timeout_seconds": self.settings.WEB_SEARCH_TIMEOUT_SECONDS,
            "min_cultural_context_length": self.settings.MIN_CULTURAL_CONTEXT_LENGTH,
            "min_theory_concepts": self.settings.MIN_THEORY_CONCEPTS,
            "required_teaching_notes": self.settings.REQUIRED_TEACHING_NOTES,
        }


# Global settings instance
settings = Settings()
validator = ConfigurationValidator(settings)


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def get_validator() -> ConfigurationValidator:
    """Get the global configuration validator."""
    return validator


def validate_and_warn():
    """
    Validate configuration and print warnings.
    
    This function should be called at application startup to ensure
    all configuration is valid and to warn about missing optional settings.
    """
    return validator.validate_configuration()


def is_web_search_available() -> bool:
    """Check if web search functionality is available."""
    return validator.get_web_search_available()


def get_configuration_summary() -> dict:
    """Get a summary of the current configuration."""
    return validator.get_configuration_summary()


# Configuration validation on module import
if __name__ == "__main__":
    print("🔧 Lit Music Mashup AI - Configuration Validation")
    print("=" * 50)
    
    validate_and_warn()
    
    print("\n📊 Configuration Summary:")
    summary = get_configuration_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
