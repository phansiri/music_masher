# Lit Music Mashup - Prompt Structure Documentation v2.0
## Educational AI Music Generation - Simplified MVP-First Approach

---

## 1. Overview

This document defines a simplified prompt engineering strategy for the Lit Music Mashup MVP, focusing on **essential educational functionality** with local model optimization. The system prioritizes working core functionality over complex agent orchestration.

**MVP Philosophy**: Simple prompts that work reliably with local models, educational content focus, incremental complexity addition through CI/CD validation.

---

## 2. Simplified Architecture for MVP

### 2.1 Basic Request/Response Models

```python
from pydantic import BaseModel
from typing import List, Optional

class MashupRequest(BaseModel):
    """Simplified request model for MVP"""
    prompt: str
    skill_level: str = "beginner"  # beginner, intermediate, advanced
    
class EducationalContent(BaseModel):
    """Educational content structure"""
    theory_concepts: List[str]
    cultural_context: str
    teaching_notes: str

class MashupResponse(BaseModel):
    """Simplified response model"""
    title: str
    lyrics: str
    educational_content: EducationalContent
    metadata: dict
```

### 2.2 Single Agent Approach (MVP)

```python
class SimplifiedMashupAgent:
    """Single agent for MVP - no complex orchestration"""
    
    def __init__(self, model_name: str = "llama3.1:8b-instruct"):
        self.model_name = model_name
    
    async def generate_educational_mashup(self, request: MashupRequest) -> MashupResponse:
        """Main generation function - single prompt approach"""
        
        prompt = self._build_educational_prompt(request)
        response = await self._call_local_model(prompt)
        return self._parse_response(response)
```

---

## 3. Core Educational Prompt (MVP)

### 3.1 Master Prompt Template

```python
MVP_EDUCATIONAL_PROMPT = """
You are an expert music educator specializing in creating educational content through music mashups.

TASK: Create an educational music mashup based on the user's request.

USER REQUEST: {user_prompt}
SKILL LEVEL: {skill_level}

REQUIREMENTS:
1. Create a catchy, educational title
2. Write simple lyrics (4-8 lines) that blend musical concepts
3. Include educational content that teaches music theory and cultural context
4. Make content appropriate for {skill_level} level students

OUTPUT FORMAT (JSON):
{{
    "title": "Creative title that reflects the mashup concept",
    "lyrics": "Simple, educational lyrics here...",
    "educational_content": {{
        "theory_concepts": ["2-4 specific music theory concepts"],
        "cultural_context": "Brief explanation of cultural significance and history",
        "teaching_notes": "Practical suggestions for educators on how to use this content"
    }},
    "metadata": {{
        "genres_identified": ["genre1", "genre2"],
        "complexity_level": "{skill_level}",
        "estimated_duration": "estimated time to teach this content"
    }}
}}

EDUCATIONAL FOCUS AREAS:
- Music theory concepts (rhythm, harmony, melody, form)
- Cultural awareness and historical context
- Age-appropriate content and vocabulary
- Practical classroom applications
- Respectful representation of musical traditions

QUALITY STANDARDS:
- Factually accurate music theory information
- Culturally sensitive and respectful content
- Clear, engaging educational value
- Appropriate complexity for skill level
- Practical teaching applications

Generate educational mashup content now:
"""
```

### 3.2 Skill Level Adaptations

```python
SKILL_LEVEL_ADAPTATIONS = {
    "beginner": {
        "vocabulary": "simple music terms",
        "concepts": "basic rhythm, melody, instruments",
        "lyrics_complexity": "short sentences, repetitive patterns",
        "theory_depth": "fundamental concepts only"
    },
    "intermediate": {
        "vocabulary": "standard music theory terms",
        "concepts": "chord progressions, song structure, genre characteristics",
        "lyrics_complexity": "moderate complexity, some music terminology",
        "theory_depth": "intermediate theory with examples"
    },
    "advanced": {
        "vocabulary": "advanced musical terminology",
        "concepts": "complex harmony, cultural analysis, historical connections",
        "lyrics_complexity": "sophisticated language, music theory integration",
        "theory_depth": "detailed analysis with cultural context"
    }
}
```

