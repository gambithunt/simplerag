from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from config import settings as app_settings


def init_llama_index():
    """Initialize LlamaIndex global settings with Ollama LLM and HuggingFace embeddings."""
    
    Settings.llm = Ollama(
        model=app_settings.llm_model,
        base_url=app_settings.ollama_base_url,
        request_timeout=120.0
    )
    
    Settings.embed_model = resolve_embed_model(f"local:{app_settings.embedding_model}")
    
    Settings.chunk_size = app_settings.chunk_size
    Settings.chunk_overlap = app_settings.chunk_overlap
