import pytest
from ingestion.loaders import NativeDocument
from embeddings.manager import EmbeddingManager
from vectordb.vector_store import VectorStoreManager

def test_supabase_database_connection_and_crud():
    """Test Supabase Cloud Vector DB connection, add, search, and purge operations."""
    emb_model = EmbeddingManager.get_embedding_model("all-MiniLM-L6-v2 (384d)")
    vdb = VectorStoreManager(embedding_model=emb_model)

    assert vdb.client is not None, "Supabase client should initialize successfully."

    test_doc_id = "pytest_db_123"
    chunks = [
        NativeDocument(
            page_content="Supabase pgvector handles cloud vector embeddings for Adaptive RAG.",
            metadata={"doc_id": test_doc_id, "chunk_id": "pytest_c1", "filename": "pytest_doc.txt", "page": 1}
        ),
        NativeDocument(
            page_content="PostgreSQL with vector extension enables high-speed semantic search.",
            metadata={"doc_id": test_doc_id, "chunk_id": "pytest_c2", "filename": "pytest_doc.txt", "page": 1}
        )
    ]

    try:
        # Add documents to Supabase
        added_ids = vdb.add_documents(chunks)
        assert len(added_ids) == 2

        # Similarity search
        results = vdb.similarity_search_with_score("vector embeddings", k=2)
        assert len(results) > 0, "Should retrieve semantic vector results from Supabase."
        retrieved_text = results[0][0].page_content
        assert "vector" in retrieved_text.lower() or "supabase" in retrieved_text.lower()

    finally:
        # Purge test document
        vdb.delete_document_by_id(test_doc_id)

        # Verify deletion
        res_after = vdb.similarity_search_with_score("vector embeddings", k=5)
        for doc, score in res_after:
            assert doc.metadata.get("doc_id") != test_doc_id, "Deleted document chunks should not be returned."
