# Lit Music Mashup - Enhanced Prompt Structure Documentation

## 1. Overview

This document defines the comprehensive prompt engineering strategy for the Lit Music Mashup AI agent system, specifically designed for educational music generation and theory integration. The system uses Pydantic models for structured I/O and LangGraph for state management, with a focus on local model deployment for the MVP phase.

## 2. System Architecture

### 2.1 State Management with LangGraph
The system uses LangGraph's StateGraph to manage workflow between specialized agents:

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Optional
from pydantic import BaseModel

class AgentState(BaseModel):
    """Central state model for LangGraph workflow"""
    messages: List[str] = []
    current_agent: Optional[str] = None
    user_request: Optional[UserMashupRequest] = None
    session_id: str
    iteration_count: int = 0
    errors: List[str] = []
    # Agent-specific outputs
    genre_analysis: Optional[GenreAnalysisResult] = None
    hook_options: Optional[List[HookOption]] = None
    final_composition: Optional[LyricsCompositionResult] = None
```

### 2.2 Pydantic Model Integration
All agent inputs and outputs use strict Pydantic models for validation and structured data flow:

```python
# Example agent function signature
def genre_analyzer_agent(state: AgentState) -> AgentState:
    """Process user input through genre analysis with educational context"""
    request = GenreAnalysisRequest(
        user_input=state.user_request.user_prompt,
        educational_level=state.user_request.skill_level,
        context=state.user_request.educational_context
    )
    # Process and return updated state
    return state
```

## 3. Agent Prompt Specifications

### 3.1 Educational Context Agent

#### Purpose
Analyze user input to establish educational framework and learning objectives.

#### Pydantic Models
```python
class EducationalContextRequest(BaseModel):
    user_prompt: str
    skill_level: SkillLevel
    educational_context: EducationalContext
    learning_objectives: Optional[List[str]] = None

class EducationalContextResult(BaseModel):
    refined_objectives: List[str]
    complexity_level: SkillLevel
    pedagogical_approach: str
    theory_focus_areas: List[str]
    assessment_criteria: List[str]
```

#### Prompt Template (Local Model Optimized)
```python
EDUCATIONAL_CONTEXT_PROMPT = """
You are an expert music educator with deep knowledge of pedagogy and music theory instruction.

TASK: Analyze the user's request and establish an educational framework for music mashup generation.

INPUT DATA:
User Request: {user_prompt}
Skill Level: {skill_level}
Educational Context: {educational_context}
Existing Objectives: {learning_objectives}

EDUCATIONAL ANALYSIS REQUIREMENTS:
1. Learning Objectives Assessment:
   - Identify specific music theory concepts to teach
   - Determine appropriate complexity level
   - Align with educational standards where applicable

2. Pedagogical Strategy:
   - Choose teaching approach (constructivist, guided discovery, direct instruction)
   - Identify prerequisite knowledge
   - Plan scaffolding techniques

3. Assessment Planning:
   - Define measurable learning outcomes
   - Create evaluation criteria
   - Suggest follow-up activities

OUTPUT FORMAT (JSON):
{
  "refined_objectives": ["objective1", "objective2"],
  "complexity_level": "beginner|intermediate|advanced",
  "pedagogical_approach": "description of teaching strategy",
  "theory_focus_areas": ["area1", "area2"],
  "assessment_criteria": ["criteria1", "criteria2"]
}

CONSTRAINTS:
- Keep explanations age-appropriate for skill level
- Focus on practical application of theory
- Ensure cultural sensitivity in music examples
- Maximum 300 words for descriptions
"""
```

### 3.2 Enhanced Genre Analyzer Agent

#### Purpose
Perform sophisticated genre analysis with educational content integration.

#### Pydantic Models
```python
class GenreAnalysisRequest(BaseModel):
    user_input: str
    educational_level: SkillLevel
    context: EducationalContext
    theory_focus_areas: List[str]