---

## 4. Local Model Optimization (MVP)

### 4.1 Simplified Prompt Engineering

```python
def build_mvp_prompt(request: MashupRequest) -> str:
    """Build optimized prompt for local models"""
    
    # Extract key elements from user request
    genres = extract_genres_from_prompt(request.prompt)
    educational_focus = determine_educational_focus(request.prompt, request.skill_level)
    
    # Build simplified prompt
    prompt = f"""
Create educational music mashup:

Request: {request.prompt}
Level: {request.skill_level}
Focus: {educational_focus}

Generate JSON with:
- title: Creative mashup title
- lyrics: 4-6 educational lines
- educational_content:
  - theory_concepts: [2-3 music concepts]
  - cultural_context: Brief cultural info
  - teaching_notes: How to use in class

Make it educational, respectful, and {request.skill_level}-appropriate.
"""
    
    return prompt

def extract_genres_from_prompt(prompt: str) -> List[str]:
    """Extract likely genres from user prompt"""
    common_genres = [
        "jazz", "blues", "rock", "pop", "hip-hop", "country", 
        "classical", "folk", "electronic", "reggae", "latin"
    ]
    
    found_genres = []
    prompt_lower = prompt.lower()
    
    for genre in common_genres:
        if genre in prompt_lower:
            found_genres.append(genre)
    
    return found_genres[:3]  # Limit to 3 for simplicity
```

### 4.2 Response Parsing & Validation

```python
import json
import re
from typing import Dict, Any

def parse_and_validate_response(raw_response: str) -> Dict[str, Any]:
    """Parse and validate AI response for educational content"""
    
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")
        
        # Validate required fields
        validated_response = validate_educational_content(response_json)
        return validated_response
        
    except Exception as e:
        # Return fallback response
        return create_fallback_response(e)

def validate_educational_content(response: Dict) -> Dict:
    """Validate educational content meets MVP standards"""
    
    # Ensure required fields exist
    required_fields = ["title", "lyrics", "educational_content"]
    for field in required_fields:
        if field not in response:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate educational content structure
    edu_content = response["educational_content"]
    required_edu_fields = ["theory_concepts", "cultural_context", "teaching_notes"]
    
    for field in required_edu_fields:
        if field not in edu_content:
            edu_content[field] = get_default_educational_content(field)
    
    # Ensure theory concepts is a list with at least 2 items
    if not isinstance(edu_content["theory_concepts"], list):
        edu_content["theory_concepts"] = ["rhythm", "melody"]
    
    if len(edu_content["theory_concepts"]) < 2:
        edu_content["theory_concepts"].extend(["rhythm", "melody"])
    
    return response

def create_fallback_response(error: Exception) -> Dict:
    """Create fallback response when AI generation fails"""
    
    return {
        "title": "Educational Music Mashup",
        "lyrics": "Music brings us together, learning through song\nDifferent styles unite, making knowledge strong\nRhythm and melody, culture and time\nEducation through music, reason and rhyme",
        "educational_content": {
            "theory_concepts": ["rhythm", "melody", "cultural fusion"],
            "cultural_context": "Music serves as a universal language that connects different cultures and traditions, allowing students to explore diversity through creative expression.",
            "teaching_notes": "Use this mashup to introduce students to the concept of cultural fusion in music. Discuss how different musical traditions can be respectfully combined to create new learning experiences."
        },
        "metadata": {
            "genres_identified": ["educational"],
            "complexity_level": "beginner",
            "estimated_duration": "15-20 minutes",
            "fallback_used": True,
            "error": str(error)
        }
    }
```

---

## 5. Quality Assurance for MVP

### 5.1 Educational Content Validation

