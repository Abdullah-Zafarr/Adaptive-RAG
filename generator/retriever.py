import time
from typing import List, Tuple, Dict, Any, Optional
from ingestion.loaders import NativeDocument
from vectordb.vector_store import VectorStoreManager

# Handles semantic document retrieval, distance score filtering, provenance formatting, and telemetry.
class RetrieverTool:
    """Native Retriever Tool with distance threshold filtering & telemetry metrics without LangChain."""

    # Binds the retriever to an active VectorStoreManager instance
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vdb_manager = vector_store_manager

    # Executes query search, applies similarity thresholds, formats provenance text, and calculates stats
    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        search_type: str = "Similarity Search",
        distance_threshold: float = 2.0,
        active_doc_ids: Optional[List[str]] = None
    ) -> Tuple[List[Dict[str, Any]], str, float, Dict[str, Any]]:
        """
        Execute semantic retrieval with distance thresholding.
        Returns (retrieved_items, formatted_context, retrieval_time_ms, compression_stats).
        """
        # Start timer for latency telemetry
        start_time = time.time()
        
        # Vector store query execution (MMR or standard similarity search)
        if search_type == "Maximal Marginal Relevance (MMR)":
            raw_docs = self.vdb_manager.max_marginal_relevance_search(query, k=top_k, active_doc_ids=active_doc_ids)
            doc_score_pairs = [(doc, 1.0) for doc in raw_docs]
        else:
            doc_score_pairs = self.vdb_manager.similarity_search_with_score(query, k=top_k, active_doc_ids=active_doc_ids)

        # Record total retrieval time in milliseconds
        retrieval_time_ms = (time.time() - start_time) * 1000.0

        retrieved_items = []
        context_parts = []
        raw_char_count = 0

        # Filter matching document chunks by distance threshold and format context
        for idx, (doc, score) in enumerate(doc_score_pairs):
            norm_score = float(score)
            
            # Apply Distance Threshold Filtering (discard low similarity matches)
            if norm_score > distance_threshold:
                continue

            filename = doc.metadata.get("filename", "Unknown Document")
            page = doc.metadata.get("page", 1)
            chunk_id = doc.metadata.get("chunk_id", f"chunk_{idx}")
            raw_char_count += len(doc.page_content)

            # Store structured metadata for each retrieved chunk
            retrieved_items.append({
                "chunk_id": chunk_id,
                "content": doc.page_content,
                "filename": filename,
                "page": page,
                "score": norm_score,
                "char_count": len(doc.page_content),
                "metadata": doc.metadata
            })

            # Create readable context snippet with provenance metadata tag
            context_parts.append(
                f"[Provenance Node {idx+1} | Document: {filename} (Page {page})]\n{doc.page_content}"
            )

        # Combine context snippets and compute compression metrics
        formatted_context = "\n\n---\n\n".join(context_parts) if context_parts else "NO_MATCHING_PROVENANCE_FOUND"

        context_char_count = len(formatted_context)
        compression_stats = {
            "retrieved_nodes": len(retrieved_items),
            "payload_char_count": context_char_count,
            "raw_retrieved_chars": raw_char_count
        }

        return retrieved_items, formatted_context, retrieval_time_ms, compression_stats


