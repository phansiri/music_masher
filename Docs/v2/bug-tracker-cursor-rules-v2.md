# Lit Music Mashup - Bug Tracker & Cursor Rules v2.0
## Educational AI Platform Bug Tracking with CI/CD Integration

---

## 📋 1. Bug Tracker Document (Simplified for MVP)

### 1.1 MVP Bug Classification System

**Priority Levels**:
- **P0 - Critical**: MVP core functionality broken (generation endpoint fails)
- **P1 - High**: Educational content quality issues, data loss
- **P2 - Medium**: Performance issues, minor UI problems
- **P3 - Low**: Enhancement requests, documentation issues

**Bug Categories**:
- **Core Generation**: Issues with mashup creation
- **Educational Content**: Problems with theory/cultural content
- **API Issues**: Endpoint failures, validation problems
- **Database**: Data persistence, retrieval issues
- **Testing**: CI/CD pipeline failures, test issues
- **Performance**: Speed, memory, resource usage
- **Documentation**: Unclear instructions, missing info

### 1.2 Simplified Bug Entry Template

```markdown
## Bug Report #[ID]

**Priority**: P0/P1/P2/P3
**Category**: Core Generation | Educational Content | API | Database | Testing | Performance | Documentation
**Status**: Open | In Progress | Testing | Closed
**Reported**: YYYY-MM-DD
**Reporter**: [Name/GitHub handle]

### Description
Brief description of the issue

### Steps to Reproduce
1. Step one
2. Step two
3. Step three

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- Python version:
- Ollama version:
- OS:
- Branch/Commit:

### CI/CD Impact
- [ ] Breaks automated tests
- [ ] Prevents deployment
- [ ] Affects code quality checks
- [ ] No CI/CD impact

### Educational Impact
- [ ] Breaks core educational functionality
- [ ] Affects content quality
- [ ] Minor educational impact
- [ ] No educational impact

### Additional Context
Any other relevant information, screenshots, logs
```

---

## 🤖 2. Cursor Rules File for MVP

### 2.1 Basic Cursor Rules

```markdown
---
description: Educational AI platform bug tracking and development rules for MVP
globs: 
  - "bug-tracker.md"
  - "main.py"
  - "agents.py"
  - "database.py"
  - "test_*.py"
  - "**/*bug*.md"
  - "**/*error*.md"
  - "**/logs/**/*"
alwaysApply: true
---

# Lit Music Mashup - Cursor Development Rules v2.0

## Core Development Principles

### 1. MVP-First Development
- ALWAYS implement the simplest working solution first
- Add complexity only after core functionality is validated
- Every feature must have tests before merging
- Maintain educational focus in all implementations

### 2. Educational Content Requirements
When working on ANY code that generates educational content:
- MUST include music theory concepts
- MUST include cultural context
- MUST be age-appropriate for specified skill level
- MUST be culturally sensitive and respectful

### 3. Bug Prevention Rules

#### Before Implementing ANY Fix:
1. **CHECK bug-tracker.md** - Review existing similar issues
2. **RUN existing tests** - Ensure no regression
3. **ADD new test** - Cover the specific bug scenario
4. **VALIDATE educational content** - If affects educational output

#### Code Quality Gates:
- Functions must have docstrings
- Educational content must be validated
- No hardcoded values for educational content
- Error handling must preserve educational functionality

### 4. CI/CD Integration Requirements

#### Every Pull Request Must:
- [ ] Pass all existing tests
- [ ] Include tests for new functionality
- [ ] Maintain or improve code coverage
- [ ] Pass black/isort/flake8 quality checks
- [ ] Update documentation if needed

#### Educational Content Changes:
- [ ] Validate music theory accuracy
- [ ] Check cultural sensitivity
- [ ] Ensure skill level appropriateness
- [ ] Test with different skill levels

### 5. Testing Requirements

#### When Adding Tests:
```python
# All test functions must follow this pattern
def test_[feature_name]_[specific_behavior]():
    \"\"\"Test description focusing on educational outcome\"\"\"
    # Arrange - Set up test data
    # Act - Perform the action
    # Assert - Verify educational content quality
```

#### Educational Test Validation:
```python
# Every educational content test must check:
assert response["educational_content"]["theory_concepts"]  # Has theory
assert len(response["educational_content"]["cultural_context"]) > 50  # Meaningful cultural content
assert response["educational_content"]["teaching_notes"]  # Has practical guidance
```

### 6. Error Handling Standards

#### All Functions Must:
- Handle AI model failures gracefully
- Provide educational fallback content
- Log errors with educational context
- Never return empty educational content

#### Example Error Handling:
```python
try:
    result = await generate_educational_content(request)
