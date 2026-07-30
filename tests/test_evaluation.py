import os
import tempfile
from evaluation.performance_monitor import PerformanceMonitor

def test_performance_monitor_logging():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        log_file = f.name

    try:
        monitor = PerformanceMonitor(log_file=log_file)
        retrieved_chunks = [
            {"chunk_id": "c1", "content": "RAG architecture combines retrieval and generation.", "score": 0.85, "filename": "doc1.pdf"}
        ]
        
        entry = monitor.log_query_event(
            query="What is RAG?",
            response="RAG combines retrieval and generation.",
            retrieved_chunks=retrieved_chunks,
            retrieval_time_ms=25.0,
            gen_time_ms=120.0,
            embedding_model="all-MiniLM-L6-v2 (384d)",
            llm_model="llama-3.3-70b-versatile",
            active_doc_count=1
        )

        assert entry["total_latency_ms"] == 145.0
        assert entry["vector_db"] == "Supabase"

        logs = monitor.load_logs()
        assert len(logs) >= 1
        assert entry["query"] == "What is RAG?"
        assert entry["grounding_confidence_index"] > 0.0

    finally:
        if os.path.exists(log_file):
            os.remove(log_file)
