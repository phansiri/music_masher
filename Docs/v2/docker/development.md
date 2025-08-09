# Development Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the Lit Music Mashup AI platform for development using Docker.

## 🎯 Prerequisites

### System Requirements

- **Docker Engine**: 20.10+ with Docker Compose 2.0+
- **Operating System**: macOS, Linux, or Windows (WSL2)
- **Hardware**: Minimum 8GB RAM, 4 CPU cores (recommended)
- **Storage**: 10GB+ available disk space
- **Network**: Stable internet connection for model downloads

### Software Dependencies

- Docker Engine and Docker Compose
- Git (for version control)
- VS Code or preferred IDE
- curl (for testing)
- jq (for JSON processing)

### Development Tools

- **Code Editor**: VS Code with Python extensions
- **Terminal**: iTerm2 (macOS), Windows Terminal (Windows)
- **Version Control**: Git
- **API Testing**: Postman, Insomnia, or curl

## 🚀 Quick Start

### Step 1: Environment Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd music_masher_ai
   ```

2. **Create Development Environment**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit environment variables
   nano .env
   ```

3. **Configure Environment Variables**
   ```bash
   # Development configuration
   ENVIRONMENT=development
   LOG_LEVEL=DEBUG
   DATABASE_PATH=/app/data/conversations.db
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OLLAMA_MODEL=llama3.1:8b-instruct
   
   # Optional: Web search API key
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Step 2: Start Development Environment

1. **Start with Host Ollama** (Recommended)
   ```bash
   # Start development environment using host's Ollama
   ./scripts/docker/build.sh run-dev
   ```

2. **Start with Ollama Container**
   ```bash
   # Start development environment with Ollama container
   ./scripts/docker/build.sh run-dev-ollama
   ```

3. **Verify Setup**
   ```bash
   # Check container status
   docker ps
   
   # Check application health
   curl -f http://localhost:8000/health
   
   # Check Ollama status
   curl -f http://localhost:11434/api/tags
   ```

## 🔧 Development Workflow

### Hot Reloading

The development environment includes hot reloading for instant code changes:

```bash
# Code changes are automatically detected and reloaded
# No need to restart containers for most changes
```

### Source Code Mounting

The development configuration mounts the source code for live development:

```yaml
volumes:
  - .:/app  # Mount source code for development
  - ./data:/app/data
  - ./.env:/app/.env:ro
```

### Debugging

1. **Logs**
   ```bash
   # View application logs
   docker-compose -f docker-compose.dev.yml logs -f app
   
   # View Ollama logs (if using container)
   docker-compose -f docker-compose.dev-with-ollama.yml logs -f ollama
   ```

2. **Debug Mode**
   ```bash
   # Enable debug logging
   LOG_LEVEL=DEBUG
   ```

3. **Interactive Shell**
   ```bash
   # Access container shell
   docker exec -it music_masher_ai-app-1 bash
   ```

## 🛠️ Development Tools

### IDE Configuration

#### VS Code Setup

1. **Install Extensions**
   - Python
   - Docker
   - Python Test Explorer
   - GitLens

2. **Workspace Settings**
   ```json
   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": false,
     "python.linting.flake8Enabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true
   }
   ```

3. **Debug Configuration**
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "program": "${workspaceFolder}/app/main.py",
         "console": "integratedTerminal",
         "env": {
           "ENVIRONMENT": "development",
           "LOG_LEVEL": "DEBUG"
         }
       }
     ]
   }
   ```

### Testing

1. **Run Tests**
   ```bash
   # Run all tests
   docker exec -it music_masher_ai-app-1 pytest
   
   # Run specific test file
   docker exec -it music_masher_ai-app-1 pytest tests/test_conversation_agent.py
   
   # Run with coverage
   docker exec -it music_masher_ai-app-1 pytest --cov=app
   ```

2. **Test Development**
   ```bash
   # Run tests in development mode
   docker exec -it music_masher_ai-app-1 pytest -v
   
   # Run integration tests
   docker exec -it music_masher_ai-app-1 pytest tests/integration/
   ```

### Code Quality

1. **Linting**
   ```bash
   # Run ruff linter
   docker exec -it music_masher_ai-app-1 ruff check .
   
   # Fix issues automatically
   docker exec -it music_masher_ai-app-1 ruff check --fix .
   ```

2. **Type Checking**
   ```bash
   # Run mypy type checking
   docker exec -it music_masher_ai-app-1 mypy app/
   ```

3. **Formatting**
   ```bash
   # Format code with black
   docker exec -it music_masher_ai-app-1 black .
   
   # Sort imports
   docker exec -it music_masher_ai-app-1 ruff check --fix --select I .
   ```

## 📊 Development Monitoring

### Health Checks

1. **Application Health**
   ```bash
   # Check application health
   curl -f http://localhost:8000/health
   
   # Expected response
   {
     "status": "healthy",
     "timestamp": "2024-12-19T10:30:00Z",
     "version": "0.1.0"
   }
   ```

2. **Ollama Health**
   ```bash
   # Check Ollama health
   curl -f http://localhost:11434/api/tags
   
   # Expected response
   {
     "models": [
       {
         "name": "llama3.1:8b-instruct",
         "modified_at": "2024-12-19T10:30:00Z",
         "size": 4567890123
       }
     ]
   }
   ```

### Logging

1. **Application Logs**
   ```bash
   # View application logs
   docker-compose -f docker-compose.dev.yml logs -f app
   
   # Filter logs by level
   docker-compose -f docker-compose.dev.yml logs -f app | grep "DEBUG"
   ```

