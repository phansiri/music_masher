# Examples

This directory contains example scripts demonstrating the functionality of the Lit Music Mashup platform.

## 🧪 Tavily API Integration Test

### `test_tavily_integration.py`

**🎯 Purpose**: Test your Tavily API key integration and verify that web search functionality is working correctly with the conversational AI agent.

**🚀 Quick Start:**
```bash
# 1. Copy environment file
cp env.example .env

# 2. Add your Tavily API key to .env
# Edit .env and add: TAVILY_API_KEY=your_actual_tavily_api_key_here

# 3. Run the test
python examples/test_tavily_integration.py
```

**🔍 What this test does:**
1. **Configuration Validation**: Checks your .env setup and API key
2. **Web Search Service**: Tests direct Tavily API integration
3. **Tool Orchestrator**: Tests concurrent search execution
4. **Conversational Agent**: Tests full AI agent with web search integration

**✅ Expected Results:**
```
🧪 Lit Music Mashup AI - Tavily Integration Test Suite
======================================================================

🔧 Test 1: Configuration and API Key Validation
✅ Configuration test passed!

🌐 Test 2: Direct Web Search Service Testing
✅ Search completed successfully!

🛠️  Test 3: Tool Orchestrator Integration  
✅ Concurrent searches completed!

🤖 Test 4: Conversational AI Agent with Tavily Integration
✅ Agent Response Received!

🏁 Final Test Results
🎯 Overall Result: ✅ ALL TESTS PASSED
```

**🔧 Setup Requirements:**
- Valid Tavily API key (get free key at https://tavily.com/)
- .env file with TAVILY_API_KEY configured
- Internet connection for web search functionality

**🎉 Benefits:**
- Verify your API key is working
- Test all web search functionality  
- Validate the full conversational AI pipeline
- Get educational search results in real-time

## 🤖 Conversation Agent Demo

### `conversation_agent_demo.py`

This demo script shows how to use the `AsyncConversationalMashupAgent` for educational music mashup generation.

**Features demonstrated:**
- Phase-based conversation management
- Context extraction for each phase
- Integration with database layer
- Error handling and fallback responses

**To run the demo:**

```bash
# From the project root
uv run python examples/conversation_agent_demo.py
```

**Requirements:**
- Ollama running locally with `llama3.1:8b-instruct` model
- Or OpenAI API key for OpenAI model type

**What the demo shows:**
1. **Initial Phase**: Context gathering for educational goals
2. **Genre Exploration**: Music genre analysis and preferences
3. **Educational Clarification**: Skill level and learning objectives
4. **Cultural Research**: Cultural context and significance
5. **Ready for Generation**: Confirmation and summary

**Expected output:**
```
🎵 Lit Music Mashup - Conversation Agent Demo
==================================================

📝 Phase 1: Initial Context Gathering
----------------------------------------
User: I want to create an educational mashup for my high school music class
Agent: [AI response based on initial phase prompt]
Phase: initial

🎼 Phase 2: Genre Exploration
----------------------------------------
User: I'm interested in jazz and classical music...
Agent: [AI response based on genre exploration prompt]
Phase: genre_exploration

[... continues through all phases ...]
```

## Running the Demo

1. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```

2. **Pull the required model:**
   ```bash
   ollama pull llama3.1:8b-instruct
   ```

3. **Run the demo:**
   ```bash
   uv run python examples/conversation_agent_demo.py
   ```

## Customization

You can modify the demo script to:
- Use different models (OpenAI, other Ollama models)
- Test different conversation flows
- Explore context extraction with different messages
- Test error handling scenarios

## Next Steps

After running the demo, you can:
1. Explore the database to see stored conversations
2. Modify the agent parameters for different use cases
3. Integrate with the web search service (T006)
4. Add tool integration (T008) 