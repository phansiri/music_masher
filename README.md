# Lit Music Mashup AI v2.0
## Educational AI Music Generation Platform

An educational AI platform that generates music mashups with comprehensive educational content, including music theory, cultural context, and teaching materials.

### 🎵 Features

- **Conversational AI Interface**: Multi-turn dialogue to gather context and preferences
- **Educational Focus**: Every mashup includes music theory concepts and cultural context
- **Web Search Integration**: Current information gathering via Tavily API
- **Local AI Processing**: Privacy-focused with Ollama and Llama 3.1
- **Cultural Sensitivity**: Respectful representation of musical traditions
- **Skill Level Adaptation**: Content tailored for beginner, intermediate, and advanced learners

### 🚀 Quick Start

#### Prerequisites
- Python 3.11+
- UV package manager
- Ollama (for local AI processing)
- Tavily API key (optional, for web search)

#### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd music_masher_ai
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Tavily API key (optional)
   ```

3. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ollama pull llama3.1:8b-instruct
   ```

4. **Run the application**:
   ```bash
   uv run fastapi run app/main.py --reload
   ```

5. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### 📚 API Usage

#### Conversational Interface
```bash
# Start a conversation
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to create a mashup for my high school music class",
    "session_id": "optional-session-id"
  }'
```

#### Direct Generation
```bash
# Generate educational mashup
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a jazz and hip-hop mashup for intermediate students",
    "skill_level": "intermediate"
  }'
```

### 🏗️ Project Structure

```
music_masher_ai/
├── app/
│   ├── api/          # FastAPI endpoints
│   ├── agents/       # Conversational AI agents
│   ├── db/           # Database operations
│   ├── services/     # Business logic services
│   └── utils/        # Utility functions
├── tests/            # Test suite
├── data/             # Database files
├── Docs/             # Documentation
└── .github/          # CI/CD workflows
```

### 🧪 Development

#### Running Tests
```bash
uv run pytest
```

#### Code Quality
```bash
uv run ruff check .
uv run mypy app/
```

#### Docker Development
```bash
docker-compose up --build
```

### 📖 Documentation

- [Product Requirements (PRD)](Docs/v2/prd-v2-1.md)
- [Prompt Structure](Docs/v2/prompt-structure-v2-1.md)
- [Implementation Guide](Docs/v2/implementation-documentation-v2-2.md)
- [Task Management](Docs/v2/task.md)

### 🤝 Contributing

1. Follow the task-based development approach
2. Ensure all tests pass
3. Maintain code quality standards
4. Update documentation as needed

### 📄 License

MIT License - see LICENSE file for details.

### 🆘 Support

For issues and questions:
- Check the documentation in `Docs/v2/`
- Review the task management in `Docs/v2/task.md`
- Create an issue with detailed information