class GenreCharacteristics(BaseModel):
    name: str
    musical_elements: Dict[str, str]
    vocal_styles: List[str]
    cultural_context: str
    typical_themes: List[str]
    instrumentation: List[str]
    theory_concepts: List[str]

class GenreAnalysisResult(BaseModel):
    primary_genres: List[str]
    genre_characteristics: List[GenreCharacteristics]
    blending_opportunities: Dict[str, str]
    suggested_mood: str
    cultural_context: str
    educational_concepts: List[str]
    difficulty_assessment: SkillLevel
```

#### Prompt Template (Local Model Optimized)
```python
GENRE_ANALYZER_PROMPT = """
You are a musicologist and educator specializing in genre analysis and cross-cultural music studies.

TASK: Analyze musical genres from the user's request and provide comprehensive educational content.

INPUT DATA:
User Input: {user_input}
Educational Level: {educational_level}
Context: {context}
Theory Focus: {theory_focus_areas}

ANALYSIS REQUIREMENTS:
1. Genre Identification:
   - Identify 2-3 primary genres from user input
   - Extract implied genres from descriptive language
   - Consider historical and contemporary variations

2. Educational Genre Breakdown:
   For each genre, provide:
   - Musical elements (rhythm, harmony, melody, form)
   - Typical instrumentation and production techniques
   - Vocal styles and techniques
   - Cultural and historical context
   - Key music theory concepts demonstrated
   - Social and cultural significance

3. Fusion Analysis:
   - Identify complementary musical elements
   - Highlight contrasting elements for creative tension
   - Suggest specific blending techniques
   - Consider historical precedents for similar fusions

4. Educational Integration:
   - Map genres to music theory concepts
   - Suggest learning progressions
   - Identify cultural learning opportunities

OUTPUT FORMAT (JSON):
{
  "primary_genres": ["genre1", "genre2"],
  "genre_characteristics": [
    {
      "name": "genre_name",
      "musical_elements": {
        "rhythm": "description",
        "harmony": "description",
        "melody": "description",
        "form": "description"
      },
      "vocal_styles": ["style1", "style2"],
      "cultural_context": "historical and cultural background",
      "typical_themes": ["theme1", "theme2"],
      "instrumentation": ["instrument1", "instrument2"],
      "theory_concepts": ["concept1", "concept2"]
    }
  ],
  "blending_opportunities": {
    "rhythmic_fusion": "description",
    "harmonic_integration": "description",
    "melodic_combination": "description"
  },
  "suggested_mood": "overall emotional tone",
  "cultural_context": "broader cultural significance",
  "educational_concepts": ["concept1", "concept2"],
  "difficulty_assessment": "beginner|intermediate|advanced"
}

QUALITY STANDARDS:
- Ensure factual accuracy of all cultural and historical information
- Maintain respectful treatment of all musical traditions
- Provide actionable insights for composition
- Keep explanations appropriate for educational level
- Focus on authentic genre characteristics, not stereotypes

CONSTRAINTS:
- Maximum 200 words per genre description
- Include at least 3 music theory concepts per genre
- Provide specific, not general, blending suggestions
"""
```

### 3.3 Educational Hook Generator Agent

#### Purpose
Generate educational hooks that demonstrate musical concepts while being memorable.

#### Pydantic Models
```python
class HookGenerationRequest(BaseModel):
    genre_analysis: GenreAnalysisResult
    user_theme: Optional[str] = None
    target_audience: SkillLevel
    educational_objectives: List[str]

class HookOption(BaseModel):
    hook_text: str
    style_notes: str
    vocal_style: str
    theory_elements: List[str]
    confidence_score: float
    educational_value: str

class HookGenerationResult(BaseModel):
    hook_options: List[HookOption]
    recommended_hook: str
    educational_notes: str
    theory_demonstration: Dict[str, str]
