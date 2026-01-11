import React, { useState, useEffect, useRef } from 'react';
import { getFileIconClass, escapeHtml } from '../utils/helpers';

export default function Sidebar({ sessionId, onFileSelect, onReset }) {
  const [currentTab, setCurrentTab] = useState('uploads');
  const [files, setFiles] = useState({ uploads: [], workspace: [] });
  const [uploadStatus, setUploadStatus] = useState('');
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const fileInputRef = useRef(null);
  const uploadAreaRef = useRef(null);

  useEffect(() => {
    if (sessionId) {
      refreshFiles();
    }
  }, [sessionId, currentTab]);

  const refreshFiles = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`/files?session_id=${encodeURIComponent(sessionId)}`);
      if (!response.ok) return;
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    setUploadStatus(`Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    let url = '/upload';
    if (sessionId) {
      url += `?session_id=${encodeURIComponent(sessionId)}`;
    }

    try {
      const response = await fetch(url, { method: 'POST', body: formData });
      const data = await response.json();

      if (response.ok) {
        setUploadStatus(`Uploaded: ${data.filename}`);
        refreshFiles();
      } else {
        setUploadStatus(`Error: ${data.detail}`);
      }
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    setTimeout(() => setUploadStatus(''), 3000);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    uploadAreaRef.current?.classList.add('border-text-muted', 'bg-bg-hover');
  };

  const handleDragLeave = () => {
    uploadAreaRef.current?.classList.remove('border-text-muted', 'bg-bg-hover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    uploadAreaRef.current?.classList.remove('border-text-muted', 'bg-bg-hover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  };

  const buildFileTree = (filePaths) => {
    const root = {};

    for (const filePath of filePaths) {
      let normalizedPath = filePath;
      if (normalizedPath.startsWith('/workspace/')) {
        normalizedPath = normalizedPath.slice('/workspace/'.length);
      } else if (normalizedPath.startsWith('/')) {
        normalizedPath = normalizedPath.slice(1);
      }

      const parts = normalizedPath.split('/');
      let current = root;

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (!part) continue;

        if (i === parts.length - 1) {
          current[part] = { __isFile: true, __path: filePath };
        } else {
          if (!current[part]) {
            current[part] = {};
          }
          current = current[part];
        }
      }
    }

    return root;
  };

  const toggleFolder = (folderPath) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(folderPath)) {
        newSet.delete(folderPath);
      } else {
        newSet.add(folderPath);
      }
      return newSet;
    });
  };

  const renderFileTree = (node, depth = 0, parentPath = '/workspace') => {
    const entries = Object.entries(node).sort((a, b) => {
      const aIsFile = a[1].__isFile;
      const bIsFile = b[1].__isFile;
      if (aIsFile && !bIsFile) return 1;
      if (!aIsFile && bIsFile) return -1;
      return a[0].localeCompare(b[0]);
    });

    return entries.map(([name, value]) => {
      if (name.startsWith('__')) return null;

      const currentPath = `${parentPath}/${name}`;
      const indent = depth * 12;

      if (value.__isFile) {
        const iconClass = getFileIconClass(name);
        return (
          <div
            key={currentPath}
            className="file-item flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer text-text-muted hover:bg-bg-element hover:text-text-main whitespace-nowrap overflow-hidden text-ellipsis"
            style={{ paddingLeft: `${indent + 8}px` }}
            onClick={() => onFileSelect(value.__path)}
            title={value.__path}
          >
            <i className={`${iconClass} text-base`}></i>
            <span className="overflow-hidden text-ellipsis">{name}</span>
          </div>
        );
      } else {
        const isExpanded = expandedFolders.has(currentPath);
        const folderIcon = isExpanded ? 'ri-folder-open-line' : 'ri-folder-line';
        const chevronIcon = isExpanded ? 'ri-arrow-down-s-line' : 'ri-arrow-right-s-line';

        return (
          <div key={currentPath}>
            <div
              className={`folder-item flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer text-text-muted hover:bg-bg-element hover:text-text-main whitespace-nowrap overflow-hidden text-ellipsis select-none ${isExpanded ? 'text-text-main' : ''}`}
              style={{ paddingLeft: `${indent + 8}px` }}
              onClick={() => toggleFolder(currentPath)}
            >
              <i className={`folder-chevron ${chevronIcon} text-sm text-text-muted transition-transform`}></i>
              <i className={`folder-icon ${folderIcon} text-base ${isExpanded ? 'text-accent-primary' : 'text-warning'}`}></i>
              <span className="overflow-hidden text-ellipsis">{name}</span>
            </div>
            {isExpanded && (
              <div className="folder-children">
                {renderFileTree(value, depth + 1, currentPath)}
              </div>
            )}
          </div>
        );
      }
    }).filter(Boolean);
  };

  const currentFiles = currentTab === 'uploads' ? files.uploads : files.workspace;
  const fileTree = currentTab === 'workspace' ? buildFileTree(currentFiles) : null;

  return (
    <aside className="sidebar bg-bg-panel border-r border-border-subtle flex flex-col h-full overflow-hidden">
      <div className="sidebar-header p-6 border-b border-border-subtle whitespace-nowrap">
        <div className="brand font-mono font-semibold text-sm flex items-center gap-2.5 text-text-main">
          <span className="brand-icon text-accent-primary text-lg">
            <i className="ri-robot-2-line"></i>
          </span>
          Deep Agent
        </div>
      </div>

      <div className="sidebar-content flex-1 overflow-y-auto p-6">
        <div className="section-title text-xs uppercase tracking-wider text-text-muted mb-3 font-semibold">
          Files & Context
        </div>

        <div
          ref={uploadAreaRef}
          className="upload-zone border border-dashed border-border-focus bg-bg-app rounded-md p-3 cursor-pointer flex items-center justify-center gap-2 transition-all hover:border-text-muted hover:bg-bg-hover"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={handleFileSelect}
          />
          <span className="upload-icon text-accent-primary text-lg">
            <i className="ri-upload-cloud-2-line"></i>
          </span>
          <span className="upload-text text-sm text-text-muted">Upload File</span>
        </div>

        {uploadStatus && (
          <div className={`mt-2 text-xs ${uploadStatus.includes('Error') ? 'text-error' : 'text-success'}`}>
            {uploadStatus.includes('Uploading') && <i className="ri-loader-4-line spin inline-block mr-1"></i>}
            {uploadStatus.includes('Uploaded') && <i className="ri-check-line inline-block mr-1"></i>}
            {uploadStatus}
          </div>
        )}

        <div className="tabs flex gap-1 my-4 bg-bg-app p-1 rounded-md">
          <button
            className={`tab-btn flex-1 bg-transparent border-none text-text-muted px-1.5 py-1.5 text-xs cursor-pointer rounded transition-all ${
              currentTab === 'uploads' ? 'bg-bg-element text-text-main font-medium' : ''
            }`}
            onClick={() => setCurrentTab('uploads')}
          >
            Uploads
          </button>
          <button
            className={`tab-btn flex-1 bg-transparent border-none text-text-muted px-1.5 py-1.5 text-xs cursor-pointer rounded transition-all ${
              currentTab === 'workspace' ? 'bg-bg-element text-text-main font-medium' : ''
            }`}
            onClick={() => setCurrentTab('workspace')}
          >
            Workspace
          </button>
        </div>

        <div className="file-tree font-mono text-sm">
          {currentTab === 'uploads' ? (
            currentFiles.length === 0 ? (
              <p className="empty-state text-text-muted text-sm">No files yet</p>
            ) : (
              currentFiles.map((file) => {
                const name = typeof file === 'string' ? file.split('/').pop() : file;
                const fullPath = `/uploads/${name}`;
                const iconClass = getFileIconClass(name);
                return (
                  <div
                    key={fullPath}
                    className="file-item flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer text-text-muted hover:bg-bg-element hover:text-text-main whitespace-nowrap overflow-hidden text-ellipsis"
                    onClick={() => onFileSelect(fullPath)}
                    title="Click to preview"
                  >
                    <i className={`${iconClass} text-base`}></i>
                    <span className="overflow-hidden text-ellipsis">{name}</span>
                  </div>
                );
              })
            )
          ) : (
            currentFiles.length === 0 ? (
              <p className="empty-state text-text-muted text-sm">No files yet</p>
            ) : (
              renderFileTree(fileTree)
            )
          )}
        </div>
      </div>

      <div className="sidebar-footer p-4 border-t border-border-subtle">
        <button
          className="action-btn w-full bg-transparent border border-border-subtle text-text-muted px-2 py-2 rounded-md cursor-pointer text-xs flex items-center justify-center gap-2 transition-all hover:bg-bg-element hover:text-text-main hover:border-border-focus"
          onClick={onReset}
        >
          <span className="icon">
            <i className="ri-refresh-line"></i>
          </span>
          Reset Session
        </button>
      </div>
    </aside>
  );
}
