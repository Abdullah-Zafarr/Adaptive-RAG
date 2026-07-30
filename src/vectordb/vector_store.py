import os
import shutil
from typing import List, Tuple, Optional, Any
import chromadb
from src.ingestion.loaders import NativeDocument
from src.config import CHROMA_PERSIST_DIR

class VectorStoreManager:
    """Manager for ChromaDB Vector Database using native ChromaDB client without LangChain."""

    def __init__(self, embedding_model: Any = None):
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        """Initialize local ChromaDB persistent collection."""
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="rag_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: List[NativeDocument]) -> List[str]:
        """Add document chunks to ChromaDB natively."""
        if not chunks:
            return []

        ids = [chunk.metadata.get("chunk_id", f"chunk_{i}") for i, chunk in enumerate(chunks)]
        documents = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        if self.embedding_model:
            embeddings = self.embedding_model.embed_documents(documents)
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        return ids

    def delete_document_by_id(self, doc_id: str):
        """Delete all vector embeddings matching doc_id from ChromaDB."""
        try:
            results = self.collection.get(where={"doc_id": doc_id})
            matching_ids = results.get("ids", [])
            if matching_ids:
                self.collection.delete(ids=matching_ids)
        except Exception as e:
            print(f"Error purging doc_id {doc_id} from ChromaDB: {e}")

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[NativeDocument, float]]:
        """Perform native semantic similarity search returning documents and distance scores."""
        if not self.collection:
            return []
        try:
            if self.embedding_model:
                query_embedding = self.embedding_model.embed_query(query)
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=k
                )

            docs_with_scores = []
            if results and results.get("documents") and results["documents"][0]:
                retrieved_texts = results["documents"][0]
                retrieved_metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(retrieved_texts)
                retrieved_dists = results["distances"][0] if results.get("distances") else [0.0] * len(retrieved_texts)

                for text, meta, dist in zip(retrieved_texts, retrieved_metas, retrieved_dists):
                    doc = NativeDocument(page_content=text, metadata=meta)
                    docs_with_scores.append((doc, float(dist)))

            return docs_with_scores
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def max_marginal_relevance_search(self, query: str, k: int = 4) -> List[NativeDocument]:
        """Perform similarity search as default MMR alternative."""
        results = self.similarity_search_with_score(query, k=k)
        return [doc for doc, _ in results]

    def reset_db(self):
        """Purge and reset the ChromaDB database."""
        try:
            self.client.delete_collection(name="rag_knowledge_base")
        except Exception:
            pass
        shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        self._init_db()