```python
class EducationalContentValidator:
    """Simplified validation for MVP educational content"""
    
    @staticmethod
    def validate_theory_concepts(concepts: List[str]) -> bool:
        """Validate music theory concepts are reasonable"""
        valid_concepts = [
            "rhythm", "melody", "harmony", "tempo", "dynamics",
            "chord progressions", "scales", "improvisation", "structure",
            "instrumentation", "cultural context", "historical significance"
        ]
        
        # At least 50% of concepts should be recognizable
        valid_count = sum(1 for concept in concepts 
                         if any(valid in concept.lower() for valid in valid_concepts))
        
        return valid_count >= len(concepts) * 0.5
    
    @staticmethod
    def validate_cultural_sensitivity(cultural_content: str) -> bool:
        """Basic cultural sensitivity check"""
        
        # Check for potentially problematic terms
        sensitive_terms = [
            "primitive", "exotic", "weird", "strange", "inferior",
            "superior", "savage", "tribal" # Add more as needed
        ]
        
        content_lower = cultural_content.lower()
        for term in sensitive_terms:
            if term in content_lower:
                return False
        
        # Must have minimum length for meaningful content
        return len(cultural_content.strip()) >= 50
    
    @staticmethod
    def validate_skill_level_appropriateness(content: Dict, skill_level: str) -> bool:
        """Check if content matches skill level"""
        
        lyrics = content.get("lyrics", "")
        theory_concepts = content.get("educational_content", {}).get("theory_concepts", [])
        
        if skill_level == "beginner":
            # Check for overly complex vocabulary
            complex_terms = ["polyrhythm", "diminished", "augmented", "modulation"]
            return not any(term in lyrics.lower() for term in complex_terms)
        
        elif skill_level == "advanced":
            # Should have more sophisticated concepts
            return len(theory_concepts) >= 3
        
        return True  # Intermediate or other levels pass
```

### 5.2 Testing Framework for Educational Content

```python
import pytest
from typing import Dict

class TestEducationalContent:
    """Test educational content generation and validation"""
    
    @pytest.fixture
    def sample_requests(self):
        return [
            MashupRequest(prompt="Jazz and blues for beginners", skill_level="beginner"),
            MashupRequest(prompt="Hip-hop and country fusion", skill_level="intermediate"),
            MashupRequest(prompt="Classical and electronic blend", skill_level="advanced")
        ]
    
    def test_basic_content_generation(self, sample_requests):
        """Test that basic content is generated for all skill levels"""
        agent = SimplifiedMashupAgent()
        
        for request in sample_requests:
            response = agent.generate_educational_mashup(request)
            
            # Check required fields exist
            assert response.title
            assert response.lyrics
            assert response.educational_content.theory_concepts
            assert response.educational_content.cultural_context
            assert response.educational_content.teaching_notes
            
            # Check minimum content quality
            assert len(response.lyrics.split()) >= 10  # At least 10 words
            assert len(response.educational_content.theory_concepts) >= 2
            assert len(response.educational_content.cultural_context) >= 50
    
    def test_skill_level_appropriateness(self):
        """Test that content matches skill level"""
        validator = EducationalContentValidator()
        
        beginner_content = {
            "lyrics": "Simple rhythm, easy beat, music makes learning neat",
            "educational_content": {
                "theory_concepts": ["rhythm", "beat", "melody"]
            }
        }
        
        advanced_content = {
            "lyrics": "Complex polyrhythmic structures interweave with harmonic progressions",
            "educational_content": {
                "theory_concepts": ["polyrhythm", "harmonic progression", "modulation", "counterpoint"]
            }
        }
        
        assert validator.validate_skill_level_appropriateness(beginner_content, "beginner")
        assert not validator.validate_skill_level_appropriateness(advanced_content, "beginner")
        assert validator.validate_skill_level_appropriateness(advanced_content, "advanced")
    
    def test_cultural_sensitivity(self):
        """Test cultural sensitivity validation"""
        validator = EducationalContentValidator()
        
        good_content = "Jazz emerged from African American communities in New Orleans, representing a rich cultural tradition of musical innovation and expression."
        
        problematic_content = "This primitive music from exotic cultures is strange but interesting."
        
        assert validator.validate_cultural_sensitivity(good_content)
        assert not validator.validate_cultural_sensitivity(problematic_content)
    
    def test_fallback_response(self):
        """Test that fallback responses work"""
        fallback = create_fallback_response(Exception("Test error"))
        
        assert fallback["title"]
        assert fallback["lyrics"]
        assert fallback["educational_content"]["theory_concepts"]
        assert fallback["metadata"]["fallback_used"] is True
```

