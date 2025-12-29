import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from config import settings


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_dir,
            anonymized_telemetry=False
        ))

        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        self.embedding_model = SentenceTransformer(settings.embedding_model)

    async def add_chunks(
        self,
        chunks: List[str],
        document_id: int,
        metadata: List[Dict[str, Any]] = None
    ):
        embeddings = self.embedding_model.encode(chunks, convert_to_numpy=True)

        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]

        if metadata is None:
            metadata = [{"document_id": document_id, "chunk_index": i}
                        for i in range(len(chunks))]
        else:
            for i, meta in enumerate(metadata):
                meta.update({"document_id": document_id, "chunk_index": i})

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=metadata
        )

    async def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        query_embedding = self.embedding_model.encode(
            [query], convert_to_numpy=True)

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        return results

    async def delete_document(self, document_id: int):
        results = self.collection.get(
            where={"document_id": document_id}
        )

        if results['ids']:
            self.collection.delete(ids=results['ids'])
