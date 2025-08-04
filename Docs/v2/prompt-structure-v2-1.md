# Lit Music Mashup - Prompt Structure Documentation v2.0
## Educational AI Music Generation - Conversational MVP-First Approach

---

## 1. Overview

This document defines a conversational prompt engineering strategy for the Lit Music Mashup MVP, focusing on **educational functionality with conversational AI and web search capabilities**. The system uses LangChain/LangGraph for agent orchestration and Tavily for web search integration.

**MVP Philosophy**: Conversational prompts that gather context through dialogue, utilize web search for current information, and generate educational content with local model optimization.

---

## 2. Conversational Architecture for MVP

### 2.1 Enhanced Request/Response Models

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    """Conversational chat request model"""
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Conversational chat response model"""
    session_id: str
    agent_response: str
    tool_calls: List[Dict[str, Any]] = []
    ready_for_generation: bool = False
    gathered_context: Dict[str, Any] = {}

class MashupRequest(BaseModel):
    """Enhanced request model for final generation"""
    prompt: str
    skill_level: str = "beginner"
    gathered_context: Optional[Dict[str, Any]] = None
    
class EducationalContent(BaseModel):
    """Educational content structure"""
    theory_concepts: List[str]
    cultural_context: str
    teaching_notes: str

class MashupResponse(BaseModel):
    """Enhanced response model with web-enriched content"""
    title: str
    lyrics: str
    educational_content: EducationalContent
    metadata: Dict[str, Any]
    web_sources: List[str] = []
```

### 2.2 Conversational Agent Architecture

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

class ConversationalMashupAgent:
    """Conversational agent with web search capabilities"""
    
    def __init__(self, model_name: str = "llama3.1:8b-instruct", tavily_api_key: str = None):
        self.model_name = model_name
        self.tavily_api_key = tavily_api_key
        self.conversation_sessions = {}
        self.tools = self._setup_tools()
        
    def _setup_tools(self):
        """Setup available tools including web search"""
        tools = []
        
        if self.tavily_api_key:
            search_tool = TavilySearchResults(
                api_key=self.tavily_api_key,
                max_results=3,
                search_depth="basic"
            )
            tools.append(search_tool)
        
        return tools
    
    async def chat_with_user(self, request: ChatRequest) -> ChatResponse:
        """Handle conversational interaction with user"""
        
        session_id = request.session_id or self._generate_session_id()
        session = self._get_or_create_session(session_id)
        
        # Process user message and determine next action
        response = await self._process_conversation_turn(session, request.message)
        
        return ChatResponse(
            session_id=session_id,
            agent_response=response["agent_response"],
            tool_calls=response.get("tool_calls", []),
            ready_for_generation=response.get("ready_for_generation", False),
            gathered_context=session.gathered_context
        )
    
    async def generate_educational_mashup(self, request: MashupRequest) -> MashupResponse:
        """Generate final mashup using gathered context"""
        
        enhanced_prompt = self._build_context_enhanced_prompt(request)
        response = await self._call_local_model(enhanced_prompt)
        return self._parse_response(response, request.gathered_context)
```

---

## 3. Conversational Prompt Templates

### 3.1 Context Gathering Conversation Prompts

```python
CONVERSATION_SYSTEM_PROMPT = """
You are an expert music educator and conversational AI assistant specializing in creating educational music mashups. Your role is to engage users in thoughtful dialogue to gather sufficient information for creating high-quality educational content.

CONVERSATION OBJECTIVES:
1. Understand the educational context and goals
2. Identify desired musical genres and their characteristics
3. Assess appropriate skill level for content
4. Gather cultural context through web search when needed
5. Clarify specific learning outcomes

CONVERSATION GUIDELINES:
- Ask clear, focused questions to gather essential information
- Use web search to find current musical trends and cultural context
- Maintain educational focus throughout the conversation
- Be culturally sensitive and respectful
- Adapt language to the user's expertise level
- Build rapport while gathering comprehensive context

TOOLS AVAILABLE:
- Web Search: Use for current music trends, artist information, cultural context, educational resources

CONVERSATION FLOW:
1. Initial greeting and context gathering
2. Genre exploration and research
3. Educational objective clarification
4. Cultural context research
5. Final confirmation before generation

