from typing import Any, List
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODELS

# =====================================================================
# NATIVE EMBEDDING MODEL CLASS
# Direct wrapper around HuggingFace SentenceTransformers
# =====================================================================
class NativeEmbeddingModel:
    """Native Wrapper for SentenceTransformer embeddings without LangChain."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    # -----------------------------------------------------------------
    # DOCUMENT EMBEDDINGS
    # Encodes list of document texts into normalized vector arrays
    # -----------------------------------------------------------------
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized vector embeddings for a list of document strings."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    # -----------------------------------------------------------------
    # QUERY EMBEDDING
    # Encodes single search query into normalized vector array
    # -----------------------------------------------------------------
    def embed_query(self, text: str) -> List[float]:
        """Generate normalized vector embedding for a query string."""
        embedding = self.model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()

# =====================================================================
# EMBEDDING MANAGER CLASS
# Factory to instantiate embedding models and retrieve vector dimensions
# =====================================================================
class EmbeddingManager:
    """Manager to load local SentenceTransformer embedding models natively."""

    @staticmethod
    def get_embedding_model(model_key: str) -> NativeEmbeddingModel:
        """Instantiate native SentenceTransformer embedding model."""
        if model_key not in EMBEDDING_MODELS:
            model_key = "all-MiniLM-L6-v2 (384d)"
        
        config = EMBEDDING_MODELS[model_key]
        model_name = config["name"]

        return NativeEmbeddingModel(model_name=model_name)

    @staticmethod
    def get_dimension(model_key: str) -> int:
        """Get embedding dimension for a given model key."""
        if model_key in EMBEDDING_MODELS:
            return EMBEDDING_MODELS[model_key]["dimension"]
        return 384

