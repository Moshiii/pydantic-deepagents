import { marked } from 'marked';

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

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持 GitHub 风格的换行
  gfm: true, // 启用 GitHub Flavored Markdown
  headerIds: false, // 禁用标题 ID
  mangle: false, // 不混淆邮箱地址
});

// 自定义渲染器以添加 Tailwind CSS 类
const renderer = new marked.Renderer();

// 标题
renderer.heading = (text, level) => {
  const sizes = {
    1: 'text-3xl font-bold mt-6 mb-4',
    2: 'text-2xl font-semibold mt-6 mb-3',
    3: 'text-xl font-semibold mt-6 mb-3',
    4: 'text-lg font-semibold mt-4 mb-2',
    5: 'text-base font-semibold mt-4 mb-2',
    6: 'text-sm font-semibold mt-4 mb-2',
  };
  return `<h${level} class="${sizes[level] || 'text-base'} text-text-main">${text}</h${level}>`;
};

// 段落
renderer.paragraph = (text) => {
  return `<p class="my-2 text-text-main">${text}</p>`;
};

// 代码块
renderer.code = (code, language) => {
  const escapedCode = escapeHtml(code);
  const lang = language || 'text';
  return `<pre class="bg-gray-900 border border-border-subtle p-4 rounded-md overflow-x-auto my-4"><code class="language-${lang} font-mono text-sm">${escapedCode}</code></pre>`;
};

// 行内代码
renderer.codespan = (code) => {
  return `<code class="bg-white/10 px-1 py-0.5 rounded text-accent-primary font-mono text-sm">${escapeHtml(code)}</code>`;
};

// 链接
renderer.link = (href, title, text) => {
  return `<a href="${escapeHtml(href)}" class="text-accent-primary underline hover:text-white" target="_blank" rel="noopener noreferrer"${title ? ` title="${escapeHtml(title)}"` : ''}>${text}</a>`;
};

// 列表
renderer.list = (body, ordered) => {
  const tag = ordered ? 'ol' : 'ul';
  const className = ordered 
    ? 'my-3 space-y-1 list-decimal ml-6' 
    : 'my-3 space-y-1 list-disc ml-6';
  return `<${tag} class="${className}">${body}</${tag}>`;
};

renderer.listitem = (text) => {
  return `<li class="my-1">${text}</li>`;
};

// 表格
renderer.table = (header, body) => {
  return `<div class="overflow-x-auto my-4"><table class="w-full border-collapse border border-border-subtle rounded-md overflow-hidden">${header}${body}</table></div>`;
};

renderer.tablerow = (content) => {
  // 检查是否是表头行（通过检查是否包含 th 标签）
  const isHeader = content.includes('<th');
  const rowClass = isHeader 
    ? 'bg-bg-element' 
    : 'bg-bg-panel hover:bg-bg-hover';
  return `<tr class="${rowClass}">${content}</tr>`;
};

renderer.tablecell = (content, flags) => {
  const tag = flags.header ? 'th' : 'td';
  const align = flags.align || 'left';
  const headerClass = flags.header 
    ? 'bg-bg-element font-semibold text-accent-primary border-b border-border-subtle' 
    : 'text-text-main border-b border-border-subtle';
  const cellClass = flags.header 
    ? `px-4 py-2 ${headerClass}`
    : `px-4 py-2 ${headerClass}`;
  
  return `<${tag} class="${cellClass}" style="text-align: ${align}">${content}</${tag}>`;
};

// 引用块
renderer.blockquote = (quote) => {
  return `<blockquote class="border-l-4 border-accent-primary pl-4 my-3 italic text-text-muted">${quote}</blockquote>`;
};

// 水平线
renderer.hr = () => {
  return '<hr class="my-4 border-border-subtle">';
};

// 粗体
renderer.strong = (text) => {
  return `<strong class="font-semibold text-white">${text}</strong>`;
};

// 斜体
renderer.em = (text) => {
  return `<em>${text}</em>`;
};

marked.use({ renderer });

export function formatMessage(content) {
  if (!content) return '';
  
  try {
    let processedContent = content.trim();
    
    // 检查内容是否被包裹在代码块中（``` 标记）
    // 如果整个内容是一个代码块，且看起来像 Markdown（包含表格、标题等），则提取出来解析
    const codeBlockRegex = /^```[\w]*\n?([\s\S]*?)```$/m;
    const codeBlockMatch = processedContent.match(codeBlockRegex);
    
    if (codeBlockMatch) {
      const codeContent = codeBlockMatch[1].trim();
      // 检查是否包含 Markdown 特征（表格、标题、列表等）
      const hasMarkdownFeatures = 
        codeContent.includes('|') || // 表格
        codeContent.match(/^#+\s/m) || // 标题
        codeContent.match(/^[\*\-\+]\s/m) || // 无序列表
        codeContent.match(/^\d+\.\s/m); // 有序列表
      
      if (hasMarkdownFeatures) {
        // 如果包含 Markdown 特征，当作 Markdown 解析而不是代码块
        processedContent = codeContent;
      }
    }
    
    // 使用 marked 解析 Markdown
    let html = marked.parse(processedContent, {
      breaks: true,
      gfm: true,
      headerIds: false,
      mangle: false,
    });
    
    // 文件路径链接（在最后处理）
    html = linkifyFilePaths(html);
    
    return html;
  } catch (error) {
    console.error('Error parsing markdown:', error);
    // 如果解析失败，返回转义后的原始内容
    return `<p class="my-2">${escapeHtml(content)}</p>`;
  }
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
