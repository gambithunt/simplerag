import os
import shutil
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from models import Document
from schemas import DocumentCreate
from config import settings


class DocumentService:
    def __init__(self):
        db = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        chroma_collection = db.get_or_create_collection("documents")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
    
    async def process_and_store_document(
        self, 
        file_path: str,
        filename: str,
        classification: str,
        department: str,
        db: AsyncSession
    ) -> Document:
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if not documents:
            raise ValueError("Failed to extract content from document")
        
        text_content = "\n\n".join([doc.text for doc in documents])
        file_stat = os.stat(file_path)
        file_ext = Path(file_path).suffix
        
        doc_data = DocumentCreate(
            filename=filename,
            file_path=file_path,
            file_type=file_ext,
            file_size_bytes=file_stat.st_size,
            classification=classification,
            department=department,
            content_preview=text_content[:500] if text_content else None,
            metadata_json={"file_extension": file_ext, "size": file_stat.st_size}
        )
        
        db_document = Document(**doc_data.model_dump())
        db.add(db_document)
        await db.flush()
        
        for doc in documents:
            doc.metadata["document_id"] = db_document.id
            doc.metadata["filename"] = filename
            doc.metadata["classification"] = classification
        
        VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context
        )
        
        await db.commit()
        await db.refresh(db_document)
        
        return db_document
    
    async def scan_folder(self, db: AsyncSession) -> Tuple[int, int, List[str]]:
        scan_path = Path(settings.scan_dir)
        
        if not scan_path.exists():
            return 0, 0, ["Scan directory does not exist"]
        
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls']
        files = [f for f in scan_path.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]
        
        files_found = len(files)
        files_processed = 0
        errors = []
        
        for file_path in files:
            try:
                result = await db.execute(
                    select(Document).where(Document.filename == file_path.name)
                )
                existing_doc = result.scalar_one_or_none()
                
                if existing_doc:
                    errors.append(f"{file_path.name}: Already exists in database")
                    continue
                
                destination = Path(settings.upload_dir) / file_path.name
                shutil.copy2(file_path, destination)
                
                await self.process_and_store_document(
                    str(destination),
                    file_path.name,
                    "internal",
                    None,
                    db
                )
                
                files_processed += 1
                
                file_path.unlink()
                
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")
        
        return files_found, files_processed, errors
    
    async def get_all_documents(self, db: AsyncSession) -> List[Document]:
        result = await db.execute(
            select(Document).where(Document.is_active == True).order_by(Document.created_at.desc())
        )
        return result.scalars().all()
    
    async def delete_document(self, document_id: int, db: AsyncSession) -> bool:
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        document.is_active = False
        await db.commit()
        
        try:
            chroma_db = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            collection = chroma_db.get_collection("documents")
            results = collection.get(where={"document_id": document_id})
            if results['ids']:
                collection.delete(ids=results['ids'])
        except Exception:
            pass
        
        return True
