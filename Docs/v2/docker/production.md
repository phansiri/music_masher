# Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Lit Music Mashup AI platform to production environments using Docker.

## 🎯 Prerequisites

### System Requirements

- **Docker Engine**: 20.10+ with Docker Compose 2.0+
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Hardware**: Minimum 4GB RAM, 2 CPU cores
- **Storage**: 20GB+ available disk space
- **Network**: Stable internet connection for model downloads

### Software Dependencies

- Docker Engine and Docker Compose
- Git (for code deployment)
- curl (for health checks)
- jq (for JSON processing)

### Security Requirements

- Firewall configured (ports 8000, 11434)
- SSL/TLS certificates (for HTTPS)
- Secure secrets management
- Regular security updates

## 🚀 Deployment Process

### Step 1: Environment Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd music_masher_ai
   ```

2. **Create Production Environment**
   ```bash
   # Copy production environment template
   cp env.production.example .env.production
   
   # Edit environment variables
   nano .env.production
   ```

3. **Configure Environment Variables**
   ```bash
   # Required configuration
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   DATABASE_PATH=/app/data/conversations.db
   OLLAMA_BASE_URL=http://ollama:11434
   OLLAMA_MODEL=llama3.1:8b-instruct
   
   # Optional configuration
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Step 2: Security Configuration

1. **Run Security Scan**
   ```bash
   # Scan for vulnerabilities
   ./scripts/docker/security-scan.sh scan-all
   
   # Check for hardcoded secrets
   ./scripts/docker/security-scan.sh check-secrets
   
   # Validate configuration
   ./scripts/docker/security-scan.sh validate-config
   ```

2. **Configure Firewall**
   ```bash
   # Allow required ports
   sudo ufw allow 8000/tcp  # Application
   sudo ufw allow 11434/tcp # Ollama
   sudo ufw enable
   ```

3. **Set Up SSL/TLS** (Recommended)
   ```bash
   # Using Let's Encrypt with Certbot
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

### Step 3: Build and Deploy

1. **Build Production Images**
   ```bash
   # Build production image
   ./scripts/docker/build.sh build-prod
   
   # Verify image
   docker images | grep lit-music-mashup
   ```

2. **Deploy with Ollama**
   ```bash
   # Start production environment with Ollama
   ./scripts/docker/build.sh run-prod-ollama
   
   # Or start without Ollama (if using external Ollama)
   ./scripts/docker/build.sh run-prod
   ```

3. **Verify Deployment**
   ```bash
   # Check container status
   docker ps
   
   # Check health status
   curl -f http://localhost:8000/health
   
   # Check Ollama status
   curl -f http://localhost:11434/api/tags
   ```

## 🔧 Configuration Management

### Environment Variables

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATABASE_PATH` | Database file path | `/app/data/conversations.db` |
| `OLLAMA_BASE_URL` | Ollama service URL | `http://ollama:11434` |
| `OLLAMA_MODEL` | Default AI model | `llama3.1:8b-instruct` |

#### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TAVILY_API_KEY` | Web search API key | `your_api_key_here` |
| `MAX_CONVERSATION_TURNS` | Max conversation turns | `10` |
| `CONVERSATION_TIMEOUT_MINUTES` | Conversation timeout | `30` |

### Volume Management

#### Persistent Data

```yaml
volumes:
  app_data:
    driver: local
  ollama_data:
    driver: local
```

#### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup application data
docker run --rm -v music_masher_ai_app_data:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/app_data_$DATE.tar.gz -C /data .

# Backup Ollama models
docker run --rm -v music_masher_ai_ollama_data:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/ollama_data_$DATE.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

## 📊 Monitoring and Logging

### Health Monitoring

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

### Log Management

1. **View Logs**
   ```bash
   # View application logs
   docker-compose -f docker-compose.prod-with-ollama.yml logs -f app
   
   # View Ollama logs
   docker-compose -f docker-compose.prod-with-ollama.yml logs -f ollama
   ```

2. **Log Rotation**
   ```bash
   # Configure log rotation
   sudo nano /etc/docker/daemon.json
   
   {
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "10m",
       "max-file": "3"
     }
   }
   ```

## 🔄 Maintenance and Updates

### Regular Maintenance

1. **Security Updates**
   ```bash
   # Update base images
   docker pull python:3.11-slim
   docker pull ollama/ollama:latest
   
   # Rebuild images
   ./scripts/docker/build.sh build-prod
   ```