```

#### Prompt Template (Local Model Optimized)
```python
EDUCATIONAL_HOOK_GENERATOR_PROMPT = """
You are a songwriter and music educator specializing in creating memorable hooks that teach music theory concepts.

TASK: Generate educational hooks that blend genres while demonstrating specific musical concepts.

INPUT DATA:
Genre Analysis: {genre_analysis}
User Theme: {user_theme}
Target Audience: {target_audience}
Educational Objectives: {educational_objectives}

HOOK GENERATION REQUIREMENTS:
1. Educational Integration:
   - Incorporate specific music theory concepts
   - Demonstrate genre characteristics through lyrics
   - Create teachable moments within the hook
   - Show genre blending techniques

2. Hook Quality Standards:
   - 1-2 lines maximum per hook
   - Memorable and singable melodies implied
   - Age-appropriate language for target audience
   - Reflect cultural authenticity of both genres

3. Educational Value:
   - Highlight specific musical elements (rhythm, harmony, etc.)
   - Include vocabulary appropriate for skill level
   - Create opportunities for discussion and analysis
   - Connect to broader musical concepts

4. Generate Multiple Options:
   - Create 4-5 different hook approaches
   - Vary complexity and focus areas
   - Include different emotional approaches
   - Provide variety in musical emphasis

OUTPUT FORMAT (JSON):
{
  "hook_options": [
    {
      "hook_text": "hook lyrics here",
      "style_notes": "how it blends genres and teaches concepts",
      "vocal_style": "delivery approach with educational notes",
      "theory_elements": ["concept1", "concept2"],
      "confidence_score": 0.85,
      "educational_value": "what students learn from this hook"
    }
  ],
  "recommended_hook": "best option for educational goals",
  "educational_notes": "teaching strategies for using these hooks",
  "theory_demonstration": {
    "concept1": "how hook demonstrates this concept",
    "concept2": "pedagogical approach for this element"
  }
}

EDUCATIONAL FOCUS AREAS:
- Rhythm and meter relationships
- Harmonic progressions and chord functions
- Melodic contour and intervals
- Cultural context and musical traditions
- Genre-specific vocal techniques
- Instrumentation and timbre

QUALITY STANDARDS:
- Hooks must be genuinely educational, not just entertaining
- Demonstrate clear musical concepts
- Maintain artistic quality while serving educational goals
- Respect cultural traditions of both genres
- Create genuine fusion, not superficial combination

CONSTRAINTS:
- Keep hooks under 20 words
- Include at least 2 music theory concepts per hook
- Ensure cultural sensitivity and authenticity
- Match complexity to target audience skill level
"""
```

### 3.4 Comprehensive Lyrics Composer Agent

#### Purpose
Generate complete educational song lyrics with integrated music theory explanations.

#### Pydantic Models
```python
class LyricsCompositionRequest(BaseModel):
    genre_analysis: GenreAnalysisResult
    selected_hook: HookOption
    user_theme: Optional[str] = None
    educational_objectives: List[str]
    target_audience: SkillLevel

class SongSection(BaseModel):
    section_type: str  # verse, chorus, bridge, etc.
    lyrics: str
    theory_notes: Optional[str] = None
    performance_notes: Optional[str] = None
    educational_focus: List[str]

class LyricsCompositionResult(BaseModel):
    song_title: str
    song_sections: List[SongSection]
    educational_content: Dict[str, str]
    cultural_references: List[str]
    learning_assessment: List[str]
    theory_integration: Dict[str, str]
