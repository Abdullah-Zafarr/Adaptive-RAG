import time
from typing import List
from src.ingestion.loaders import NativeDocument
from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class TextChunker:
    """Native recursive character text chunking strategy in pure Python."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text into segments within chunk_size limit."""
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        sep = separators[0] if separators else ""
        next_separators = separators[1:] if len(separators) > 1 else []

        if sep:
            splits = text.split(sep)
        else:
            splits = list(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for s in splits:
            item = s + (sep if sep else "")
            item_len = len(item)

            if item_len > self.chunk_size:
                if current_chunk:
                    chunks.append("".join(current_chunk).strip())
                    current_chunk = []
                    current_length = 0
                if next_separators:
                    sub_chunks = self._split_text_recursive(s, next_separators)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(s[:self.chunk_size])
            elif current_length + item_len <= self.chunk_size:
                current_chunk.append(item)
                current_length += item_len
            else:
                if current_chunk:
                    chunks.append("".join(current_chunk).strip())
                overlap_text = "".join(current_chunk)
                overlap_tail = overlap_text[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                current_chunk = [overlap_tail, item] if overlap_tail else [item]
                current_length = len("".join(current_chunk))

        if current_chunk:
            final_str = "".join(current_chunk).strip()
            if final_str:
                chunks.append(final_str)

        return [c for c in chunks if c.strip()]

    def split_documents(self, docs: List[NativeDocument], doc_id: str) -> List[NativeDocument]:
        """Split NativeDocuments into chunks with attached doc_id and unique chunk_ids."""
        chunked_docs = []
        timestamp = int(time.time())
        global_idx = 0

        for doc in docs:
            raw_text = doc.page_content
            text_splits = self._split_text_recursive(raw_text, self.separators)

            for split_text in text_splits:
                meta = dict(doc.metadata)
                meta["doc_id"] = doc_id
                meta["chunk_id"] = f"{doc_id}_chunk_{global_idx}"
                meta["chunk_index"] = global_idx
                meta["chunk_size"] = len(split_text)
                meta["ingest_timestamp"] = timestamp

                chunked_docs.append(NativeDocument(page_content=split_text, metadata=meta))
                global_idx += 1

        return chunked_docs
