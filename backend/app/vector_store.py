# vector_store.py
import numpy as np
from .embeddings import embed_text
from typing import List, Dict, Optional, Any
from collections import defaultdict
from .chunking_service import EnhancedChunk

class InMemoryStore:
    def __init__(self):
        self.docs: List[str] = []
        self.embeddings: np.ndarray | None = None
        self.chunk_metadata: List[Dict[str, Any]] = []  # Metadata for each chunk
        self.documents: Dict[str, Dict[str, Any]] = {}  # Document-level metadata
        self.doc_to_chunks: Dict[str, List[int]] = defaultdict(list)  # Map doc_id to chunk indices

    async def ingest(self, texts: List[str]) -> int:
        """Legacy method for backward compatibility"""
        resp_data = await embed_text(texts)
        embs = np.array([item["embedding"] for item in resp_data])
        self.docs.extend(texts)
        
        # Add empty metadata for legacy chunks
        for text in texts:
            self.chunk_metadata.append({
                "source_file": "unknown",
                "file_type": "text",
                "chunk_id": f"legacy_{len(self.chunk_metadata)}"
            })
        
        if self.embeddings is None:
            self.embeddings = embs
        else:
            self.embeddings = np.vstack((self.embeddings, embs))
        return len(texts)

    async def ingest_with_metadata(self, texts: List[str], enhanced_chunks: List[EnhancedChunk]) -> int:
        """Enhanced ingestion with metadata support"""
        resp_data = await embed_text(texts)
        embs = np.array([item["embedding"] for item in resp_data])
        
        start_index = len(self.docs)
        self.docs.extend(texts)
        
        # Store chunk metadata and build document mappings
        for i, chunk in enumerate(enhanced_chunks):
            chunk_index = start_index + i
            self.chunk_metadata.append(chunk.metadata)
            self.doc_to_chunks[chunk.parent_doc_id].append(chunk_index)
            
            # Store document-level metadata (only once per document)
            if chunk.parent_doc_id not in self.documents:
                self.documents[chunk.parent_doc_id] = {
                    "doc_id": chunk.parent_doc_id,
                    "filename": chunk.metadata.get("source_file", ""),
                    "file_type": chunk.metadata.get("file_type", ""),
                    "title": chunk.metadata.get("doc_title", ""),
                    "author": chunk.metadata.get("doc_author", ""),
                    "created_date": chunk.metadata.get("doc_created_date"),
                    "file_size": chunk.metadata.get("doc_file_size", 0),
                    "total_pages": chunk.metadata.get("total_pages", 0),
                    "total_chunks": 0  # Will be updated below
                }
        
        # Update chunk counts for documents
        for doc_id in set(chunk.parent_doc_id for chunk in enhanced_chunks):
            self.documents[doc_id]["total_chunks"] = len(self.doc_to_chunks[doc_id])
        
        if self.embeddings is None:
            self.embeddings = embs
        else:
            self.embeddings = np.vstack((self.embeddings, embs))
        
        return len(texts)

    async def query(self, text: str, top_k: int = 3):
        """Query with similarity search"""
        if self.embeddings is None or len(self.docs) == 0:
            return []
            
        resp_data = await embed_text([text])
        emb = np.array(resp_data[0]["embedding"])
        sims = (self.embeddings @ emb) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(emb))
        top_ids = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in top_ids]

    def get_chunk_metadata(self, chunk_text: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific chunk"""
        try:
            chunk_index = self.docs.index(chunk_text)
            return self.chunk_metadata[chunk_index]
        except (ValueError, IndexError):
            return None

    async def get_documents_list(self) -> List[Dict[str, Any]]:
        """Get list of all documents with their metadata"""
        return list(self.documents.values())

    async def delete_document(self, doc_id: str) -> int:
        """Delete a document and all its chunks"""
        if doc_id not in self.doc_to_chunks:
            return 0
        
        chunk_indices = self.doc_to_chunks[doc_id]
        chunk_indices.sort(reverse=True)  # Delete from end to avoid index shifting
        
        deleted_count = 0
        for idx in chunk_indices:
            if idx < len(self.docs):
                # Remove from all arrays
                del self.docs[idx]
                del self.chunk_metadata[idx]
                if self.embeddings is not None:
                    self.embeddings = np.delete(self.embeddings, idx, axis=0)
                deleted_count += 1
        
        # Update mappings after deletion
        del self.doc_to_chunks[doc_id]
        del self.documents[doc_id]
        
        # Update chunk indices in remaining documents
        for remaining_doc_id, remaining_indices in self.doc_to_chunks.items():
            updated_indices = []
            for idx in remaining_indices:
                # Count how many indices were deleted before this one
                deleted_before = sum(1 for del_idx in chunk_indices if del_idx < idx)
                updated_indices.append(idx - deleted_before)
            self.doc_to_chunks[remaining_doc_id] = updated_indices
        
        return deleted_count

    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.docs),
            "total_embeddings": self.embeddings.shape[0] if self.embeddings is not None else 0,
            "documents_by_type": self._get_documents_by_type()
        }

    def _get_documents_by_type(self) -> Dict[str, int]:
        """Count documents by file type"""
        type_counts = defaultdict(int)
        for doc_meta in self.documents.values():
            file_type = doc_meta.get("file_type", "unknown")
            type_counts[file_type] += 1
        return dict(type_counts)