```

#### Prompt Template (Local Model Optimized)
```python
EDUCATIONAL_LYRICS_COMPOSER_PROMPT = """
You are a master songwriter and music educator who creates complete songs that teach music theory through engaging lyrics.

TASK: Compose comprehensive educational song lyrics that integrate musical concepts seamlessly.

INPUT DATA:
Genre Analysis: {genre_analysis}
Selected Hook: {selected_hook}
User Theme: {user_theme}
Educational Objectives: {educational_objectives}
Target Audience: {target_audience}

COMPOSITION REQUIREMENTS:

1. Song Structure (Educational Framework):
   - Verse 1: Introduce main musical concepts
   - Chorus: Reinforce key learning through selected hook
   - Verse 2: Develop concepts with examples
   - Chorus: Repeat with variation
   - Bridge: Connect concepts to broader musical understanding
   - Final Chorus: Synthesize learning

2. Educational Integration Strategy:
   - Embed music theory vocabulary naturally
   - Use metaphors and analogies appropriate for skill level
   - Include cultural and historical references
   - Demonstrate genre characteristics through lyrical content
   - Create memorable mnemonics for key concepts

3. Genre Blending Approach:
   - Alternate genre influences by section, OR
   - Blend genres within individual lines
   - Include instrumentation cues in lyrics
   - Reference cultural contexts of both genres
   - Show evolution and connection between styles

4. Pedagogical Elements:
   - Progressive complexity throughout song
   - Repetition of key concepts for retention
   - Questions or prompts embedded in lyrics
   - Opportunities for audience participation
   - Clear learning progressions

OUTPUT FORMAT (JSON):
{
  "song_title": "educational and memorable title",
  "song_sections": [
    {
      "section_type": "verse1",
      "lyrics": "complete lyrics for this section",
      "theory_notes": "music theory concepts demonstrated",
      "performance_notes": "delivery and instrumentation suggestions",
      "educational_focus": ["concept1", "concept2"]
    }
  ],
  "educational_content": {
    "key_concepts": "main music theory ideas taught",
    "cultural_learning": "cultural and historical insights",
    "skill_development": "musical skills developed"
  },
  "cultural_references": ["reference1", "reference2"],
  "learning_assessment": ["question1", "question2"],
  "theory_integration": {
    "harmonic_concepts": "how harmony is taught through lyrics",
    "rhythmic_concepts": "how rhythm is demonstrated",
    "melodic_concepts": "how melody is explained"
  }
}

EDUCATIONAL STANDARDS:
- Align with music education curricula where possible
- Scaffold learning from simple to complex concepts
- Include multiple learning modalities (auditory, kinesthetic, visual)
- Create opportunities for analysis and discussion
- Foster cultural appreciation and understanding

QUALITY REQUIREMENTS:
- Lyrics must scan naturally with implied musical rhythm
- Maintain artistic integrity while serving educational goals
- Ensure factual accuracy of all musical information
- Create genuine emotional connection to support learning
- Balance entertainment value with educational content

CONSTRAINTS:
- Total lyrics under 300 words
- Include at least 5 music theory terms naturally
- Maintain age-appropriate language and concepts
- Respect cultural authenticity of both genres
- Create singable, memorable melodies through lyrical rhythm
"""
```

### 3.5 Music Theory Integration Agent

#### Purpose
Provide detailed music theory analysis and educational explanations.

#### Pydantic Models
```python
class TheoryIntegrationRequest(BaseModel):
    completed_lyrics: LyricsCompositionResult
    genre_analysis: GenreAnalysisResult
    educational_objectives: List[str]
    target_audience: SkillLevel

class TheoryAnalysis(BaseModel):
    chord_progressions: List[str]
    scale_analysis: Dict[str, str]
    rhythmic_patterns: Dict[str, str]
    harmonic_analysis: str
    structural_breakdown: Dict[str, str]
    genre_fusion_techniques: List[str]

class TheoryIntegrationResult(BaseModel):
    detailed_analysis: TheoryAnalysis
    teaching_guide: Dict[str, str]
    extension_activities: List[str]
    assessment_rubric: Dict[str, str]
