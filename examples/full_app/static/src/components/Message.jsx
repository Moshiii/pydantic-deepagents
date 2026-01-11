import React from 'react';
import { formatMessage, escapeHtml } from '../utils/helpers';

export default function Message({ message, onFileClick, onApproval }) {
  const { type, content, tools, thinking, status, todos, approvalRequests } = message;

  const labelMap = {
    'user': { text: 'You', icon: 'ri-user-smile-line', color: 'text-accent-primary' },
    'assistant': { text: 'Deep Agent', icon: 'ri-robot-2-fill', color: 'text-success' },
    'system': { text: 'System', icon: 'ri-error-warning-fill', color: 'text-warning' },
  };

  const info = labelMap[type] || labelMap['system'];

  return (
    <div className={`message flex flex-col gap-2 fade-in ${type === 'user' ? 'user' : ''}`}>
      <div className={`message-header flex items-center gap-2 text-xs font-semibold text-text-muted uppercase font-mono tracking-wider mb-1 ${info.color}`}>
        <i className={`${info.icon} text-sm`}></i>
        <span>{info.text}</span>
      </div>

      {thinking && (
        <div className="message-thinking border-l-2 border-border-focus my-2 pl-3">
          <span className="thinking-label text-xs uppercase text-text-muted mb-1 block">
            <i className="ri-brain-line"></i> Thinking...
          </span>
          <div className="thinking-content text-sm text-gray-500 font-mono whitespace-pre-wrap">
            {thinking}
          </div>
        </div>
      )}

      {tools && tools.length > 0 && (
        <div className="message-tools mb-2 flex flex-col gap-1">
          {tools.map((tool, idx) => (
            <div key={idx} className="tool-call font-mono text-xs bg-black border border-border-subtle rounded overflow-hidden">
              <div className="tool-header bg-bg-element px-3 py-1.5 flex items-center gap-2 border-b border-border-subtle">
                <span className="tool-name text-accent-primary font-semibold">./{escapeHtml(tool.name)}</span>
                <span className={`tool-status ml-auto uppercase text-xs opacity-70 ${
                  tool.status === 'streaming' ? 'text-warning' :
                  tool.status === 'running' ? 'text-warning' :
                  tool.status === 'done' ? 'text-success' : 'text-text-muted'
                }`}>
                  {tool.status === 'streaming' ? 'STREAMING' :
                   tool.status === 'running' ? 'RUNNING...' :
                   tool.status === 'done' ? 'done' : tool.status}
                </span>
              </div>
              {tool.args && (
                <div className="tool-args px-3 py-2 text-text-muted bg-black m-0 whitespace-pre-wrap border-none">
                  {typeof tool.args === 'string' ? (
                    <code>{escapeHtml(tool.args)}</code>
                  ) : (
                    Object.entries(tool.args).map(([key, value]) => (
                      <div key={key}>
                        <span className="arg-key text-accent-primary">{escapeHtml(key)}:</span>{' '}
                        <span className="arg-value text-text-muted">
                          {escapeHtml(typeof value === 'string' && value.length > 100
                            ? value.substring(0, 100) + '...'
                            : JSON.stringify(value))}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
              {tool.output && (
                <div className="tool-output border-t border-dashed border-border-subtle">
                  <pre className="px-3 py-2 text-success bg-black m-0 whitespace-pre-wrap border-none">
                    {escapeHtml(tool.output)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {todos && todos.length > 0 && (
        <div className="message-todos mt-3 px-3.5 py-3 bg-bg-element border border-border-subtle rounded-md font-mono text-xs">
          <div className="todos-header flex items-center gap-1.5 text-text-muted text-xs uppercase tracking-wider mb-2 pb-1.5 border-b border-border-subtle">
            <i className="ri-list-check-2 text-xs text-accent-primary"></i>
            Task Progress{' '}
            <span className="todos-count ml-auto text-text-main font-medium">
              {todos.filter(t => t.status === 'completed').length}/{todos.length}
            </span>
          </div>
          <div className="todos-items flex flex-col gap-1">
            {todos.map((todo, idx) => {
              const status = todo.status || 'pending';
              const iconMap = {
                'completed': 'ri-checkbox-circle-fill',
                'in_progress': 'ri-loader-4-line',
                'pending': 'ri-checkbox-blank-circle-line',
              };
              const icon = iconMap[status] || iconMap['pending'];
              const text = status === 'in_progress' && todo.activeForm ? todo.activeForm : todo.content;
              return (
                <div
                  key={idx}
                  className={`todo-item-inline flex items-start gap-2 py-1 text-text-main leading-snug ${
                    status === 'completed' ? 'text-text-muted line-through opacity-70' : ''
                  }`}
                >
                  <i className={`${icon} text-sm flex-shrink-0 mt-0.5 ${
                    status === 'completed' ? 'text-success' :
                    status === 'in_progress' ? 'text-warning pulse' :
                    'text-text-muted'
                  }`}></i>
                  <span>{escapeHtml(text)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {status && (
        <div className="message-status-line text-xs text-gray-500 font-mono mt-1 pl-4">
          <i className="ri-loader-4-line spin inline-block mr-1"></i>
          {escapeHtml(status)}
        </div>
      )}

      {approvalRequests && approvalRequests.length > 0 && (
        <div className="approval-dialog bg-bg-panel border border-accent-primary rounded-lg p-6 mt-4 fade-in">
          <h4 className="text-text-main font-semibold mb-2 text-sm flex items-center gap-2">
            <i className="ri-alert-line text-base text-warning"></i>
            Approval Required
          </h4>
          <p className="text-text-muted mb-6 text-sm">
            The following operations require your approval:
          </p>
          {approvalRequests.map((req, idx) => (
            <div key={idx} className="approval-item bg-black border border-border-subtle rounded-md p-3 mb-3 font-mono text-xs">
              <div className="approval-tool flex items-center gap-2 text-accent-primary mb-2 pb-2 border-b border-border-subtle">
                <span className="tool-icon">
                  <i className="ri-settings-5-line"></i>
                </span>
                <strong>{escapeHtml(req.tool_name)}</strong>
              </div>
              <div className="approval-args text-text-muted whitespace-pre-wrap leading-snug">
                {typeof req.args === 'string' ? (
                  <code>{escapeHtml(req.args)}</code>
                ) : (
                  Object.entries(req.args || {}).map(([key, value]) => (
                    <div key={key}>
                      <span className="arg-key text-accent-primary">{escapeHtml(key)}:</span>{' '}
                      <span className="arg-value text-text-muted">
                        {escapeHtml(typeof value === 'string' && value.length > 100
                          ? value.substring(0, 100) + '...'
                          : JSON.stringify(value))}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
          <div className="approval-buttons flex gap-3 mt-6">
            <button
              className="approve-btn flex-1 px-2.5 py-2.5 rounded-md font-ui text-sm font-medium cursor-pointer transition-all bg-success text-black hover:opacity-90 hover:shadow-[0_0_10px_rgba(105,179,138,0.2)]"
              onClick={() => onApproval && onApproval(approvalRequests, true)}
            >
              Approve All
            </button>
            <button
              className="deny-btn flex-1 px-2.5 py-2.5 rounded-md font-ui text-sm font-medium cursor-pointer transition-all bg-transparent border border-border-subtle text-text-muted hover:border-error hover:text-error hover:bg-red-900/10"
              onClick={() => onApproval && onApproval(approvalRequests, false)}
            >
              Deny All
            </button>
          </div>
        </div>
      )}

      {content && (
        <div
          className={`message-content text-text-main text-base leading-relaxed font-normal ${
            type === 'user' ? 'bg-bg-panel px-4 py-3 rounded-lg border border-border-subtle font-mono text-sm' : ''
          }`}
          dangerouslySetInnerHTML={{ __html: formatMessage(content) }}
        />
      )}

      {type === 'system' && content && content.includes('Ready via Deep Agent') && (
        <div className="welcome-banner text-center p-8 border border-border-subtle rounded-lg bg-bg-element mb-8">
          <h3 className="font-medium mb-2 text-text-main flex items-center justify-center gap-2">
            <i className="ri-flashlight-fill"></i> Ready via Deep Agent
          </h3>
          <p className="text-text-muted mb-4">System initialized. Waiting for commands.</p>
          <div className="capabilities text-xs text-text-muted font-mono flex justify-center flex-wrap gap-3">
            <span className="flex items-center gap-1">
              <i className="ri-file-text-line"></i> File Ops
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <i className="ri-terminal-box-line"></i> Python Sandbox
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <i className="ri-bar-chart-box-line"></i> Data Analysis
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
