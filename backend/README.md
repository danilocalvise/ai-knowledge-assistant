# AI Knowledge Assistant Backend

Enhanced backend with file upload, metadata extraction, and intelligent chunking capabilities.

## Features

### File Upload & Processing
- **Supported formats**: PDF, DOCX, Markdown, Plain Text
- **Automatic format detection** using python-magic
- **Metadata extraction** including:
  - Document title, author, creation date
  - Page numbers, file size
  - Section headings and structure

### Intelligent Chunking
- **Token-aware chunking** using tiktoken
- **Structure preservation** for markdown sections and document headings
- **Configurable overlap** between chunks
- **Metadata preservation** throughout the chunking process

### Enhanced Vector Store
- **Metadata-rich storage** with chunk-level and document-level metadata
- **Document management** with listing and deletion capabilities
- **Statistics and analytics** about the knowledge base

## API Endpoints

### File Upload
```
POST /api/upload
```
Upload and process files (PDF, DOCX, Markdown, Text)

**Request**: Form data with file
**Response**:
```json
{
  "filename": "document.pdf",
  "file_type": "pdf", 
  "chunks_created": 15,
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "pages": 10,
    "file_size": 1048576,
    "created_date": "2024-01-01T00:00:00"
  }
}
```

### Query Knowledge Base
```
POST /api/query
```
Search and get AI-generated answers with metadata

**Request**:
```json
{
  "query": "What is machine learning?",
  "top_k": 3
}
```

**Response**:
```json
{
  "results": [
    {
      "text": "Machine learning is...",
      "score": 0.95,
      "metadata": {
        "source_file": "ml_guide.pdf",
        "page_number": 5,
        "section_title": "Introduction to ML"
      }
    }
  ],
  "answer": "AI-generated comprehensive answer...",
  "total_results": 3
}
```

### Document Management
```
GET /api/documents
```
List all uploaded documents

```
DELETE /api/documents/{doc_id}
```
Delete a document and all its chunks

```
GET /api/stats
```
Get knowledge base statistics

### Legacy Endpoints
```
POST /api/ingest
```
Legacy text ingestion (backward compatible)

```
GET /api/health
```
Health check

## Installation

1. **Install core dependencies:**
```bash
pip install -r requirements.txt
```

2. **Optional: Install additional document processors**
```bash
# For PDF support (if not working, try alternative methods)
pip install PyMuPDF

# For better file type detection
pip install python-magic

# For advanced document processing
pip install unstructured[pdf,docx] nltk
```

3. **Set environment variables:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. **Run the server:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Current Status

✅ **Working Features:**
- File upload endpoint (`/api/upload`)
- Markdown file processing
- Text file processing  
- DOCX file processing
- Enhanced chunking with metadata
- Vector storage with metadata
- Query API with metadata results
- Document management (list, delete)
- Knowledge base statistics

⚠️ **Known Issues:**
- PDF processing may require additional setup depending on your environment
- python-magic requires system-level libmagic (optional)

## Troubleshooting

### PDF Processing Issues
If you encounter issues with PDF processing:
1. Try: `pip uninstall PyMuPDF && pip install PyMuPDF`
2. Alternative: Use other document formats (Markdown, DOCX, Text)
3. The system gracefully falls back and provides clear error messages

### File Type Detection
Without python-magic, the system uses file extensions for type detection, which works fine for most cases.

## Dependencies

- **FastAPI**: Web framework
- **PyMuPDF**: PDF processing
- **python-docx**: DOCX processing  
- **python-multipart**: File upload handling
- **python-magic**: File type detection
- **unstructured**: Advanced document processing
- **tiktoken**: Token counting
- **numpy**: Vector operations

## Configuration

The chunking service can be configured with:
- `chunk_size`: Maximum tokens per chunk (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `preserve_structure`: Keep document structure intact (default: True)

## Architecture

1. **File Processor**: Handles format detection and content extraction
2. **Chunking Service**: Creates intelligent chunks with metadata
3. **Vector Store**: Manages embeddings and metadata
4. **API Layer**: FastAPI endpoints for client interaction