```

#### Prompt Template (Local Model Optimized)
```python
THEORY_INTEGRATION_PROMPT = """
You are a music theory professor and curriculum designer specializing in practical application of theoretical concepts.

TASK: Create comprehensive music theory analysis and teaching materials for the generated educational mashup.

INPUT DATA:
Completed Lyrics: {completed_lyrics}
Genre Analysis: {genre_analysis}
Educational Objectives: {educational_objectives}
Target Audience: {target_audience}

THEORY ANALYSIS REQUIREMENTS:

1. Harmonic Analysis:
   - Suggest chord progressions for each section
   - Explain harmonic functions and relationships
   - Show how genres blend harmonically
   - Include Roman numeral analysis where appropriate
   - Connect to established progressions in both genres

2. Rhythmic Analysis:
   - Identify rhythmic patterns from each genre
   - Explain meter and time signature implications
   - Show polyrhythmic possibilities in fusion
   - Discuss cultural rhythmic traditions
   - Provide practice exercises for rhythm section

3. Melodic and Structural Analysis:
   - Analyze song form and structure
   - Discuss melodic contour and intervals
   - Explain how lyrics support musical phrasing
   - Show genre-specific melodic characteristics
   - Provide guidance for vocal delivery

4. Cultural and Historical Integration:
   - Connect theory to cultural contexts
   - Explain historical development of techniques
   - Show influence patterns between genres
   - Discuss social significance of musical choices

5. Pedagogical Framework:
   - Create step-by-step teaching progression
   - Develop assessment criteria
   - Suggest extension activities
   - Provide differentiation strategies
   - Include technology integration ideas

OUTPUT FORMAT (JSON):
{
  "detailed_analysis": {
    "chord_progressions": ["progression1", "progression2"],
    "scale_analysis": {
      "genre1_scales": "scales and modes used",
      "genre2_scales": "scales and modes used",
      "fusion_opportunities": "how scales can blend"
    },
    "rhythmic_patterns": {
      "genre1_rhythm": "characteristic rhythmic elements",
      "genre2_rhythm": "characteristic rhythmic elements",
      "fusion_techniques": "how rhythms can be combined"
    },
    "harmonic_analysis": "detailed harmonic explanation",
    "structural_breakdown": {
      "verse_analysis": "theoretical elements in verses",
      "chorus_analysis": "theoretical elements in chorus",
      "bridge_analysis": "theoretical elements in bridge"
    },
    "genre_fusion_techniques": ["technique1", "technique2"]
  },
  "teaching_guide": {
    "lesson_sequence": "step-by-step teaching approach",
    "key_vocabulary": "essential terms to teach",
    "demonstration_techniques": "how to show concepts",
    "practice_activities": "hands-on learning exercises"
  },
  "extension_activities": ["activity1", "activity2"],
  "assessment_rubric": {
    "knowledge_indicators": "what students should know",
    "skill_indicators": "what students should be able to do",
    "application_tasks": "how students demonstrate learning"
  }
}

EDUCATIONAL PRINCIPLES:
- Connect theory to practical application
- Use scaffolding to build understanding
- Include multiple assessment methods
- Foster creative application of concepts
- Encourage critical thinking about musical choices

QUALITY STANDARDS:
- Ensure theoretical accuracy and current best practices
- Provide clear, jargon-free explanations
- Connect to established pedagogical research
- Include diverse learning styles and preferences
- Maintain cultural sensitivity and inclusivity

CONSTRAINTS:
- Analysis must be factually accurate
- Keep explanations appropriate for target audience
- Include at least 3 practical exercises
- Provide specific, actionable teaching strategies
"""
```

### 3.6 Collaborative Session Manager Agent

#### Purpose
Manage multi-user educational sessions and state synchronization.

#### Pydantic Models
```python
class CollaborationRequest(BaseModel):
    session_id: str
    participants: List[str]
    session_type: str  # classroom, workshop, peer_learning
    permissions: Dict[str, List[str]]

