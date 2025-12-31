# LlamaIndex Migration Plan

This plan outlines the steps to migrate SimpleRAG from a manual RAG implementation to a LlamaIndex-based architecture.

## Phase 1: Preparation & Dependencies

1.  **Create Feature Branch**: `git checkout -b feature/llamaindex-migration`
2.  **Update `requirements.txt`**:
    - Remove: `pypdf2`, `python-docx`, `openpyxl`, `sentence-transformers` (LlamaIndex handles these).
    - Add:
      - `llama-index`
      - `llama-index-vector-stores-chroma`
      - `llama-index-llms-ollama`
      - `llama-index-embeddings-huggingface`

## Phase 2: Core Configuration

3.  **Create `services/llm_factory.py`**:
    - Import `Settings` from `llama_index.core`.
    - Configure `Settings.llm` to use `Ollama` (pointing to `config.ollama_base_url`).
    - Configure `Settings.embed_model` to use `HuggingFaceEmbedding` (model: `BAAI/bge-small-en-v1.5`).
    - Create a function `init_llama_index()` to be called at app startup.

## Phase 3: Ingestion Layer (The "R")

4.  **Refactor `services/document_service.py`**:
    - **Delete** usage of `DocumentProcessor`.
    - **Implement** `SimpleDirectoryReader` to load files from `uploads/`.
    - **Implement** `ChromaVectorStore` connection:
      ```python
      db = chromadb.PersistentClient(path=settings.chroma_persist_dir)
      chroma_collection = db.get_or_create_collection("documents")
      vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
      ```
    - **Implement** Indexing:
      ```python
      storage_context = StorageContext.from_defaults(vector_store=vector_store)
      VectorStoreIndex.from_documents(documents, storage_context=storage_context)
      ```
    - _Note_: Keep the SQL `Document` creation logic to maintain the metadata database.

## Phase 4: Query Layer (The "G")

5.  **Refactor `services/rag_engine.py`**:
    - Remove manual `vector_store.search` and prompt construction.
    - Initialize `VectorStoreIndex` from the existing `vector_store`.
    - Create a query engine: `query_engine = index.as_query_engine()`.
    - Return the response.

## Phase 5: Cleanup

6.  **Delete Obsolete Files**:
    - `services/document_processor.py` (No longer needed).
    - `services/vector_store.py` (Logic moved to `document_service` or `rag_engine` via LlamaIndex wrappers).

## Phase 6: Verification// filepath: plan.md

# LlamaIndex Migration Plan

This plan outlines the steps to migrate SimpleRAG from a manual RAG implementation to a LlamaIndex-based architecture.

## Phase 1: Preparation & Dependencies

1.  **Create Feature Branch**: `git checkout -b feature/llamaindex-migration`
2.  **Update `requirements.txt`**:
    - Remove: `pypdf2`, `python-docx`, `openpyxl`, `sentence-transformers` (LlamaIndex handles these).
    - Add:
      - `llama-index`
      - `llama-index-vector-stores-chroma`
      - `llama-index-llms-ollama`
      - `llama-index-embeddings-huggingface`

## Phase 2: Core Configuration

3.  **Create `services/llm_factory.py`**:
    - Import `Settings` from `llama_index.core`.
    - Configure `Settings.llm` to use `Ollama` (pointing to `config.ollama_base_url`).
    - Configure `Settings.embed_model` to use `HuggingFaceEmbedding` (model: `BAAI/bge-small-en-v1.5`).
    - Create a function `init_llama_index()` to be called at app startup.

## Phase 3: Ingestion Layer (The "R")

4.  **Refactor `services/document_service.py`**:
    - **Delete** usage of `DocumentProcessor`.
    - **Implement** `SimpleDirectoryReader` to load files from `uploads/`.
    - **Implement** `ChromaVectorStore` connection:
      ```python
      db = chromadb.PersistentClient(path=settings.chroma_persist_dir)
      chroma_collection = db.get_or_create_collection("documents")
      vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
      ```
    - **Implement** Indexing:
      ```python
      storage_context = StorageContext.from_defaults(vector_store=vector_store)
      VectorStoreIndex.from_documents(documents, storage_context=storage_context)
      ```
    - _Note_: Keep the SQL `Document` creation logic to maintain the metadata database.

## Phase 4: Query Layer (The "G")

5.  **Refactor `services/rag_engine.py`**:
    - Remove manual `vector_store.search` and prompt construction.
    - Initialize `VectorStoreIndex` from the existing `vector_store`.
    - Create a query engine: `query_engine = index.as_query_engine()`.
    - Return the response.

## Phase 5: Cleanup

6.  **Delete Obsolete Files**:
    - `services/document_processor.py` (No longer needed).
    - `services/vector_store.py` (Logic moved to `document_service` or `rag_engine` via LlamaIndex wrappers).

## Phase 6: Verification
