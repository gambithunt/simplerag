# SimpleRAG - Local Document Search & Chat

A production-ready RAG (Retrieval-Augmented Generation) system that allows you to upload documents, store them in a vector database, and chat with them using a local LLM. **Now fully containerized with Docker!**

## Features

- 📄 **Document Upload**: Support for PDF, DOCX, TXT, MD, XLSX files
- 🔄 **Folder Scanning**: Automatically scan and ingest documents from a folder
- 🔍 **Vector Search**: Fast semantic search using ChromaDB and embeddings
- 💬 **Chat Interface**: Clean, reactive Alpine.js frontend
- 🤖 **Local LLM**: Uses Ollama for local language model inference
- 📊 **PostgreSQL**: Structured data storage with audit logging
- ⚡ **FastAPI Backend**: Async Python backend for performance
- 🐳 **Docker**: Fully containerized - no manual setup required!

## Prerequisites

**Only Docker is required!**
- **Docker** (with Docker Compose)
- That's it! Everything else runs in containers.

Install Docker: https://docs.docker.com/get-docker/

## Quick Start (3 Commands)

```bash
cd /Users/delon/Documents/code/projects/simplerag

# Start everything
./run.sh

# Access the app
open http://localhost:8000
```

The script will:
- Build all Docker images
- Start PostgreSQL, Ollama, and the app
- Pull the Ollama llama2 model
- Set everything up automatically

## Manual Docker Commands

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Pull Ollama model
docker-compose exec ollama ollama pull llama2

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## Using the Makefile (Recommended)

```bash
make up          # Start all services
make logs        # View logs
make logs-app    # View just app logs
make down        # Stop services
make restart     # Restart services
make pull-model  # Pull Ollama model
make clean       # Remove everything
```

## Access the Application

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432 (user/password from docker-compose.yml)
- **Ollama**: http://localhost:11434

## Usage

### Upload Documents
1. Click "Choose File" in the left sidebar
2. Select a document (PDF, DOCX, TXT, MD, XLSX)
3. Click "Upload"

### Scan Folder
1. Place documents in `./documents_to_scan/`
2. Click "🔄 Scan Folder"
3. Documents will be automatically processed and added

### Chat
1. Type your question in the chat input
2. Click "Send"
3. View answers with relevant source documents

## Docker Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Network                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │  Ollama  │  │   App    │  │
│  │  :5432   │  │  :11434  │  │  :8000   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       │             │              │         │
│       └─────────────┴──────────────┘         │
└─────────────────────────────────────────────┘
         │             │              │
    [postgres_data] [ollama_data] [volumes]
```

## Project Structure

```
simplerag/
├── Dockerfile                   # App container
├── docker-compose.yml           # Service orchestration
├── Makefile                     # Convenient commands
├── main.py                      # FastAPI application
├── config.py                    # Configuration settings
├── database.py                  # Database connection
├── models.py                    # SQLAlchemy models
├── schemas.py                   # Pydantic schemas
├── services/
│   ├── document_processor.py   # Text extraction & chunking
│   ├── vector_store.py         # ChromaDB integration
│   ├── rag_engine.py           # Query & LLM generation
│   └── document_service.py     # Document management
├── static/
│   └── index.html              # Alpine.js frontend
├── uploads/                     # Uploaded documents (volume)
├── documents_to_scan/          # Folder for bulk ingestion (volume)
└── chroma_db/                  # Vector database storage (volume)
```

## API Endpoints

- `POST /api/upload` - Upload a document
- `POST /api/scan` - Scan folder for new documents
- `POST /api/query` - Ask a question
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{id}` - Delete a document

## Configuration

Configuration is handled via environment variables in `docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/simplerag
  - OLLAMA_BASE_URL=http://ollama:11434
  - LLM_MODEL=llama2
  - EMBEDDING_MODEL=all-MiniLM-L6-v2
  - CHUNK_SIZE=500
  - CHUNK_OVERLAP=50
```

**Note**: Service names (`postgres`, `ollama`) are used instead of `localhost` because containers communicate via Docker network.

## Supported File Types

- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`
- **Text**: `.txt`, `.md`
- **Excel**: `.xlsx`, `.xls`

## Troubleshooting

### Services Not Starting
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart app
```

### Database Connection Error
```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Ollama Model Issues
```bash
# Pull model manually
docker-compose exec ollama ollama pull llama2

# Check Ollama status
curl http://localhost:11434/api/version
```

### Port Already in Use
```bash
# Stop conflicting services
docker ps
docker stop <container_id>

# Or change ports in docker-compose.yml
```

### Reset Everything
```bash
# Nuclear option - removes all data
make clean
# or
docker-compose down -v
rm -rf chroma_db/* uploads/*
```

## Volumes and Data Persistence

Data is persisted in Docker volumes and local directories:
- `postgres_data` - Database data (Docker volume)
- `ollama_data` - Ollama models (Docker volume)
- `./uploads/` - Uploaded documents (bind mount)
- `./documents_to_scan/` - Scan folder (bind mount)
- `./chroma_db/` - Vector embeddings (bind mount)

## Development Mode

For local development without Docker:
```bash
# Use alternative script
./docker-run-local.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Update .env to use localhost instead of service names
python main.py
```

## Production Deployment

For production:
1. Use secrets management for credentials
2. Set strong `SECRET_KEY` in environment
3. Add reverse proxy (nginx) with HTTPS
4. Configure backup strategy for volumes
5. Set up monitoring and alerting
6. Use production-grade Ollama deployment
7. Consider resource limits in docker-compose.yml

## License

MIT License
