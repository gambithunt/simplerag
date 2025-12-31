# SimpleRAG Learning Guide

## 📚 The Learning Plan

1.  **High-Level Overview**: The "Big Picture" architecture, Docker containers, and how the pieces fit together.
2.  **The Frontend & API Layer**: How the user interacts (`index.html`) and how requests enter the system (`main.py`).
3.  **Document Ingestion (The "R" in RAG - Part 1)**: How raw files (PDFs, DOCX) are turned into text (`document_service.py`).
4.  **Vector Storage (The "R" in RAG - Part 2)**: How text is turned into numbers and stored (`vector_store.py`, ChromaDB).
5.  **The RAG Engine (The "G" in RAG)**: How a question is answered using retrieval + generation (`rag_engine.py`).
6.  **Database & Configuration**: The glue holding it all together (`models.py`, `database.py`).

---

## Step 1: High-Level Overview

SimpleRAG is a **Local RAG (Retrieval-Augmented Generation)** system built with **LlamaIndex**.

**The Goal:** You upload a document (PDF, Word, etc.), and then you can ask an AI questions about it. The AI answers _only_ using the information from your documents.

### The Infrastructure (Docker)

The entire system runs on three main "computers" (containers) defined in `docker-compose.yml`.

1.  **`postgres`**:
    - **Role**: The "Librarian's Notebook".
    - **What it stores**: Document metadata. "File X was uploaded on Tuesday", "File Y has ID 5". It does _not_ store the vector embeddings, chunks, or the AI model.
2.  **`ollama`**:
    - **Role**: The "Brain".
    - **What it does**: It runs the Large Language Model (like Llama 2). It takes text and generates answers. It exposes an API on port `11434`.
3.  **`app`**:
    - **Role**: The "Coordinator" (Your Code).
    - **What it does**: This is the FastAPI Python application using LlamaIndex. It talks to the user (Frontend), talks to Postgres (to save metadata), talks to ChromaDB (to save vectors), and talks to Ollama (to get answers).

### Key Data Volumes (Folders)

The `app` container has access to four special folders on your hard drive:

- `uploads/`: Where files uploaded via the web UI are saved.
- `documents_to_scan/`: A "drop folder". If you manually paste a file here, the system can scan and ingest it automatically.
- `chroma_db/`: This is where the **Vector Database** lives. Unlike Postgres, ChromaDB is running _inside_ your Python app (embedded), but it saves its data here so it survives restarts.
- `model_cache/`: Caches the downloaded HuggingFace embedding model (BAAI/bge-large-en-v1.5) for faster startups.

### The Flow

1.  **User** -> Uploads PDF -> **App** saves to `uploads/`.
2.  **App** -> Uses LlamaIndex SimpleDirectoryReader -> Extracts Text -> Automatically chunks and embeds it.
3.  **App** -> LlamaIndex stores Vectors in `chroma_db/` and metadata in PostgreSQL.
4.  **User** -> Asks Question -> **App** uses LlamaIndex QueryEngine to search `chroma_db/`.
5.  **App** -> LlamaIndex sends Question + Relevant Text to **Ollama**.
6.  **Ollama** -> Generates Answer -> **App** sends answer to User

---

## Step 2: The Frontend & API Layer

Now that we know the containers, let's see how a user actually talks to the system.

### The Frontend (`static/index.html`)

This project uses a **"No-Build" Frontend**. There is no React build step, no Webpack, and no `node_modules` for the UI. It uses **Alpine.js** directly in the HTML file.

- **Why Alpine.js?** It allows us to add interactivity (like "click button -> send data") directly in the HTML without writing a separate JavaScript application.
- **Key Logic**: Look at the `<script>` tag at the bottom of `index.html`.
  - `uploadFile()`: Takes the file from the `<input>` and sends it to `POST /api/upload`.
  - `sendMessage()`: Takes the text from the chat box and sends it to `POST /api/query`.

### The Backend Entry Point (`main.py`)

This is the "Front Door" of the Python application. It uses **FastAPI**.

**1. Serving the UI**

```python
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Reads static/index.html and sends it to the browser
```

2. The Upload Route
   When you upload a file, it hits this endpoint:

