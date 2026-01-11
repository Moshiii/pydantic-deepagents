# 项目启动指南

## 快速启动

### 1. 设置 API 密钥

项目使用 OpenAI 模型（`gpt-4.1`），需要设置 `OPENAI_API_KEY`：

```bash
export OPENAI_API_KEY=your-api-key-here
```

或者使用 Anthropic（Claude）模型，需要修改 `examples/full_app/app.py` 中的模型配置：

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

### 2. 启动示例应用

进入示例应用目录并启动：

```bash
cd examples/full_app
uv run uvicorn app:app --reload --port 8080
```

或者使用 make 命令（如果已配置）：

```bash
cd examples/full_app
uv run python -m uvicorn app:app --reload --port 8080
```

### 3. 访问应用

打开浏览器访问：http://localhost:8080

## 功能说明

示例应用包含以下功能：

- ✅ **文件上传**：支持 CSV、PDF、TXT、JSON、Python 文件
- ✅ **代码执行**：在 Docker 容器中执行 Python 代码（需要 Docker）
- ✅ **GitHub 工具**：模拟的 GitHub API 工具（仓库、问题、PR 等）
- ✅ **技能系统**：数据分析技能（CSV 分析）
- ✅ **子代理**：笑话生成器
- ✅ **WebSocket 流式传输**：实时响应流
- ✅ **多用户会话**：每个会话独立的 Docker 容器
- ✅ **记忆系统**：长期记忆存储（Markdown 格式）

## Docker 支持（可选）

如果已安装 Docker，应用会自动使用 Docker 容器执行代码。如果没有 Docker，会回退到文件系统后端（代码执行功能受限）。

确保 Docker 正在运行：

```bash
docker ps
```

## 开发模式

### 运行测试

```bash
make test
```

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

### 类型检查

```bash
make typecheck
```

## 故障排除

### API 密钥未设置

确保环境变量已正确设置：

```bash
echo $OPENAI_API_KEY
```

### Docker 未运行

如果看到 "Docker not available" 警告，应用仍可运行，但代码执行功能会受限。

### 端口被占用

如果 8080 端口被占用，可以更改端口：

```bash
uv run uvicorn app:app --reload --port 8081
```

## 更多信息

- [完整文档](https://vstorm-co.github.io/pydantic-deepagents/)
- [示例应用 README](examples/full_app/README.md)
- [安装指南](docs/installation.md)
