import os
import tempfile
import pytest
from ingestion.loaders import DocumentLoaderTool, get_file_hash
from ingestion.chunker import TextChunker
from ingestion.source_manager import DataSourceManager

def test_file_hash():
    content = b"Hello RAG World"
    h1 = get_file_hash(content)
    h2 = get_file_hash(content)
    assert h1 == h2
    assert len(h1) == 64

def test_txt_loader_and_chunker():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("This is a sample document for RAG system testing.\nIt contains multiple lines of text.\n\nSection 2: Performance Evaluation and Vector Database.")
        temp_path = f.name

    try:
        docs = DocumentLoaderTool.load_txt(temp_path)
        assert len(docs) > 0
        assert docs[0].metadata["file_type"] == "txt"

        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.split_documents(docs, doc_id="test_doc_1")
        assert len(chunks) >= 1
        assert chunks[0].metadata["doc_id"] == "test_doc_1"
        assert "chunk_id" in chunks[0].metadata
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_data_source_manager():
    with tempfile.TemporaryDirectory() as temp_dir:
        reg_file = os.path.join(temp_dir, "test_registry.json")
        docs_dir = os.path.join(temp_dir, "docs")
        
        manager = DataSourceManager(registry_file=reg_file, docs_dir=docs_dir)
        test_content = b"Artificial Intelligence and Retrieval-Augmented Generation."
        
        doc_info, chunks = manager.add_file("test.txt", test_content, chunk_size=100, chunk_overlap=10)
        assert doc_info["filename"] == "test.txt"
        assert len(manager.get_active_documents()) == 1

        deleted = manager.remove_document(doc_info["doc_id"])
        assert deleted["doc_id"] == doc_info["doc_id"]
        assert len(manager.get_active_documents()) == 0
