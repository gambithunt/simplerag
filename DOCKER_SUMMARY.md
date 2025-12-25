# 🐳 SimpleRAG - Now Fully Dockerized!

## What Was Done

SimpleRAG has been completely containerized. All services now run in Docker containers with zero manual setup required.

## 🎯 Quick Start

```bash
# Only prerequisite: Docker installed
# Then just run:
./run.sh

# Access at http://localhost:8000
```

That's it! Everything is automated.

## 📦 What's Included

### Three Docker Containers

1. **PostgreSQL** (postgres:15)
   - Database for metadata and audit logs
   - Port: 5432
   - Volume: `postgres_data`

2. **Ollama** (ollama/ollama:latest)
   - Local LLM inference engine
   - Port: 11434
   - Volume: `ollama_data`
   - Auto-pulls llama2 model

3. **Application** (custom build)
   - FastAPI backend + Alpine.js frontend
   - Port: 8000
   - Volumes: uploads, documents_to_scan, chroma_db

### All Connected

Containers communicate via `simplerag_network` Docker bridge network.

## 📝 New Files Created

1. **Dockerfile** - App container definition
2. **.dockerignore** - Build exclusions
3. **Makefile** - Convenient commands
4. **DOCKER.md** - Full Docker guide
5. **CHANGES.md** - Migration details
6. **docker-run-local.sh** - Non-Docker alternative
7. **DOCKER_SUMMARY.md** - This file

## 🔧 Modified Files

1. **docker-compose.yml** - Now includes all 3 services
2. **run.sh** - Rewritten for Docker
3. **.env/.env.example** - Updated for container networking
4. **README.md** - Docker-first documentation
5. **QUICKSTART.md** - Simplified for Docker
6. **.gitignore** - Added Docker-related patterns

## 🚀 Commands

### Basic Operations
```bash
./run.sh              # Start everything
make up               # Alternative start
make down             # Stop everything
make logs             # View all logs
make restart          # Restart services
```

### Docker Compose
```bash
docker-compose up -d          # Start in background
docker-compose down           # Stop all
docker-compose ps             # Check status
docker-compose logs -f app    # Follow app logs
docker-compose restart app    # Restart just app
```

### Ollama Management
```bash
docker-compose exec ollama ollama list         # List models
docker-compose exec ollama ollama pull llama2  # Pull model
docker-compose exec ollama ollama pull mistral # Try different model
```

### Database Operations
```bash
docker-compose exec postgres psql -U user simplerag    # Access DB
docker-compose exec postgres pg_dump -U user simplerag # Backup
```

## 🔑 Key Changes

### Configuration
**Before:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/simplerag
OLLAMA_BASE_URL=http://localhost:11434
```

**After (Docker):**
```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/simplerag
OLLAMA_BASE_URL=http://ollama:11434
```

Service names (`postgres`, `ollama`) are used instead of `localhost` for container-to-container communication.

### Prerequisites
**Before:**
- Python 3.11+
- PostgreSQL 15
- Ollama
- Multiple installation steps

**After:**
- Docker (only!)
- One command: `./run.sh`

## 📊 Data Persistence

### Docker Volumes (Managed by Docker)
- `postgres_data` → Database files
- `ollama_data` → LLM models (~4GB)

### Bind Mounts (Your Local Folders)
- `./uploads/` → Uploaded documents
- `./documents_to_scan/` → Bulk import folder
- `./chroma_db/` → Vector embeddings

**Your data is safe!** Volumes persist even if containers are removed.

## 🎨 Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Network (simplerag)          │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │PostgreSQL│  │  Ollama  │  │   App    │ │
│  │  :5432   │◄─┤  :11434  │◄─┤  :8000   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │              │        │
└───────┼─────────────┼──────────────┼────────┘
        │             │              │
   [postgres_   [ollama_      [bind mounts]
     data]        data]        uploads/
                               chroma_db/
```

## ✅ Benefits

1. **Zero Setup** - Only Docker needed
2. **Consistency** - Same environment everywhere
3. **Isolation** - No system conflicts
4. **Portability** - Works on any OS with Docker
5. **Reproducibility** - Exact same setup every time
6. **Easy Updates** - `docker-compose pull && docker-compose up -d`

## 🔄 Upgrading from Old Version

If you had the old manual setup:

```bash
# 1. Backup your data
cp -r uploads uploads_backup
cp -r chroma_db chroma_db_backup

# 2. Pull changes
git pull

# 3. Start with Docker
./run.sh

# 4. Your uploads/ and chroma_db/ folders are automatically used!
```

## 🆘 Troubleshooting

### Services won't start
```bash
docker-compose ps        # Check status
docker-compose logs -f   # View logs
```

### Port conflicts
```bash
# Find what's using the port
lsof -i :8000
lsof -i :5432
lsof -i :11434

# Stop conflicting service
docker stop <container>
```

### Reset everything
```bash
make clean
# or
docker-compose down -v
rm -rf chroma_db/* uploads/*
./run.sh
```

### Out of disk space
```bash
docker system df         # Check usage
docker system prune -a   # Clean up
```

## 📚 Documentation

- **README.md** - Main documentation (updated for Docker)
- **QUICKSTART.md** - Quick start guide (Docker focus)
- **DOCKER.md** - Comprehensive Docker guide
- **CHANGES.md** - Detailed migration info
- **SETUP.md** - Detailed setup (now simpler!)

## 🎯 Next Steps

1. **Start the system:**
   ```bash
   ./run.sh
   ```

2. **Wait for model download** (first time only, ~5 min)

3. **Upload a document** at http://localhost:8000

4. **Start chatting!**

## 💡 Tips

- Use `make logs-app` to watch application logs
- Use `make shell` to access container shell
- Check `make help` for all available commands
- Edit `docker-compose.yml` to change ports or resources

## 🚀 Production Ready

The Docker setup is production-ready:
- Health checks on all services
- Restart policies configured
- Volume persistence
- Network isolation
- Easy to add reverse proxy (nginx)
- Ready for Docker Swarm or Kubernetes

## 🎉 Success!

You now have a fully containerized RAG system that:
- ✅ Runs everywhere Docker runs
- ✅ Starts with one command
- ✅ Persists data safely
- ✅ Is easy to maintain and update
- ✅ Works identically in dev and prod

**Happy document searching! 🔍**