2. **Ollama Logs**
   ```bash
   # View Ollama logs (if using container)
   docker-compose -f docker-compose.dev-with-ollama.yml logs -f ollama
   ```

## 🔄 Development Workflow

### Daily Development

1. **Start Development Environment**
   ```bash
   # Start with host Ollama
   ./scripts/docker/build.sh run-dev
   
   # Or start with Ollama container
   ./scripts/docker/build.sh run-dev-ollama
   ```

2. **Make Code Changes**
   - Edit code in your IDE
   - Changes are automatically reloaded
   - Test changes immediately

3. **Run Tests**
   ```bash
   # Run tests after changes
   docker exec -it music_masher_ai-app-1 pytest
   ```

4. **Commit Changes**
   ```bash
   # Stage changes
   git add .
   
   # Commit with meaningful message
   git commit -m "feat: add new conversation feature"
   
   # Push to remote
   git push origin main
   ```

### Feature Development

1. **Create Feature Branch**
   ```bash
   # Create and switch to feature branch
   git checkout -b feature/new-feature
   ```

2. **Develop Feature**
   - Implement feature
   - Write tests
   - Update documentation

3. **Test Feature**
   ```bash
   # Run all tests
   docker exec -it music_masher_ai-app-1 pytest
   
   # Run specific feature tests
   docker exec -it music_masher_ai-app-1 pytest tests/test_new_feature.py
   ```

4. **Create Pull Request**
   - Push feature branch
   - Create pull request
   - Request code review

## 🐛 Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.dev.yml logs app
   
   # Check resource usage
   docker stats
   
   # Check disk space
   df -h
   ```

2. **Hot Reloading Not Working**
   ```bash
   # Check volume mounts
   docker exec -it music_masher_ai-app-1 ls -la /app
   
   # Restart containers
   ./scripts/docker/build.sh stop
   ./scripts/docker/build.sh run-dev
   ```

3. **Ollama Connection Issues**
   ```bash
   # Check Ollama status
   curl -v http://localhost:11434/api/tags
   
   # Check network connectivity
   docker exec -it music_masher_ai-app-1 ping host.docker.internal
   ```

4. **Performance Issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Check memory usage
   free -h
   
   # Check CPU usage
   top
   ```

### Debugging Tips

1. **Container Access**
   ```bash
   # Access container shell
   docker exec -it music_masher_ai-app-1 bash
   
   # Check environment variables
   docker exec -it music_masher_ai-app-1 env
   ```

2. **File System**
   ```bash
   # Check mounted volumes
   docker exec -it music_masher_ai-app-1 df -h
   
   # Check file permissions
   docker exec -it music_masher_ai-app-1 ls -la /app
   ```

3. **Network**
   ```bash
   # Check network connectivity
   docker exec -it music_masher_ai-app-1 ping google.com
   
   # Check port availability
   docker exec -it music_masher_ai-app-1 netstat -tulpn
   ```

## 📚 Development Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Documentation](https://docs.python.org/3/)
- [UV Documentation](https://docs.astral.sh/uv/)

### Tools

- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### Community

- [FastAPI Community](https://github.com/tiangolo/fastapi)
- [Docker Community](https://www.docker.com/community/)
- [Python Community](https://www.python.org/community/)

## 🔄 Development Best Practices

### Code Quality

1. **Follow PEP 8**
   - Use consistent formatting
   - Follow naming conventions
   - Write docstrings

2. **Type Hints**
   - Use type hints for all functions
   - Use mypy for type checking
   - Document complex types

3. **Testing**
   - Write unit tests for all functions
   - Write integration tests for APIs
   - Maintain high test coverage

### Git Workflow

1. **Branch Naming**
   - `feature/feature-name` for new features
   - `bugfix/bug-description` for bug fixes
   - `hotfix/urgent-fix` for urgent fixes

2. **Commit Messages**
   - Use conventional commit format
   - Write descriptive messages
   - Reference issues when applicable

3. **Pull Requests**
   - Write descriptive PR descriptions
   - Include tests and documentation
   - Request code reviews

### Documentation

1. **Code Documentation**
   - Write docstrings for all functions
   - Document complex algorithms
   - Include examples

2. **API Documentation**
   - Document all endpoints
   - Include request/response examples
   - Update OpenAPI specification

3. **User Documentation**
   - Write user guides
   - Include troubleshooting sections
   - Keep documentation updated

## 📞 Support

### Development Support

- **Technical Questions**: dev-support@litmusicmashup.com
- **Code Reviews**: GitHub Pull Requests
- **Documentation**: GitHub Wiki

### Community

- **Discord**: [Lit Music Mashup Community](https://discord.gg/litmusicmashup)
- **GitHub**: [Issues and Discussions](https://github.com/your-org/music_masher_ai)
- **Email**: community@litmusicmashup.com

---

## 📋 Development Checklist

### Initial Setup

- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Docker containers running
- [ ] Health checks passing
- [ ] IDE configured
- [ ] Development tools installed
- [ ] Documentation reviewed

### Daily Development

- [ ] Development environment started
- [ ] Code changes tested
- [ ] Tests passing
- [ ] Code quality checks passed
- [ ] Documentation updated
- [ ] Changes committed
- [ ] Pull request created (if applicable)

### Feature Development

- [ ] Feature branch created
- [ ] Feature implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Feature merged
- [ ] Branch deleted

---

*Last updated: December 2024*
