# SimpleRAG Copilot Instructions

## Project Overview

SimpleRAG is a local, Dockerized Retrieval-Augmented Generation system using FastAPI, PostgreSQL, ChromaDB, and Ollama. **It uses LlamaIndex as the core framework for document ingestion, indexing, and retrieval.**

## Architecture & Core Components

- **Backend**: Async FastAPI application (`main.py`).
- **Services Layer** (`services/`): Encapsulates all business logic using LlamaIndex.
  - `llm_factory.py`: Central configuration for LlamaIndex `Settings` (Ollama LLM + HuggingFace Embeddings).
  - `document_service.py`: Handles document ingestion using `SimpleDirectoryReader` and `VectorStoreIndex`.
  - `rag_engine.py`: Orchestrates retrieval and generation using LlamaIndex `QueryEngine`.
- **Data Storage**:
  - **PostgreSQL**: Stores document metadata (filename, upload date) and audit logs (`models.py`).
  - **ChromaDB**: Stores vector embeddings via LlamaIndex `ChromaVectorStore` (persisted in `chroma_db/`).
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

- **LlamaIndex**: Use `llama_index.core` abstractions (`VectorStoreIndex`, `SimpleDirectoryReader`, `Settings`) instead of manual vector math.
- **Async/Await**: Use `async def` for all route handlers and DB operations. Note: LlamaIndex operations may be synchronous; wrap them or use async variants where available.
- **Configuration**: Use `config.py` (Pydantic `BaseSettings`) for all env vars.
- **Error Handling**: Raise `HTTPException` in routes; let services propagate standard Python exceptions.
- **Frontend**: Keep logic in `static/index.html` using Alpine.js directives.
- **Docker**: Service names (`postgres`, `ollama`) are hostnames within the Docker network.

## Key Files

- `main.py`: API entry point and dependency injection.
- `services/llm_factory.py`: LlamaIndex global settings initialization.
- `services/rag_engine.py`: Query logic.
- `docker-compose.yml`: Infrastructure definition.
- `Makefile`: Operational shortcuts.
