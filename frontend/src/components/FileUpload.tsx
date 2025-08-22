'use client';

import { useState, useRef } from 'react';

interface UploadResponse {
  filename: string;
  file_type: string;
  chunks_created: number;
  metadata: {
    title?: string;
    author?: string;
    pages?: number;
    file_size?: number;
    created_date?: string;
  };
}

export default function FileUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setError(null);
    setUploadStatus(null);

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data: UploadResponse = await response.json();
      setUploadStatus(data);
      // Smoothly scroll to chat after a short delay to allow UI to update
      setTimeout(() => {
        const chat = document.getElementById('chat-section');
        chat?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    handleUpload(e.dataTransfer.files);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-300'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
          accept=".pdf,.docx,.md,.txt"
        />

        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
            <svg
              className="w-6 h-6 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          {isUploading ? (
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin" />
              <p className="text-sm text-gray-500">Uploading...</p>
            </div>
          ) : (
            <>
              <p className="text-lg font-medium">
                Drop your file here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, DOCX, Markdown, and Text files
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {uploadStatus && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <h3 className="font-medium text-green-900">Upload Successful!</h3>
          <div className="mt-2 text-sm text-green-800">
            <p>Filename: {uploadStatus.filename}</p>
            <p>Type: {uploadStatus.file_type}</p>
            <p>Chunks Created: {uploadStatus.chunks_created}</p>
            {uploadStatus.metadata && (
              <div className="mt-2 border-t border-green-200 pt-2">
                <p>Title: {uploadStatus.metadata.title || 'N/A'}</p>
                <p>Author: {uploadStatus.metadata.author || 'N/A'}</p>
                {uploadStatus.metadata.pages && (
                  <p>Pages: {uploadStatus.metadata.pages}</p>
                )}
                {uploadStatus.metadata.file_size && (
                  <p>Size: {formatFileSize(uploadStatus.metadata.file_size)}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
