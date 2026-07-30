import os
import json
import time
from typing import List, Dict, Any, Optional
from src.config import PERFORMANCE_LOG_FILE

class PerformanceMonitor:
    """Advanced Telemetry & Grounding Confidence Index (GCI) Monitor."""

    def __init__(self, log_file: str = PERFORMANCE_LOG_FILE):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_logs(self) -> List[Dict[str, Any]]:
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_logs(self, logs: List[Dict[str, Any]]):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

    def log_query_event(
        self,
        query: str,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
        retrieval_time_ms: float,
        gen_time_ms: float,
        embedding_model: str,
        llm_model: str,
        active_doc_count: int,
        compression_stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record telemetry log with Grounding Confidence Index (GCI) metrics."""
        total_latency_ms = retrieval_time_ms + gen_time_ms
        scores = [item.get("score", 0.0) for item in retrieved_chunks]
        avg_retrieval_score = sum(scores) / len(scores) if scores else 0.0
        top_score = scores[0] if scores else 0.0

        if compression_stats is None:
            compression_stats = {}

        gci_metrics = self.compute_gci_metrics(response, retrieved_chunks)

        log_entry = {
            "query_id": f"tx_{int(time.time() * 1000)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "response": response,
            "nodes_retrieved": len(retrieved_chunks),
            "retrieval_latency_ms": round(retrieval_time_ms, 2),
            "generation_latency_ms": round(gen_time_ms, 2),
            "total_latency_ms": round(total_latency_ms, 2),
            "avg_distance_score": round(avg_retrieval_score, 4),
            "top_distance_score": round(top_score, 4),
            "grounding_confidence_index": gci_metrics["gci_score"],
            "lexical_overlap_ratio": gci_metrics["lexical_overlap"],
            "citation_density": gci_metrics["citation_density"],
            "hallucination_risk": gci_metrics["risk_level"],
            "vector_db": "ChromaDB",
            "embedding_model": embedding_model,
            "llm_model": llm_model,
            "active_doc_count": active_doc_count,
            "payload_chars": compression_stats.get("payload_char_count", 0)
        }

        logs = self.load_logs()
        logs.append(log_entry)
        self._save_logs(logs)

        return log_entry

    def compute_gci_metrics(self, response: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate Grounding Confidence Index (GCI), Citation Density, and Risk Category."""
        if not response or not retrieved_chunks:
            return {"gci_score": 0.0, "lexical_overlap": 0.0, "citation_density": 0.0, "risk_level": "HIGH_RISK"}

        if "do not contain sufficient information" in response.lower() or "sorry" in response.lower():
            return {"gci_score": 1.0, "lexical_overlap": 1.0, "citation_density": 0.0, "risk_level": "GROUNDED_REFUSAL"}

        context_text = " ".join([c.get("content", "") for c in retrieved_chunks]).lower()
        response_words = [w.strip(".,!?\"'()[]") for w in response.lower().split() if len(w) > 3]

        if not response_words:
            return {"gci_score": 1.0, "lexical_overlap": 1.0, "citation_density": 0.0, "risk_level": "GROUNDED_REFUSAL"}

        matches = sum(1 for word in response_words if word in context_text)
        lexical_overlap = round(matches / len(response_words), 2)
        
        citations_count = response.count("Document:") + response.count("Source:") + response.count(".pdf") + response.count(".txt")
        total_words = len(response.split())
        citation_density = round((citations_count / max(1, total_words)) * 100, 2)

        gci_score = min(1.0, max(0.0, lexical_overlap * 1.15))

        if gci_score >= 0.70:
            risk_level = "LOW_RISK"
        elif gci_score >= 0.40:
            risk_level = "MODERATE_RISK"
        else:
            risk_level = "HIGH_RISK"

        return {
            "gci_score": round(gci_score, 2),
            "lexical_overlap": lexical_overlap,
            "citation_density": citation_density,
            "risk_level": risk_level
        }

    def clear_logs(self):
        """Purge telemetry log history."""
        self._save_logs([])