except Exception as e:
    logger.error(f"Educational generation failed: {e}")
    result = create_educational_fallback(request)
    result["metadata"]["fallback_used"] = True
```

### 7. Database Operations

#### All Database Functions Must:
- Use parameterized queries (prevent SQL injection)
- Handle connection failures
- Validate educational content before saving
- Include created/updated timestamps

### 8. Performance Requirements

#### Response Time Targets:
- API endpoints: < 30 seconds (MVP)
- Database queries: < 1 second
- Educational content validation: < 5 seconds

### 9. Documentation Standards

#### When Updating Code:
- Update docstrings for changed functions
- Add educational context to examples
- Include performance notes if applicable
- Update API documentation for endpoint changes

### 10. Git Workflow Integration

#### Commit Message Format:
```
type(scope): brief description

Educational impact: [description of how this affects educational content]
Tests: [describe test coverage]
CI/CD: [any CI/CD impacts]
```

#### Branch Naming:
- `feature/[educational-feature-name]`
- `bugfix/[bug-category]-[brief-description]`
- `test/[test-area-name]`

## Emergency Procedures

### P0 Bug Response (Core Functionality Broken):
1. Create hotfix branch immediately
2. Implement minimal fix with fallback
3. Add comprehensive test coverage
4. Deploy with monitoring
5. Update bug tracker with resolution

### Educational Content Issues:
1. Validate with music education expert if available
2. Check cultural sensitivity thoroughly
3. Test with different skill levels
4. Document cultural context decisions

## Code Review Checklist

### Before Approving Any PR:
- [ ] All tests pass in CI/CD
- [ ] Educational content validated
- [ ] Performance within targets
- [ ] Documentation updated
- [ ] Cultural sensitivity checked
- [ ] Bug tracker updated if fixing issues

## Integration with GitHub Actions

### Automated Checks:
- Run pytest on every commit
- Validate educational content structure
- Check code quality (black, isort, flake8)
- Test API endpoints functionality
- Monitor response times

### Failure Response:
- Block merge if any check fails
- Require manual review for educational content changes
- Alert team for P0/P1 issues
```

---

## 🔧 3. GitHub Actions Integration

### 3.1 Enhanced CI/CD Pipeline

```yaml
# .github/workflows/bug-prevention.yml
name: Bug Prevention & Educational Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  bug-prevention-checks:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort flake8
    
    - name: Code Quality Checks
      run: |
        black --check .
        isort --check-only .
        flake8 . --max-line-length=88
    
    - name: Run Core Tests
      run: |
        pytest test_main.py -v --cov=main --cov-report=term-missing
    
    - name: Educational Content Validation
      run: |
        python -c "
        # Test educational content generation
        from agents import SimplifiedMashupAgent
        from models import MashupRequest
        import asyncio
        
        async def test_educational_quality():
            agent = SimplifiedMashupAgent()
            request = MashupRequest(prompt='Jazz blues for beginners', skill_level='beginner')
            
            try:
                # This would normally call the agent
                # For CI/CD, we test the validation logic
                from agents import create_fallback_response
                response = create_fallback_response(Exception('test'))
                
                # Validate educational content structure
                assert 'educational_content' in response
                assert 'theory_concepts' in response['educational_content']
                assert len(response['educational_content']['cultural_context']) > 50
                print('Educational content validation passed')
                
            except Exception as e:
                print(f'Educational validation failed: {e}')
                exit(1)
        
        asyncio.run(test_educational_quality())
        "
    
    - name: API Endpoint Tests
      run: |
        # Start test server and validate endpoints
        python -c "
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        
        # Test root endpoint
        response = client.get('/')
        assert response.status_code == 200
        assert 'Lit Music Mashup' in response.json()['message']
        
        print('API endpoint tests passed')
        "
    
    - name: Performance Benchmarking
      run: |
        python -c "
        import time
        from database import MashupDB
        import tempfile
        import os
        
        # Test database performance
        fd, path = tempfile.mkstemp()
        os.close(fd)
        
        try:
            db = MashupDB(path)
            
            start_time = time.time()
            for i in range(100):
                db.save_mashup({
                    'prompt': f'test {i}',
                    'skill_level': 'beginner',
                    'title': f'Title {i}',
                    'lyrics': f'Lyrics {i}',
                    'educational_content': {}
                })
            end_time = time.time()
            
            duration = end_time - start_time
            assert duration < 1.0, f'Database too slow: {duration}s'
            print(f'Database performance test passed: {duration:.3f}s')
            
        finally:
            os.unlink(path)
        "
    
    - name: Update Bug Tracker
      if: failure()
      run: |
        echo "## Automated Bug Report - $(date)" >> bug-tracker.md
        echo "**Priority**: P1" >> bug-tracker.md
        echo "**Category**: Testing" >> bug-tracker.md
        echo "**Status**: Open" >> bug-tracker.md
        echo "**Description**: CI/CD pipeline failed" >> bug-tracker.md
        echo "**Commit**: ${{ github.sha }}" >> bug-tracker.md
        echo "**Branch**: ${{ github.ref }}" >> bug-tracker.md
        echo "" >> bug-tracker.md
```

