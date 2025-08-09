#!/bin/bash

# Docker Security Scanning Script for Lit Music Mashup AI
# This script provides security scanning and vulnerability assessment for Docker images

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
    echo "  scan-image [IMAGE]     Scan a Docker image for vulnerabilities"
    echo "  scan-container [CONTAINER] Scan a running container"
    echo "  scan-all              Scan all project images"
    echo "  audit-dependencies    Audit Python dependencies for vulnerabilities"
    echo "  check-secrets         Check for hardcoded secrets in code"
    echo "  validate-config       Validate Docker configuration security"
    echo "  help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 scan-image lit-music-mashup:prod"
    echo "  $0 scan-all"
    echo "  $0 audit-dependencies"
}

# Function to check if required tools are installed
check_requirements() {
    local missing_tools=()
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # Check for trivy (optional)
    if ! command -v trivy &> /dev/null; then
        print_warning "trivy not found. Install for enhanced vulnerability scanning:"
        print_warning "  brew install trivy  # macOS"
        print_warning "  sudo apt-get install trivy  # Ubuntu"
    fi
    
    # Check for bandit (optional)
    if ! command -v bandit &> /dev/null; then
        print_warning "bandit not found. Install for Python security scanning:"
        print_warning "  pip install bandit"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
}

# Function to scan Docker image for vulnerabilities
scan_image() {
    local image_name=$1
    
    if [ -z "$image_name" ]; then
        print_error "Image name is required"
        show_usage
        exit 1
    fi
    
    print_status "Scanning Docker image: $image_name"
    
    # Check if image exists
    if ! docker image inspect "$image_name" &> /dev/null; then
        print_error "Image $image_name not found"
        exit 1
    fi
    
    # Use trivy if available, otherwise use Docker Scout
    if command -v trivy &> /dev/null; then
        print_status "Using trivy for vulnerability scanning..."
        trivy image --severity HIGH,CRITICAL "$image_name"
    else
        print_status "Using Docker Scout for vulnerability scanning..."
        docker scout cves "$image_name"
    fi
    
    print_success "Image scanning completed for: $image_name"
}

# Function to scan running container
scan_container() {
    local container_name=$1
    
    if [ -z "$container_name" ]; then
        print_error "Container name is required"
        show_usage
        exit 1
    fi
    
    print_status "Scanning running container: $container_name"
    
    # Check if container exists and is running
    if ! docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        print_error "Container $container_name not found or not running"
        exit 1
    fi
    
    # Use trivy if available
    if command -v trivy &> /dev/null; then
        print_status "Using trivy for container scanning..."
        trivy container --severity HIGH,CRITICAL "$container_name"
    else
        print_warning "trivy not available. Please install for container scanning."
    fi
    
    print_success "Container scanning completed for: $container_name"
}

# Function to scan all project images
scan_all() {
    print_status "Scanning all project images..."
    
    # List of project images to scan
    local images=("lit-music-mashup:dev" "lit-music-mashup:prod")
    
    for image in "${images[@]}"; do
        if docker image inspect "$image" &> /dev/null; then
            print_status "Scanning image: $image"
            scan_image "$image"
        else
            print_warning "Image $image not found, skipping..."
        fi
    done
    
    print_success "All image scanning completed"
}

# Function to audit Python dependencies
audit_dependencies() {
    print_status "Auditing Python dependencies for vulnerabilities..."
    
    # Check if we're in the project directory
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Please run from project root."
        exit 1
    fi
    
    # Use safety if available, otherwise use pip-audit
    if command -v safety &> /dev/null; then
        print_status "Using safety for dependency auditing..."
        safety check
    elif command -v pip-audit &> /dev/null; then
        print_status "Using pip-audit for dependency auditing..."
        pip-audit
    else
        print_warning "Neither safety nor pip-audit found. Install for dependency auditing:"
        print_warning "  pip install safety"
        print_warning "  or"
        print_warning "  pip install pip-audit"
    fi
    
    print_success "Dependency auditing completed"
}

# Function to check for hardcoded secrets
check_secrets() {
    print_status "Checking for hardcoded secrets in code..."
    
    # Common secret patterns to check for
    local secret_patterns=(
        "password.*=.*['\"][^'\"]{8,}['\"]"
        "secret.*=.*['\"][^'\"]{8,}['\"]"
        "api_key.*=.*['\"][^'\"]{8,}['\"]"
        "token.*=.*['\"][^'\"]{8,}['\"]"
        "private_key.*=.*['\"][^'\"]{8,}['\"]"
    )
    
    local found_secrets=false
    
    for pattern in "${secret_patterns[@]}"; do
        if grep -r --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.venv -E "$pattern" .; then
            found_secrets=true
        fi
    done
    
    if [ "$found_secrets" = true ]; then
        print_warning "Potential hardcoded secrets found. Please review the output above."
    else
        print_success "No obvious hardcoded secrets found"
    fi
}

# Function to validate Docker configuration security
validate_config() {
    print_status "Validating Docker configuration security..."
    
    # Check Dockerfile security best practices
    local security_issues=0
    
    # Check for non-root user
    if ! grep -q "USER.*app" Dockerfile.prod; then
        print_warning "Production Dockerfile should run as non-root user"
        ((security_issues++))
    fi
    
    # Check for unnecessary packages
    if grep -q "apt-get install.*-y" Dockerfile.prod; then
        print_warning "Consider removing unnecessary packages in production"
    fi
    
    # Check for proper cleanup
    if ! grep -q "rm -rf.*/var/lib/apt/lists" Dockerfile.prod; then
        print_warning "Consider cleaning up package cache in production"
    fi
    
    # Check for health checks
    if ! grep -q "HEALTHCHECK" Dockerfile.prod; then
        print_warning "Production Dockerfile should include health checks"
        ((security_issues++))
    fi
    
    if [ $security_issues -eq 0 ]; then
        print_success "Docker configuration security validation passed"
    else
        print_warning "Found $security_issues security issues in Docker configuration"
    fi
}

# Main script logic
case "${1:-help}" in
    scan-image)
        check_requirements
        scan_image "$2"
        ;;
    scan-container)
        check_requirements
        scan_container "$2"
        ;;
    scan-all)
        check_requirements
        scan_all
        ;;
    audit-dependencies)
        audit_dependencies
        ;;
    check-secrets)
        check_secrets
        ;;
    validate-config)
        validate_config
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
