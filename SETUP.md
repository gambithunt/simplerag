# SimpleRAG Setup Guide

Complete setup instructions for SimpleRAG - Local Document Search & Chat system.

## Quick Start (5 minutes)

```bash
# 1. Navigate to project
cd /Users/delon/Documents/code/projects/simplerag

# 2. Run setup script
./run.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Start PostgreSQL (via Docker if needed)
- Check Ollama status
- Start the application

## Manual Setup

### Step 1: Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: PostgreSQL Setup

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d postgres
```

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb simplerag

# Initialize schema
psql simplerag < init_db.sql
```

### Step 3: Ollama Setup

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama2

# Or for smaller/faster model:
ollama pull llama2:7b-chat

# Or for better quality:
ollama pull mistral
```

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit configuration
nano .env
```

Required settings in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/simplerag
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
```

### Step 5: Start Application

```bash
python main.py
```

Access at: **http://localhost:8000**

## Verification

### Test Database Connection
```bash
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"
```

### Test Ollama
```bash
curl http://localhost:11434/api/version
```

### Test Embeddings
```bash
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print('✓ Embeddings OK')"
```

## Common Issues

### Issue: Database connection refused
**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start Docker PostgreSQL
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

### Issue: Ollama not found
**Solution:**
```bash
# Check if Ollama is installed
which ollama

# Install
brew install ollama  # macOS
# or download from https://ollama.ai

# Start service
ollama serve

# Pull model
ollama pull llama2
```

### Issue: Port 8000 already in use
**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill it or change port in main.py
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Issue: Embedding model download fails
**Solution:**
- Check internet connection
- Model will download on first run (~90MB)
- Retry or use different mirror

### Issue: File upload fails
**Solution:**
```bash
# Ensure directories exist
mkdir -p uploads documents_to_scan chroma_db

# Check permissions
chmod 755 uploads documents_to_scan chroma_db
```

## Directory Structure

After setup, you should have:
```
simplerag/
├── venv/                    # Virtual environment
├── uploads/                 # Uploaded documents stored here
├── documents_to_scan/       # Place files here for bulk import
├── chroma_db/              # Vector database storage
├── static/                 # Frontend files
├── services/               # Backend services
├── .env                    # Your configuration (not in git)
└── main.py                # Application entry point
```

## Testing the System

### 1. Upload a Test Document

Create a test file:
```bash
cat > documents_to_scan/test.txt << 'EOF'
SimpleRAG is a document search system.
It uses vector embeddings for semantic search.
You can chat with your documents using natural language.
EOF
```

### 2. Run Scan
- Open http://localhost:8000
- Click "🔄 Scan Folder"
- Should see: "Scanned: 1/1 files processed"

### 3. Test Chat
- Type: "What is SimpleRAG?"
- Should get an answer based on the document

## Performance Tips

### Faster Embeddings
Use a smaller model in `.env`:
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Default, good balance
# or
EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2  # Faster, less accurate
```

### Faster LLM
Use a smaller Ollama model:
```bash
ollama pull tinyllama  # Very fast, less capable
ollama pull phi  # Good balance
```

Update `.env`:
```env
LLM_MODEL=tinyllama
```

### Adjust Chunk Size
Smaller chunks = faster search, but less context:
```env
CHUNK_SIZE=300
CHUNK_OVERLAP=30
```

## Production Deployment

For production use:

1. **Use proper secrets**
   ```env
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Use production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

3. **Enable HTTPS**
   - Use reverse proxy (nginx)
   - Get SSL certificate (Let's Encrypt)

4. **Database backups**
   ```bash
   pg_dump simplerag > backup.sql
   ```

5. **Monitoring**
   - Set up logging
   - Monitor disk space (uploads/, chroma_db/)
   - Track query performance

## Next Steps

- Add more documents via upload or folder scan
- Customize chunk size for your use case
- Try different LLM models (mistral, mixtral, etc.)
- Adjust top_k parameter for more/fewer sources
- Implement authentication (see spec reference)

## Support

For issues or questions:
1. Check logs: `docker-compose logs` or console output
2. Verify all services running: PostgreSQL, Ollama
3. Test each component individually (see Verification section)

Refer to `/Users/delon/Documents/code/projects/ai-rag-system/.githhub/copilot-instructions.md` for the full specification and advanced features.
