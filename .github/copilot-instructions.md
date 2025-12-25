# SimpleRAG Copilot Instructions

## Project Overview

SimpleRAG is a local, Dockerized Retrieval-Augmented Generation system using FastAPI, PostgreSQL, ChromaDB, and Ollama. It features a lightweight Alpine.js frontend.

## Architecture & Core Components

- **Backend**: Async FastAPI application (`main.py`).
- **Services Layer** (`services/`): Encapsulates all business logic.
  - `document_processor.py`: Handles text extraction (PDF, DOCX, etc.) and chunking.
  - `vector_store.py`: Manages ChromaDB interactions.
  - `rag_engine.py`: Orchestrates retrieval and LLM generation.
  - `document_service.py`: High-level CRUD and orchestration.
- **Data Storage**:
  - **PostgreSQL**: Stores document metadata and audit logs (`models.py`).
  - **ChromaDB**: Stores vector embeddings (persisted in `chroma_db/`).
  - **Filesystem**: Raw files in `uploads/` and `documents_to_scan/`.
- **Frontend**: Single-file SPA (`static/index.html`) using Alpine.js and TailwindCSS. No build step required.

## Critical Workflows

- **Running the App**: Always prefer Docker.
  - Start: `make up` (builds, starts services, pulls LLM model).
  - Stop: `make down`.
  - Logs: `make logs` or `make logs-app`.
- **Database Changes**: Schema defined in `models.py` and initialized via `init_db.sql` / `database.py`.
- **LLM Management**: Ollama runs in a container. Models are pulled automatically via `run.sh` or `make pull-model`.

## Coding Conventions

- **Async/Await**: Use `async def` for all route handlers and DB operations (`sqlalchemy.ext.asyncio`).
- **Configuration**: Use `config.py` (Pydantic `BaseSettings`) for all env vars.
- **Error Handling**: Raise `HTTPException` in routes; let services propagate standard Python exceptions.
- **Frontend**: Keep logic in `static/index.html` using Alpine.js directives (`x-data`, `x-on:click`). Do not introduce a JS build system.
- **Docker**: Service names (`postgres`, `ollama`) are hostnames within the Docker network.

## Key Files

- `main.py`: API entry point and dependency injection.
- `services/rag_engine.py`: Core RAG logic (Search + Generate).
- `docker-compose.yml`: Infrastructure definition.
- `Makefile`: Operational shortcuts.
