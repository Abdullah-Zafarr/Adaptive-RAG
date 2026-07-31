import os
import json
import time
import uuid
import shutil
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from config import REGISTRY_FILE, DOCUMENTS_DIR, SUPABASE_URL, SUPABASE_KEY
from ingestion.loaders import DocumentLoaderTool, get_file_hash
from ingestion.chunker import TextChunker

# =====================================================================
# DATA SOURCE MANAGER CLASS
# Manages document registry, file ingestion, chunking, & Supabase cloud state
# =====================================================================
class DataSourceManager:
    """Manager to track active documents and coordinate dynamic add/delete operations backed by Supabase."""

    # -----------------------------------------------------------------
    # STEP 1: INITIALIZATION & DB CONNECTIVITY
    # Prepares document storage directory and connects to Supabase
    # -----------------------------------------------------------------
    def __init__(self, registry_file: str = REGISTRY_FILE, docs_dir: str = DOCUMENTS_DIR):
        self.registry_file = registry_file
        self.docs_dir = docs_dir
        os.makedirs(self.docs_dir, exist_ok=True)
        self.client: Optional[Client] = None
        self._init_client()

    def _init_client(self):
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Supabase DataSourceManager client error: {e}")
                self.client = None

    # -----------------------------------------------------------------
    # STEP 2: REGISTRY FETCHING
    # Loads active documents registry from Supabase (or local JSON fallback)
    # -----------------------------------------------------------------
    def load_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load registry of active documents from Supabase (fallback to local)."""
        if self.client:
            try:
                res = self.client.table("active_documents").select("*").execute()
                if res.data is not None:
                    reg = {}
                    for row in res.data:
                        reg[row["doc_id"]] = row
                    return reg
            except Exception as e:
                print(f"Supabase load_registry error: {e}")

        # Local fallback
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_active_documents(self) -> List[Dict[str, Any]]:
        """Return list of active document metadata dicts."""
        registry = self.load_registry()
        return list(registry.values())

    # -----------------------------------------------------------------
    # STEP 3: FILE ADDITION & INGESTION PIPELINE
    # Receives file bytes, parses document, splits into chunks, and upserts
    # metadata into active_documents table.
    # -----------------------------------------------------------------
    def add_file(self, file_name: str, file_bytes: bytes, chunk_size: int, chunk_overlap: int) -> tuple[Dict[str, Any], List[Any]]:
        """
        Save uploaded file, extract text, chunk with metadata, and register document in Supabase.
        Returns (doc_metadata, chunks).
        """
        doc_id = str(uuid.uuid4())[:8]
        file_hash = get_file_hash(file_bytes)
        
        # Save file locally for parsing
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
            "file_size": len(file_bytes),
            "file_hash": file_hash,
            "total_chunks": len(chunks),
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }

        if self.client:
            try:
                record = {
                    "doc_id": doc_id,
                    "filename": file_name,
                    "file_size": len(file_bytes),
                    "total_chunks": len(chunks),
                    "added_at": doc_info["added_at"],
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                }
                self.client.table("active_documents").upsert(record).execute()
            except Exception as e:
                print(f"Error upserting active_document into Supabase: {e}")

        # Cleanup temp file
        try:
            os.remove(save_path)
        except Exception:
            pass

        return doc_info, chunks

    # -----------------------------------------------------------------
    # STEP 4: DOCUMENT DELETION & RESET
    # Deletes active document metadata from Supabase cloud database
    # -----------------------------------------------------------------
    def remove_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Remove document record from Supabase."""
        registry = self.load_registry()
        if doc_id not in registry:
            return None

        doc_info = registry[doc_id]

        if self.client:
            try:
                self.client.table("active_documents").delete().eq("doc_id", doc_id).execute()
            except Exception as e:
                print(f"Error removing active_document from Supabase: {e}")

        return doc_info

    def clear_all(self):
        """Purge all active documents from Supabase."""
        if self.client:
            try:
                self.client.table("active_documents").delete().neq("doc_id", "").execute()
            except Exception as e:
                print(f"Error clearing active_documents in Supabase: {e}")

