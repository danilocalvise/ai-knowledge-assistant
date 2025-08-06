# file_processor.py
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

# Optional imports for various document processors
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

@dataclass
class DocumentMetadata:
    """Metadata extracted from documents"""
    filename: str
    file_type: str
    file_size: int
    pages: int = 0
    author: str = ""
    title: str = ""
    subject: str = ""
    creator: str = ""
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    language: str = ""

@dataclass
class ContentChunk:
    """A chunk of content with associated metadata"""
    text: str
    metadata: Dict[str, any]
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: int = 0

class FileProcessor:
    """Handles file upload, format detection, and content extraction"""
    
    SUPPORTED_FORMATS = {
        'application/pdf': 'pdf',
        'text/markdown': 'markdown', 
        'text/x-markdown': 'markdown',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'text'
    }
    
    def __init__(self):
        self.mime = magic.Magic(mime=True) if MAGIC_AVAILABLE else None
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect file type using python-magic or fallback to file extension"""
        if MAGIC_AVAILABLE and self.mime:
            try:
                mime_type = self.mime.from_file(file_path)
                return self.SUPPORTED_FORMATS.get(mime_type, 'unknown')
            except Exception:
                pass  # Fall through to extension-based detection
        
        # Fallback to file extension
        ext = Path(file_path).suffix.lower()
        extension_map = {
            '.pdf': 'pdf',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.docx': 'docx',
            '.txt': 'text'
        }
        return extension_map.get(ext, 'unknown')
    
    def extract_pdf_content(self, file_path: str) -> Tuple[List[ContentChunk], DocumentMetadata]:
        """Extract content and metadata from PDF files"""
        if not PYMUPDF_AVAILABLE:
            raise ValueError("PyMuPDF (fitz) is not available. Install with: pip install PyMuPDF")
        
        doc = fitz.open(file_path)
        chunks = []
        
        # Extract metadata
        metadata = DocumentMetadata(
            filename=Path(file_path).name,
            file_type='pdf',
            file_size=os.path.getsize(file_path),
            pages=len(doc),
            author=doc.metadata.get('author', ''),
            title=doc.metadata.get('title', ''),
            subject=doc.metadata.get('subject', ''),
            creator=doc.metadata.get('creator', ''),
            created_date=self._parse_pdf_date(doc.metadata.get('creationDate')),
            modified_date=self._parse_pdf_date(doc.metadata.get('modDate'))
        )
        
        # Extract text content page by page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():  # Only add non-empty pages
                chunk = ContentChunk(
                    text=text.strip(),
                    metadata={
                        'source_file': metadata.filename,
                        'file_type': 'pdf',
                        'page_number': page_num + 1,
                        'total_pages': len(doc)
                    },
                    page_number=page_num + 1
                )
                chunks.append(chunk)
        
        doc.close()
        return chunks, metadata
    
    def extract_docx_content(self, file_path: str) -> Tuple[List[ContentChunk], DocumentMetadata]:
        """Extract content and metadata from DOCX files"""
        if not DOCX_AVAILABLE:
            raise ValueError("python-docx is not available. Install with: pip install python-docx")
        
        doc = Document(file_path)
        chunks = []
        
        # Extract metadata
        core_props = doc.core_properties
        metadata = DocumentMetadata(
            filename=Path(file_path).name,
            file_type='docx',
            file_size=os.path.getsize(file_path),
            pages=0,  # DOCX doesn't have fixed pages
            author=core_props.author or '',
            title=core_props.title or '',
            subject=core_props.subject or '',
            creator=core_props.author or '',
            created_date=core_props.created,
            modified_date=core_props.modified,
            language=core_props.language or ''
        )
        
        # Extract text content
        full_text = []
        current_section = None
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # Detect headings (simple heuristic based on style or formatting)
            if self._is_heading(para):
                current_section = text
            
            full_text.append(text)
        
        # Create chunks from paragraphs or sections
        if full_text:
            combined_text = '\n\n'.join(full_text)
            chunk = ContentChunk(
                text=combined_text,
                metadata={
                    'source_file': metadata.filename,
                    'file_type': 'docx',
                    'section_title': current_section
                },
                section_title=current_section
            )
            chunks.append(chunk)
        
        return chunks, metadata
    
    def extract_markdown_content(self, file_path: str) -> Tuple[List[ContentChunk], DocumentMetadata]:
        """Extract content and metadata from Markdown files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        metadata = DocumentMetadata(
            filename=Path(file_path).name,
            file_type='markdown',
            file_size=os.path.getsize(file_path),
            pages=0
        )
        
        # Parse markdown structure
        chunks = self._parse_markdown_sections(content, metadata.filename)
        
        return chunks, metadata
    
    def extract_text_content(self, file_path: str) -> Tuple[List[ContentChunk], DocumentMetadata]:
        """Extract content from plain text files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = DocumentMetadata(
            filename=Path(file_path).name,
            file_type='text',
            file_size=os.path.getsize(file_path),
            pages=0
        )
        
        chunk = ContentChunk(
            text=content.strip(),
            metadata={
                'source_file': metadata.filename,
                'file_type': 'text'
            }
        )
        
        return [chunk], metadata
    
    def process_file(self, file_path: str) -> Tuple[List[ContentChunk], DocumentMetadata]:
        """Main method to process any supported file type"""
        file_type = self.detect_file_type(file_path)
        
        if file_type == 'pdf':
            if not PYMUPDF_AVAILABLE:
                raise ValueError("PDF processing requires PyMuPDF. Install with: pip install PyMuPDF")
            return self.extract_pdf_content(file_path)
        elif file_type == 'docx':
            if not DOCX_AVAILABLE:
                raise ValueError("DOCX processing requires python-docx. Install with: pip install python-docx")
            return self.extract_docx_content(file_path)
        elif file_type == 'markdown':
            return self.extract_markdown_content(file_path)
        elif file_type == 'text':
            return self.extract_text_content(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported types: markdown, text" + 
                           (", pdf" if PYMUPDF_AVAILABLE else "") + 
                           (", docx" if DOCX_AVAILABLE else ""))
    
    def _parse_pdf_date(self, date_str: str) -> Optional[datetime]:
        """Parse PDF date format"""
        if not date_str:
            return None
        try:
            # PDF dates are often in format: D:YYYYMMDDHHmmSSOHH'mm
            if date_str.startswith('D:'):
                date_str = date_str[2:16]  # Take YYYYMMDDHHMMSS part
                return datetime.strptime(date_str, '%Y%m%d%H%M%S')
        except:
            pass
        return None
    
    def _is_heading(self, paragraph) -> bool:
        """Simple heuristic to detect if a paragraph is a heading"""
        # Check if paragraph uses heading style
        if paragraph.style.name.startswith('Heading'):
            return True
        
        # Check if text is short and potentially a title
        text = paragraph.text.strip()
        if len(text) < 100 and len(text.split()) < 10:
            # Check if it's all caps or title case
            if text.isupper() or text.istitle():
                return True
        
        return False
    
    def _parse_markdown_sections(self, content: str, filename: str) -> List[ContentChunk]:
        """Parse markdown content into sections based on headers"""
        chunks = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for markdown headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section if exists
                if current_content:
                    chunk = ContentChunk(
                        text='\n'.join(current_content).strip(),
                        metadata={
                            'source_file': filename,
                            'file_type': 'markdown',
                            'section_title': current_section
                        },
                        section_title=current_section
                    )
                    chunks.append(chunk)
                
                # Start new section
                current_section = header_match.group(2).strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # Add final section
        if current_content:
            chunk = ContentChunk(
                text='\n'.join(current_content).strip(),
                metadata={
                    'source_file': filename,
                    'file_type': 'markdown',
                    'section_title': current_section
                },
                section_title=current_section
            )
            chunks.append(chunk)
        
        return chunks
