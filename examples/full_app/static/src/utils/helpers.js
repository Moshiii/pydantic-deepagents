export function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function getFileIconClass(filename) {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const icons = {
    'py': 'ri-code-s-slash-line',
    'js': 'ri-javascript-line',
    'ts': 'ri-braces-line',
    'json': 'ri-braces-line',
    'csv': 'ri-grid-line',
    'md': 'ri-markdown-line',
    'txt': 'ri-file-text-line',
    'html': 'ri-html5-line',
    'css': 'ri-css3-line',
    'pdf': 'ri-file-pdf-line',
    'zip': 'ri-file-zip-line',
    'png': 'ri-image-line',
    'jpg': 'ri-image-line',
    'jpeg': 'ri-image-line',
    'gif': 'ri-image-line',
    'webp': 'ri-image-line',
    'svg': 'ri-image-line',
  };
  return icons[ext] || 'ri-file-line';
}

export function formatMessage(content) {
  if (!content) return '';
  
  let html = content;
  
  // 1. 代码块（必须在其他处理之前）
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, code) => {
    const escapedCode = escapeHtml(code.trim());
    return `<pre class="bg-gray-900 border border-border-subtle p-4 rounded-md overflow-x-auto my-4"><code class="language-${lang || 'text'} font-mono text-sm">${escapedCode}</code></pre>`;
  });
  
  // 2. 行内代码（避免匹配代码块内的）
  html = html.replace(/`([^`\n]+)`/g, '<code class="bg-white/10 px-1 py-0.5 rounded text-accent-primary font-mono text-sm">$1</code>');
  
  // 3. 表格
  html = html.replace(/\|(.+)\|\n\|([-|:\s]+)\|\n((?:\|.+\|\n?)+)/g, (match, header, separator, rows) => {
    const headers = header.split('|').map(h => h.trim()).filter(h => h);
    const alignments = separator.split('|').map(s => {
      const trimmed = s.trim();
      if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center';
      if (trimmed.endsWith(':')) return 'right';
      return 'left';
    }).filter((_, i) => i > 0); // 跳过第一个空元素
    
    let tableHtml = '<table class="w-full border-collapse my-4 border border-border-subtle rounded-md overflow-hidden"><thead><tr class="bg-bg-element">';
    headers.forEach((h, i) => {
      const align = alignments[i] || 'left';
      tableHtml += `<th class="px-4 py-2 text-left font-semibold text-accent-primary border-b border-border-subtle" style="text-align: ${align}">${escapeHtml(h)}</th>`;
    });
    tableHtml += '</tr></thead><tbody>';
    
    const rowLines = rows.trim().split('\n');
    rowLines.forEach((row, rowIdx) => {
      if (!row.trim()) return;
      const cells = row.split('|').map(c => c.trim()).filter((c, i) => i > 0 && i <= headers.length);
      tableHtml += `<tr class="${rowIdx % 2 === 0 ? 'bg-bg-panel' : 'bg-bg-element'} hover:bg-bg-hover">`;
      cells.forEach((cell, i) => {
        const align = alignments[i] || 'left';
        tableHtml += `<td class="px-4 py-2 border-b border-border-subtle text-text-main" style="text-align: ${align}">${escapeHtml(cell)}</td>`;
      });
      tableHtml += '</tr>';
    });
    
    tableHtml += '</tbody></table>';
    return tableHtml;
  });
  
  // 4. 标题
  html = html.replace(/^### (.*$)/gm, '<h3 class="text-xl font-semibold mt-6 mb-3 text-text-main">$1</h3>');
  html = html.replace(/^## (.*$)/gm, '<h2 class="text-2xl font-semibold mt-6 mb-3 text-text-main">$1</h2>');
  html = html.replace(/^# (.*$)/gm, '<h1 class="text-3xl font-bold mt-6 mb-4 text-text-main">$1</h1>');
  
  // 5. 无序列表
  html = html.replace(/^[\*\-\+] (.+)$/gm, '<li class="ml-6 list-disc">$1</li>');
  html = html.replace(/(<li class="ml-6 list-disc">.*<\/li>\n?)+/g, (match) => {
    return `<ul class="my-3 space-y-1">${match}</ul>`;
  });
  
  // 6. 有序列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li class="ml-6 list-decimal">$1</li>');
  html = html.replace(/(<li class="ml-6 list-decimal">.*<\/li>\n?)+/g, (match) => {
    return `<ol class="my-3 space-y-1">${match}</ol>`;
  });
  
  // 7. 粗体和斜体
  html = html.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-white">$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  
  // 8. 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-accent-primary underline hover:text-white" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // 9. 水平线
  html = html.replace(/^---$/gm, '<hr class="my-4 border-border-subtle">');
  
  // 10. 引用块
  html = html.replace(/^> (.+)$/gm, '<blockquote class="border-l-4 border-accent-primary pl-4 my-3 italic text-text-muted">$1</blockquote>');
  
  // 11. 换行（保留段落结构）
  // 先处理双换行（段落分隔）
  html = html.replace(/\n\n+/g, '</p><p class="my-2">');
  // 然后处理单换行
  html = html.replace(/\n/g, '<br>');
  
  // 12. 包装在段落中（如果还没有）
  if (!html.startsWith('<')) {
    html = '<p class="my-2">' + html + '</p>';
  } else if (!html.startsWith('<p')) {
    html = '<p class="my-2">' + html + '</p>';
  }
  
  // 13. 文件路径链接（在最后处理，避免被其他规则影响）
  html = linkifyFilePaths(html);
  
  return html;
}

export function linkifyFilePaths(html, onFileClick) {
  const pathPattern = /(\/(?:workspace|uploads|app|home|tmp|var|etc)\/[^\s<>"'`,;()[\]{}]+\.[a-zA-Z0-9]+)/g;
  return html.replace(pathPattern, (match, path) => {
    const cleanPath = path.replace(/[.,;:!?)]+$/, '');
    const trailing = path.slice(cleanPath.length);
    return `<span class="file-link cursor-pointer text-accent-primary underline underline-offset-2 hover:text-white" onclick="window.openFilePreview('${cleanPath}')" title="Click to preview">${escapeHtml(cleanPath)}</span>${trailing}`;
  });
}

