from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil
from typing import List

from database import get_db, init_db
from schemas import QueryRequest, QueryResponse, DocumentResponse, ScanStatusResponse
from services.rag_engine import RAGEngine
from services.document_service import DocumentService
from services.llm_factory import init_llama_index
from config import settings

app = FastAPI(title="SimpleRAG", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    init_llama_index()
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = Path("static/index.html")
    if html_path.exists():
        return html_path.read_text()
    return "<h1>SimpleRAG is running. Please create static/index.html</h1>"


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    rag_engine = RAGEngine()
    return await rag_engine.query(request.question, request.top_k, db)


@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    classification: str = Form("internal"),
    department: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
        )
    
    file_path = Path(settings.upload_dir) / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        doc_service = DocumentService()
        document = await doc_service.process_and_store_document(
            str(file_path),
            file.filename,
            classification,
            department,
            db
        )
        return document
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@app.post("/api/scan", response_model=ScanStatusResponse)
async def scan_documents(db: AsyncSession = Depends(get_db)):
    doc_service = DocumentService()
    files_found, files_processed, errors = await doc_service.scan_folder(db)
    
    return ScanStatusResponse(
        status="completed",
        files_found=files_found,
        files_processed=files_processed,
        errors=errors
    )


@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    doc_service = DocumentService()
    return await doc_service.get_all_documents(db)


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    doc_service = DocumentService()
    success = await doc_service.delete_document(document_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
