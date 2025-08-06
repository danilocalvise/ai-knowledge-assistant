# chunking_service.py
import re
import tiktoken
from typing import List, Dict, Optional
from dataclasses import dataclass
from .file_processor import ContentChunk, DocumentMetadata

@dataclass
class EnhancedChunk:
    """Enhanced chunk with better metadata and indexing"""
    text: str
    metadata: Dict[str, any]
    token_count: int
    chunk_id: str
    parent_doc_id: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: int = 0
    overlap_with_previous: bool = False

class ChunkingService:
    """Advanced chunking service with metadata preservation"""
    
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200,
                 model_name: str = "text-embedding-3-small"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Use compatible encoding
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def create_chunks_from_content(self, 
                                   content_chunks: List[ContentChunk], 
                                   metadata: DocumentMetadata) -> List[EnhancedChunk]:
        """Create enhanced chunks from extracted content"""
        enhanced_chunks = []
        doc_id = self._generate_doc_id(metadata.filename)
        global_chunk_index = 0
        
        for content_chunk in content_chunks:
            # Check if content needs to be split further
            token_count = self.count_tokens(content_chunk.text)
            
            if token_count <= self.chunk_size:
                # Content fits in one chunk
                chunk = self._create_enhanced_chunk(
                    text=content_chunk.text,
                    content_chunk=content_chunk,
                    doc_id=doc_id,
                    chunk_index=global_chunk_index,
                    metadata=metadata
                )
                enhanced_chunks.append(chunk)
                global_chunk_index += 1
            else:
                # Need to split content further
                sub_chunks = self._split_large_content(content_chunk, doc_id, global_chunk_index, metadata)
                enhanced_chunks.extend(sub_chunks)
                global_chunk_index += len(sub_chunks)
        
        return enhanced_chunks
    
    def _split_large_content(self, 
                             content_chunk: ContentChunk, 
                             doc_id: str, 
                             start_index: int,
                             metadata: DocumentMetadata) -> List[EnhancedChunk]:
        """Split large content into smaller chunks with overlap"""
        chunks = []
        text = content_chunk.text
        
        # Try to split on natural boundaries first
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_sentences = []
        chunk_index = start_index
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                # Current chunk is full, save it
                if current_chunk:
                    chunk = self._create_enhanced_chunk(
                        text=current_chunk.strip(),
                        content_chunk=content_chunk,
                        doc_id=doc_id,
                        chunk_index=chunk_index,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_sentences)
                current_chunk = " ".join(overlap_sentences + [sentence])
                current_sentences = overlap_sentences + [sentence]
        
        # Add final chunk if there's remaining content
        if current_chunk.strip():
            chunk = self._create_enhanced_chunk(
                text=current_chunk.strip(),
                content_chunk=content_chunk,
                doc_id=doc_id,
                chunk_index=chunk_index,
                metadata=metadata,
                has_overlap=chunk_index > start_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_enhanced_chunk(self, 
                               text: str, 
                               content_chunk: ContentChunk, 
                               doc_id: str,
                               chunk_index: int,
                               metadata: DocumentMetadata,
                               has_overlap: bool = False) -> EnhancedChunk:
        """Create an enhanced chunk with comprehensive metadata"""
        
        chunk_id = f"{doc_id}_chunk_{chunk_index}"
        token_count = self.count_tokens(text)
        
        # Combine metadata from content chunk and document
        enhanced_metadata = {
            **content_chunk.metadata,
            'doc_title': metadata.title,
            'doc_author': metadata.author,
            'doc_created_date': metadata.created_date.isoformat() if metadata.created_date else None,
            'doc_file_size': metadata.file_size,
            'total_pages': metadata.pages,
            'chunk_token_count': token_count,
            'chunk_character_count': len(text),
            'has_overlap': has_overlap
        }
        
        return EnhancedChunk(
            text=text,
            metadata=enhanced_metadata,
            token_count=token_count,
            chunk_id=chunk_id,
            parent_doc_id=doc_id,
            page_number=content_chunk.page_number,
            section_title=content_chunk.section_title,
            chunk_index=chunk_index,
            overlap_with_previous=has_overlap
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Simple sentence splitting - can be enhanced with NLTK
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap with previous chunk"""
        if not sentences:
            return []
        
        # Calculate how many sentences to include for overlap
        overlap_text = ""
        overlap_sentences = []
        
        # Work backwards from end of sentences
        for sentence in reversed(sentences):
            test_overlap = sentence + " " + overlap_text if overlap_text else sentence
            if self.count_tokens(test_overlap) <= self.chunk_overlap:
                overlap_text = test_overlap
                overlap_sentences.insert(0, sentence)
            else:
                break
        
        return overlap_sentences
    
    def _generate_doc_id(self, filename: str) -> str:
        """Generate a document ID from filename"""
        # Remove extension and special characters
        doc_id = re.sub(r'[^a-zA-Z0-9_-]', '_', filename.lower())
        doc_id = re.sub(r'_+', '_', doc_id).strip('_')
        return doc_id
    
    def create_smart_chunks(self, 
                            content_chunks: List[ContentChunk], 
                            metadata: DocumentMetadata,
                            preserve_structure: bool = True) -> List[EnhancedChunk]:
        """Create chunks with smart structure preservation"""
        if not preserve_structure:
            return self.create_chunks_from_content(content_chunks, metadata)
        
        enhanced_chunks = []
        doc_id = self._generate_doc_id(metadata.filename)
        global_chunk_index = 0
        
        for content_chunk in content_chunks:
            # For structured content (with sections), try to keep sections together
            if content_chunk.section_title and metadata.file_type in ['markdown', 'docx']:
                section_chunks = self._create_section_aware_chunks(
                    content_chunk, doc_id, global_chunk_index, metadata
                )
                enhanced_chunks.extend(section_chunks)
                global_chunk_index += len(section_chunks)
            else:
                # Regular chunking for unstructured content
                if self.count_tokens(content_chunk.text) <= self.chunk_size:
                    chunk = self._create_enhanced_chunk(
                        text=content_chunk.text,
                        content_chunk=content_chunk,
                        doc_id=doc_id,
                        chunk_index=global_chunk_index,
                        metadata=metadata
                    )
                    enhanced_chunks.append(chunk)
                    global_chunk_index += 1
                else:
                    sub_chunks = self._split_large_content(content_chunk, doc_id, global_chunk_index, metadata)
                    enhanced_chunks.extend(sub_chunks)
                    global_chunk_index += len(sub_chunks)
        
        return enhanced_chunks
    
    def _create_section_aware_chunks(self, 
                                     content_chunk: ContentChunk, 
                                     doc_id: str,
                                     start_index: int,
                                     metadata: DocumentMetadata) -> List[EnhancedChunk]:
        """Create chunks while trying to preserve section boundaries"""
        text = content_chunk.text
        
        # If section fits in one chunk, keep it together
        if self.count_tokens(text) <= self.chunk_size:
            chunk = self._create_enhanced_chunk(
                text=text,
                content_chunk=content_chunk,
                doc_id=doc_id,
                chunk_index=start_index,
                metadata=metadata
            )
            return [chunk]
        
        # Section is too large, split it but preserve context
        # Add section title to each chunk for context
        section_title = content_chunk.section_title or ""
        if section_title:
            text_with_context = f"Section: {section_title}\n\n{text}"
        else:
            text_with_context = text
        
        # Create a temporary content chunk with context
        temp_content_chunk = ContentChunk(
            text=text_with_context,
            metadata=content_chunk.metadata,
            page_number=content_chunk.page_number,
            section_title=content_chunk.section_title,
            chunk_index=content_chunk.chunk_index
        )
        
        return self._split_large_content(temp_content_chunk, doc_id, start_index, metadata)
