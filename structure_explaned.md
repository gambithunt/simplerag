# Project Structure Explained

This document explains the layout and purpose of each part of the SimpleRAG repository.

---

## 1. Top-Level Structure

```
simplerag/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── services/
│   ├── document_processor.py
│   ├── vector_store.py
│   ├── rag_engine.py
│   └── document_service.py
├── static/
│   └── index.html
├── uploads/
├── documents_to_scan/
├── chroma_db/
├── test_system.py
├── requirements.txt
├── *.md (docs)
└── ...other scripts
```

---

## 2. Folder & File Breakdown

### Core App Code

- **main.py**  
  FastAPI application entry point. Defines the web server, API routes, and launches the app.

- **config.py**  
  Handles configuration (reads environment variables, sets up app settings).

- **database.py**  
  Sets up the database connection (PostgreSQL, via SQLAlchemy/asyncpg).

- **models.py**  
  SQLAlchemy models: defines the database tables (e.g., Document, AuditLog).

- **schemas.py**  
  Pydantic schemas: defines the data shapes for API requests/responses.

---

### Services (Business Logic Layer)

- **services/document_processor.py**  
  Extracts text from documents (PDF, DOCX, TXT, etc.), splits into chunks for embedding.

- **services/vector_store.py**  
  Handles vector database (ChromaDB) operations: storing, searching, and retrieving embeddings.

- **services/rag_engine.py**  
  The RAG (Retrieval-Augmented Generation) engine: combines search results with LLM (Ollama) to generate answers.

- **services/document_service.py**  
  Manages document metadata, upload, deletion, and scanning logic.

---

### Frontend

- **static/index.html**  
  The web UI (Alpine.js, minimal JS/CSS). Provides the chat interface and document upload.

---

### Data & Storage

- **uploads/**  
  Stores user-uploaded documents (bind-mounted in Docker for persistence).

- **documents_to_scan/**  
  Folder for bulk document ingestion (drop files here to auto-scan).

- **chroma_db/**  
  Stores ChromaDB vector database files (bind-mounted for persistence).

---

### Infrastructure & DevOps

- **Dockerfile**  
  Builds the app container (Python, FastAPI, dependencies).

- **docker-compose.yml**  
  Orchestrates all services: app, PostgreSQL, Ollama (LLM), and volumes.

- **Makefile**  
  Provides handy commands for building, running, and managing the stack.

- **requirements.txt**  
  Python dependencies.

- **init_db.sql**  
  SQL script to initialize the database schema.

- **run.sh, docker-run-local.sh, verify-docker.sh**  
  Helper scripts for running and verifying the app (with or without Docker).

---

### Docs & Misc

- **README.md, QUICKSTART.md, SETUP.md, PROJECT_SUMMARY.md, DOCKER.md, DOCKER_SUMMARY.md, CHANGES.md**  
  Documentation files for setup, usage, architecture, and change history.

- **test_system.py**  
  System-level tests (likely for API endpoints and integration).

---

## 3. Visual Folder Diagram

```
simplerag/
│
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
│
├── services/
│   ├── document_processor.py
│   ├── vector_store.py
│   ├── rag_engine.py
│   └── document_service.py
│
├── static/
│   └── index.html
│
├── uploads/
├── documents_to_scan/
├── chroma_db/
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── test_system.py
├── *.md (docs)
└── ...scripts
```

---

## 4. How It All Fits Together

- **User uploads a document** via the web UI (`static/index.html`).
- **Backend (`main.py`)** receives the file, uses `services/document_processor.py` to extract and chunk text.
- **Chunks are embedded** and stored in **ChromaDB** via `services/vector_store.py`.
- **Metadata** is stored in **PostgreSQL** (`models.py`, `database.py`).
- **User asks a question** in the chat UI.
- **RAG engine (`services/rag_engine.py`)**:
  - Searches ChromaDB for relevant chunks.
  - Sends context + question to **Ollama** (local LLM).
  - Returns the answer and sources to the user.
- **All services** (app, DB, LLM) are managed by **Docker Compose** for easy setup and persistence.

---

## 5. Summary Table

| Folder/File          | Purpose                                                |
| -------------------- | ------------------------------------------------------ |
| `main.py`            | FastAPI app entrypoint, API routes                     |
| `config.py`          | App configuration                                      |
| `database.py`        | DB connection setup                                    |
| `models.py`          | SQLAlchemy models                                      |
| `schemas.py`         | Pydantic schemas for API                               |
| `services/`          | Core business logic (processing, RAG, vector DB, docs) |
| `static/`            | Frontend (HTML/JS)                                     |
| `uploads/`           | Uploaded docs (persisted)                              |
| `documents_to_scan/` | Folder for bulk ingestion                              |
| `chroma_db/`         | Vector DB storage                                      |
| `Dockerfile`         | App container build                                    |
| `docker-compose.yml` | Orchestration of all services                          |
| `Makefile`           | Dev commands                                           |
| `requirements.txt`   | Python dependencies                                    |
| `*.md`               | Documentation                                          |
| `test_system.py`     | System/integration tests                               |

---

## 6. TL;DR

- **/services/** = All the brains (processing, search, RAG, doc mgmt)
- **/static/** = The face (web UI)
- **/uploads/, /documents_to_scan/, /chroma_db/** = The memory (data storage)
- **Docker, Compose, Makefile** = The skeleton (infrastructure)
- **main.py, config.py, models.py, schemas.py** = The glue (API, config, DB, data shapes)
- **Docs** = The manual

---

If you want a deeper dive into any specific file or flow, just check this file or ask for more details!
