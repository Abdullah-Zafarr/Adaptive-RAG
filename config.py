import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db"))
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", str(DATA_DIR / "documents"))
REGISTRY_FILE = os.getenv("REGISTRY_FILE", str(DATA_DIR / "active_docs.json"))
PERFORMANCE_LOG_FILE = os.getenv("PERFORMANCE_LOG_FILE", str(DATA_DIR / "performance_logs.json"))

# Ensure required directories exist
for path_str in [CHROMA_PERSIST_DIR, DOCUMENTS_DIR, DATA_DIR]:
    os.makedirs(path_str, exist_ok=True)

# Default Settings
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 4

# Available Embedding Models (Local HuggingFace Models)
EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2 (384d)": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384
    },
    "bge-small-en-v1.5 (384d)": {
        "name": "BAAI/bge-small-en-v1.5",
        "dimension": 384
    },
    "all-mpnet-base-v2 (768d)": {
        "name": "sentence-transformers/all-mpnet-base-v2",
        "dimension": 768
    }
}

# Groq LLM Models
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