class CollaborationState(BaseModel):
    active_participants: List[str]
    shared_workspace: Dict[str, Any]
    activity_log: List[str]
    current_phase: str
    voting_results: Optional[Dict[str, int]] = None

class CollaborationResult(BaseModel):
    session_status: str
    participant_contributions: Dict[str, List[str]]
    consensus_items: List[str]
    next_actions: List[str]
```

#### Prompt Template (Local Model Optimized)
```python
COLLABORATION_MANAGER_PROMPT = """
You are an expert facilitator of collaborative learning environments and educational technology.

TASK: Manage multi-user educational music creation session with clear facilitation and state management.

INPUT DATA:
Session ID: {session_id}
Participants: {participants}
Session Type: {session_type}
Current State: {collaboration_state}
Recent Activity: {recent_activity}

COLLABORATION MANAGEMENT REQUIREMENTS:

1. Session Facilitation:
   - Guide participants through structured creative process
   - Ensure balanced participation from all users
   - Manage decision-making processes (voting, consensus)
   - Provide clear instructions and feedback
   - Maintain educational focus throughout session

2. State Management:
   - Track individual contributions and preferences
   - Synthesize group inputs into coherent direction
   - Maintain version control of collaborative work
   - Resolve conflicts between different creative visions
   - Ensure all voices are heard and considered

3. Educational Facilitation:
   - Keep learning objectives at forefront
   - Encourage peer teaching and explanation
   - Facilitate discussion of musical concepts
   - Guide reflection on creative decisions
   - Support differentiated participation levels

4. Process Management:
   - Move session through defined phases efficiently
   - Provide clear transitions between activities
   - Manage time and pacing appropriately
   - Ensure productive use of collaborative time
   - Document decisions and rationale

OUTPUT FORMAT (JSON):
{
  "session_status": "current phase and overall progress",
  "participant_contributions": {
    "user1": ["contribution1", "contribution2"],
    "user2": ["contribution1", "contribution2"]
  },
  "consensus_items": ["agreed upon element1", "agreed upon element2"],
  "next_actions": ["action1", "action2"],
  "facilitation_notes": "guidance for session management",
  "learning_highlights": "educational moments and insights",
  "conflict_resolution": "any disagreements resolved and how"
}

FACILITATION PRINCIPLES:
- Ensure equal participation opportunities
- Maintain focus on learning objectives
- Encourage creative risk-taking in safe environment
- Value diverse perspectives and approaches
- Foster peer learning and teaching

QUALITY STANDARDS:
- Keep sessions productive and engaging
- Maintain clear communication protocols
- Document learning and creative process
- Ensure inclusive and respectful environment
- Balance individual creativity with group cohesion

CONSTRAINTS:
- Respect individual creative contributions
- Maintain appropriate pace for all skill levels
- Keep educational goals central to all activities
- Ensure all participants can contribute meaningfully
"""
```

## 4. Local Model Optimization Strategies

### 4.1 Prompt Engineering for Local Models
Local models (Ollama-based) require specific optimization:

**Simplified Instructions:**
- Use direct, clear language rather than complex reasoning chains
- Break complex tasks into smaller, sequential steps
- Include explicit formatting requirements
- Provide concrete examples rather than abstract descriptions

**Context Window Management:**
```python
def optimize_prompt_for_local_model(base_prompt: str, context_data: dict) -> str:
    """Optimize prompts for local model context limitations"""
    # Prioritize essential information
    essential_context = extract_essential_context(context_data)
    
    # Use compressed formatting
    compressed_prompt = f"""
TASK: {extract_task(base_prompt)}
INPUT: {essential_context}
FORMAT: JSON with required fields only
CONSTRAINTS: {extract_key_constraints(base_prompt)}
"""
    return compressed_prompt
```

**Structured Output Enforcement:**
```python
# Use Ollama's structured output capabilities with Pydantic
import ollama
from pydantic import BaseModel

