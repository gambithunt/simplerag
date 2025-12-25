# Docker Deployment Guide

Complete guide for running SimpleRAG with Docker.

## Architecture

SimpleRAG uses three Docker containers:

1. **PostgreSQL** - Database for metadata and audit logs
2. **Ollama** - Local LLM inference engine
3. **App** - FastAPI application with frontend

All containers communicate via a custom Docker network (`simplerag_network`).

## Services

### PostgreSQL Container
- **Image**: `postgres:15`
- **Port**: 5432
- **Volume**: `postgres_data` (persisted)
- **Health check**: Built-in pg_isready

### Ollama Container
- **Image**: `ollama/ollama:latest`
- **Port**: 11434
- **Volume**: `ollama_data` (models cached)
- **Health check**: API version endpoint

### App Container
- **Image**: Built from local Dockerfile
- **Port**: 8000
- **Volumes**: 
  - `./uploads` - Document storage
  - `./documents_to_scan` - Bulk import folder
  - `./chroma_db` - Vector embeddings
- **Dependencies**: postgres, ollama

## Quick Commands

```bash
# Start everything
./run.sh

# Or use Makefile
make up

# Manual commands
docker-compose up -d           # Start all services
docker-compose down            # Stop all services
docker-compose ps              # Check status
docker-compose logs -f         # View logs
docker-compose restart         # Restart services
```

## First Time Setup

1. **Build images:**
   ```bash
   docker-compose build
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Pull Ollama model:**
   ```bash
   docker-compose exec ollama ollama pull llama2
   ```

4. **Verify services:**
   ```bash
   docker-compose ps
   # All should show "Up" status
   ```

5. **Access application:**
   - Web: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development Workflow

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f ollama
docker-compose logs -f postgres
```

### Execute Commands in Containers
```bash
# App container
docker-compose exec app python -c "print('Hello')"
docker-compose exec app /bin/bash

# Ollama - list models
docker-compose exec ollama ollama list

# PostgreSQL
docker-compose exec postgres psql -U user -d simplerag
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart app
docker-compose restart ollama
```

### Update Code
```bash
# After code changes, rebuild and restart
docker-compose build app
docker-compose up -d app
```

## Data Persistence

### Docker Volumes (Managed)
- `postgres_data` - Database data
- `ollama_data` - LLM models

### Bind Mounts (Local Directories)
- `./uploads/` - Uploaded documents
- `./documents_to_scan/` - Scan folder
- `./chroma_db/` - Vector embeddings

### Backup Data
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U user simplerag > backup.sql

# Backup files
tar -czf backup-uploads.tar.gz uploads/
tar -czf backup-chroma.tar.gz chroma_db/

# Backup Ollama models
docker run --rm -v simplerag_ollama_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama-models.tar.gz -C /data .
```

### Restore Data
```bash
# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U user simplerag

# Restore files
tar -xzf backup-uploads.tar.gz
tar -xzf backup-chroma.tar.gz
```

## Environment Variables

Set in `docker-compose.yml` under `app.environment`:

```yaml
environment:
  - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/simplerag
  - OLLAMA_BASE_URL=http://ollama:11434
  - LLM_MODEL=llama2
  - EMBEDDING_MODEL=all-MiniLM-L6-v2
  - CHUNK_SIZE=500
  - CHUNK_OVERLAP=50
```

**Important**: Use service names (`postgres`, `ollama`) not `localhost`.

## Resource Management

### View Resource Usage
```bash
docker stats
```

### Set Resource Limits
Edit `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Prune Unused Resources
```bash
docker system prune -a
docker volume prune
```

## Networking

### Access Between Containers
Containers use service names as hostnames:
- App → PostgreSQL: `postgres:5432`
- App → Ollama: `ollama:11434`

### Access from Host
Use `localhost` with mapped ports:
- PostgreSQL: `localhost:5432`
- Ollama: `localhost:11434`
- App: `localhost:8000`

### Custom Network
Created automatically: `simplerag_network`
```bash
docker network inspect simplerag_network
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check if port is in use
lsof -i :8000
lsof -i :5432
lsof -i :11434
```

### Database Connection Issues
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U user -d simplerag -c "SELECT 1"

# Reset database
docker-compose down
docker volume rm simplerag_postgres_data
docker-compose up -d
```

### Ollama Model Not Found
```bash
# List available models
docker-compose exec ollama ollama list

# Pull model
docker-compose exec ollama ollama pull llama2

# Try different model
docker-compose exec ollama ollama pull mistral
# Update docker-compose.yml: LLM_MODEL=mistral
```

### App Container Crashes
```bash
# View logs
docker-compose logs app

# Check if dependencies are ready
docker-compose ps

# Rebuild
docker-compose build app
docker-compose up -d app
```

### Out of Disk Space
```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a
docker volume prune

# Remove specific volumes
docker volume rm simplerag_postgres_data
docker volume rm simplerag_ollama_data
```

## Production Deployment

### Security Hardening

1. **Change default passwords:**
   ```yaml
   environment:
     - POSTGRES_PASSWORD=<strong-password>
     - SECRET_KEY=<generated-key>
   ```

2. **Don't expose unnecessary ports:**
   ```yaml
   # Remove port mappings for internal services
   postgres:
     # ports:
     #   - "5432:5432"  # Comment out
   ```

3. **Use secrets:**
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### HTTPS with Let's Encrypt
```bash
# Add certbot service to docker-compose.yml
docker-compose exec certbot certbot --nginx
```

### Monitoring

Add to `docker-compose.yml`:
```yaml
services:
  prometheus:
    image: prom/prometheus
  
  grafana:
    image: grafana/grafana
```

### Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U user simplerag > backup_$DATE.sql
tar czf uploads_$DATE.tar.gz uploads/
tar czf chroma_$DATE.tar.gz chroma_db/
```

## Advanced Configuration

### Multi-stage Build
Optimize Dockerfile for smaller images:
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]
```

### Health Checks
```yaml
app:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Auto-restart
```yaml
app:
  restart: unless-stopped
```

## FAQ

**Q: How do I use a different LLM model?**
```bash
# Pull new model
docker-compose exec ollama ollama pull mistral

# Update docker-compose.yml
environment:
  - LLM_MODEL=mistral

# Restart
docker-compose restart app
```

**Q: Can I run without Ollama?**
No, the app requires Ollama for LLM inference. You can modify the code to use OpenAI API instead.

**Q: How much disk space is needed?**
- Base images: ~2GB
- PostgreSQL data: ~100MB (varies with documents)
- Ollama model: ~4GB (llama2)
- Embedding model: ~90MB
- **Total**: ~6-7GB minimum

**Q: Can I run on ARM (M1/M2 Mac)?**
Yes! Docker images are multi-arch and work on ARM64.

**Q: How do I scale horizontally?**
Use Docker Swarm or Kubernetes. PostgreSQL and Ollama would need separate scaling strategies.

## Reference

- Docker Compose docs: https://docs.docker.com/compose/
- Ollama Docker: https://hub.docker.com/r/ollama/ollama
- PostgreSQL Docker: https://hub.docker.com/_/postgres
