-- SimpleRAG Database Schema

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT,
    classification VARCHAR(50) DEFAULT 'internal',
    department VARCHAR(100),
    content_preview TEXT,
    metadata_json JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_classification ON documents(classification);
CREATE INDEX IF NOT EXISTS idx_documents_department ON documents(department);
CREATE INDEX IF NOT EXISTS idx_documents_active ON documents(is_active);
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin(metadata_json);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    word_count INTEGER,
    classification VARCHAR(50) DEFAULT 'internal',
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_classification ON document_chunks(classification);

CREATE TABLE IF NOT EXISTS query_audit_log (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response_time_ms INTEGER,
    documents_accessed JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_time ON query_audit_log(created_at DESC);
