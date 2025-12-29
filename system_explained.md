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

SimpleRAG is a **Local RAG (Retrieval-Augmented Generation)** system.

**The Goal:** You upload a document (PDF, Word, etc.), and then you can ask an AI questions about it. The AI answers _only_ using the information from your documents.

### The Infrastructure (Docker)

The entire system runs on three main "computers" (containers) defined in `docker-compose.yml`.

1.  **`postgres`**:
    - **Role**: The "Librarian's Notebook".
    - **What it stores**: Metadata. "File X was uploaded on Tuesday", "File Y has ID 5". It does _not_ store the vector embeddings or the AI model.
2.  **`ollama`**:
    - **Role**: The "Brain".
    - **What it does**: It runs the Large Language Model (like Llama 2 or Mistral). It takes text and generates answers. It exposes an API on port `11434`.
3.  **`app`**:
    - **Role**: The "Coordinator" (Your Code).
    - **What it does**: This is the FastAPI Python application. It talks to the user (Frontend), talks to Postgres (to save metadata), talks to ChromaDB (to save vectors), and talks to Ollama (to get answers).

### Key Data Volumes (Folders)

The `app` container has access to three special folders on your hard drive:

- `uploads/`: Where files uploaded via the web UI are saved.
- `documents_to_scan/`: A "drop folder". If you manually paste a file here, the system can scan and ingest it automatically.
- `chroma_db/`: This is where the **Vector Database** lives. Unlike Postgres, ChromaDB is running _inside_ your Python app (embedded), but it saves its data here so it survives restarts.

### The Flow

1.  **User** -> Uploads PDF -> **App** saves to `uploads/`.
2.  **App** -> Reads PDF -> Extracts Text -> Turns text into Numbers (Vectors).
3.  **App** -> Saves Vectors to `chroma_db/` and Metadata to `postgres`.
4.  **User** -> Asks Question -> **App** searches `chroma_db/` for relevant text.
5.  **App** -> Sends Question + Relevant Text to **Ollama**.
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

This is where the magic begins. How do we turn a PDF into something an AI can understand?

### The Orchestrator: `DocumentService`
Located in `services/document_service.py`, this class manages the entire lifecycle of a document.

**The `process_and_store_document` method does 4 things:**
1.  **Extract Text**: Calls `DocumentProcessor` to pull raw text from the file.
2.  **Save to Postgres**: Creates a `Document` record (filename, size, etc.) in the SQL database.
3.  **Chunking**: Splits the massive text into smaller pieces (e.g., 500 words each).
4.  **Vectorize**: Sends these chunks to `VectorStore` (ChromaDB) to be turned into numbers.

### The Worker: `DocumentProcessor`
Located in `services/document_processor.py`, this is a utility class that knows how to read different file formats.

**1. Text Extraction**
It switches logic based on file extension:
*   **PDF**: Uses `PyPDF2` to read page by page.
*   **DOCX**: Uses `python-docx` to read paragraphs.
*   **Excel**: Uses `openpyxl` to read rows and joins cells with `|`.
*   **Text/MD**: Reads directly.

**2. Chunking (Crucial Concept)**
AI models have a limit on how much text they can read at once (Context Window). We cannot feed a 100-page PDF into Llama 2 in one go.
*   **The Solution**: We break the text into "Chunks".
*   **The Code**: `chunk_text` method splits text into groups of words (defined in `config.py`, usually ~500 words) with a small "overlap" (e.g., 50 words) to ensure context isn't lost between cuts.

### The "Scan Folder" Feature
There is a special method `scan_folder` in `DocumentService`.
*   It looks at the `documents_to_scan/` directory.
*   If it finds a file that isn't in the database yet, it automatically moves it to `uploads/` and triggers the processing pipeline.
*   This is great for bulk-importing documents without using the UI.

---

## Step 4: Vector Storage (The "R" in RAG - Part 2)

We have text chunks. Now we need to make them searchable by *meaning*, not just by keywords. This is where **Embeddings** and **ChromaDB** come in.

### The Concept: Embeddings
Computers don't understand "The cat sat on the mat". They understand numbers.
*   **Embedding Model**: A small AI model (specifically `all-MiniLM-L6-v2` in this project) that reads text and outputs a list of 384 numbers (a vector).
*   **Magic**: Sentences with similar meanings get similar numbers. "Hello" and "Hi" will be mathematically close. "Hello" and "Banana" will be far apart.

### The Manager: `VectorStore`
Located in `services/vector_store.py`, this class wraps ChromaDB.

**1. Initialization**
```python
self.client = chromadb.Client(...)
self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
````

**2. Upserting Vectors (The "Store" part)**

```python
def upsert(self, document_id: str, text: str, metadata: dict):
    # 1. Embeds the text using the embedding model
    # 2. Upserts the vector into ChromaDB with associated metadata
```

**3. Querying Vectors (The "Retrieve" part)**

```python
def query(self, query_text: str, top_k: int = 5):
    # 1. Embeds the query text
    # 2. Searches ChromaDB for the top_k most similar vectors
    # 3. Returns the associated metadata
```

---

## Step 5: The RAG Engine (The "G" in RAG)

This is the brain of the operation. It combines the search results (Retrieval) with the LLM (Generation) to give you a coherent answer.

### The Orchestrator: `RAGEngine`

Located in `services/rag_engine.py`, this class ties everything together.

**The `query` method workflow:**

1.  **Retrieve (`self.vector_store.search`)**:

    - It takes your question ("How do I reset my password?").
    - It asks ChromaDB for the top 5 most relevant text chunks.
    - _Result_: A list of raw text snippets from your PDF.

2.  **Augment (Building the Context)**:

    - It loops through the search results.
    - It fetches the filename from Postgres (so it can say "Source: Manual.pdf").
    - It constructs a big string called `context` that looks like this:

      ```text
      Document: Manual.pdf

      To reset your password, go to settings...

      Document: Policy.docx
      Passwords must be 8 characters...
      ```

3.  **Generate (`_generate_answer`)**:

    - It constructs a **Prompt** for the LLM:

      ```text
      You are a helpful assistant. Answer the question based on the context provided.

      Context:
      [The big string from step 2]

      Question: How do I reset my password?
      ```

    - It sends this prompt to **Ollama** (running in the other Docker container) via HTTP POST.

4.  **Audit**:
    - It saves the query and response time to the `query_audit_logs` table in Postgres. This is useful for seeing what users are asking.

### The LLM Connection

- **Tool**: `httpx` (an async HTTP client).
- **Endpoint**: `http://ollama:11434/api/generate`.
- **Model**: Defined in `config.py` (default: `llama2`).
- **Fallback**: If Ollama is down, the code catches the error and returns the raw context snippets instead, so the user still gets _some_ information.

---

## Step 6: Database & Configuration

Finally, let's look at the foundation that holds the data and settings.

### The Database Models (`models.py`)

We use **SQLAlchemy** to define our Postgres tables.

1.  **`Document`**:

    - The master record for every file.
    - Stores `filename`, `file_path`, `file_size_bytes`, and `metadata_json`.
    - Has an `is_active` flag (Soft Delete). When you delete a file, we just set this to `False` instead of destroying the record immediately.

2.  **`DocumentChunk`**:

    - Stores the actual text pieces.
    - Linked to `Document` via `document_id`.
    - _Note_: We store the text here _and_ in ChromaDB. Why? ChromaDB is for searching, Postgres is for reliable storage and display.

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
