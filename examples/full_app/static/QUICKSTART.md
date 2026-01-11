# React Frontend 快速开始指南

## 安装依赖

```bash
cd examples/full_app/static
npm install
```

## 开发模式

### 方式一：自动启动（推荐）

只需启动后端，前端开发服务器会自动启动：

```bash
cd examples/full_app
# 首先安装前端依赖（只需要运行一次）
cd static && npm install && cd ..

# 然后启动后端（会自动启动前端）
uvicorn app:app --reload --port 8080
```

后端会自动检测并启动前端开发服务器（如果 `dist/` 目录不存在且 `node_modules/` 存在）。

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8080`

### 方式二：手动启动（可选）

如果你想手动控制前端服务器：

1. 在一个终端启动后端：
```bash
cd examples/full_app
uvicorn app:app --reload --port 8080
```

2. 在另一个终端启动前端开发服务器：
```bash
cd examples/full_app/static
npm run dev
```

前端开发服务器会在 `http://localhost:3000` 运行，并自动代理到后端的 `http://localhost:8080`。

## 生产构建

1. 构建 React 应用：
```bash
cd examples/full_app/static
npm run build
```

2. 启动后端（会自动提供构建后的文件）：
```bash
cd examples/full_app
uvicorn app:app --port 8080
```

访问 `http://localhost:8080` 即可看到应用。

## 主要功能

- ✅ WebSocket 实时通信
- ✅ 文件上传（拖拽或点击）
- ✅ 文件树导航（支持文件夹展开/折叠）
- ✅ 代码预览（语法高亮）
- ✅ CSV 表格查看器
- ✅ 图片和 PDF 预览
- ✅ HTML/SVG 实时预览
- ✅ 任务进度跟踪
- ✅ 人工审批对话框
- ✅ 响应式设计（Tailwind CSS）

## 技术栈

- React 18
- Vite
- Tailwind CSS
- WebSocket API
- Prism.js (代码高亮)
