import pytest
from embeddings.manager import EmbeddingManager
from vectordb.vector_store import VectorStoreManager
from generator.retriever import RetrieverTool
from evaluation.performance_monitor import PerformanceMonitor
from ingestion.loaders import NativeDocument

def test_rag_retrieval_relevance_and_precision():
    """Verify RAG Semantic Precision & Relevance thresholding."""
    emb_model = EmbeddingManager.get_embedding_model("all-MiniLM-L6-v2 (384d)")
    vdb = VectorStoreManager(embedding_model=emb_model)
    retriever = RetrieverTool(vdb)

    test_doc_id = "quality_test_101"
    chunks = [
        NativeDocument(
            page_content="Quantum computing leverages qubits, superposition, and quantum entanglement to solve complex problems.",
            metadata={"doc_id": test_doc_id, "chunk_id": "q1", "filename": "physics.txt", "page": 1}
        ),
        NativeDocument(
            page_content="Photosynthesis is the biological process used by plants to convert light energy into chemical energy.",
            metadata={"doc_id": test_doc_id, "chunk_id": "q2", "filename": "biology.txt", "page": 1}
        )
    ]

    try:
        vdb.add_documents(chunks)

        # High Relevance Query (Quantum Computing)
        retrieved_q, _, _, _ = retriever.retrieve(query="How does quantum computing use superposition?", top_k=1, distance_threshold=1.5)
        assert len(retrieved_q) == 1
        assert "qubits" in retrieved_q[0]["content"].lower()

        # High Relevance Query (Biology)
        retrieved_b, _, _, _ = retriever.retrieve(query="What is the chemical energy conversion process in plants?", top_k=1, distance_threshold=1.5)
        assert len(retrieved_b) == 1
        assert "photosynthesis" in retrieved_b[0]["content"].lower()

    finally:
        vdb.delete_document_by_id(test_doc_id)

def test_grounding_confidence_index_scoring():
    """Verify Grounding Confidence Index (GCI) audit accuracy for hallucination prevention."""
    perf_monitor = PerformanceMonitor()

    # Grounded response test
    entry_high = perf_monitor.log_query_event(
        query="What is photosynthesis?",
        response="Photosynthesis is the process plants use to convert light into chemical energy.",
        retrieved_chunks=[
            {"content": "Photosynthesis is the biological process used by plants to convert light energy into chemical energy.", "score": 0.25}
        ],
        retrieval_time_ms=10.0,
        gen_time_ms=50.0,
        embedding_model="all-MiniLM-L6-v2 (384d)",
        llm_model="llama-3.3-70b-versatile",
        active_doc_count=1
    )
    assert entry_high["grounding_confidence_index"] >= 0.70, "Grounded response must score high GCI"
    assert entry_high["hallucination_risk"] == "LOW_RISK"

    # Ungrounded response test (Hallucination)
    entry_low = perf_monitor.log_query_event(
        query="What is photosynthesis?",
        response="Photosynthesis was invented by Thomas Edison in 1879.",
        retrieved_chunks=[
            {"content": "Photosynthesis is the biological process used by plants to convert light energy into chemical energy.", "score": 0.25}
        ],
        retrieval_time_ms=10.0,
        gen_time_ms=50.0,
        embedding_model="all-MiniLM-L6-v2 (384d)",
        llm_model="llama-3.3-70b-versatile",
        active_doc_count=1
    )
    assert entry_low["grounding_confidence_index"] < 0.60, "Hallucinated response must produce lower GCI score"

