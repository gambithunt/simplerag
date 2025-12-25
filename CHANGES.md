# Docker Migration Changes

## Summary
SimpleRAG has been fully containerized! All components now run in Docker containers for easy deployment and consistency.

## What Changed

### New Files
1. **Dockerfile** - Container definition for the FastAPI app
2. **.dockerignore** - Files to exclude from Docker build
3. **docker-run-local.sh** - Alternative script for non-Docker local development
4. **Makefile** - Convenient shortcuts for Docker commands
5. **DOCKER.md** - Comprehensive Docker deployment guide
6. **CHANGES.md** - This file

### Modified Files
1. **docker-compose.yml**
   - Added `ollama` service (Ollama LLM in container)
   - Added `app` service (FastAPI application)
   - Updated `postgres` service with health checks
   - Added custom network for container communication
   - Added volume mounts for data persistence

2. **run.sh**
   - Completely rewritten for Docker
   - Now handles all services via docker-compose
   - Automatically pulls Ollama model
   - Provides status and logging information

3. **.env and .env.example**
   - Changed `localhost` to service names (`postgres`, `ollama`)
   - Updated for Docker network communication
   - Added comments explaining Docker vs local setup

4. **README.md**
   - Updated with Docker-first approach
   - Simplified prerequisites (only Docker needed)
   - Updated troubleshooting for containers
   - Added Docker architecture diagram

5. **QUICKSTART.md**
   - Streamlined to Docker-only workflow
   - Updated commands for Docker Compose
   - Removed manual installation steps

6. **.gitignore**
   - Added Docker-related files (backups, .env.local)
   - Added .gitkeep exceptions for empty directories

7. **main.py**
   - Added log_level parameter to uvicorn.run()

## Architecture Changes

### Before (Manual Setup)
```
User Machine
├── PostgreSQL (installed locally)
├── Ollama (installed locally)
└── Python App (virtualenv)
```

### After (Docker)
```
Docker Host
├── simplerag_postgres (container)
├── simplerag_ollama (container)
└── simplerag_app (container)
    └── FastAPI + Frontend
```

## Network Communication

### Container-to-Container
- App connects to `postgres:5432` (not localhost)
- App connects to `ollama:11434` (not localhost)
- Uses Docker network: `simplerag_network`

### Host-to-Container
- PostgreSQL: `localhost:5432`
- Ollama: `localhost:11434`
- App: `localhost:8000`

## Data Persistence

### Docker Volumes (Managed)
- `postgres_data` - Database files
- `ollama_data` - LLM models

### Bind Mounts (Local Directories)
- `./uploads/` - Uploaded documents
- `./documents_to_scan/` - Bulk import folder
- `./chroma_db/` - Vector embeddings

## Benefits

1. **No Manual Installation** - Only Docker needed
2. **Consistent Environment** - Same setup on any machine
3. **Easy Updates** - Pull new images
4. **Isolation** - No conflicts with system packages
5. **Reproducible** - Identical dev/prod environments
6. **Scalable** - Easy to add more services

## Migration Guide

### For Existing Users

If you were running the old version:

1. **Backup your data:**
   ```bash
   cp -r uploads uploads_backup
   cp -r chroma_db chroma_db_backup
   pg_dump simplerag > backup.sql
   ```

2. **Stop old services:**
   ```bash
   # Stop local PostgreSQL
   brew services stop postgresql
   
   # Stop Ollama
   pkill ollama
   ```

3. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

4. **Update configuration:**
   ```bash
   # .env file should now use service names
   DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/simplerag
   OLLAMA_BASE_URL=http://ollama:11434
   ```

5. **Start with Docker:**
   ```bash
   ./run.sh
   ```

6. **Restore data (if needed):**
   ```bash
   # Restore database
   cat backup.sql | docker-compose exec -T postgres psql -U user simplerag
   
   # Files are already in ./uploads and ./chroma_db (bind mounts)
   ```

### For New Users

Just run:
```bash
./run.sh
```

## Backward Compatibility

The old manual setup still works! Use:
```bash
./docker-run-local.sh
```

This script:
- Creates a Python virtualenv
- Uses PostgreSQL in Docker
- Expects Ollama installed locally
- Updates .env to use localhost

## Configuration Differences

### Docker Mode (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/simplerag
OLLAMA_BASE_URL=http://ollama:11434
```

### Local Mode (.env.local)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/simplerag
OLLAMA_BASE_URL=http://localhost:11434
```

## Commands Reference

### Docker Mode (Default)
```bash
./run.sh                    # Start everything
make up                     # Alternative start
make down                   # Stop everything
make logs                   # View logs
docker-compose ps           # Check status
```

### Local Development Mode
```bash
./docker-run-local.sh       # Start in local mode
python main.py              # Run manually
```

## Troubleshooting

### "Docker not found"
Install Docker Desktop: https://docs.docker.com/get-docker/

### "Port already in use"
```bash
docker ps
docker stop <conflicting-container>
```

### "Can't connect to database"
```bash
# Check service is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### "Ollama model not found"
```bash
# Pull model manually
docker-compose exec ollama ollama pull llama2
```

## Performance Notes

- **First run**: Takes 5-10 minutes (downloading images + model)
- **Subsequent runs**: ~30 seconds (containers start quickly)
- **Model download**: llama2 is ~4GB
- **Disk usage**: ~7GB total for all images and data

## Future Improvements

Potential enhancements:
- [ ] Add health check endpoint in FastAPI
- [ ] GPU support for Ollama (NVIDIA)
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline for automated builds
- [ ] Multi-stage Dockerfile for smaller images
- [ ] Separate frontend container (nginx)
- [ ] Redis for caching
- [ ] Monitoring (Prometheus/Grafana)

## Questions?

See:
- **DOCKER.md** - Comprehensive Docker guide
- **README.md** - Updated main documentation
- **QUICKSTART.md** - Quick start guide
