#!/usr/bin/env python3
"""
Quick test script to verify SimpleRAG components
"""
import asyncio
import sys
from pathlib import Path

print("🧪 Testing SimpleRAG Components...\n")

# Test 1: Python version
print("1. Python version:")
print(f"   ✓ Python {sys.version.split()[0]}")

# Test 2: Import dependencies
print("\n2. Testing imports:")
try:
    import fastapi
    print(f"   ✓ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"   ✗ FastAPI: {e}")

try:
    import sqlalchemy
    print(f"   ✓ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"   ✗ SQLAlchemy: {e}")

try:
    import chromadb
    print(f"   ✓ ChromaDB {chromadb.__version__}")
except ImportError as e:
    print(f"   ✗ ChromaDB: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print(f"   ✓ SentenceTransformers")
except ImportError as e:
    print(f"   ✗ SentenceTransformers: {e}")

# Test 3: Configuration
print("\n3. Testing configuration:")
try:
    from config import settings
    print(f"   ✓ Config loaded")
    print(f"   - Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
    print(f"   - Ollama: {settings.ollama_base_url}")
    print(f"   - Model: {settings.llm_model}")
except Exception as e:
    print(f"   ✗ Config: {e}")

# Test 4: Directories
print("\n4. Testing directories:")
dirs = ['uploads', 'documents_to_scan', 'chroma_db']
for dir_name in dirs:
    path = Path(dir_name)
    if path.exists():
        print(f"   ✓ {dir_name}/")
    else:
        print(f"   ✗ {dir_name}/ (creating...)")
        path.mkdir(parents=True, exist_ok=True)

# Test 5: Database connection
print("\n5. Testing database:")
async def test_db():
    try:
        from database import engine
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"   ✗ Database connection: {e}")
        return False

try:
    if asyncio.run(test_db()):
        print(f"   ✓ Database connection successful")
except Exception as e:
    print(f"   ✗ Database test failed: {e}")

# Test 6: Ollama
print("\n6. Testing Ollama:")
try:
    import httpx
    response = httpx.get("http://localhost:11434/api/version", timeout=2.0)
    if response.status_code == 200:
        print(f"   ✓ Ollama is running")
        print(f"   - Version: {response.json().get('version', 'unknown')}")
    else:
        print(f"   ✗ Ollama returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Ollama not accessible: {e}")
    print(f"   - Start with: ollama serve")
    print(f"   - Pull model: ollama pull llama2")

# Test 7: Sample files
print("\n7. Checking sample files:")
sample_path = Path("documents_to_scan/sample.txt")
if sample_path.exists():
    print(f"   ✓ Sample document exists ({sample_path.stat().st_size} bytes)")
else:
    print(f"   ℹ No sample document found")

print("\n" + "="*50)
print("Test complete! Check results above.")
print("\nTo start the application:")
print("  python main.py")
print("\nOr use the convenience script:")
print("  ./run.sh")
print("="*50)
