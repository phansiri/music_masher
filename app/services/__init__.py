"""
Services module for Lit Music Mashup AI platform.

This module contains all service implementations including web search,
content generation, and other external service integrations.
"""

from .web_search import AsyncWebSearchService, get_web_search_service

__all__ = [
    "AsyncWebSearchService",
    "get_web_search_service"
]
