from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/simplerag"
    
    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"
    scan_dir: str = "./documents_to_scan"
    model_cache_dir: str = "./model_cache"
    
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama2"
    
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.scan_dir).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
Path(settings.model_cache_dir).mkdir(parents=True, exist_ok=True)
