#!/usr/bin/env python3
"""
Test script for the AsyncEnhancedGenerationService.

This script tests the content generation service with Ollama integration.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.generation_service import (
    AsyncEnhancedGenerationService,
    GenerationRequest,
    ContentType,
    SkillLevel
)

async def test_ollama_connection():
    """Test basic Ollama connection."""
    print("🔍 Testing Ollama connection...")
    
    service = AsyncEnhancedGenerationService()
    
    try:
        # Test health check
        health = await service.health_check()
        print(f"✅ Health check: {health}")
        
        # Test model listing
        models = await service.get_available_models()
        print(f"✅ Available models: {models}")
        
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

async def test_content_generation():
    """Test content generation with a simple request."""
    print("\n🎵 Testing content generation...")
    
    service = AsyncEnhancedGenerationService()
    
    try:
        # Create a test request
        request = GenerationRequest(
            prompt="Create a beginner lesson about jazz music",
            content_type=ContentType.THEORY_LESSON,
            skill_level=SkillLevel.BEGINNER,
            context={
                "genre": "jazz",
                "learning_objectives": "Understand basic jazz concepts",
                "target_audience": "music students"
            }
        )
        
        # Generate content
        print("⏳ Generating content...")
        response = await service.generate_with_context(request)
        
        print(f"✅ Content generated successfully!")
        print(f"📝 Content Type: {response.content_type.value}")
        print(f"🎯 Skill Level: {response.skill_level.value}")
        print(f"⭐ Quality Score: {response.quality_score:.2f}/10")
        print(f"🏷️ Quality Level: {response.quality_level.value}")
        print(f"⏱️ Generation Time: {response.generation_time:.2f}s")
        print(f"🤖 Model Used: {response.model_used}")
        print(f"💡 Suggestions: {len(response.suggestions)} suggestions")
        
        print(f"\n📄 Generated Content:")
        print("-" * 50)
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        return False

async def test_different_content_types():
    """Test different content types."""
    print("\n🎭 Testing different content types...")
    
    service = AsyncEnhancedGenerationService()
    
    content_types = [
        (ContentType.CULTURAL_CONTEXT, "Explain the cultural background of blues music"),
        (ContentType.PRACTICAL_EXERCISE, "Create a simple rhythm exercise for beginners"),
        (ContentType.TEACHING_NOTES, "Provide teaching notes for a music theory lesson")
    ]
    
    for content_type, prompt in content_types:
        try:
            print(f"\n🔄 Testing {content_type.value}...")
            
            request = GenerationRequest(
                prompt=prompt,
                content_type=content_type,
                skill_level=SkillLevel.INTERMEDIATE,
                context={"genre": "blues"}
            )
            
            response = await service.generate_with_context(request)
            
            print(f"✅ {content_type.value}: Quality {response.quality_score:.2f}/10")
            print(f"📝 Content preview: {response.content[:100]}...")
            
        except Exception as e:
            print(f"❌ {content_type.value} failed: {e}")

async def main():
    """Main test function."""
    print("🚀 Starting Generation Service Tests")
    print("=" * 50)
    
    # Test 1: Ollama connection
    connection_ok = await test_ollama_connection()
    
    if not connection_ok:
        print("\n❌ Ollama connection failed. Please ensure Ollama is running.")
        return
    
    # Test 2: Basic content generation
    generation_ok = await test_content_generation()
    
    if not generation_ok:
        print("\n❌ Content generation failed.")
        return
    
    # Test 3: Different content types
    await test_different_content_types()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
