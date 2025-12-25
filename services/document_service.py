import os
import shutil
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Document, DocumentChunk
from schemas import DocumentCreate
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from config import settings


class DocumentService:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore()
    
    async def process_and_store_document(
        self, 
        file_path: str,
        filename: str,
        classification: str,
        department: str,
        db: AsyncSession
    ) -> Document:
        text = await self.processor.extract_text(file_path)
        
        metadata = self.processor.get_file_metadata(file_path)
        
        doc_data = DocumentCreate(
            filename=filename,
            file_path=file_path,
            file_type=metadata['extension'],
            file_size_bytes=metadata['size'],
            classification=classification,
            department=department,
            content_preview=text[:500] if text else None,
            metadata_json=metadata
        )
        
        db_document = Document(**doc_data.model_dump())
        db.add(db_document)
        await db.flush()
        
        chunks = self.processor.chunk_text(text)
        
        for idx, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=db_document.id,
                chunk_index=idx,
                text=chunk,
                word_count=len(chunk.split()),
                classification=classification
            )
            db.add(db_chunk)
        
        await db.commit()
        await db.refresh(db_document)
        
        await self.vector_store.add_chunks(chunks, db_document.id)
        
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
        
        await self.vector_store.delete_document(document_id)
        
        return True