---

## 6. CI/CD Integration for Prompt Testing

### 6.1 Automated Prompt Testing

```yaml
# .github/workflows/prompt-testing.yml
name: Educational Content Quality Check

on:
  push:
    branches: [ main, develop ]
    paths: 
      - 'agents.py'
      - 'prompts.py'
      - 'test_prompts.py'

jobs:
  test-educational-content:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install pytest ollama pydantic
    
    - name: Test prompt structure
      run: |
        python -c "
        from agents import SimplifiedMashupAgent
        from models import MashupRequest
        
        # Test basic prompt building
        agent = SimplifiedMashupAgent()
        request = MashupRequest(prompt='Test mashup', skill_level='beginner')
        
        # Should not crash
        prompt = agent._build_educational_prompt(request)
        assert len(prompt) > 100
        assert 'educational' in prompt.lower()
        
        print('Prompt structure tests passed')
        "
    
    - name: Test response validation
      run: |
        python -c "
        from agents import parse_and_validate_response, create_fallback_response
        
        # Test valid response parsing
        valid_json = '''
        {
          \"title\": \"Test Title\",
          \"lyrics\": \"Test lyrics here\",
          \"educational_content\": {
            \"theory_concepts\": [\"rhythm\", \"melody\"],
            \"cultural_context\": \"Test cultural context information\",
            \"teaching_notes\": \"Test teaching notes\"
          }
        }
        '''
        
        result = parse_and_validate_response(valid_json)
        assert result['title'] == 'Test Title'
        
        # Test fallback response
        fallback = create_fallback_response(Exception('test'))
        assert fallback['metadata']['fallback_used'] is True
        
        print('Response validation tests passed')
        "
    
    - name: Test educational content validation
      run: |
        pytest test_prompts.py::TestEducationalContent -v
```

### 6.2 Performance Monitoring for Prompts

```python
# performance_monitor.py
import time
import asyncio
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PromptPerformanceMetrics:
    """Track prompt performance metrics"""
    prompt_type: str
    response_time: float
    success_rate: float
    educational_quality_score: float
    token_usage: int

class PromptPerformanceMonitor:
    """Monitor prompt performance in CI/CD"""
    
    def __init__(self):
        self.metrics: List[PromptPerformanceMetrics] = []
    
    async def benchmark_prompt_performance(self, test_requests: List[MashupRequest]) -> Dict:
        """Benchmark prompt performance with test requests"""
        
        agent = SimplifiedMashupAgent()
        results = {
            "total_requests": len(test_requests),
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0,
            "educational_quality_scores": []
        }
        
        total_time = 0
        
        for request in test_requests:
            start_time = time.time()
            
            try:
                # Generate response
                response = await agent.generate_educational_mashup(request)
                
                # Calculate metrics
                response_time = time.time() - start_time
                total_time += response_time
                
                # Validate educational quality
                quality_score = self._assess_educational_quality(response)
                results["educational_quality_scores"].append(quality_score)
                results["successful_requests"] += 1
                
            except Exception as e:
                results["failed_requests"] += 1
                print(f"Request failed: {e}")
        
        # Calculate averages
        if results["successful_requests"] > 0:
            results["average_response_time"] = total_time / results["successful_requests"]
            results["average_quality_score"] = sum(results["educational_quality_scores"]) / len(results["educational_quality_scores"])
        
        return results
    
    def _assess_educational_quality(self, response: MashupResponse) -> float:
        """Assess educational quality of response (0-1 score)"""
        score = 0.0
        
        # Check for educational content completeness
        if response.educational_content.theory_concepts and len(response.educational_content.theory_concepts) >= 2:
            score += 0.3
        
        if response.educational_content.cultural_context and len(response.educational_content.cultural_context) >= 50:
            score += 0.3
        
        if response.educational_content.teaching_notes and len(response.educational_content.teaching_notes) >= 30:
            score += 0.2
        
        # Check lyrics quality
        if response.lyrics and len(response.lyrics.split()) >= 10:
            score += 0.2
        
        return min(score, 1.0)

# Performance test for CI/CD
async def run_performance_tests():
    """Run performance tests for CI/CD pipeline"""
    monitor = PromptPerformanceMonitor()
    
    test_requests = [
        MashupRequest(prompt="Jazz and blues fusion for music class", skill_level="beginner"),
        MashupRequest(prompt="Hip-hop meets classical music", skill_level="intermediate"),
        MashupRequest(prompt="Electronic and folk music blend", skill_level="advanced"),
    ]
    
    results = await monitor.benchmark_prompt_performance(test_requests)
    
    # CI/CD quality gates
    assert results["successful_requests"] >= len(test_requests) * 0.8, "Success rate too low"
    assert results["average_response_time"] < 30, "Response time too slow"
    assert results.get("average_quality_score", 0) >= 0.7, "Educational quality too low"
    
    print("Performance tests passed!")
    print(f"Success rate: {results['successful_requests']}/{results['total_requests']}")
    print(f"Average response time: {results['average_response_time']:.2f}s")
    print(f"Average quality score: {results.get('average_quality_score', 0):.2f}")

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
```

