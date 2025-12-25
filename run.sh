#!/bin/bash

# SimpleRAG Startup Script (Docker)

echo "🚀 Starting SimpleRAG with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Create directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p uploads documents_to_scan chroma_db

# Check if .env exists (not used by containers but good for reference)
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🔨 Building containers..."
docker-compose build

echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo ""
echo "📊 Service Status:"
docker-compose ps

# Pull Ollama model if not exists
echo ""
echo "🤖 Checking Ollama model..."
echo "   Pulling llama2 model (this may take a few minutes on first run)..."
docker-compose exec -T ollama ollama pull llama2

echo ""
echo "✅ SimpleRAG is ready!"
echo ""
echo "📍 Access the application at: http://localhost:8000"
echo "📍 API documentation at: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo "   View status:      docker-compose ps"
echo ""
echo "🔍 To view application logs in real-time, run:"
echo "   docker-compose logs -f app"
echo ""
