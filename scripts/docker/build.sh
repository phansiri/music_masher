#!/bin/bash

# Docker Build Script for Lit Music Mashup AI
# This script provides convenient commands for building and managing Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build-dev     Build development Docker image"
    echo "  build-prod    Build production Docker image"
    echo "  run-dev       Run development environment (uses host's Ollama)"
    echo "  run-dev-ollama Run development environment with Ollama container"
    echo "  run-prod      Run production environment (uses host's Ollama)"
    echo "  run-prod-ollama Run production environment with Ollama container"
    echo "  stop          Stop all containers"
    echo "  clean         Clean up Docker resources"
    echo "  logs          Show container logs"
    echo "  help          Show this help message"
    echo ""
    echo "Ollama Configuration:"
    echo "  - Default: Uses host's Ollama installation (http://host.docker.internal:11434)"
    echo "  - Alternative: Use Ollama container by adding '-ollama' suffix to commands"
    echo ""
    echo "Examples:"
    echo "  $0 build-dev"
    echo "  $0 run-prod"
    echo "  $0 run-dev-ollama"
    echo "  $0 stop"
}

# Function to build development image
build_dev() {
    print_status "Building development Docker image..."
    docker build -f Dockerfile.dev -t lit-music-mashup:dev .
    print_success "Development image built successfully!"
}

# Function to build production image
build_prod() {
    print_status "Building production Docker image..."
    docker build -f Dockerfile.prod --target production -t lit-music-mashup:prod .
    print_success "Production image built successfully!"
}

# Function to run development environment (host Ollama)
run_dev() {
    print_status "Starting development environment (using host's Ollama)..."
    print_warning "Make sure Ollama is running on your host machine!"
    docker-compose -f docker-compose.dev.yml up -d
    print_success "Development environment started!"
    print_status "Application available at: http://localhost:8000"
    print_status "Using host's Ollama at: http://localhost:11434"
}

# Function to run development environment with Ollama container
run_dev_ollama() {
    print_status "Starting development environment with Ollama container..."
    docker-compose -f docker-compose.dev-with-ollama.yml up -d
    print_success "Development environment with Ollama container started!"
    print_status "Application available at: http://localhost:8000"
    print_status "Ollama container available at: http://localhost:11434"
}

# Function to run production environment (host Ollama)
run_prod() {
    print_status "Starting production environment (using host's Ollama)..."
    print_warning "Make sure Ollama is running on your host machine!"
    docker-compose -f docker-compose.prod.yml up -d
    print_success "Production environment started!"
    print_status "Application available at: http://localhost:8000"
    print_status "Using host's Ollama at: http://localhost:11434"
}

# Function to run production environment with Ollama container
run_prod_ollama() {
    print_status "Starting production environment with Ollama container..."
    docker-compose -f docker-compose.prod-with-ollama.yml up -d
    print_success "Production environment with Ollama container started!"
    print_status "Application available at: http://localhost:8000"
    print_status "Ollama container available at: http://localhost:11434"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping all containers..."
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker-compose -f docker-compose.dev-with-ollama.yml down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker-compose -f docker-compose.prod-with-ollama.yml down 2>/dev/null || true
    print_success "All containers stopped!"
}

# Function to clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose -f docker-compose.dev.yml logs -f 2>/dev/null || \
    docker-compose -f docker-compose.dev-with-ollama.yml logs -f 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml logs -f 2>/dev/null || \
    docker-compose -f docker-compose.prod-with-ollama.yml logs -f 2>/dev/null || \
    print_error "No running containers found"
}

# Main script logic
case "${1:-help}" in
    build-dev)
        build_dev
        ;;
    build-prod)
        build_prod
        ;;
    run-dev)
        run_dev
        ;;
    run-dev-ollama)
        run_dev_ollama
        ;;
    run-prod)
        run_prod
        ;;
    run-prod-ollama)
        run_prod_ollama
        ;;
    stop)
        stop_containers
        ;;
    clean)
        cleanup
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
