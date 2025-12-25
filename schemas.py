from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    classification: str = "internal"
    department: Optional[str] = None


class DocumentCreate(DocumentBase):
    file_path: str
    file_size_bytes: int
    content_preview: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    id: int
    file_size_bytes: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    document_id: int
    filename: str
    chunk_text: str
    relevance_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    response_time_ms: int


class ScanStatusResponse(BaseModel):
    status: str
    files_found: int
    files_processed: int
    errors: List[str]