2. **Dependency Updates**
   ```bash
   # Update dependencies
   uv sync --upgrade
   
   # Rebuild images
   ./scripts/docker/build.sh build-prod
   ```

3. **Backup Verification**
   ```bash
   # Test backup restoration
   ./backup.sh
   
   # Verify backup integrity
   tar -tzf /backups/app_data_$(date +%Y%m%d).tar.gz
   ```

### Update Process

1. **Staging Deployment**
   ```bash
   # Deploy to staging first
   ./scripts/docker/build.sh run-prod-ollama
   
   # Run tests
   curl -f http://localhost:8000/health
   ```

2. **Production Deployment**
   ```bash
   # Stop current deployment
   ./scripts/docker/build.sh stop
   
   # Deploy new version
   ./scripts/docker/build.sh run-prod-ollama
   
   # Verify deployment
   curl -f http://localhost:8000/health
   ```

3. **Rollback Plan**
   ```bash
   # If issues occur, rollback
   docker-compose -f docker-compose.prod-with-ollama.yml down
   docker tag lit-music-mashup:prod-backup lit-music-mashup:prod
   ./scripts/docker/build.sh run-prod-ollama
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod-with-ollama.yml logs app
   
   # Check resource usage
   docker stats
   
   # Check disk space
   df -h
   ```

2. **Health Check Failures**
   ```bash
   # Check application status
   curl -v http://localhost:8000/health
   
   # Check Ollama status
   curl -v http://localhost:11434/api/tags
   
   # Check container logs
   docker logs <container_name>
   ```

3. **Performance Issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Check memory usage
   free -h
   
   # Check CPU usage
   top
   ```

### Emergency Procedures

1. **Service Outage**
   ```bash
   # Stop all services
   ./scripts/docker/build.sh stop
   
   # Check system resources
   df -h && free -h
   
   # Restart services
   ./scripts/docker/build.sh run-prod-ollama
   ```

2. **Data Corruption**
   ```bash
   # Stop services
   ./scripts/docker/build.sh stop
   
   # Restore from backup
   tar -xzf /backups/app_data_$(date +%Y%m%d).tar.gz -C /path/to/restore
   
   # Restart services
   ./scripts/docker/build.sh run-prod-ollama
   ```

## 📈 Performance Optimization

### Resource Tuning

1. **Memory Optimization**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G  # Increase for production
       reservations:
         memory: 1G
   ```

2. **CPU Optimization**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'  # Increase for production
       reservations:
         cpus: '0.5'
   ```

3. **Storage Optimization**
   ```bash
   # Use SSD storage for better performance
   # Configure volume mounts for optimal I/O
   ```

### Monitoring Setup

1. **Prometheus Metrics**
   ```yaml
   # Add monitoring service
   monitoring:
     image: prom/prometheus
     ports:
       - "9090:9090"
     volumes:
       - ./monitoring:/etc/prometheus
   ```

2. **Grafana Dashboard**
   ```yaml
   # Add visualization service
   grafana:
     image: grafana/grafana
     ports:
       - "3000:3000"
     volumes:
       - grafana_data:/var/lib/grafana
   ```

## 🔐 Security Hardening

### Additional Security Measures

1. **Network Security**
   ```bash
   # Configure network policies
   docker network create --driver bridge --opt com.docker.network.bridge.name=br0 app-network
   ```

2. **Access Control**
   ```bash
   # Restrict container access
   docker run --security-opt no-new-privileges --cap-drop=ALL
   ```

3. **Audit Logging**
   ```bash
   # Enable audit logging
   docker run --log-driver=json-file --log-opt mode=non-blocking
   ```

## 📞 Support

### Contact Information

- **Technical Support**: tech-support@litmusicmashup.com
- **Emergency Contact**: +1-XXX-XXX-XXXX
- **Documentation**: [GitHub Wiki](https://github.com/your-org/music_masher_ai/wiki)

### Escalation Process

1. **Level 1**: Technical support team
2. **Level 2**: DevOps team
3. **Level 3**: Engineering team
4. **Level 4**: Management team

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] Security scan completed
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Documentation updated

### Deployment

- [ ] Images built successfully
- [ ] Containers started
- [ ] Health checks passing
- [ ] Services accessible
- [ ] Logs being collected
- [ ] Performance acceptable
- [ ] Security validated

### Post-Deployment

- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Backup tested
- [ ] Documentation updated
- [ ] Team notified
- [ ] Support procedures documented

---

*Last updated: December 2024*