---

## 7. Incremental Complexity Addition

### 7.1 Phase 2: Enhanced Prompts

```python
# Phase 2: Add multiple hook generation
ENHANCED_PROMPT_TEMPLATE = """
{base_educational_prompt}

ADDITIONAL REQUIREMENTS FOR PHASE 2:
- Generate 3 different hook options
- Include genre-specific vocabulary
- Add more detailed cultural context
- Provide teaching activity suggestions

ENHANCED OUTPUT FORMAT:
{{
    "title": "Creative mashup title",
    "lyrics": "Main verse lyrics",
    "hooks": [
        {{"text": "Hook option 1", "style_notes": "Performance guidance"}},
        {{"text": "Hook option 2", "style_notes": "Performance guidance"}},
        {{"text": "Hook option 3", "style_notes": "Performance guidance"}}
    ],
    "educational_content": {{
        "theory_concepts": ["expanded theory concepts"],
        "cultural_context": "Detailed cultural background",
        "teaching_notes": "Expanded teaching guidance",
        "classroom_activities": ["activity 1", "activity 2"]
    }}
}}
"""
```

### 7.2 Phase 3: Advanced Features

```python
# Phase 3: Add collaboration support
COLLABORATION_PROMPT_ADDITION = """
COLLABORATION SUPPORT:
- Include discussion questions for group work
- Suggest roles for different participants
- Provide conflict resolution guidance for creative differences
- Add peer learning opportunities

COLLABORATIVE OUTPUT ADDITION:
"collaboration_guide": {{
    "discussion_questions": ["question 1", "question 2"],
    "participant_roles": ["role 1", "role 2"],
    "group_activities": ["activity 1", "activity 2"]
}}
"""
```

---

## 8. Summary

### 8.1 MVP v2.0 Prompt Strategy

**Simplified Approach**:
- Single comprehensive prompt for all educational content
- Local model optimization (Llama 3.1 8B focus)
- Structured JSON output with validation
- Educational content validation built-in
- Fallback responses for reliability

**Quality Assurance**:
- Automated testing in CI/CD pipeline
- Educational content validation
- Cultural sensitivity checking
- Performance monitoring
- Skill level appropriateness validation

**Incremental Enhancement**:
- Phase-based prompt evolution
- Feature flags for new capabilities
- Backward compatibility maintenance
- Performance benchmarking for each addition

### 8.2 Key Benefits

1. **Reliability**: Fallback responses ensure system always works
2. **Educational Focus**: Every response has educational value
3. **Local Model Optimized**: Works well with privacy-focused deployments
4. **Test-Driven**: Comprehensive testing prevents regression
5. **Scalable**: Easy to add complexity incrementally

This simplified prompt structure ensures the MVP delivers educational value while maintaining reliability and providing a foundation for future enhancements.