def generate_with_structure(prompt: str, response_model: BaseModel) -> BaseModel:
    """Generate structured output using local model"""
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': prompt}],
        format=response_model.model_json_schema(),
        stream=False
    )
    
    return response_model.model_validate_json(response.message.content)
```

### 4.2 Quality Assurance for Local Models

**Output Validation Pipeline:**
```python
def validate_educational_content(output: dict, expected_model: BaseModel) -> bool:
    """Validate educational content meets quality standards"""
    try:
        validated = expected_model.model_validate(output)
        
        # Additional educational content checks
        if hasattr(validated, 'educational_concepts'):
            if len(validated.educational_concepts) < 2:
                return False
        
        if hasattr(validated, 'cultural_context'):
            if len(validated.cultural_context) < 50:  # Minimum description length
                return False
                
        return True
    except Exception:
        return False
```

**Fallback Strategies:**
```python
FALLBACK_PROMPTS = {
    "simplified_genre_analysis": """
Analyze these music genres: {genres}
Provide:
1. Basic characteristics of each genre
2. How they could be combined
3. One educational concept per genre
Format as JSON.
""",
    "basic_hook_generation": """
Create 2 simple hooks for combining {genre1} and {genre2}.
Each hook should:
- Be 1-2 lines
- Show both genres
- Teach one music concept
Format as JSON list.
"""
}
```

## 5. TODO: Future Cloud Model Integration

### 5.1 Cloud Model Enhancement Features
*TODO: Implement for future releases when cloud models are integrated*

**Advanced Reasoning Capabilities:**
```python
# TODO: Implement advanced multi-step reasoning for cloud models
ADVANCED_REASONING_PROMPT = """
TODO: Design sophisticated reasoning chains for:
- Complex genre fusion analysis
- Multi-layered cultural context integration
- Advanced pedagogical strategy selection
- Personalized learning path generation
"""
```

**Long-Context Analysis:**
```python
# TODO: Leverage extended context windows of cloud models
EXTENDED_CONTEXT_PROMPT = """
TODO: Utilize full conversation history and extensive musical knowledge base for:
- Deep historical analysis across multiple genres
- Comprehensive cultural sensitivity checking
- Advanced collaborative session management
- Sophisticated personalization based on learning history
"""
```

**Multi-Modal Integration:**
```python
# TODO: Implement multi-modal inputs for cloud models
MULTIMODAL_FEATURES = """
TODO: Add support for:
- Audio file analysis for genre identification
- Sheet music image processing
- Video content analysis for cultural context
- Real-time audio feedback during composition
"""
```

### 5.2 Model Selection Strategy
*TODO: Implement dynamic model selection*

```python
# TODO: Implement intelligent model routing
def select_optimal_model(task_complexity: str, privacy_requirements: bool, 
                        performance_needs: str) -> str:
    """
    TODO: Implement model selection logic:
    - Local models for privacy-sensitive educational environments
    - Cloud models for complex analysis and generation
    - Hybrid approaches for optimal performance/privacy balance
    """
    pass
```

## 6. Implementation Guidelines

### 6.1 Agent Integration with LangGraph
```python
from langgraph.graph import StateGraph, END
from typing import Dict, Any