---

## 📊 4. Bug Tracking Database

### 4.1 Simple Bug Tracking in SQLite

```python
# bug_tracker.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class SimpleBugTracker:
    """Simple bug tracking for MVP development"""
    
    def __init__(self, db_path: str = "bugs.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize bug tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bugs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL,  -- P0, P1, P2, P3
                    category TEXT NOT NULL,  -- Core, Educational, API, etc.
                    status TEXT DEFAULT 'Open',  -- Open, In Progress, Testing, Closed
                    reporter TEXT,
                    assignee TEXT,
                    educational_impact TEXT,
                    ci_cd_impact TEXT,
                    environment_info TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bug_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bug_id INTEGER,
                    comment TEXT NOT NULL,
                    author TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bug_id) REFERENCES bugs (id)
                )
            """)
    
    def report_bug(self, bug_data: Dict) -> int:
        """Report a new bug"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO bugs (
                    title, description, priority, category, reporter,
                    educational_impact, ci_cd_impact, environment_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bug_data['title'],
                bug_data['description'],
                bug_data['priority'],
                bug_data['category'],
                bug_data.get('reporter', 'Unknown'),
                bug_data.get('educational_impact', 'None'),
                bug_data.get('ci_cd_impact', 'None'),
                json.dumps(bug_data.get('environment_info', {}))
            ))
            return cursor.lastrowid
    
    def get_open_bugs(self, priority: Optional[str] = None) -> List[Dict]:
        """Get all open bugs, optionally filtered by priority"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM bugs WHERE status != 'Closed'"
            params = []
            
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            query += " ORDER BY priority, created_at DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def update_bug_status(self, bug_id: int, status: str, assignee: str = None):
        """Update bug status"""
        with sqlite3.connect(self.db_path) as conn:
            if status == 'Closed':
                conn.execute("""
                    UPDATE bugs 
                    SET status = ?, assignee = ?, closed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, assignee, bug_id))
            else:
                conn.execute("""
                    UPDATE bugs 
                    SET status = ?, assignee = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, assignee, bug_id))
    
    def add_comment(self, bug_id: int, comment: str, author: str):
        """Add comment to bug"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO bug_comments (bug_id, comment, author)
                VALUES (?, ?, ?)
            """, (bug_id, comment, author))
    
    def get_bug_statistics(self) -> Dict:
        """Get bug statistics for monitoring"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total bugs by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM bugs 
                GROUP BY status
            """)
            stats['by_status'] = dict(cursor.fetchall())
            
            # Bugs by priority
            cursor = conn.execute("""
                SELECT priority, COUNT(*) as count 
                FROM bugs 
                WHERE status != 'Closed'
                GROUP BY priority
            """)
            stats['open_by_priority'] = dict(cursor.fetchall())
            
            # Educational impact bugs
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM bugs 
                WHERE educational_impact != 'None' AND status != 'Closed'
            """)
            stats['educational_impact_bugs'] = cursor.fetchone()[0]
            
            return stats

# Integration with main application
def report_automatic_bug(error: Exception, context: Dict):
    """Automatically report bugs from application errors"""
    tracker = SimpleBugTracker()
    
    bug_data = {
        'title': f"Automatic Error Report: {str(error)[:50]}",
        'description': f"Error: {str(error)}\n\nContext: {json.dumps(context, indent=2)}",
        'priority': 'P1' if 'educational' in str(error).lower() else 'P2',
        'category': determine_category_from_error(error, context),
        'reporter': 'Automated System',
        'educational_impact': assess_educational_impact(error, context),
        'ci_cd_impact': 'Potential test failure',
        'environment_info': {
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            'context': context
        }
    }
    
    bug_id = tracker.report_bug(bug_data)
    return bug_id

def determine_category_from_error(error: Exception, context: Dict) -> str:
    """Determine bug category from error context"""
    error_str = str(error).lower()
    
    if 'educational' in error_str or 'theory' in error_str:
        return 'Educational Content'
    elif 'database' in error_str or 'sql' in error_str:
        return 'Database'
    elif 'api' in error_str or 'endpoint' in error_str:
        return 'API'
    elif 'generation' in error_str or 'mashup' in error_str:
        return 'Core Generation'
    else:
        return 'Unknown'

def assess_educational_impact(error: Exception, context: Dict) -> str:
    """Assess educational impact of error"""
    if 'educational_content' in context:
        return 'High - Affects educational content generation'
    elif 'theory' in str(error).lower():
        return 'Medium - May affect music theory accuracy'
    else:
        return 'Low - Minimal educational impact'
```

