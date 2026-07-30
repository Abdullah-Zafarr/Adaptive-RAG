import pytest
from ingestion.loaders import NativeDocument
from embeddings.manager import EmbeddingManager
from vectordb.vector_store import VectorStoreManager
from generator.retriever import RetrieverTool
from generator.llm import LLMResponseGenerator
from evaluation.performance_monitor import PerformanceMonitor

def test_rag_pipeline_end_to_end():
    """Test full RAG pipeline: Ingestion -> Vector Retrieval -> LLM Context Grounding -> Telemetry Audit."""
    emb_model = EmbeddingManager.get_embedding_model("all-MiniLM-L6-v2 (384d)")
    vdb = VectorStoreManager(embedding_model=emb_model)
    retriever = RetrieverTool(vdb)
    perf_monitor = PerformanceMonitor()

    test_doc_id = "rag_test_999"
    test_chunks = [
        NativeDocument(
            page_content="The Apollo 11 moon landing occurred in July 1969 with astronauts Neil Armstrong and Buzz Aldrin.",
            metadata={"doc_id": test_doc_id, "chunk_id": "rag_c1", "filename": "apollo.txt", "page": 1}
        ),
        NativeDocument(
            page_content="Saturn V was a human-rated super heavy-lift launch vehicle used by NASA between 1967 and 1973.",
            metadata={"doc_id": test_doc_id, "chunk_id": "rag_c2", "filename": "apollo.txt", "page": 1}
        )
    ]

    try:
        # 1. Ingest
        vdb.add_documents(test_chunks)

        # 2. Retrieve
        query = "When did the Apollo 11 moon landing happen and who were the astronauts?"
        retrieved_items, formatted_ctx, retrieval_time, comp_stats = retriever.retrieve(query=query, top_k=2, distance_threshold=1.5)

        assert len(retrieved_items) > 0, "Retriever should return relevant context chunks."
        assert any("Apollo 11" in item["content"] for item in retrieved_items)

        # 3. LLM Response Generation & Prompt Format
        from generator.prompts import RAG_SYSTEM_PROMPT
        prompt = RAG_SYSTEM_PROMPT.format(context=formatted_ctx, question=query)
        assert "Apollo 11" in prompt, "Prompt should contain grounded context."


        # 4. Telemetry GCI Audit
        log_entry = perf_monitor.log_query_event(
            query=query,
            response="The Apollo 11 moon landing occurred in July 1969 with Neil Armstrong and Buzz Aldrin.",
            retrieved_chunks=retrieved_items,
            retrieval_time_ms=120.0,
            gen_time_ms=450.0,
            embedding_model="all-MiniLM-L6-v2 (384d)",
            llm_model="llama-3.3-70b-versatile",
            active_doc_count=1,
            compression_stats=comp_stats
        )

        assert log_entry["grounding_confidence_index"] >= 0.70, "GCI score should indicate high grounding confidence."
        assert log_entry["hallucination_risk"] == "LOW_RISK"

    finally:
        # Cleanup
        vdb.delete_document_by_id(test_doc_id)
