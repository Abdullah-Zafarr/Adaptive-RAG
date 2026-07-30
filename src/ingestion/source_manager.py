import os
import json
import time
import uuid
import shutil
from typing import List, Dict, Any, Optional
from src.config import REGISTRY_FILE, DOCUMENTS_DIR
from src.ingestion.loaders import DocumentLoaderTool, get_file_hash
from src.ingestion.chunker import TextChunker

class DataSourceManager:
    """Manager to track active documents and coordinate dynamic add/delete operations."""

    def __init__(self, registry_file: str = REGISTRY_FILE, docs_dir: str = DOCUMENTS_DIR):
        self.registry_file = registry_file
        self.docs_dir = docs_dir
        os.makedirs(self.docs_dir, exist_ok=True)
        self._ensure_registry()

    def _ensure_registry(self):
        """Initialize registry JSON if absent."""
        if not os.path.exists(self.registry_file):
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def load_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load registry of active documents."""
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_registry(self, registry: Dict[str, Dict[str, Any]]):
        """Save updated registry to disk."""
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

    def add_file(self, file_name: str, file_bytes: bytes, chunk_size: int, chunk_overlap: int) -> tuple[Dict[str, Any], List[Any]]:
        """
        Save uploaded file, extract text, chunk with metadata, and register document.
        Returns (doc_metadata, chunks).
        """
        doc_id = str(uuid.uuid4())[:8]
        file_hash = get_file_hash(file_bytes)
        
        # Save file to documents directory
        save_path = os.path.join(self.docs_dir, f"{doc_id}_{file_name}")
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Load & Chunk
        raw_docs = DocumentLoaderTool.load_file(save_path)
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = chunker.split_documents(raw_docs, doc_id=doc_id)

        # Create registry record
        doc_info = {
            "doc_id": doc_id,
            "filename": file_name,
            "save_path": save_path,
            "file_hash": file_hash,
            "file_size": len(file_bytes),
            "upload_timestamp": int(time.time()),
            "total_chunks": len(chunks),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }

        registry = self.load_registry()
        registry[doc_id] = doc_info
        self._save_registry(registry)

        return doc_info, chunks

    def add_url(self, url: str, chunk_size: int, chunk_overlap: int) -> tuple[Dict[str, Any], List[Any]]:
        """Process and register content from web URL."""
        doc_id = str(uuid.uuid4())[:8]
        raw_docs = DocumentLoaderTool.load_url(url)
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = chunker.split_documents(raw_docs, doc_id=doc_id)

        doc_info = {
            "doc_id": doc_id,
            "filename": url,
            "save_path": url,
            "file_hash": hashlib_url(url),
            "file_size": 0,
            "upload_timestamp": int(time.time()),
            "total_chunks": len(chunks),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }

        registry = self.load_registry()
        registry[doc_id] = doc_info
        self._save_registry(registry)

        return doc_info, chunks

    def remove_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Remove document record from registry and delete saved physical file."""
        registry = self.load_registry()
        if doc_id not in registry:
            return None

        doc_info = registry.pop(doc_id)
        save_path = doc_info.get("save_path")
        if save_path and os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception as e:
                print(f"Warning deleting file {save_path}: {e}")

        self._save_registry(registry)
        return doc_info

    def get_active_documents(self) -> List[Dict[str, Any]]:
        """Return list of active document metadata dicts."""
        return list(self.load_registry().values())

    def clear_all(self):
        """Purge all active documents from registry and filesystem."""
        registry = self.load_registry()
        for doc_id, doc_info in registry.items():
            save_path = doc_info.get("save_path")
            if save_path and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except Exception:
                    pass
        self._save_registry({})

def hashlib_url(url: str) -> str:
    import hashlib
    return hashlib.md5(url.encode("utf-8")).hexdigest()
