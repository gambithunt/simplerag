#!/bin/bash

# Docker Setup Verification Script

echo "🔍 Verifying Docker Setup for SimpleRAG"
echo "========================================"
echo ""

# Check Docker
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker found: $(docker --version)"
else
    echo "   ❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
echo ""
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "   ✅ Docker Compose found: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check Docker daemon
echo ""
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check required files
echo ""
echo "4. Checking required files..."
FILES=("Dockerfile" "docker-compose.yml" "requirements.txt" "main.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
    fi
done

# Check directories
echo ""
echo "5. Checking directories..."
DIRS=("uploads" "documents_to_scan" "chroma_db" "static" "services")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/"
    else
        echo "   ⚠️  $dir/ missing (will be created)"
        mkdir -p "$dir"
    fi
done

# Check if services are already running
echo ""
echo "6. Checking for running containers..."
if docker-compose ps | grep -q "Up"; then
    echo "   ℹ️  SimpleRAG containers are running"
    docker-compose ps
else
    echo "   ℹ️  No containers running (this is normal if not started yet)"
fi

# Check disk space
echo ""
echo "7. Checking disk space..."
AVAILABLE=$(df -h . | awk 'NR==2 {print $4}')
echo "   Available space: $AVAILABLE"
echo "   ℹ️  Recommended: At least 10GB free"

# Check ports
echo ""
echo "8. Checking ports..."
PORTS=(5432 8000 11434)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ⚠️  Port $port is in use"
    else
        echo "   ✅ Port $port is available"
    fi
done

echo ""
echo "========================================"
echo "✅ Verification Complete!"
echo ""
echo "Next steps:"
echo "  1. Run: ./run.sh"
echo "  2. Wait for services to start (~30 seconds)"
echo "  3. Access: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "  make up      - Start services"
echo "  make down    - Stop services"
echo "  make logs    - View logs"
echo "  make help    - See all commands"
echo ""
