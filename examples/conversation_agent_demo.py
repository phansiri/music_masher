#!/usr/bin/env python3
"""
Demo script for the AsyncConversationalMashupAgent.

This script demonstrates how to use the conversation agent
for educational music mashup generation.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.agents import AsyncConversationalMashupAgent, ConversationPhase


async def demo_conversation_agent():
    """Demonstrate the conversation agent functionality."""
    
    print("🎵 Lit Music Mashup - Conversation Agent Demo")
    print("=" * 50)
    
    # Initialize the agent
    agent = AsyncConversationalMashupAgent(
        model_name="llama3.1:8b-instruct",
        model_type="ollama",
        db_path="./data/demo_conversations.db"
    )
    
    try:
        # Demo conversation flow
        session_id = "demo-session-001"
        
        # Initial phase
        print("\n📝 Phase 1: Initial Context Gathering")
        print("-" * 40)
        
        response1 = await agent.process_message(
            session_id=session_id,
            user_message="I want to create an educational mashup for my high school music class"
        )
        print(f"User: I want to create an educational mashup for my high school music class")
        print(f"Agent: {response1['response']}")
        print(f"Phase: {response1['phase']}")
        
        # Genre exploration phase
        print("\n🎼 Phase 2: Genre Exploration")
        print("-" * 40)
        
        response2 = await agent.process_message(
            session_id=session_id,
            user_message="I'm interested in jazz and classical music, and I want to explore their cultural backgrounds"
        )
        print(f"User: I'm interested in jazz and classical music, and I want to explore their cultural backgrounds")
        print(f"Agent: {response2['response']}")
        print(f"Phase: {response2['phase']}")
        
        # Educational clarification phase
        print("\n📚 Phase 3: Educational Clarification")
        print("-" * 40)
        
        response3 = await agent.process_message(
            session_id=session_id,
            user_message="My students are beginners and I want to teach them about rhythm, melody, and harmony"
        )
        print(f"User: My students are beginners and I want to teach them about rhythm, melody, and harmony")
        print(f"Agent: {response3['response']}")
        print(f"Phase: {response3['phase']}")
        
        # Cultural research phase
        print("\n🌍 Phase 4: Cultural Research")
        print("-" * 40)
        
        response4 = await agent.process_message(
            session_id=session_id,
            user_message="I want to explore the cultural traditions and history behind jazz and classical music"
        )
        print(f"User: I want to explore the cultural traditions and history behind jazz and classical music")
        print(f"Agent: {response4['response']}")
        print(f"Phase: {response4['phase']}")
        
        # Ready for generation phase
        print("\n✅ Phase 5: Ready for Generation")
        print("-" * 40)
        
        response5 = await agent.process_message(
            session_id=session_id,
            user_message="Yes, I'm ready to proceed with creating the educational mashup"
        )
        print(f"User: Yes, I'm ready to proceed with creating the educational mashup")
        print(f"Agent: {response5['response']}")
        print(f"Phase: {response5['phase']}")
        
        print("\n🎉 Demo completed successfully!")
        print("The conversation agent successfully guided through all phases:")
        print("1. Initial context gathering")
        print("2. Genre exploration")
        print("3. Educational clarification")
        print("4. Cultural research")
        print("5. Ready for generation")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
    
    finally:
        # Clean up
        await agent.close()


async def demo_context_extraction():
    """Demonstrate context extraction functionality."""
    
    print("\n🔍 Context Extraction Demo")
    print("=" * 30)
    
    agent = AsyncConversationalMashupAgent(
        model_name="llama3.1:8b-instruct",
        model_type="ollama"
    )
    
    try:
        # Test different types of context extraction
        test_messages = [
            ("I want to teach my college students about jazz and blues", ConversationPhase.INITIAL),
            ("I'm interested in rock, pop, and electronic music", ConversationPhase.GENRE_EXPLORATION),
            ("My students are intermediate level and need to learn about chord progressions", ConversationPhase.EDUCATIONAL_CLARIFICATION),
            ("I want to explore the cultural heritage of African American music traditions", ConversationPhase.CULTURAL_RESEARCH),
            ("Yes, let's proceed with the generation", ConversationPhase.READY_FOR_GENERATION)
        ]
        
        for message, phase in test_messages:
            print(f"\n📝 Testing {phase.value} phase:")
            print(f"Message: {message}")
            
            context = await agent._extract_context(message, phase)
            print(f"Extracted context: {context['extracted_info']}")
    
    except Exception as e:
        print(f"❌ Error during context extraction demo: {e}")
    
    finally:
        await agent.close()


if __name__ == "__main__":
    print("Starting Lit Music Mashup Conversation Agent Demo...")
    
    # Run the demos
    asyncio.run(demo_conversation_agent())
    asyncio.run(demo_context_extraction())
    
    print("\n✨ Demo completed!") 