Never generate the final mashup during conversation - only gather context and confirm readiness.
"""

CONTEXT_GATHERING_PROMPTS = {
    "initial_greeting": """
    Hello! I'm excited to help you create an educational music mashup. To create the best possible content for your needs, I'd love to learn more about your situation.

    Could you tell me:
    1. What's the educational context? (classroom, workshop, individual study, etc.)
    2. What genres are you interested in combining?
    3. What's the skill level of your audience? (beginner, intermediate, advanced)
    4. What are your main learning objectives?
    """,
    
    "genre_exploration": """
    Great choice on {genres}! Let me research some current information about these genres to make sure our mashup includes the most relevant and up-to-date context.
    
    [This would trigger a web search for current trends in the specified genres]
    
    Based on my research, I found some interesting connections between these genres. Would you like to focus on:
    - Musical technique similarities and differences
    - Historical and cultural connections
    - Contemporary fusion examples
    - Specific artists or songs as reference points?
    """,
    
    "educational_clarification": """
    To make this truly educational, let's clarify your specific learning goals:
    
    For {skill_level} level students studying {genres}, which aspects are most important:
    1. Music theory concepts (rhythm, harmony, melody, structure)
    2. Cultural understanding and historical context
    3. Performance techniques and skills
    4. Creative composition and analysis
    5. Cross-cultural musical dialogue
    
    Are there any specific concepts you want to emphasize or avoid?
    """,
    
    "cultural_research": """
    I want to ensure we represent these musical traditions respectfully and accurately. Let me research the current cultural context and significance of {genres}.
    
    [This would trigger web searches for cultural context and recent developments]
    
    Based on my research, I found important cultural considerations for {genres}. Is it important to address:
    - Historical origins and cultural significance
    - Contemporary cultural impact and evolution
    - Cross-cultural connections and influences
    - Sensitivity around cultural appropriation
    """,
    
    "generation_confirmation": """
    Perfect! I now have a comprehensive understanding of your needs:
    
    📚 Educational Context: {educational_context}
    🎵 Genres: {genres}
    📊 Skill Level: {skill_level}
    🎯 Learning Objectives: {learning_objectives}
    🌍 Cultural Focus: {cultural_focus}
    
    I'm ready to create your educational mashup! This will include:
    - Engaging lyrics that blend your chosen genres
    - Detailed music theory concepts appropriate for {skill_level}
    - Rich cultural context and historical background
    - Practical teaching notes and classroom activities
    
    Would you like me to generate your educational mashup now?
    """
}
```

### 3.2 Web Search Integration Prompts

```python
WEB_SEARCH_DECISION_PROMPT = """
Based on the user's message: "{user_message}"

Determine if web search is needed for any of these scenarios:
1. Current music trends or recent developments
2. Specific artist or song information
3. Cultural context beyond general knowledge
4. Recent educational resources or methods
4. Contemporary genre fusion examples

If web search is needed, provide search queries. If not, continue conversation.