export function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current.trim());
  return result;
}

export function parseCSVtoTable(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length === 0) return '<p>Empty CSV</p>';

  const headers = parseCSVLine(lines[0]);
  const numCols = headers.length;

  let html = '<table class="w-full min-w-full border-collapse font-mono text-xs text-text-main"><thead><tr>';
  html += `<th class="bg-bg-element sticky top-7 text-right w-10 min-w-10 p-2 border border-border-subtle border-r-2 border-r-border-subtle sticky left-0 z-10 bg-bg-panel text-text-muted">#</th>`;
  headers.forEach(h => html += `<th class="bg-bg-element sticky top-7 text-left font-semibold text-accent-primary border border-border-subtle p-2 z-20 whitespace-nowrap">${escapeHtml(h)}</th>`);
  html += '</tr></thead><tbody>';

  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;

    const row = parseCSVLine(lines[i]);

    html += '<tr>';
    html += `<td class="bg-bg-panel text-text-muted text-right w-10 min-w-10 p-2 border border-border-subtle border-r-2 border-r-border-subtle sticky left-0 z-10">${i}</td>`;
    for (let j = 0; j < numCols; j++) {
      const cell = row[j] || '';
      const displayCell = cell.length > 100 ? cell.substring(0, 100) + '...' : cell;
      html += `<td class="border border-border-subtle p-2 whitespace-nowrap max-w-xs overflow-hidden text-ellipsis hover:whitespace-pre-wrap hover:max-w-none hover:bg-bg-hover" title="${escapeHtml(cell)}">${escapeHtml(displayCell)}</td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';

  const rowCount = lines.length - 1;
  html = `<div class="p-2 bg-bg-element border-b border-border-subtle text-xs text-text-muted font-mono sticky top-0 z-30">${rowCount} rows × ${numCols} columns</div>` + html;

  return html;
}

export function stripLineNumbers(content) {
  if (!content) return content;
  return content.split('\n').map(line => {
    const match = line.match(/^\s*\d+\t(.*)$/);
    return match ? match[1] : line;
  }).join('\n');
}
