import tempfile
from langchain_core.documents import Document
from embeddings.manager import EmbeddingManager
from vectordb.vector_store import VectorStoreManager

def test_chroma_vector_store_add_and_delete():
    emb_model = EmbeddingManager.get_embedding_model("all-MiniLM-L6-v2 (384d)")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        vdb = VectorStoreManager(embedding_model=emb_model)
        
        chunks = [
            Document(page_content="RAG architecture uses vector stores.", metadata={"doc_id": "doc123", "chunk_id": "c1", "filename": "doc1.txt"}),
            Document(page_content="Embeddings represent semantic text vectors.", metadata={"doc_id": "doc123", "chunk_id": "c2", "filename": "doc1.txt"}),
            Document(page_content="Python is a popular programming language.", metadata={"doc_id": "doc456", "chunk_id": "c3", "filename": "doc2.txt"})
        ]

        vdb.add_documents(chunks)

        results = vdb.similarity_search_with_score("vector stores", k=2)
        assert len(results) > 0

        # Purge doc123
        vdb.delete_document_by_id("doc123")

        res_after = vdb.similarity_search_with_score("vector stores", k=5)
        for doc, score in res_after:
            assert doc.metadata.get("doc_id") != "doc123"
