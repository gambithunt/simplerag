# SimpleRAG - Quick Start Guide (Docker)

## 🚀 Get Running in 2 Steps

### Step 1: Install Docker
```bash
# Install Docker Desktop from https://docs.docker.com/get-docker/
# That's the only prerequisite!
```

### Step 2: Run SimpleRAG
```bash
cd /Users/delon/Documents/code/projects/simplerag
./run.sh
```

**That's it!** The script will:
- Build Docker images
- Start PostgreSQL container
- Start Ollama container  
- Start application container
- Pull the llama2 model
- Set everything up automatically

### Step 3: Use the App
1. Open http://localhost:8000
2. Upload a document or click "🔄 Scan Folder"
3. Start chatting!

---

## 📝 Using Makefile (Recommended)

```bash
# Start everything
make up

# View logs
make logs

# Stop everything
make down

# See all commands
make help
```

---

## 🐳 Manual Docker Commands

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Pull Ollama model (first time only)
docker-compose exec ollama ollama pull llama2

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

---

## 🧪 Verify Installation

```bash
# Check services are running
docker-compose ps

# Should show 3 services: postgres, ollama, app (all "Up")

# Check logs for any errors
docker-compose logs app
```

---

## 📂 Upload Your First Document

**Option 1: Web Upload**
1. Click "Choose File" in sidebar
2. Select a PDF, DOCX, TXT, or XLSX file
3. Click "Upload"

**Option 2: Folder Scan**
1. Put files in `./documents_to_scan/`
2. Click "🔄 Scan Folder" in web interface
3. Files are auto-processed and removed from folder

---

## 💬 Chat with Your Documents

1. Wait for document to process (~2 seconds)
2. Type a question: "What is this document about?"
3. Get an AI answer with source references
4. Sources show which parts of which documents were used

---

## ⚙️ Configuration

Edit `.env` to customize:

```env
# Use different LLM model
LLM_MODEL=mistral          # Faster/better than llama2

# Adjust chunk size
CHUNK_SIZE=300             # Smaller = faster search
CHUNK_OVERLAP=30           

# Change ports/paths as needed
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/simplerag
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🔧 Troubleshooting

**Services not starting?**
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

**Port already in use?**
```bash
# Stop other containers
docker ps
docker stop <container_id>

# Or edit docker-compose.yml to change ports
```

**Ollama model issues?**
```bash
# Pull model manually
docker-compose exec ollama ollama pull llama2

# Check Ollama
curl http://localhost:11434/api/version
```

**Reset everything?**
```bash
# Stop and remove all data
docker-compose down -v
rm -rf chroma_db/* uploads/*

# Start fresh
./run.sh
```

---

## 📚 Supported File Types

- ✅ PDF (`.pdf`)
- ✅ Word (`.docx`, `.doc`)
- ✅ Text (`.txt`, `.md`)
- ✅ Excel (`.xlsx`, `.xls`)

---

## 🎯 Use Cases

- **Knowledge Base**: Upload company docs, search with natural language
- **Research**: Add papers, ask questions about findings
- **Documentation**: Search technical docs conversationally
- **Legal**: Review contracts by asking specific questions
- **Personal**: Organize notes, journals, articles

---

## 📊 System Requirements

**Minimum:**
- Python 3.11+
- 4GB RAM
- 2GB disk space

**Recommended:**
- 8GB+ RAM (for better LLM performance)
- SSD for faster vector search
- Modern CPU (for embeddings)

---

## 🌟 Key Features

✨ **100% Local** - All data stays on your machine
🔒 **Private** - No cloud services, no data leaks
⚡ **Fast** - Vector search returns results in <100ms
🤖 **Smart** - Uses AI for semantic understanding
📦 **Easy** - No build tools, no complex setup
🔄 **Reactive** - Real-time UI updates with Alpine.js

---

## 📖 More Information

- **Full Documentation**: See `README.md`
- **Detailed Setup**: See `SETUP.md`
- **Project Overview**: See `PROJECT_SUMMARY.md`
- **Specification**: `/Users/delon/Documents/code/projects/ai-rag-system/.githhub/copilot-instructions.md`

---

## 🆘 Getting Help

1. Check logs in terminal where you ran `python main.py`
2. Run `python test_system.py` to diagnose issues
3. Verify Ollama: `curl http://localhost:11434/api/version`
4. Check database: `psql simplerag -c "SELECT COUNT(*) FROM documents;"`

---

## 🎉 You're Ready!

Start by uploading the sample document:
```bash
# Already created at: ./documents_to_scan/sample.txt
# Just click "🔄 Scan Folder" in the web UI
```

Then ask: "What is SimpleRAG?" to test the system!

---

**Happy searching! 🔍**
