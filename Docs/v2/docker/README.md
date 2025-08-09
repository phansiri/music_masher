# Docker Configuration Guide

## Overview

This guide explains how to use Docker with the Lit Music Mashup AI platform, including the new Ollama configuration options.

## 🎯 Key Features

- **Host Ollama Integration**: Default configuration uses your host's Ollama installation
- **Optional Ollama Container**: Can run Ollama as a container when needed
- **Multi-environment Support**: Development and production configurations
- **Resource Optimization**: No duplication of Ollama when using host installation
- **Flexible Deployment**: Easy switching between host and container Ollama

## 🏗️ Architecture

### Default Configuration (Host Ollama)
```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Docker App    │    │   Host Ollama   │                │
│  │   Container     │    │   Installation  │                │
│  │   - FastAPI     │    │   - AI Models   │                │
│  │   - UV Runtime  │    │   - Model Mgmt  │                │
│  │   - Port 8000   │    │   - Port 11434  │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────────────────┘                        │
│           host.docker.internal:11434                       │
└─────────────────────────────────────────────────────────────┘
```

### Optional Configuration (Container Ollama)
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Environment                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   App Container │    │  Ollama Container│                │
│  │   - FastAPI     │    │   - AI Models   │                │
│  │   - UV Runtime  │    │   - Model Mgmt  │                │
│  │   - Port 8000   │    │   - Port 11434  │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────────────────┘                        │
│                    ollama:11434                            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Docker and Docker Compose** installed
2. **Ollama** installed on your host machine (for default configuration)
3. **Git** for cloning the repository

### Option 1: Using Host's Ollama (Recommended)

This is the default and recommended approach. It uses your existing Ollama installation and avoids resource duplication.

```bash
# Clone the repository
git clone <repository-url>
cd music_masher_ai

# Copy environment configuration
cp env.example .env

# Start development environment (uses host's Ollama)
./scripts/docker/build.sh run-dev

# Or start production environment
./scripts/docker/build.sh run-prod
```

### Option 2: Using Ollama Container

Use this option if you want to run Ollama as a container or don't have Ollama installed on your host.

```bash
# Start development environment with Ollama container
./scripts/docker/build.sh run-dev-ollama

# Or start production environment with Ollama container
./scripts/docker/build.sh run-prod-ollama
```

## 📁 File Structure

```
music_masher_ai/
├── Dockerfile                    # Original (backward compatibility)
├── Dockerfile.prod              # Production multi-stage build
├── Dockerfile.dev               # Development build
├── docker-compose.yml           # Default (uses host Ollama)
├── docker-compose.dev.yml       # Development (uses host Ollama)
├── docker-compose.prod.yml      # Production (uses host Ollama)
├── docker-compose.with-ollama.yml           # Default with Ollama container
├── docker-compose.dev-with-ollama.yml       # Development with Ollama container
├── docker-compose.prod-with-ollama.yml      # Production with Ollama container
├── .dockerignore                # Optimized build context
├── env.example                  # Environment configuration
├── env.production.example       # Production environment template
└── scripts/
    └── docker/
        └── build.sh             # Docker utility script
```

## 🔧 Configuration Options

### Environment Variables

#### Ollama Configuration
```bash
# Default: Use host's Ollama installation
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Alternative: Use Ollama container
OLLAMA_BASE_URL=http://ollama:11434
```

#### Application Configuration
```bash
# Environment
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO          # or DEBUG

# Database
DATABASE_PATH=/app/data/conversations.db

# AI Model
OLLAMA_MODEL=llama3.1:8b-instruct
```

## 🛠️ Available Commands

### Build Commands
```bash
# Build development image
./scripts/docker/build.sh build-dev

# Build production image
./scripts/docker/build.sh build-prod
```

### Run Commands
```bash
# Development (host Ollama)
./scripts/docker/build.sh run-dev

# Development (Ollama container)
./scripts/docker/build.sh run-dev-ollama

# Production (host Ollama)
./scripts/docker/build.sh run-prod

# Production (Ollama container)
./scripts/docker/build.sh run-prod-ollama
```