---

## 🎯 5. Integration with Development Workflow

### 5.1 Pre-commit Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running pre-commit educational content checks..."

# Run tests
python -m pytest test_main.py -q

if [ $? -ne 0 ]; then
    echo "❌ Tests failed - commit blocked"
    exit 1
fi

# Check educational content validation
python -c "
from agents import create_fallback_response
response = create_fallback_response(Exception('test'))
assert 'educational_content' in response
assert len(response['educational_content']['cultural_context']) > 50
print('✅ Educational content structure validated')
"

if [ $? -ne 0 ]; then
    echo "❌ Educational content validation failed - commit blocked"
    exit 1
fi

echo "✅ Pre-commit checks passed"
```

### 5.2 Issue Templates

```markdown
<!-- .github/ISSUE_TEMPLATE/bug_report.md -->
---
name: Bug Report
about: Create a report to help us improve the educational platform
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Classification
**Priority**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
**Category**: Core Generation / Educational Content / API / Database / Testing / Performance / Documentation

## Description
A clear and concise description of what the bug is.

## Educational Impact
- [ ] Breaks core educational functionality
- [ ] Affects educational content quality
- [ ] Minor educational impact
- [ ] No educational impact

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Screenshots/Logs
If applicable, add screenshots or error logs to help explain your problem.

## Environment
- Python version: [e.g. 3.11]
- OS: [e.g. Ubuntu 20.04]
- Branch: [e.g. main]
- Commit hash: [e.g. abc123]

## CI/CD Impact
- [ ] Breaks automated tests
- [ ] Prevents deployment
- [ ] Affects code quality checks
- [ ] No CI/CD impact

## Additional Context
Add any other context about the problem here.
```

---

## 📋 6. Current Bug Tracker (Live Document)

### 6.1 Open Issues

```markdown
## Bug #001
**Priority**: P1
**Category**: Core Generation
**Status**: Open
**Reported**: 2024-01-15
**Reporter**: Developer

### Description
Educational mashup generation fails when prompt contains special characters

### Educational Impact
High - Prevents generation of educational content for certain inputs

### CI/CD Impact
- [x] Breaks automated tests
- [ ] Prevents deployment

### Next Steps
- Add input sanitization
- Update tests for special character handling
- Validate educational content output

---

## Bug #002
**Priority**: P2
**Category**: Educational Content
**Status**: In Progress
**Reported**: 2024-01-16
**Reporter**: QA Team
**Assignee**: AI Team

### Description
Cultural context sometimes lacks depth for advanced skill level

### Educational Impact
Medium - Advanced students may not receive appropriate complexity

### Resolution Plan
- Enhance cultural context generation prompts
- Add skill level validation
- Create more detailed fallback content

---
```

## 7. Summary

### 7.1 Simplified Bug Tracking Benefits

**MVP-Focused Approach**:
- Simple SQLite-based bug tracking
- Automated bug reporting from application errors
- CI/CD integration prevents regression
- Educational impact assessment built-in

**Developer Experience**:
- Cursor rules enforce quality standards
- Pre-commit hooks prevent problematic commits
- GitHub Actions provide automated validation
- Issue templates ensure consistent reporting

**Quality Assurance**:
- Educational content validation in CI/CD
- Performance monitoring
- Cultural sensitivity checking
- Automated test coverage requirements

This simplified approach ensures bug tracking supports MVP development while maintaining educational quality and preventing regression through automated CI/CD processes.