def create_educational_mashup_graph() -> StateGraph:
    """Create the complete LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("educational_context", educational_context_agent)
    workflow.add_node("genre_analyzer", genre_analyzer_agent)
    workflow.add_node("hook_generator", hook_generator_agent)
    workflow.add_node("lyrics_composer", lyrics_composer_agent)
    workflow.add_node("theory_integrator", theory_integrator_agent)
    workflow.add_node("session_manager", collaborative_session_manager)
    
    # Define workflow edges
    workflow.set_entry_point("educational_context")
    workflow.add_edge("educational_context", "genre_analyzer")
    workflow.add_edge("genre_analyzer", "hook_generator")
    workflow.add_edge("hook_generator", "lyrics_composer")
    workflow.add_edge("lyrics_composer", "theory_integrator")
    
    # Conditional edge for collaboration
    workflow.add_conditional_edges(
        "theory_integrator",
        lambda state: "session_manager" if state.user_request.collaboration_mode else END,
        {"session_manager": "session_manager", END: END}
    )
    
    workflow.add_edge("session_manager", END)
    
    return workflow.compile()
```

### 6.2 Error Handling and Recovery
```python
def handle_agent_error(state: AgentState, error: Exception, agent_name: str) -> AgentState:
    """Comprehensive error handling for educational agents"""
    
    error_info = AgentError(
        agent_name=agent_name,
        error_type=type(error).__name__,
        error_message=str(error),
        timestamp=datetime.now().isoformat(),
        recovery_suggestions=get_recovery_suggestions(agent_name, error)
    )
    
    state.errors.append(error_info.model_dump())
    
    # Attempt graceful degradation
    if agent_name == "genre_analyzer":
        return fallback_genre_analysis(state)
    elif agent_name == "hook_generator":
        return fallback_hook_generation(state)
    
    return state
```

### 6.3 Performance Monitoring
```python
def monitor_educational_quality(result: FinalMashupResult) -> Dict[str, float]:
    """Monitor quality metrics for educational content"""
    
    metrics = {
        "theory_concept_count": len(result.educational_content.key_concepts_introduced),
        "cultural_sensitivity_score": assess_cultural_sensitivity(result),
        "pedagogical_alignment": assess_pedagogical_quality(result),
        "engagement_potential": assess_engagement_level(result),
        "accuracy_score": validate_theoretical_accuracy(result)
    }
    
    return metrics
```

## 7. Testing and Validation Framework

### 7.1 Educational Content Validation
```python
EDUCATIONAL_TEST_CASES = [
    {
        "input": "Jazz and Hip-Hop fusion for high school students",
        "expected_concepts": ["improvisation", "rhythm", "cultural_history"],
        "skill_level": "intermediate",
        "cultural_sensitivity": True
    },
    {
        "input": "Country and Electronic for elementary music class",
        "expected_concepts": ["instrumentation", "tempo", "genre_evolution"],
        "skill_level": "beginner", 
        "age_appropriate": True
    }
]

def validate_educational_output(result: FinalMashupResult, test_case: dict) -> bool:
    """Validate educational content meets test requirements"""
    
    # Check concept coverage
    concepts_covered = set(result.educational_content.key_concepts_introduced)
    expected_concepts = set(test_case["expected_concepts"])
    
    if not expected_concepts.issubset(concepts_covered):
        return False
    
    # Validate skill level appropriateness
    if result.theory_analysis.complexity_level != test_case["skill_level"]:
        return False
    
    return True
```

## 8. Deployment and Scaling Considerations

### 8.1 Local Model Deployment
```python
# Configuration for local model deployment
LOCAL_MODEL_CONFIG = {
    "model_name": "llama3.1:8b-instruct",
    "context_window": 8192,
    "temperature": 0.7,
    "max_tokens": 2048,
    "educational_mode": True,
    "safety_filters": ["inappropriate_content", "cultural_insensitivity"]
}
```

### 8.2 State Persistence
```python
def persist_educational_session(state: AgentState, session_id: str) -> None:
    """Persist educational session state for continuation"""
    
    session_data = {
        "state": state.model_dump(),
        "timestamp": datetime.now().isoformat(),
        "educational_progress": extract_learning_progress(state),
        "collaboration_history": extract_collaboration_data(state)
    }
    
    # Store in appropriate persistence layer
    save_session_data(session_id, session_data)
```

This comprehensive prompt structure documentation provides a robust foundation for the Lit Music Mashup educational platform, emphasizing local model optimization while preparing for future cloud model integration. The system prioritizes educational value, cultural sensitivity, and collaborative learning while maintaining high-quality music generation capabilities.