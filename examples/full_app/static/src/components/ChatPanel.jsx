import React, { useState, useRef, useEffect, useCallback } from 'react';
import Message from './Message';
import { useWebSocket } from '../hooks/useWebSocket';

export default function ChatPanel({ sessionId, onFileClick }) {
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Ready via Deep Agent\nSystem initialized. Waiting for commands.',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const currentMessageRef = useRef(null);
  const currentToolsRef = useRef(null);
  const streamedTextRef = useRef('');
  const streamingToolArgsRef = useRef('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'session_created':
        if (data.session_id && !sessionId) {
          localStorage.setItem('sessionId', data.session_id);
        }
        break;

      case 'start':
        currentMessageRef.current = {
          type: 'assistant',
          content: '',
          tools: [],
          thinking: '',
        };
        currentToolsRef.current = null;
        streamedTextRef.current = '';
        setMessages(prev => [...prev, currentMessageRef.current]);
        break;

      case 'status':
        if (currentMessageRef.current) {
          currentMessageRef.current.status = data.content;
          setMessages(prev => [...prev]);
        }
        break;

      case 'tool_call_start':
        if (!currentMessageRef.current) break;
        if (!currentMessageRef.current.tools) {
          currentMessageRef.current.tools = [];
        }
        streamingToolArgsRef.current = '';
        const streamingTool = {
          name: data.tool_name,
          tool_call_id: data.tool_call_id,
          status: 'streaming',
          args: '',
        };
        currentMessageRef.current.tools.push(streamingTool);
        currentToolsRef.current = streamingTool;
        setMessages(prev => [...prev]);
        break;

      case 'tool_args_delta':
        if (currentToolsRef.current) {
          streamingToolArgsRef.current += data.args_delta;
          currentToolsRef.current.args = streamingToolArgsRef.current;
          setMessages(prev => [...prev]);
        }
        break;

      case 'tool_start':
        if (currentToolsRef.current && currentToolsRef.current.status === 'streaming') {
          currentToolsRef.current.status = 'running';
          currentToolsRef.current.args = data.args;
        } else if (currentMessageRef.current) {
          if (!currentMessageRef.current.tools) {
            currentMessageRef.current.tools = [];
          }
          const tool = {
            name: data.tool_name,
            status: 'running',
            args: data.args,
          };
          currentMessageRef.current.tools.push(tool);
          currentToolsRef.current = tool;
        }
        setMessages(prev => [...prev]);
        break;

      case 'tool_output':
        if (currentToolsRef.current) {
          currentToolsRef.current.output = data.output;
          currentToolsRef.current.status = 'done';
          setMessages(prev => [...prev]);
        }
        break;

      case 'text_delta':
        if (currentMessageRef.current) {
          streamedTextRef.current += data.content;
          currentMessageRef.current.content = streamedTextRef.current;
          setMessages(prev => [...prev]);
        }
        break;

      case 'thinking_delta':
        if (currentMessageRef.current) {
          if (!currentMessageRef.current.thinking) {
            currentMessageRef.current.thinking = '';
          }
          currentMessageRef.current.thinking += data.content;
          setMessages(prev => [...prev]);
        }
        break;

      case 'response':
        if (currentMessageRef.current) {
          currentMessageRef.current.content = data.content;
          setMessages(prev => [...prev]);
        }
        break;

      case 'todos_update':
        if (currentMessageRef.current) {
          currentMessageRef.current.todos = data.todos || [];
          setMessages(prev => [...prev]);
        }
        break;

      case 'done':
        currentMessageRef.current = null;
        currentToolsRef.current = null;
        break;

      case 'error':
        if (currentMessageRef.current) {
          currentMessageRef.current.content = `Error: ${data.content}`;
          currentMessageRef.current.type = 'system';
        } else {
          setMessages(prev => [...prev, {
            type: 'system',
            content: `Error: ${data.content}`,
          }]);
        }
        currentMessageRef.current = null;
        currentToolsRef.current = null;
        break;

      case 'approval_required':
        if (currentMessageRef.current) {
          currentMessageRef.current.approvalRequests = data.requests;
          setMessages(prev => [...prev]);
        }
        break;
    }
  }, [sessionId]);

  const { send: sendWebSocket, isConnected } = useWebSocket('/ws/chat', handleWebSocketMessage);

  const handleApproval = useCallback((requests, approved) => {
    const approvalResponse = {};
    for (const req of requests) {
      approvalResponse[req.tool_call_id] = approved;
    }
    sendWebSocket({ approval: approvalResponse });
    
    // Update the message to show approval status
    setMessages(prev => prev.map(msg => {
      if (msg === currentMessageRef.current && msg.approvalRequests) {
        return {
          ...msg,
          approvalRequests: undefined,
          content: msg.content || `${approved ? '✓ Approved' : '✗ Denied'} - continuing...`,
        };
      }
      return msg;
    }));
  }, [sendWebSocket]);

  const sendMessage = () => {
    const message = inputValue.trim();
    if (!message || !isConnected) return;

    setInputValue('');
    setMessages(prev => [...prev, {
      type: 'user',
      content: message,
    }]);

    const payload = { message };
    if (sessionId) {
      payload.session_id = sessionId;
    }
    sendWebSocket(payload);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
  };

  const sendQuickMessage = (message) => {
    setInputValue(message);
    setTimeout(() => sendMessage(), 0);
  };

  return (
    <div className="chat-panel flex flex-col flex-1 min-w-0 h-full overflow-hidden">
      <div className="chat-stream flex-1 overflow-y-auto px-[15%] py-8 flex flex-col gap-8">
        {messages.map((msg, idx) => (
          <Message key={idx} message={msg} onFileClick={onFileClick} onApproval={handleApproval} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container px-[15%] py-6 bg-bg-app border-t border-border-subtle">
        <div className="input-wrapper relative bg-bg-panel border border-border-subtle rounded-lg p-0 transition-colors focus-within:border-accent-primary focus-within:shadow-[0_0_0_1px_var(--accent-glow)]">
          <textarea
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or request..."
            className="w-full bg-transparent border-none text-text-main p-4 pr-12 font-ui text-base resize-none outline-none min-h-[56px] max-h-[200px]"
            rows={1}
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected}
            className="absolute right-2 bottom-2 bg-bg-element border border-border-subtle text-text-muted w-8 h-8 rounded cursor-pointer flex items-center justify-center transition-all hover:bg-accent-primary hover:text-white hover:border-accent-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i className="ri-send-plane-fill text-base"></i>
          </button>
        </div>
        <div className="input-hints flex gap-2 mt-3 overflow-x-auto pb-1">
          <button
            onClick={() => sendQuickMessage('Load the data-analysis skill')}
            className="bg-transparent border border-border-subtle text-text-muted px-3 py-1.5 rounded-full text-xs cursor-pointer whitespace-nowrap transition-all flex items-center gap-1.5 hover:border-text-muted hover:text-text-main"
          >
            <i className="ri-database-2-line text-sm"></i>
            Load Data Skill
          </button>
          <button
            onClick={() => sendQuickMessage('Analyze the uploaded CSV file')}
            className="bg-transparent border border-border-subtle text-text-muted px-3 py-1.5 rounded-full text-xs cursor-pointer whitespace-nowrap transition-all flex items-center gap-1.5 hover:border-text-muted hover:text-text-main"
          >
            <i className="ri-file-chart-line text-sm"></i>
            Analyze CSV
          </button>
        </div>
      </div>
    </div>
  );
}
