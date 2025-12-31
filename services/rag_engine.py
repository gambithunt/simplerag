import time
import chromadb
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from models import Document, QueryAuditLog
from schemas import Source, QueryResponse
from config import settings


class RAGEngine:
    def __init__(self):
        db = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        chroma_collection = db.get_or_create_collection("documents")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(vector_store)
    
    async def query(self, question: str, top_k: int, db: AsyncSession) -> QueryResponse:
        start_time = time.time()
        
        query_engine = self.index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(question)
        
        sources = []
        doc_ids = []
        
        for node in response.source_nodes:
            document_id = node.metadata.get('document_id')
            filename = node.metadata.get('filename', 'Unknown')
            
            if document_id:
                doc_ids.append(document_id)
                
                chunk_text = node.text
                relevance_score = node.score if node.score else 0.0
                
                sources.append(Source(
                    document_id=document_id,
                    filename=filename,
                    chunk_text=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    relevance_score=round(relevance_score, 3)
                ))
        
        answer = str(response)
        response_time = int((time.time() - start_time) * 1000)
        
        audit_log = QueryAuditLog(
            query=question,
            response_time_ms=response_time,
            documents_accessed=list(set(doc_ids))
        )
        db.add(audit_log)
        await db.commit()
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            response_time_ms=response_time
        )