### Management Commands
```bash
# Stop all containers
./scripts/docker/build.sh stop

# Show logs
./scripts/docker/build.sh logs

# Clean up resources
./scripts/docker/build.sh clean

# Show help
./scripts/docker/build.sh help
```

## 🔄 Switching Between Configurations

### From Host Ollama to Container Ollama

1. **Stop current containers**:
   ```bash
   ./scripts/docker/build.sh stop
   ```

2. **Start with Ollama container**:
   ```bash
   # For development
   ./scripts/docker/build.sh run-dev-ollama
   
   # For production
   ./scripts/docker/build.sh run-prod-ollama
   ```

### From Container Ollama to Host Ollama

1. **Stop current containers**:
   ```bash
   ./scripts/docker/build.sh stop
   ```

2. **Ensure Ollama is running on host**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   ```

3. **Start with host Ollama**:
   ```bash
   # For development
   ./scripts/docker/build.sh run-dev
   
   # For production
   ./scripts/docker/build.sh run-prod
   ```

## 🔍 Troubleshooting

### Common Issues

#### 1. Ollama Connection Issues

**Problem**: App can't connect to Ollama
```bash
# Check if Ollama is running on host
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

**Solution**: Ensure Ollama is running on your host machine before starting the Docker containers.

#### 2. Port Conflicts

**Problem**: Port 8000 or 11434 already in use
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :11434

# Stop conflicting services or change ports in docker-compose files
```

#### 3. Permission Issues

**Problem**: Permission denied when accessing volumes
```bash
# Fix permissions
sudo chown -R $USER:$USER ./data
```

### Debug Commands

```bash
# Check container status
docker ps

# View container logs
docker-compose -f docker-compose.dev.yml logs

# Check Ollama connectivity
docker exec -it <container_name> curl http://host.docker.internal:11434/api/tags
```

## 📊 Performance Considerations

### Host Ollama (Recommended)
- ✅ **Lower resource usage** - No duplication of Ollama
- ✅ **Faster startup** - No need to download/start Ollama container
- ✅ **Shared models** - Models available to both host and containers
- ✅ **Better performance** - Direct access to host resources

### Container Ollama
- ✅ **Isolated environment** - Complete containerization
- ✅ **Consistent environment** - Same Ollama version across deployments
- ✅ **Easy deployment** - Self-contained setup
- ❌ **Higher resource usage** - Duplicates Ollama installation
- ❌ **Slower startup** - Needs to download/start Ollama container

## 🔒 Security Considerations

### Host Ollama
- **Network access**: Uses `host.docker.internal` for cross-platform compatibility
- **File permissions**: Respects host file permissions
- **Resource sharing**: Shares host resources

### Container Ollama
- **Network isolation**: Runs in separate container network
- **Resource limits**: Can be configured with Docker resource limits
- **Volume isolation**: Uses Docker volumes for model storage

## 📝 Best Practices

1. **Use host Ollama by default** - Saves resources and provides better performance
2. **Use container Ollama for deployment** - Ensures consistent environment
3. **Monitor resource usage** - Check Docker stats regularly
4. **Backup models** - Regularly backup Ollama models
5. **Update regularly** - Keep Docker images and Ollama updated

## 🤝 Contributing

When contributing to Docker configurations:

1. **Test both configurations** - Host and container Ollama
2. **Update documentation** - Keep this README current
3. **Follow naming conventions** - Use consistent file naming
4. **Add tests** - Include Docker tests in CI/CD pipeline

## 📞 Support

For issues related to Docker configuration:

1. Check the troubleshooting section above
2. Review the logs using `./scripts/docker/build.sh logs`
3. Ensure Ollama is running and accessible
4. Check Docker and Docker Compose versions
5. Create an issue with detailed error information
