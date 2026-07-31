import os
import math
from typing import List, Tuple, Optional, Any
from supabase import create_client, Client
from ingestion.loaders import NativeDocument
from config import SUPABASE_URL, SUPABASE_KEY

# =====================================================================
# VECTOR STORE MANAGER CLASS
# Manages Supabase vector store table, document embeddings, pgvector RPC matches, 
# and fallback client-side cosine similarity search.
# =====================================================================
class VectorStoreManager:
    """Manager for Supabase Vector Database using native Supabase Client + pgvector cosine similarity."""

    # -----------------------------------------------------------------
    # STEP 1: INITIALIZATION
    # Binds embedding model and opens client connection to Supabase DB.
    # -----------------------------------------------------------------
    def __init__(self, embedding_model: Any = None):
        self.embedding_model = embedding_model
        self.client: Optional[Client] = None
        self._init_db()

    def _init_db(self):
        """Initialize Supabase client connection."""
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Supabase Client Init Error: {e}")
                self.client = None

    # -----------------------------------------------------------------
    # STEP 2: EMBED & INSERT DOCUMENTS
    # Generates dense vector embeddings for text chunks and upserts 
    # records into Supabase 'documents' table.
    # -----------------------------------------------------------------
    def add_documents(self, chunks: List[NativeDocument]) -> List[str]:
        """Add document chunks to Supabase vector store table."""
        if not chunks or not self.client:
            return []

        documents = [chunk.page_content for chunk in chunks]

        if self.embedding_model:
            embeddings = self.embedding_model.embed_documents(documents)
        else:
            embeddings = [[0.0] * 384 for _ in chunks]

        rows = []
        ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = chunk.metadata.get("chunk_id", f"chunk_{i}")
            doc_id = chunk.metadata.get("doc_id", "")
            filename = chunk.metadata.get("filename", "")
            page = chunk.metadata.get("page", 1)

            rows.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embeddings[i],
                "filename": filename,
                "page": page
            })
            ids.append(chunk_id)

        try:
            self.client.table("documents").upsert(rows).execute()
        except Exception as e:
            print(f"Supabase add_documents error: {e}")

        return ids

    # -----------------------------------------------------------------
    # STEP 3: DELETE EMBEDDINGS BY DOCUMENT ID
    # Purges all rows matching a target doc_id or filename.
    # -----------------------------------------------------------------
    def delete_document_by_id(self, doc_id: str):
        """Delete all vector embeddings matching doc_id or filename from Supabase."""
        if not self.client:
            return
        try:
            # Purge by top-level doc_id column
            self.client.table("documents").delete().eq("doc_id", doc_id).execute()
            # Purge by top-level filename column (for URL endpoints where doc_id equals filename/url)
            self.client.table("documents").delete().eq("filename", doc_id).execute()
            # Purge by JSON metadata doc_id
            self.client.table("documents").delete().eq("metadata->>doc_id", doc_id).execute()
            # Purge by JSON metadata filename
            self.client.table("documents").delete().eq("metadata->>filename", doc_id).execute()
        except Exception as e:
            print(f"Error purging doc_id/filename {doc_id} from Supabase: {e}")

    # -----------------------------------------------------------------
    # STEP 4: SEMANTIC SIMILARITY SEARCH
    # Embeds user query and calculates nearest neighbors via Supabase RPC 
    # function or client-side cosine distance.
    # -----------------------------------------------------------------
    def similarity_search_with_score(self, query: str, k: int = 4, active_doc_ids: Optional[List[str]] = None) -> List[Tuple[NativeDocument, float]]:
        """Perform native semantic similarity search returning documents and distance scores via Supabase RPC or client cosine fallback."""
        if not self.client:
            return []

        try:
            if not self.embedding_model:
                return []

            query_embedding = self.embedding_model.embed_query(query)

            # Attempt Supabase RPC match_documents vector function
            try:
                rpc_res = self.client.rpc(
                    "match_documents",
                    {
                        "query_embedding": query_embedding,
                        "match_threshold": 0.0,
                        "match_count": k * 2 if active_doc_ids else k
                    }
                ).execute()

                if rpc_res.data:
                    docs_with_scores = []
                    for row in rpc_res.data:
                        meta = row.get("metadata", {})
                        doc_id = row.get("doc_id") or meta.get("doc_id")
                        filename = row.get("filename") or meta.get("filename")
                        
                        # Filter against active registry if provided
                        if active_doc_ids is not None:
                            if doc_id not in active_doc_ids and filename not in active_doc_ids:
                                continue

                        if not meta:
                            meta = {
                                "doc_id": doc_id,
                                "filename": filename,
                                "page": row.get("page", 1)
                            }
                        doc = NativeDocument(page_content=row.get("content", ""), metadata=meta)
                        # Cosine similarity -> distance (1 - similarity)
                        sim = float(row.get("similarity", 0.0))
                        dist = max(0.0, 1.0 - sim)
                        docs_with_scores.append((doc, dist))
                    return docs_with_scores[:k]
            except Exception as rpc_err:
                pass

            # Client-side fallback if RPC is not created yet
            res = self.client.table("documents").select("*").execute()
            if not res.data:
                return []

            def cosine_distance(vec1, vec2):
                dot = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = math.sqrt(sum(a * a for a in vec1))
                norm2 = math.sqrt(sum(b * b for b in vec2))
                if norm1 == 0 or norm2 == 0:
                    return 1.0
                sim = dot / (norm1 * norm2)
                return max(0.0, 1.0 - sim)

            scored = []
            for row in res.data:
                emb = row.get("embedding")
                if not emb:
                    continue
                
                doc_id = row.get("doc_id")
                filename = row.get("filename")
                meta = row.get("metadata", {}) or {}
                if not doc_id:
                    doc_id = meta.get("doc_id")
                if not filename:
                    filename = meta.get("filename")

                # Filter against active registry if provided
                if active_doc_ids is not None:
                    if doc_id not in active_doc_ids and filename not in active_doc_ids:
                        continue

                dist = cosine_distance(query_embedding, emb)
                meta_out = meta or {"doc_id": doc_id, "filename": filename}
                doc = NativeDocument(page_content=row.get("content", ""), metadata=meta_out)
                scored.append((doc, dist))

            scored.sort(key=lambda x: x[1])
            return scored[:k]

        except Exception as e:
            print(f"Supabase search error: {e}")
            return []

    # -----------------------------------------------------------------
    # STEP 5: MAXIMAL MARGINAL RELEVANCE (MMR) SEARCH
    # Diversity-focused search wrapper over similarity search.
    # -----------------------------------------------------------------
    def max_marginal_relevance_search(self, query: str, k: int = 4, active_doc_ids: Optional[List[str]] = None) -> List[NativeDocument]:
        """Perform similarity search as default MMR alternative."""
        results = self.similarity_search_with_score(query, k=k, active_doc_ids=active_doc_ids)
        return [doc for doc, _ in results]

    # -----------------------------------------------------------------
    # STEP 6: DATABASE RESET
    # Purges all stored vectors from Supabase table.
    # -----------------------------------------------------------------
    def reset_db(self):
        """Purge and reset all documents from Supabase table."""
        if not self.client:
            return
        try:
            self.client.table("documents").delete().neq("chunk_id", "").execute()
        except Exception as e:
            print(f"Error resetting Supabase table: {e}")

