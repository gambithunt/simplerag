#!/bin/bash

# Alternative run script for local development (non-Docker)

echo "🚀 Starting SimpleRAG locally (without Docker)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Update .env for local development
if [ ! -f ".env.local" ]; then
    cat > .env.local << 'EOF'
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/simplerag
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=simplerag
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
SCAN_DIR=./documents_to_scan
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo "Created .env.local for local development"
fi

# Use local env file
export $(cat .env.local | grep -v '^#' | xargs)

# Start PostgreSQL with Docker
echo "Starting PostgreSQL with Docker..."
docker run -d --name simplerag_postgres_local \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=simplerag \
  -p 5432:5432 \
  postgres:15 2>/dev/null || echo "PostgreSQL container already running"

# Check if Ollama is running
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "⚠️  Ollama not running. Please start Ollama:"
    echo "    brew install ollama  # macOS"
    echo "    ollama serve         # Start service"
    echo "    ollama pull llama2   # Pull model"
    exit 1
fi

# Create directories
mkdir -p uploads documents_to_scan chroma_db

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
sleep 3

# Start the application
echo ""
echo "✅ Starting SimpleRAG server..."
echo "📍 Access at: http://localhost:8000"
echo ""
python main.py