````
@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), ...):
    # 1. Validates file extension (must be .pdf, .docx, etc.)
    # 2. Saves the raw file to the 'uploads/' folder
    # 3. Calls 'DocumentService' to process it (We will cover this in Step 3)
    ```

3. The Query Route
When you ask a question, it hits this endpoint:

````

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, ...): # 1. Receives your question text # 2. Calls 'RAGEngine' to find answers (We will cover this in Step 5) # 3. Returns the answer + sources

````

---

## Step 3: Document Ingestion (The "R" in RAG - Part 1)

This is where the magic begins. How do we turn a PDF into something an AI can understand? We use **LlamaIndex** for this.

### The Orchestrator: `DocumentService`
Located in `services/document_service.py`, this class manages the entire lifecycle of a document using LlamaIndex.

**The `process_and_store_document` method does 3 things:**
1.  **Extract Text**: Uses LlamaIndex's `SimpleDirectoryReader` to intelligently extract text from any supported file format (PDF, DOCX, TXT, etc.).
2.  **Save Metadata to Postgres**: Creates a `Document` record (filename, size, etc.) in the SQL database for tracking.
3.  **Index with LlamaIndex**: Uses `VectorStoreIndex.from_documents()` which automatically:
    - Chunks the text into optimal sizes (configured in `config.py`)
    - Generates embeddings using the configured embedding model
    - Stores everything in ChromaDB with proper metadata

### LlamaIndex's SimpleDirectoryReader
No need for manual format handling! LlamaIndex automatically detects and processes:
*   **PDF**: Extracts text and preserves structure
*   **DOCX**: Reads paragraphs and formatting
*   **Excel**: Converts tables to readable format
*   **Text/MD**: Direct ingestion

### Chunking (Handled by LlamaIndex)
AI models have a limit on how much text they can read at once (Context Window). LlamaIndex handles this intelligently:
*   **Automatic Chunking**: Text is split into pieces based on `chunk_size` in `config.py` (default: 512 tokens)
*   **Smart Overlap**: Uses `chunk_overlap` to maintain context between chunks
*   **No Manual Work**: All chunking logic is handled by LlamaIndex's node parser

### The "Scan Folder" Feature
There is a special method `scan_folder` in `DocumentService`.
*   It looks at the `documents_to_scan/` directory.
*   If it finds a file that isn't in the database yet, it automatically moves it to `uploads/` and triggers the LlamaIndex processing pipeline.
*   This is great for bulk-importing documents without using the UI.

---

## Step 4: Vector Storage & Embeddings (The "R" in RAG - Part 2)

We have text chunks. Now we need to make them searchable by *meaning*, not just by keywords. This is where **Embeddings** and **ChromaDB** come in, all managed by LlamaIndex.

### The Concept: Embeddings
Computers don't understand "The cat sat on the mat". They understand numbers.
*   **Embedding Model**: We use `BAAI/bge-large-en-v1.5`, a powerful embedding model optimized for accuracy on systems with 24GB RAM.
*   **Magic**: Sentences with similar meanings get similar numbers. "Hello" and "Hi" will be mathematically close. "Hello" and "Banana" will be far apart.

### LlamaIndex + ChromaDB Integration
The system uses LlamaIndex's `ChromaVectorStore` wrapper:
*   **Initialization**: `services/document_service.py` sets up the connection to ChromaDB
*   **Automatic Embedding**: When documents are indexed, LlamaIndex automatically generates embeddings
*   **Persistent Storage**: All vectors and metadata are stored in `chroma_db/` directory

### Global Configuration: `llm_factory.py`
This is the central configuration point:
```python
Settings.llm = Ollama(...)  # Configure Ollama LLM
Settings.embed_model = resolve_embed_model("local:BAAI/bge-large-en-v1.5")  # Configure embeddings
Settings.chunk_size = 512  # Optimal chunk size
Settings.chunk_overlap = 50  # Context preservation
```

All LlamaIndex operations use these global settings, ensuring consistency across the application.

---

## Step 5: The RAG Engine (The "G" in RAG)

This is the brain of the operation. It combines the search results (Retrieval) with the LLM (Generation) using **LlamaIndex's QueryEngine**.

### The Orchestrator: `RAGEngine`

Located in `services/rag_engine.py`, this class uses LlamaIndex to handle the complete RAG pipeline.

**The `query` method workflow:**

1.  **Initialize QueryEngine**:
    - Creates a `VectorStoreIndex` from the existing ChromaDB collection
    - Converts it to a `QueryEngine` with `index.as_query_engine(similarity_top_k=top_k)`
    - LlamaIndex handles all the complex retrieval and generation logic

2.  **Query Execution**:
    - Simply calls `response = query_engine.query(question)`
    - LlamaIndex automatically:
      - Embeds the question
      - Searches ChromaDB for relevant chunks
      - Constructs an optimal prompt
      - Sends it to Ollama (configured in `llm_factory.py`)
      - Generates a coherent answer

3.  **Extract Sources**:
    - Loop through `response.source_nodes`
    - Each node contains:
      - `node.text`: The relevant chunk text
      - `node.metadata`: Document ID, filename, etc.
      - `node.score`: Relevance score for ranking

4.  **Audit**:
    - Saves the query and response time to `query_audit_logs` table in Postgres
    - Tracks which documents were accessed for the answer

### The LlamaIndex Advantage

Previously, we manually:
- Built prompts
- Called Ollama via HTTP
- Handled errors and fallbacks

Now LlamaIndex:
- Automatically constructs optimal prompts
- Manages LLM communication
- Handles retries and error cases
- Provides better context management

All configuration happens once in `llm_factory.py`, and every query benefits from it.

---

## Step 6: Database & Configuration

Finally, let's look at the foundation that holds the data and settings.

### The Database Models (`models.py`)

We use **SQLAlchemy** to define our Postgres tables.

1.  **`Document`**:

    - The master record for every file.
    - Stores `filename`, `file_path`, `file_size_bytes`, and `metadata_json`.
    - Has an `is_active` flag (Soft Delete). When you delete a file, we just set this to `False` instead of destroying the record immediately.

2.  **`QueryAuditLog`**:

    - Tracks every query made to the system.
    - Stores the question, response time, and which documents were accessed.
    - Useful for analytics and debugging.

**Note**: The `DocumentChunk` table has been removed. Chunking and storage are now fully handled by LlamaIndex and ChromaDB, which is more efficient and reduces database complexity.

3.  **`QueryAuditLog`**:
    - A history of every question asked.
    - Stores `query`, `response_time_ms`, and which documents were used (`documents_accessed`).

### Database Connection (`database.py`)

- **Async**: We use `AsyncSession` and `create_async_engine`. This is modern Python (FastAPI) best practice. It means the server doesn't "freeze" while waiting for the database to reply.
- **`get_db`**: This is a dependency injection helper. Every API route that needs the DB calls this function to get a fresh session.

### Configuration (`config.py`)

- We use **Pydantic Settings**.
- It reads from environment variables (or a `.env` file).
- **Key Settings**:
  - `CHUNK_SIZE`: Controls how big the text pieces are (default 500 words).
  - `LLM_MODEL`: Which AI brain to use (default `llama2`).
  - `OLLAMA_BASE_URL`: Where to find the AI (default `http://ollama:11434`).

