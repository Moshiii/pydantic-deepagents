import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import FilePreview from './components/FilePreview';

export default function App() {
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem('sessionId') || null;
  });
  const [previewFile, setPreviewFile] = useState(null);
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [isResizing, setIsResizing] = useState(false);
  const resizerRef = useRef(null);

  useEffect(() => {
    window.openFilePreview = (filePath) => {
      setPreviewFile(filePath);
    };
    return () => {
      delete window.openFilePreview;
    };
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--sidebar-width', `${sidebarWidth}px`);
  }, [sidebarWidth]);

  const handleMouseDown = (e) => {
    setIsResizing(true);
    resizerRef.current?.classList.add('bg-accent-primary');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;

      let newWidth = e.clientX;
      if (newWidth < 200) newWidth = 200;
      if (newWidth > 600) newWidth = 600;

      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        resizerRef.current?.classList.remove('bg-accent-primary');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset the agent? This will clear all files and history.')) {
      return;
    }

    try {
      if (sessionId) {
        await fetch(`/reset?session_id=${encodeURIComponent(sessionId)}`, { method: 'POST' });
      }
      setSessionId(null);
      localStorage.removeItem('sessionId');
      window.location.reload();
    } catch (error) {
      alert('Error resetting agent: ' + error.message);
    }
  };

  return (
    <div className="layout grid h-screen" style={{ gridTemplateColumns: `${sidebarWidth}px 4px 1fr` }}>
      <Sidebar
        sessionId={sessionId}
        onFileSelect={setPreviewFile}
        onReset={handleReset}
      />

      <div
        ref={resizerRef}
        className="resizer w-1 bg-bg-app cursor-col-resize transition-colors hover:bg-accent-primary z-10"
        onMouseDown={handleMouseDown}
      />

      <main className="main-area flex flex-row bg-bg-app relative h-full overflow-hidden">
        <ChatPanel sessionId={sessionId} onFileClick={setPreviewFile} />

        {previewFile && (
          <FilePreview
            filePath={previewFile}
            sessionId={sessionId}
            onClose={() => setPreviewFile(null)}
          />
        )}
      </main>
    </div>
  );
}
