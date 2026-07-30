import os
import math
from typing import List, Tuple, Optional, Any
from supabase import create_client, Client
from ingestion.loaders import NativeDocument
from config import SUPABASE_URL, SUPABASE_KEY

class VectorStoreManager:
    """Manager for Supabase Vector Database using native Supabase Client + pgvector cosine similarity."""

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

    def delete_document_by_id(self, doc_id: str):
        """Delete all vector embeddings matching doc_id from Supabase."""
        if not self.client:
            return
        try:
            self.client.table("documents").delete().eq("doc_id", doc_id).execute()
        except Exception as e:
            print(f"Error purging doc_id {doc_id} from Supabase: {e}")

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[NativeDocument, float]]:
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
                        "match_count": k
                    }
                ).execute()

                if rpc_res.data:
                    docs_with_scores = []
                    for row in rpc_res.data:
                        meta = row.get("metadata", {})
                        if not meta:
                            meta = {
                                "doc_id": row.get("doc_id"),
                                "filename": row.get("filename"),
                                "page": row.get("page", 1)
                            }
                        doc = NativeDocument(page_content=row.get("content", ""), metadata=meta)
                        # Cosine similarity -> distance (1 - similarity)
                        sim = float(row.get("similarity", 0.0))
                        dist = max(0.0, 1.0 - sim)
                        docs_with_scores.append((doc, dist))
                    return docs_with_scores
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
                dist = cosine_distance(query_embedding, emb)
                meta = row.get("metadata", {}) or {"doc_id": row.get("doc_id"), "filename": row.get("filename")}
                doc = NativeDocument(page_content=row.get("content", ""), metadata=meta)
                scored.append((doc, dist))

            scored.sort(key=lambda x: x[1])
            return scored[:k]

        except Exception as e:
            print(f"Supabase search error: {e}")
            return []

    def max_marginal_relevance_search(self, query: str, k: int = 4) -> List[NativeDocument]:
        """Perform similarity search as default MMR alternative."""
        results = self.similarity_search_with_score(query, k=k)
        return [doc for doc, _ in results]

    def reset_db(self):
        """Purge and reset all documents from Supabase table."""
        if not self.client:
            return
        try:
            self.client.table("documents").delete().neq("chunk_id", "").execute()
        except Exception as e:
            print(f"Error resetting Supabase table: {e}")