DECISION: {search_needed: boolean}
SEARCH_QUERIES: {queries: list of strings}
REASONING: {why search is or isn't needed}
"""

SEARCH_QUERY_TEMPLATES = {
    "genre_trends": "{genre} music trends 2024 characteristics",
    "cultural_context": "{genre} cultural significance history modern impact",
    "educational_resources": "{genre} music education teaching methods {skill_level}",
    "fusion_examples": "{genre1} {genre2} fusion examples contemporary artists",
    "artist_research": "{artist_name} musical style influence {genre}",
    "theory_concepts": "{genre} music theory concepts {skill_level} education"
}

def build_search_enhanced_prompt(base_prompt: str, search_results: List[Dict]) -> str:
    """Enhance conversation prompt with web search results"""
    
    if not search_results:
        return base_prompt
    
    search_context = "\n".join([
        f"Recent Information: {result['title']}\n{result['content'][:200]}..."
        for result in search_results[:3]
    ])
    
    enhanced_prompt = f"""
{base_prompt}

CURRENT WEB RESEARCH:
{search_context}

Use this current information to provide accurate, up-to-date context in your response.
"""
    
    return enhanced_prompt
```

---

## 4. Enhanced Educational Generation Prompts

### 4.1 Context-Enhanced Generation Prompt

```python
CONTEXT_ENHANCED_GENERATION_PROMPT = """
You are an expert music educator creating an educational music mashup based on detailed conversation context and current web research.

GATHERED CONTEXT:
Educational Setting: {educational_context}
Target Genres: {genres}
Skill Level: {skill_level}
Learning Objectives: {learning_objectives}
Cultural Focus Areas: {cultural_focus}
Current Research: {web_search_context}

GENERATION REQUIREMENTS:
1. Create an engaging, educational title that reflects the mashup concept
2. Write lyrics (6-12 lines) that authentically blend the genres
3. Include comprehensive educational content with current context
4. Ensure cultural sensitivity and respectful representation
5. Provide practical teaching applications

OUTPUT FORMAT (JSON):
{{
    "title": "Creative title reflecting both genres and educational focus",
    "lyrics": "Engaging lyrics that demonstrate genre fusion and educational concepts",
    "educational_content": {{
        "theory_concepts": ["3-5 specific music theory concepts with explanations"],
        "cultural_context": "Rich cultural background incorporating current research",
        "teaching_notes": "Detailed practical guidance for educators with activities"
    }},
    "metadata": {{
        "genres_analyzed": ["genre1", "genre2"],
        "complexity_level": "{skill_level}",
        "learning_focus": ["primary learning areas"],
        "cultural_elements": ["key cultural aspects covered"],
        "web_sources_used": ["sources that informed this content"],
        "estimated_teaching_time": "suggested duration for lesson"
    }}
}}

EDUCATIONAL QUALITY STANDARDS:
- All music theory information must be factually accurate
- Cultural context must be respectful and well-researched
- Content complexity must match specified skill level
- Teaching applications must be practical and actionable
- Genre representation must be authentic and balanced

CURRENT WEB RESEARCH INTEGRATION:
Use the provided web search results to ensure:
- Current accuracy of genre characteristics
- Up-to-date cultural context and significance
- Contemporary examples and references
- Modern educational approaches and resources

Generate the educational mashup now:
"""
```

### 4.2 Skill Level Adaptations with Current Context

```python
SKILL_LEVEL_ADAPTATIONS_ENHANCED = {
    "beginner": {
        "vocabulary": "simple music terms with clear definitions",
        "concepts": "basic rhythm, melody, instruments, cultural origins",
        "lyrics_complexity": "short sentences, repetitive patterns, clear rhyme schemes",
        "theory_depth": "fundamental concepts with everyday analogies",
        "cultural_depth": "introductory historical context with relatable examples",
        "web_search_focus": "basic genre characteristics, simple educational resources"
    },
    "intermediate": {
        "vocabulary": "standard music theory terms with context",
        "concepts": "chord progressions, song structure, genre evolution, improvisation",
        "lyrics_complexity": "moderate complexity, music terminology integration",
        "theory_depth": "intermediate theory with practical applications",
        "cultural_depth": "historical connections, social context, influence patterns",
        "web_search_focus": "genre analysis, contemporary fusion examples, teaching methods"
    },
    "advanced": {
        "vocabulary": "advanced musical terminology and analysis",
        "concepts": "complex harmony, cultural analysis, compositional techniques",
        "lyrics_complexity": "sophisticated language, theoretical integration, wordplay",
        "theory_depth": "detailed analysis with cultural intersections",
        "cultural_depth": "deep cultural analysis, contemporary relevance, critical thinking",
        "web_search_focus": "advanced theory, cultural studies, contemporary academic resources"
    }
}
```

---

## 5. Tool Integration and Orchestration

### 5.1 Web Search Tool Integration

```python
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
import os

class WebSearchTool:
    """Enhanced web search tool for educational content"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Tavily API key required for web search functionality")
        
        self.search_tool = TavilySearchResults(
            api_key=self.api_key,
            max_results=3,
            search_depth="basic",
            include_domains=["edu", "org"],  # Prefer educational sources
            exclude_domains=["tiktok.com", "instagram.com"]  # Avoid ephemeral content
        )
    
    async def search_for_educational_content(self, query: str, context: Dict[str, Any]) -> List[Dict]:
        """Search for educational content with context awareness"""
        
        # Enhance query with educational context
        enhanced_query = self._enhance_query_for_education(query, context)
        
        try:
            results = await self.search_tool.arun(enhanced_query)
            return self._filter_and_validate_results(results, context)
        except Exception as e:
            # Graceful degradation - return empty results
            return []
    
    def _enhance_query_for_education(self, query: str, context: Dict[str, Any]) -> str:
        """Enhance search query with educational context"""
        
        skill_level = context.get("skill_level", "")
        educational_context = context.get("educational_context", "")
        
        if skill_level:
            query += f" {skill_level} level"
        
        if educational_context in ["classroom", "school"]:
            query += " education teaching"
        
        return query
    
    def _filter_and_validate_results(self, results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Filter results for educational appropriateness"""
        
        filtered_results = []
        
        for result in results:
            # Basic quality filters
            if len(result.get("content", "")) < 100:
                continue
                
            # Prefer educational sources
            url = result.get("url", "").lower()
            if any(domain in url for domain in [".edu", ".org", "education"]):
                result["source_quality"] = "high"
            else:
                result["source_quality"] = "medium"
            
            filtered_results.append(result)
        
        return filtered_results[:3]  # Limit to top 3 results

# Tool orchestration for agent
def create_educational_tools(tavily_api_key: str = None) -> List[Tool]:
    """Create tools for educational agent"""
    
    tools = []
    
    if tavily_api_key:
        web_search = WebSearchTool(tavily_api_key)
        
        search_tool = Tool(
            name="web_search",
            description="Search the web for current information about music genres, artists, cultural context, and educational resources",
            func=web_search.search_for_educational_content
        )
        tools.append(search_tool)
    
    return tools
```

### 5.2 Conversation State Management

```python
class ConversationSession:
    """Manage conversation state and context"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        self.gathered_context = {
            "educational_context": None,
            "genres": [],
            "skill_level": None,
            "learning_objectives": [],
            "cultural_focus": [],
            "web_research": []
        }
        self.tool_calls = []
        self.current_phase = "initial"  # initial, genre_exploration, clarification, research, ready
    
    def add_message(self, role: str, content: str, tool_calls: List[Dict] = None):
        """Add message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls or []
        }
        self.messages.append(message)
    
    def update_context(self, key: str, value: Any):
        """Update gathered context"""
        if key in self.gathered_context:
            if isinstance(self.gathered_context[key], list):
                if isinstance(value, list):
                    self.gathered_context[key].extend(value)
                else:
                    self.gathered_context[key].append(value)
            else:
                self.gathered_context[key] = value
    
    def is_ready_for_generation(self) -> bool:
        """Check if enough context has been gathered"""
        context = self.gathered_context
        
        required_fields = [
            context.get("educational_context"),
            context.get("genres") and len(context["genres"]) >= 2,
            context.get("skill_level"),
            context.get("learning_objectives")
        ]
        
        return all(required_fields)
    
    def get_generation_context(self) -> Dict[str, Any]:
        """Get context formatted for generation"""
        return {
            "educational_context": self.gathered_context.get("educational_context", "general"),
            "genres": self.gathered_context.get("genres", []),
            "skill_level": self.gathered_context.get("skill_level", "beginner"),
            "learning_objectives": self.gathered_context.get("learning_objectives", []),
            "cultural_focus": self.gathered_context.get("cultural_focus", []),
            "web_search_context": self._format_web_research()
        }
    
    def _format_web_research(self) -> str:
        """Format web research for prompt inclusion"""
        research = self.gathered_context.get("web_research", [])
        if not research:
            return "No recent web research performed."
        
        formatted_research = []
        for result in research:
            formatted_research.append(f"- {result.get('title', 'Unknown')}: {result.get('content', '')[:200]}...")
        
        return "\n".join(formatted_research)
```

---

## 6. Quality Assurance for Conversational MVP

### 6.1 Enhanced Educational Content Validation

```python
class ConversationalContentValidator:
    """Validation for conversational educational content"""
    
    def __init__(self):
        self.web_source_validator = WebSourceValidator()
    
    def validate_conversation_context(self, session: ConversationSession) -> Dict[str, bool]:
        """Validate gathered conversation context"""
        
        context = session.gathered_context
        validations = {
            "has_educational_context": bool(context.get("educational_context")),
            "has_sufficient_genres": len(context.get("genres", [])) >= 2,
            "has_skill_level": bool(context.get("skill_level")),
            "has_learning_objectives": bool(context.get("learning_objectives")),
            "web_research_quality": self._validate_web_research(context.get("web_research", []))
        }
        
        return validations
    
    def validate_generated_content_with_sources(self, content: Dict, web_sources: List[Dict]) -> Dict[str, Any]:
        """Validate generated content against web sources"""
        
        validations = {
            "basic_structure": self._validate_basic_structure(content),
            "educational_quality": self._validate_educational_quality(content),
            "cultural_sensitivity": self._validate_cultural_sensitivity(content),
            "web_source_alignment": self._validate_source_alignment(content, web_sources),
            "source_credibility": self._validate_source_credibility(web_sources)
        }
        
        return validations
    
    def _validate_web_research(self, research: List[Dict]) -> bool:
        """Validate quality of web research"""
        if not research:
            return True  # No research is acceptable
        
        quality_scores = []
        for result in research:
            score = 0
            
            # Check content length (substantial content)
            if len(result.get("content", "")) > 100:
                score += 1
            
            # Check source quality indicators
            url = result.get("url", "").lower()
            if any(domain in url for domain in [".edu", ".org"]):
                score += 2
            elif any(domain in url for domain in [".com", ".net"]):
                score += 1
            
            # Check title relevance
            if result.get("title") and len(result["title"]) > 10:
                score += 1
            
            quality_scores.append(score)
        
        # At least one high-quality source (score >= 3)
        return any(score >= 3 for score in quality_scores)
    
    def _validate_source_alignment(self, content: Dict, sources: List[Dict]) -> bool:
        """Validate that content aligns with web sources"""
        if not sources:
            return True
        
        # Extract key terms from generated content
        content_text = f"{content.get('lyrics', '')} {content.get('educational_content', {}).get('cultural_context', '')}"
        content_terms = set(content_text.lower().split())
        
        # Check alignment with source content
        for source in sources:
            source_text = source.get("content", "").lower()
            source_terms = set(source_text.split())
            
            # Calculate overlap
            overlap = len(content_terms.intersection(source_terms))
            if overlap > 10:  # Reasonable overlap indicates alignment
                return True
        
        return False
    
    def _validate_source_credibility(self, sources: List[Dict]) -> Dict[str, Any]:
        """Validate credibility of web sources"""
        
        credibility_info = {
            "high_credibility_sources": 0,
            "medium_credibility_sources": 0,
            "low_credibility_sources": 0,
            "total_sources": len(sources)
        }
        
        for source in sources:
            url = source.get("url", "").lower()
            
            if any(domain in url for domain in [".edu", ".gov", ".org"]):
                credibility_info["high_credibility_sources"] += 1
            elif any(domain in url for domain in ["wikipedia.org", "britannica.com", "musictheory.net"]):
                credibility_info["medium_credibility_sources"] += 1
            else:
                credibility_info["low_credibility_sources"] += 1
        
        return credibility_info
```

### 6.2 Testing Framework for Conversational Features

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestConversationalFeatures:
    """Test conversational AI and web search integration"""
    
    @pytest.fixture
    def mock_web_search(self):
        mock_search = Mock()
        mock_search.search_for_educational_content = AsyncMock(return_value=[
            {
                "title": "Jazz and Hip-Hop Fusion in Modern Music Education",
                "content": "Contemporary music education explores the connections between jazz improvisation and hip-hop rhythmic patterns...",
                "url": "https://musiceducation.org/jazz-hiphop-fusion",
                "source_quality": "high"
            }
        ])
        return mock_search
    
    @pytest.fixture
    def sample_conversation_session(self):
        session = ConversationSession("test-session-123")
        session.update_context("educational_context", "high school classroom")
        session.update_context("genres", ["jazz", "hip-hop"])
        session.update_context("skill_level", "intermediate")
        session.update_context("learning_objectives", ["improvisation", "rhythm analysis"])
        return session
    
    def test_conversation_context_gathering(self, sample_conversation_session):
        """Test that conversation gathers sufficient context"""
        
        validator = ConversationalContentValidator()
        validations = validator.validate_conversation_context(sample_conversation_session)
        
        assert validations["has_educational_context"]
        assert validations["has_sufficient_genres"]
        assert validations["has_skill_level"]
        assert validations["has_learning_objectives"]
    
    def test_web_search_integration(self, mock_web_search):
        """Test web search tool integration"""
        
        async def run_search_test():
            context = {
                "skill_level": "intermediate",
                "educational_context": "classroom"
            }
            
            results = await mock_web_search.search_for_educational_content(
                "jazz hip-hop fusion education", 
                context
            )
            
            assert len(results) > 0
            assert results[0]["source_quality"] == "high"
            assert "education" in results[0]["content"].lower()
        
        import asyncio
        asyncio.run(run_search_test())
    
    def test_context_enhanced_generation(self, sample_conversation_session):
        """Test generation with conversation context"""
        
        generation_context = sample_conversation_session.get_generation_context()
        
        assert generation_context["educational_context"] == "high school classroom"
        assert "jazz" in generation_context["genres"]
        assert "hip-hop" in generation_context["genres"]
        assert generation_context["skill_level"] == "intermediate"
        assert "improvisation" in generation_context["learning_objectives"]
    
    def test_ready_for_generation_check(self):
        """Test readiness check for generation"""
        
        # Incomplete session
        incomplete_session = ConversationSession("incomplete")
        incomplete_session.update_context("genres", ["jazz"])
        assert not incomplete_session.is_ready_for_generation()
        
        # Complete session
        complete_session = ConversationSession("complete")
        complete_session.update_context("educational_context", "classroom")
        complete_session.update_context("genres", ["jazz", "hip-hop"])
        complete_session.update_context("skill_level", "intermediate")
        complete_session.update_context("learning_objectives", ["improvisation"])
        assert complete_session.is_ready_for_generation()
    
    def test_cultural_sensitivity_with_web_sources(self):
        """Test cultural sensitivity validation with web sources"""
        
        validator = ConversationalContentValidator()
        
        content_with_good_cultural_context = {
            "educational_content": {
                "cultural_context": "Jazz emerged from African American communities in New Orleans, representing a rich cultural tradition of musical innovation. Hip-hop, originating in the Bronx, represents another powerful form of African American cultural expression through rhythm and poetry."
            }
        }
        
        web_sources = [
            {
                "title": "History of Jazz in African American Culture",
                "content": "Jazz music has deep roots in African American communities and represents...",
                "url": "https://musichistory.edu/jazz-culture"
            }
        ]
        
        validations = validator.validate_generated_content_with_sources(
            content_with_good_cultural_context, 
            web_sources
        )
        
        assert validations["cultural_sensitivity"]
        assert validations["web_source_alignment"]
```

---

## 7. CI/CD Integration for Conversational Features

### 7.1 Enhanced Automated Testing

```yaml
# .github/workflows/conversational-testing.yml
name: Conversational AI & Web Search Quality Check

on:
  push:
    branches: [ main, develop ]
    paths: 
      - 'agents.py'
      - 'conversation.py'
      - 'web_search.py'
      - 'test_conversation.py'

jobs:
  test-conversational-features:
    runs-on: ubuntu-latest
    
    env:
      TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install pytest ollama pydantic langchain tavily-python
    
    - name: Test conversation flow structure
      run: |
        python -c "
        from conversation import ConversationSession
        
        # Test session creation and context gathering
        session = ConversationSession('test-123')
        session.update_context('genres', ['jazz', 'blues'])
        session.update_context('skill_level', 'beginner')
        
        assert len(session.gathered_context['genres']) == 2
        assert session.gathered_context['skill_level'] == 'beginner'
        print('Conversation structure tests passed')
        "
    
    - name: Test web search integration (with API key)
      if: env.TAVILY_API_KEY != ''
      run: |
        python -c "
        import asyncio
        from web_search import WebSearchTool
        import os
        
        async def test_search():
            if not os.getenv('TAVILY_API_KEY'):
                print('Skipping web search test - no API key')
                return
            
            search_tool = WebSearchTool()
            results = await search_tool.search_for_educational_content(
                'jazz music education beginner', 
                {'skill_level': 'beginner'}
            )
            
            assert isinstance(results, list)
            print(f'Web search test passed - found {len(results)} results')
        
        asyncio.run(test_search())
        "
    
    - name: Test conversation validation
      run: |
        python -c "
        from conversation import ConversationSession
        from validation import ConversationalContentValidator
        
        # Test complete conversation context
        session = ConversationSession('validation-test')
        session.update_context('educational_context', 'classroom')
        session.update_context('genres', ['jazz', 'hip-hop'])
        session.update_context('skill_level', 'intermediate')
        session.update_context('learning_objectives', ['improvisation'])
        
        validator = ConversationalContentValidator()
        validations = validator.validate_conversation_context(session)
        
        assert validations['has_educational_context']
        assert validations['has_sufficient_genres']
        assert validations['has_skill_level']
        print('Conversation validation tests passed')
        "
    
    - name: Test educational content with sources
      run: |
        pytest test_conversation.py::TestConversationalFeatures -v
```

---

## 8. Environment Configuration

### 8.1 Enhanced Environment Setup

```python
# .env configuration for conversational features
TAVILY_API_KEY=your_tavily_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./lit_music_mashup.db
LOG_LEVEL=INFO

# Conversation settings
MAX_CONVERSATION_TURNS=10
CONVERSATION_TIMEOUT_MINUTES=30
WEB_SEARCH_MAX_RESULTS=3
WEB_SEARCH_TIMEOUT_SECONDS=10

# Educational content validation
MIN_CULTURAL_CONTEXT_LENGTH=100
MIN_THEORY_CONCEPTS=2
REQUIRED_TEACHING_NOTES=true
```

### 8.2 Configuration Validation

```python
import os
from typing import Dict, Any

def validate_environment_config() -> Dict[str, Any]:
    """Validate environment configuration for conversational features"""
    
    config_status = {
        "ollama_configured": bool(os.getenv("OLLAMA_BASE_URL")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "tavily_api_available": bool(os.getenv("TAVILY_API_KEY")),
        "conversation_settings_valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Check required settings
    if not config_status["ollama_configured"]:
        config_status["errors"].append("OLLAMA_BASE_URL not configured")
    
    if not config_status["database_configured"]:
        config_status["errors"].append("DATABASE_URL not configured")
    
    # Check optional but recommended settings
    if not config_status["tavily_api_available"]:
        config_status["warnings"].append("TAVILY_API_KEY not configured - web search will be disabled")
    
    # Validate conversation settings
    try:
        max_turns = int(os.getenv("MAX_CONVERSATION_TURNS", "10"))
        if max_turns < 3 or max_turns > 20:
            config_status["warnings"].append("MAX_CONVERSATION_TURNS should be between 3 and 20")
    except ValueError:
        config_status["errors"].append("MAX_CONVERSATION_TURNS must be a valid integer")
        config_status["conversation_settings_valid"] = False
    
    return config_status
```

---

## 9. Summary

### 9.1 Enhanced MVP v2.0 Conversational Strategy

**Conversational Approach**:
- Multi-turn dialogue to gather comprehensive context
- Web search integration for current information
- LangChain/LangGraph orchestration for tool usage
- Educational content validation with web source verification
- Graceful degradation when web search unavailable

**Quality Assurance Enhancements**:
- Conversation context validation
- Web source credibility assessment
- Cultural sensitivity checking with current context
- Performance monitoring for conversation and web search
- Educational content alignment verification

**Tool Integration**:
- Tavily API for educational web search
- Context-aware search query enhancement
- Source filtering for educational appropriateness
- Conversation state management
- Tool orchestration decision making

### 9.2 Key Benefits of Conversational Approach

1. **Rich Context Gathering**: Multi-turn conversations provide comprehensive understanding
2. **Current Information**: Web search ensures up-to-date cultural and educational context
3. **Personalized Content**: Context-driven generation matches specific educational needs
4. **Quality Assurance**: Multi-layered validation ensures educational and cultural appropriateness
5. **Graceful Degradation**: System works with or without web search capabilities

This conversational prompt structure enables the MVP to deliver more personalized, current, and educationally valuable content while maintaining reliability and cultural sensitivity through comprehensive validation processes.