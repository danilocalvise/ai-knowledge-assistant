#!/usr/bin/env python3
"""
Test script for the enhanced backend functionality
"""

import httpx
import asyncio
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

async def test_file_upload():
    """Test file upload functionality"""
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("Testing health endpoint...")
        health_response = await client.get(f"{BASE_URL}/api/health")
        print(f"Health: {health_response.json()}")
        
        # Test file upload with sample Markdown
        sample_md_path = Path("test_document.md")
        if sample_md_path.exists():
            print(f"\nUploading {sample_md_path}...")
            
            with open(sample_md_path, "rb") as f:
                files = {"file": (sample_md_path.name, f, "text/markdown")}
                upload_response = await client.post(f"{BASE_URL}/api/upload", files=files)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                print(f"Upload successful!")
                print(json.dumps(upload_data, indent=2))
                
                # Test query
                print("\nTesting query...")
                query_data = {
                    "query": "What is this document about?",
                    "top_k": 3
                }
                query_response = await client.post(f"{BASE_URL}/api/query", json=query_data)
                
                if query_response.status_code == 200:
                    query_result = query_response.json()
                    print("Query results:")
                    print(f"Answer: {query_result['answer']}")
                    print(f"Found {query_result['total_results']} relevant chunks")
                    
                    for i, result in enumerate(query_result['results'][:2]):
                        print(f"\nResult {i+1} (score: {result['score']:.3f}):")
                        print(f"Text preview: {result['text'][:200]}...")
                        if result['metadata']:
                            print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
                else:
                    print(f"Query failed: {query_response.status_code}")
                    print(query_response.text)
            else:
                print(f"Upload failed: {upload_response.status_code}")
                print(upload_response.text)
        else:
            print(f"Sample markdown not found at {sample_md_path}")
            print("Creating a test markdown file...")
            with open(sample_md_path, "w") as f:
                f.write("# Test Document\n\nThis is a test document for the AI Knowledge Assistant.")
            print("Test file created. Try running the script again.")
        
        # Test document listing
        print("\nTesting document listing...")
        docs_response = await client.get(f"{BASE_URL}/api/documents")
        if docs_response.status_code == 200:
            docs = docs_response.json()
            print(f"Found {len(docs)} documents:")
            for doc in docs:
                print(f"- {doc['filename']} ({doc['file_type']}) - {doc['total_chunks']} chunks")
        
        # Test stats
        print("\nTesting stats...")
        stats_response = await client.get(f"{BASE_URL}/api/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print("Knowledge base stats:")
            print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    print("Testing Enhanced AI Knowledge Assistant Backend")
    print("=" * 50)
    print("Make sure the backend is running on http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")
    print()
    
    try:
        asyncio.run(test_file_upload())
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend server is running!")
