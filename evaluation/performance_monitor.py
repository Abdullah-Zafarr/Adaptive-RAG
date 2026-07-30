import os
import time
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, PERFORMANCE_LOG_FILE

class PerformanceMonitor:
    """Advanced Telemetry & Grounding Confidence Index (GCI) Monitor backed by Supabase Cloud."""

    def __init__(self, log_file: str = PERFORMANCE_LOG_FILE):
        self.log_file = log_file
        self.client: Optional[Client] = None
        self._init_client()

    def _init_client(self):
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Supabase PerformanceMonitor client error: {e}")
                self.client = None

    def load_logs(self) -> List[Dict[str, Any]]:
        """Load performance logs from Supabase Cloud table (fallback to local)."""
        if self.client:
            try:
                res = self.client.table("performance_logs").select("*").order("timestamp", desc=False).execute()
                if res.data is not None:
                    return res.data
            except Exception as e:
                print(f"Supabase load_logs error: {e}")

        # Local fallback
        if os.path.exists(self.log_file):
            try:
                import json
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

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
        """Record telemetry log with Grounding Confidence Index (GCI) metrics directly to Supabase."""
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
            "vector_db": "Supabase",
            "embedding_model": embedding_model,
            "llm_model": llm_model,
            "active_doc_count": active_doc_count,
            "payload_chars": compression_stats.get("payload_char_count", 0)
        }

        if self.client:
            try:
                self.client.table("performance_logs").insert(log_entry).execute()
            except Exception as e:
                print(f"Error inserting performance_log into Supabase: {e}")

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
        """Purge telemetry log history from Supabase."""
        if self.client:
            try:
                self.client.table("performance_logs").delete().neq("query_id", "").execute()
            except Exception as e:
                print(f"Error clearing performance_logs in Supabase: {e}")