---

## 🎓 Conclusion

You now understand the full lifecycle of SimpleRAG:

1.  **Docker** spins up Postgres, Ollama, and the App.
2.  **FastAPI** serves the **Alpine.js** frontend.
3.  **DocumentService** ingests files, chunks them, and saves them to **Postgres** and **ChromaDB**.
4.  **RAGEngine** searches vectors in ChromaDB and sends the context to **Ollama**.
5.  **Ollama** generates the final answer.

**Next Steps:**

- Try uploading a document and watching the logs (`make logs-app`) to see the chunking happen in real-time.
- Look at `services/rag_engine.py` and try changing the prompt to give the AI a different personality!

# Connection to db

Fill in these details:
Host name/address: localhost
Port: 5432
Maintenance database: app_db
Username: postgres
Password: postgres

What You'll See:

Once connected, expand the tree:
Servers
└── AI RAG System
└── Databases
└── app_db
└── Schemas
└── public
└── Tables
├── alembic_version
├── document_chunks
└── documents

---

Useful Queries to Run:

View All Documents

Right-click on documents table → View/Edit Data → All Rows

Or use the Query Tool:
SELECT id, original_filename, file_type, status, chunk_count, created_at
FROM documents
ORDER BY created_at DESC;

View Document Chunks

SELECT dc.id, dc.document_id, d.original_filename, dc.chunk_index,
LEFT(dc.chunk_text, 100) as chunk_preview
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id
ORDER BY dc.document_id, dc.chunk_index;

Count Documents by Status

SELECT status, COUNT(\*) as count
FROM documents
GROUP BY status;

Find Stuck Documents

SELECT id, original_filename, status,
NOW() - created_at as age
FROM documents
WHERE status = 'processing'
AND created_at < NOW() - INTERVAL '5 minutes';

---

# Quick & Free:

## Connect to database

docker exec -it airag_postgres psql -U postgres -d app_db

# Once connected, useful commands:

\dt # List all tables
\d documents # Describe documents table
\q # Quit
