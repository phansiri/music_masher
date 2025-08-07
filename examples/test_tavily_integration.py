#!/usr/bin/env python3
"""
🔍 Tavily API Key Test - Lit Music Mashup AI Platform

This script tests the Tavily API integration with the conversational AI agent
to verify that web search functionality is working correctly with your API key.

SETUP INSTRUCTIONS:
1. Copy env.example to .env: cp env.example .env
2. Add your Tavily API key to .env file:
   TAVILY_API_KEY=your_actual_tavily_api_key_here
3. Run this script: python examples/test_tavily_integration.py
4. Check the output to verify everything is working

This example demonstrates:
- Configuration validation and API key detection
- Direct web search service testing
- Conversational AI agent with web search integration
- Educational content filtering and quality assessment
- Real-time tool integration during conversations
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_settings, validate_and_warn, is_web_search_available
from app.services.web_search import AsyncWebSearchService
from app.agents.conversation_agent import AsyncConversationalMashupAgent
from app.services.tool_orchestrator import AsyncToolOrchestrator
from app.db.conversation_db import AsyncConversationDB


async def test_configuration():
    """Test 1: Configuration and API Key Validation"""
    print("🔧 Test 1: Configuration and API Key Validation")
    print("=" * 60)
    
    # Validate configuration
    is_valid = validate_and_warn()
    
    # Check web search availability
    web_search_available = is_web_search_available()
    settings = get_settings()
    
    print(f"\n📊 Configuration Status:")
    print(f"   ✅ Configuration Valid: {is_valid}")
    print(f"   🔍 Web Search Available: {web_search_available}")
    print(f"   🔑 Tavily API Key: {'✅ Configured' if settings.TAVILY_API_KEY else '❌ Missing'}")
    print(f"   🤖 Ollama Model: {settings.OLLAMA_MODEL}")
    print(f"   💾 Database Path: {settings.DATABASE_PATH}")
    
    if not web_search_available:
        print("\n⚠️  WARNING: Tavily API key not found!")
        print("   Please add your API key to .env file:")
        print("   TAVILY_API_KEY=your_actual_tavily_api_key_here")
        print("   Get your key from: https://tavily.com/")
        return False
    
    print("\n✅ Configuration test passed!")
    return True


async def test_web_search_service():
    """Test 2: Direct Web Search Service Testing"""
    print("\n🌐 Test 2: Direct Web Search Service Testing")
    print("=" * 60)
    
    # Initialize web search service
    web_search = AsyncWebSearchService()
    
    # Check service status
    status = web_search.get_service_status()
    print(f"📊 Service Status:")
    print(f"   Service Available: {status['service_available']}")
    print(f"   Tavily Available: {status['tavily_available']}")
    print(f"   API Key Configured: {status['api_key_configured']}")
    print(f"   Max Results: {status['max_results']}")
    print(f"   Timeout: {status['timeout_seconds']}s")
    
    if not status['service_available']:
        print("❌ Web search service not available")
        return False
    
    # Test educational content search
    print(f"\n🔍 Testing Educational Content Search...")
    
    search_context = {
        "skill_level": "intermediate",
        "genres": ["jazz", "classical"],
        "cultural_elements": ["improvisation", "harmonic_complexity"],
        "educational_goals": ["music_theory", "cultural_understanding"]
    }
    
    try:
        result = await web_search.search_educational_content(
            query="jazz classical music fusion educational resources",
            context=search_context
        )
        
        print(f"✅ Search completed successfully!")
        print(f"   Query: {result['query']}")
        print(f"   Enhanced Query: {result['enhanced_query']}")
        print(f"   Results Found: {len(result['results'])}")
        print(f"   Service Available: {result['service_available']}")
        print(f"   Total Results: {result['total_results']}")
        
        # Display search results
        if result['results']:
            print(f"\n📋 Search Results:")
            for i, res in enumerate(result['results'][:2], 1):  # Show first 2 results
                print(f"\n   Result {i}:")
                print(f"   📰 Title: {res['title'][:80]}...")
                print(f"   🔗 URL: {res['url']}")
                print(f"   📊 Quality Score: {res.get('quality_score', 'N/A')}")
                print(f"   🎯 Context Alignment: {res.get('context_alignment', 'N/A')}")
                if res.get('content'):
                    print(f"   📝 Content: {res['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False


async def test_tool_orchestrator():
    """Test 3: Tool Orchestrator Integration"""
    print("\n🛠️  Test 3: Tool Orchestrator Integration")
    print("=" * 60)
    
    # Initialize components
    settings = get_settings()
    db = AsyncConversationDB(settings.DATABASE_PATH)
    await db.init_db()
    
    web_search = AsyncWebSearchService()
    tool_orchestrator = AsyncToolOrchestrator(web_search_service=web_search, db=db)
    
    # Test concurrent searches
    print("🔄 Testing Concurrent Web Searches...")
    
    try:
        context = {
            "skill_level": "beginner",
            "educational_goals": ["music_theory_basics"],
            "session_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
        # Execute multiple searches concurrently
        search_queries = [
            "music theory basics for beginners",
            "jazz music history educational resources",
            "classical music elements for students"
        ]
        
        results = await tool_orchestrator.execute_concurrent_searches(
            queries=search_queries,
            context=context,
            conversation_id=context["session_id"]
        )
        
        print(f"✅ Concurrent searches completed!")
        print(f"   Queries Executed: {len(search_queries)}")
        print(f"   Results Received: {len(results)}")
        
        # Display results summary
        successful_searches = sum(1 for r in results if r.status == "completed")
        print(f"   Successful Searches: {successful_searches}/{len(results)}")
        
        for i, result in enumerate(results):
            if hasattr(result, 'status'):
                status = "✅ Success" if result.status == "completed" else f"❌ Failed: {result.error_message or 'Unknown error'}"
            else:
                status = "❓ Unknown status"
            print(f"   Query {i+1}: {status}")
        
        # Test tool statistics
        stats = await tool_orchestrator.get_tool_statistics(context["session_id"])
        print(f"\n📊 Tool Statistics:")
        print(f"   Total Tool Calls: {stats.get('total_tool_calls', 0)}")
        print(f"   Successful Calls: {stats.get('successful_calls', 0)}")
        print(f"   Failed Calls: {stats.get('failed_calls', 0)}")
        print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
        
        await db.close()
        return True
        
    except Exception as e:
        print(f"❌ Tool orchestrator test failed: {e}")
        await db.close()
        return False


async def test_conversational_agent_with_tools():
    """Test 4: Conversational AI Agent with Tavily Integration"""
    print("\n🤖 Test 4: Conversational AI Agent with Tavily Integration")
    print("=" * 60)
    
    try:
        # Initialize conversational agent with tools enabled
        settings = get_settings()
        agent = AsyncConversationalMashupAgent(
            model_name=settings.OLLAMA_MODEL,
            tavily_api_key=settings.TAVILY_API_KEY,
            db_path=settings.DATABASE_PATH,
            enable_tools=True
        )
        
        session_id = f"tavily-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"🎭 Starting conversation with session: {session_id}")
        print(f"🔍 Web search tools: {'✅ Enabled' if agent.enable_tools else '❌ Disabled'}")
        
        # Test conversation that triggers web search
        test_message = (
            "I want to create an educational mashup combining jazz and hip-hop "
            "for my intermediate music students. Can you help me understand "
            "the cultural connections between these genres?"
        )
        
        print(f"\n💬 User Message:")
        print(f"   {test_message}")
        
        print(f"\n🔄 Processing with AI agent (this may take 10-30 seconds)...")
        
        # Process message with agent
        response = await agent.process_message(
            session_id=session_id,
            user_message=test_message
        )
        
        print(f"\n✅ Agent Response Received!")
        print(f"   Session ID: {response.get('session_id', session_id)}")
        phase = response.get('phase', 'unknown')
        print(f"   Phase: {phase.value if hasattr(phase, 'value') else phase}")
        print(f"   Phase Transition: {response.get('phase_transition', False)}")
        print(f"   Response Keys: {list(response.keys())}")
        
        # Display tool results if any
        if response.get('tool_results'):
            print(f"\n🛠️  Tool Execution Results:")
            for tool_name, tool_result in response['tool_results'].items():
                if isinstance(tool_result, dict) and 'results' in tool_result:
                    result_count = len(tool_result['results'])
                    print(f"   {tool_name}: {result_count} results found")
                else:
                    print(f"   {tool_name}: executed")
        else:
            print(f"\n🛠️  Tool Execution Results: None")
        
        # Display AI response (truncated)
        ai_response = response.get('response', 'No response received')
        print(f"\n🤖 AI Agent Response:")
        print(f"   {ai_response[:300]}{'...' if len(ai_response) > 300 else ''}")
        
        # Display extracted context
        context = response.get('context', {})
        if context:
            print(f"\n🧠 Extracted Context:")
            for key, value in context.items():
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {len(value) if isinstance(value, list) else len(str(value))} items")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"\n🧠 Extracted Context: None")
        
        # Check if we have an error in the response
        if 'error' in response:
            print(f"\n❌ Agent Error: {response['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Conversational agent test failed: {e}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False


async def run_comprehensive_test():
    """Run all Tavily integration tests"""
    print("🧪 Lit Music Mashup AI - Tavily Integration Test Suite")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Test 1: Configuration
    config_success = await test_configuration()
    test_results.append(("Configuration", config_success))
    
    if not config_success:
        print("\n❌ Configuration test failed. Please check your .env file.")
        return
    
    # Test 2: Web Search Service
    web_search_success = await test_web_search_service()
    test_results.append(("Web Search Service", web_search_success))
    
    # Test 3: Tool Orchestrator
    orchestrator_success = await test_tool_orchestrator()
    test_results.append(("Tool Orchestrator", orchestrator_success))
    
    # Test 4: Conversational Agent (only if previous tests passed)
    if web_search_success and orchestrator_success:
        agent_success = await test_conversational_agent_with_tools()
        test_results.append(("Conversational Agent", agent_success))
    else:
        print("\n⚠️  Skipping conversational agent test due to previous failures.")
        test_results.append(("Conversational Agent", False))
    
    # Display final results
    print("\n" + "=" * 70)
    print("🏁 Final Test Results")
    print("=" * 70)
    
    all_passed = True
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not success:
            all_passed = False
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Congratulations! Your Tavily integration is working perfectly!")
        print("   You can now use web search functionality in the Lit Music Mashup AI platform.")
    else:
        print("\n🔧 Some tests failed. Please check:")
        print("   1. Your .env file contains a valid TAVILY_API_KEY")
        print("   2. Your internet connection is working")
        print("   3. The Tavily API service is accessible")
        print("   4. Check the error messages above for specific issues")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def print_setup_instructions():
    """Print setup instructions for users"""
    print("🚀 Tavily API Key Test Setup Instructions")
    print("=" * 50)
    print()
    print("1. 📋 Copy the example environment file:")
    print("   cp env.example .env")
    print()
    print("2. 🔑 Get your Tavily API key:")
    print("   • Visit: https://tavily.com/")
    print("   • Sign up for a free account")
    print("   • Copy your API key")
    print()
    print("3. ✏️  Edit your .env file:")
    print("   • Open .env in your text editor")
    print("   • Find: TAVILY_API_KEY=your_tavily_api_key_here")
    print("   • Replace with: TAVILY_API_KEY=your_actual_key")
    print()
    print("4. 🧪 Run this test:")
    print("   python examples/test_tavily_integration.py")
    print()
    print("5. 🎉 Verify all tests pass!")
    print()


if __name__ == "__main__":
    # Check if running from correct directory
    if not Path("app/config.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Example: python examples/test_tavily_integration.py")
        sys.exit(1)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print_setup_instructions()
        print("❌ No .env file found. Please follow the setup instructions above.")
        sys.exit(1)
    
    # Run the comprehensive test
    try:
        asyncio.run(run_comprehensive_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
