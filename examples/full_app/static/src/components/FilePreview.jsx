import React, { useState, useEffect } from 'react';
import { getFileIconClass, stripLineNumbers, parseCSVtoTable, escapeHtml } from '../utils/helpers';

const PREVIEWABLE_EXTENSIONS = ['html', 'htm', 'svg'];

export default function FilePreview({ filePath, sessionId, onClose }) {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('code');
  const filename = filePath?.split('/').pop() || '';

  useEffect(() => {
    if (!filePath || !sessionId) return;

    setLoading(true);
    setError(null);

    fetch(`/files/content/${encodeURIComponent(filePath)}?session_id=${encodeURIComponent(sessionId)}`)
      .then(async (response) => {
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to load file');
        }
        const data = await response.json();
        setContent(stripLineNumbers(data.content));
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [filePath, sessionId]);

  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const isPreviewable = PREVIEWABLE_EXTENSIONS.includes(ext);

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="p-5 text-text-muted">Loading...</div>
      );
    }

    if (error) {
      return (
        <div className="p-5 text-error">Error loading file: {escapeHtml(error)}</div>
      );
    }

    if (!content) return null;

    // Live Preview mode for HTML/SVG
    if (mode === 'preview' && isPreviewable) {
      return renderLivePreview();
    }

    // Image Preview
    if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'ico'].includes(ext)) {
      const imageUrl = `/files/binary/${encodeURIComponent(filePath)}?session_id=${encodeURIComponent(sessionId)}`;
      return (
        <div className="flex justify-center items-center h-full p-5 bg-gray-900">
          <img
            src={imageUrl}
            alt={filename}
            className="max-w-full max-h-full object-contain rounded"
          />
        </div>
      );
    }

    // CSV Reader
    if (ext === 'csv') {
      const tableHtml = parseCSVtoTable(content);
      return (
        <div className="csv-container overflow-auto w-full h-full p-0">
          <div dangerouslySetInnerHTML={{ __html: tableHtml }} />
        </div>
      );
    }

    // PDF Reader
    if (ext === 'pdf') {
      return (
        <embed
          className="w-full h-full border-none"
          src={`/files/download/${encodeURIComponent(filePath)}?session_id=${sessionId}`}
          type="application/pdf"
        />
      );
    }

    // Code / Text (PrismJS)
    const languageMap = {
      'js': 'javascript', 'py': 'python', 'rs': 'rust', 'html': 'html',
      'css': 'css', 'json': 'json', 'md': 'markdown', 'sh': 'bash',
      'ts': 'typescript', 'go': 'go', 'java': 'java', 'cpp': 'cpp',
      'htm': 'html', 'svg': 'xml',
    };

    const lang = languageMap[ext] || 'none';

    return (
      <pre className="m-0 p-4 bg-transparent border-none rounded-none font-mono text-sm leading-relaxed min-h-full overflow-auto">
        <code className={`language-${lang} font-mono`}>{content}</code>
      </pre>
    );
  };

  const renderLivePreview = () => {
    if (ext === 'svg') {
      return (
        <iframe
          className="w-full h-full border-none bg-white"
          sandbox="allow-scripts allow-same-origin"
          title="SVG Preview"
          srcDoc={`
            <!DOCTYPE html>
            <html>
            <head>
              <style>
                body {
                  margin: 0;
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  min-height: 100vh;
                  background: #1a1a1a;
                }
                svg {
                  max-width: 90%;
                  max-height: 90vh;
                }
              </style>
            </head>
            <body>${content}</body>
            </html>
          `}
        />
      );
    } else {
      const previewUrl = `/preview/${sessionId}${filePath}`;
      return (
        <iframe
          className="w-full h-full border-none bg-white"
          sandbox="allow-scripts allow-same-origin"
          title="HTML Preview"
          src={previewUrl}
        />
      );
    }
  };

  const copyContent = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const downloadFile = () => {
    if (!filePath || !content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (content && window.Prism) {
      const codeElements = document.querySelectorAll('code[class*="language-"]');
      codeElements.forEach((el) => {
        Prism.highlightElement(el);
      });
    }
  }, [content, mode]);

  if (!filePath) return null;

  return (
    <div className="file-preview-panel w-1/2 min-w-[300px] bg-bg-panel border-l border-border-subtle flex flex-col h-full relative">
      <div className="preview-header flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-bg-element">
        <div className="preview-title flex items-center gap-2 font-mono text-sm text-text-main font-medium">
          <span className="preview-icon text-accent-primary text-base">
            <i className={getFileIconClass(filename)}></i>
          </span>
          <span>{filename}</span>
        </div>
        <div className="preview-actions flex gap-1">
          {isPreviewable && (
            <div className="preview-mode-toggle flex bg-bg-app rounded p-0.5 mr-2">
              <button
                className={`mode-btn bg-transparent border-none text-text-muted w-6.5 h-6.5 rounded cursor-pointer flex items-center justify-center transition-all text-sm hover:text-text-main hover:bg-bg-hover ${
                  mode === 'code' ? 'bg-accent-primary text-white' : ''
                }`}
                onClick={() => setMode('code')}
                title="View code"
              >
                <i className="ri-code-s-slash-line"></i>
              </button>
              <button
                className={`mode-btn bg-transparent border-none text-text-muted w-6.5 h-6.5 rounded cursor-pointer flex items-center justify-center transition-all text-sm hover:text-text-main hover:bg-bg-hover ${
                  mode === 'preview' ? 'bg-accent-primary text-white' : ''
                }`}
                onClick={() => setMode('preview')}
                title="Live preview"
              >
                <i className="ri-eye-line"></i>
              </button>
            </div>
          )}
          <button
            className="preview-btn bg-transparent border border-border-subtle text-text-muted w-7 h-7 rounded cursor-pointer flex items-center justify-center transition-all text-sm hover:bg-bg-hover hover:text-text-main hover:border-border-focus"
            onClick={copyContent}
            title="Copy content"
          >
            <i className="ri-file-copy-line"></i>
          </button>
          <button
            className="preview-btn bg-transparent border border-border-subtle text-text-muted w-7 h-7 rounded cursor-pointer flex items-center justify-center transition-all text-sm hover:bg-bg-hover hover:text-text-main hover:border-border-focus"
            onClick={downloadFile}
            title="Download"
          >
            <i className="ri-download-line"></i>
          </button>
          <button
            className="preview-btn close-btn bg-transparent border border-border-subtle text-text-muted w-7 h-7 rounded cursor-pointer flex items-center justify-center transition-all text-sm hover:bg-bg-hover hover:text-text-main hover:border-border-focus hover:bg-red-900/15 hover:text-error hover:border-error"
            onClick={onClose}
            title="Close"
          >
            <i className="ri-close-line"></i>
          </button>
        </div>
      </div>
      <div className="preview-content flex-1 overflow-hidden p-0 flex flex-col bg-gray-900">
        {renderPreview()}
      </div>
    </div>
  );
}
