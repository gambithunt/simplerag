import time
import httpx
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Document, DocumentChunk, QueryAuditLog
from schemas import Source, QueryResponse
from services.vector_store import VectorStore
from config import settings


class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStore()
    
    async def query(self, question: str, top_k: int, db: AsyncSession) -> QueryResponse:
        start_time = time.time()
        
        search_results = await self.vector_store.search(question, top_k)
        
        sources = []
        context_parts = []
        doc_ids = []
        
        if search_results['ids'] and len(search_results['ids'][0]) > 0:
            for i, doc_id in enumerate(search_results['ids'][0]):
                metadata = search_results['metadatas'][0][i]
                document_id = metadata['document_id']
                doc_ids.append(document_id)
                
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = result.scalar_one_or_none()
                
                if doc:
                    chunk_text = search_results['documents'][0][i]
                    distance = search_results['distances'][0][i]
                    relevance_score = 1 - distance
                    
                    sources.append(Source(
                        document_id=document_id,
                        filename=doc.filename,
                        chunk_text=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                        relevance_score=round(relevance_score, 3)
                    ))
                    
                    context_parts.append(f"Document: {doc.filename}\n{chunk_text}")
        
        context = "\n\n".join(context_parts)
        answer = await self._generate_answer(question, context)
        
        response_time = int((time.time() - start_time) * 1000)
        
        audit_log = QueryAuditLog(
            query=question,
            response_time_ms=response_time,
            documents_accessed=doc_ids
        )
        db.add(audit_log)
        await db.commit()
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            response_time_ms=response_time
        )
    
    async def _generate_answer(self, question: str, context: str) -> str:
        if not context:
            return "I couldn't find any relevant information to answer your question."
        
        prompt = f"""You are a helpful assistant. Answer the question based on the context provided.

Context:
{context}

Question: {question}

Answer (be concise and accurate):"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.llm_model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No answer generated.")
                else:
                    return f"Error generating answer: {response.status_code}"
        except Exception as e:
            return f"Based on the documents, here's what I found:\n\n{context[:500]}...\n\n(Note: LLM is unavailable: {str(e)})"
