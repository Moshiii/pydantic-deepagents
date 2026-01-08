# 使用指南

pydantic-deep 的安装、配置和常见工作流。

## 安装

### 基本安装

```bash
pip install pydantic-deep
```

### 带 Docker 沙箱支持

```bash
pip install pydantic-deep[sandbox]
```

### 使用 uv

```bash
uv add pydantic-deep
```

### 开发安装

```bash
git clone https://github.com/vstorm-co/pydantic-deepagents.git
cd pydantic-deepagents
make install
```

## 配置

### 环境变量

pydantic-deep 使用环境变量来存储 API 密钥（通过 pydantic-ai）：

- `OPENAI_API_KEY`: OpenAI API 密钥（用于 OpenAI 模型）
- `ANTHROPIC_API_KEY`: Anthropic API 密钥（用于 Claude 模型）
- `GOOGLE_API_KEY`: Google API 密钥（用于 Gemini 模型）

使用 `python-dotenv` 从 `.env` 文件加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 代理配置

#### 基本代理

```python
from pydantic_deep import create_deep_agent, create_default_deps

agent = create_deep_agent()
deps = create_default_deps()
```

#### 自定义模型

```python
agent = create_deep_agent(model="openai:gpt-4.1")
```

#### 自定义指令

```python
agent = create_deep_agent(
    model="openai:gpt-4.1",
    instructions="You are a specialized coding assistant."
)
```

#### 选择性工具集

```python
agent = create_deep_agent(
    include_todo=True,
    include_filesystem=True,
    include_subagents=False,  # 禁用子代理
    include_skills=False,      # 禁用技能
)
```

#### 人在回路

```python
agent = create_deep_agent(
    interrupt_on={
        "execute": True,      # 代码执行需要审批
        "write_file": False, # 文件写入不需要审批
    }
)
```

#### 结构化输出

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    summary: str
    issues: list[str]

agent = create_deep_agent(output_type=Analysis)
```

#### 历史处理

```python
from pydantic_deep.processors import create_summarization_processor

processor = create_summarization_processor(
    trigger=("tokens", 100000),  # 在 100k 令牌时摘要
    keep=("messages", 20),       # 保留最后 20 条消息
)

agent = create_deep_agent(history_processors=[processor])
```

### 后端配置

#### StateBackend（内存）

```python
from pydantic_ai_backends import StateBackend
from pydantic_deep import DeepAgentDeps

deps = DeepAgentDeps(backend=StateBackend())
```

#### FilesystemBackend

```python
from pydantic_ai_backends import FilesystemBackend
from pathlib import Path

backend = FilesystemBackend(str(Path("/tmp/workspace")))
deps = DeepAgentDeps(backend=backend)
```

#### DockerSandbox

```python
from pydantic_ai_backends import DockerSandbox, get_runtime

runtime = get_runtime("python:3.12-slim")
backend = DockerSandbox(default_runtime=runtime)
deps = DeepAgentDeps(backend=backend)
```

#### SessionManager（多用户）

```python
from pydantic_ai_backends import SessionManager

session_manager = SessionManager(
    default_runtime=None,  # 使用默认 python:3.12-slim
    default_idle_timeout=3600,  # 1 小时
)
session_manager.start_cleanup_loop(interval=300)  # 每 5 分钟清理一次

# 每会话后端
sandbox = await session_manager.get_or_create(session_id)
deps = DeepAgentDeps(backend=sandbox)
```

### 子代理配置

```python
from pydantic_deep import create_deep_agent
from pydantic_deep.types import SubAgentConfig

subagents = [
    SubAgentConfig(
        name="researcher",
        description="Research assistant for finding information",
        instructions="You are a research assistant. Find and summarize information.",
    ),
    SubAgentConfig(
        name="coder",
        description="Code generation and review",
        instructions="You are a coding assistant. Write clean, tested code.",
        model="openai:gpt-4.1",  # 可选：自定义模型
    ),
]

agent = create_deep_agent(subagents=subagents)
```

### 技能配置

#### 从目录

```python
from pydantic_deep import create_deep_agent
from pydantic_deep.types import SkillDirectory

skill_dirs = [
    SkillDirectory(path="./skills", recursive=True),
    SkillDirectory(path="~/.pydantic-deep/skills", recursive=True),
]

agent = create_deep_agent(skill_directories=skill_dirs)
```

#### 预加载技能

```python
from pydantic_deep import create_deep_agent
from pydantic_deep.types import Skill

skills = [
    Skill(
        name="data-analysis",
        description="CSV data analysis",
        path="./skills/data-analysis",
        tags=["data", "csv"],
        version="1.0.0",
        author="",
        frontmatter_loaded=True,
    ),
]

agent = create_deep_agent(skills=skills)
```

## 常见工作流

### 基本代理运行

```python
import asyncio
from pydantic_deep import create_deep_agent, create_default_deps

async def main():
    agent = create_deep_agent()
    deps = create_default_deps()
    
    result = await agent.run("Create a hello world script", deps=deps)
    print(result.output)

asyncio.run(main())
```

### 文件操作

```python
result = await agent.run(
    "Create a file called test.py with print('hello')",
    deps=deps
)

result = await agent.run(
    "Read the file test.py",
    deps=deps
)
```

### 文件上传

#### 使用 run_with_files

```python
from pydantic_deep import run_with_files

with open("data.csv", "rb") as f:
    result = await run_with_files(
        agent,
        "Analyze this CSV file and find the top 5 rows",
        deps,
        files=[("data.csv", f.read())],
    )
```

#### 使用 deps.upload_file

```python
with open("data.csv", "rb") as f:
    deps.upload_file("data.csv", f.read())

result = await agent.run(
    "Analyze the uploaded CSV file",
    deps=deps
)
```

### 流式响应

```python
async with agent.iter("Create a Python script", deps=deps) as run:
    async for node in run:
        if agent.is_model_request_node(node):
            async with node.stream(run.ctx) as stream:
                async for event in stream:
                    if isinstance(event, TextPartDelta):
                        print(event.content_delta, end="", flush=True)
    
    result = run.result
    print(f"\n\nFinal result: {result.output}")
```

### 对话历史

```python
# 第一条消息
result1 = await agent.run("Create a Python script", deps=deps)

# 继续对话
result2 = await agent.run(
    "Now add error handling to that script",
    deps=deps,
    message_history=result1.all_messages(),
)
```

### 结构化输出

```python
from pydantic import BaseModel

class CodeReview(BaseModel):
    issues: list[str]
    suggestions: list[str]
    score: int

agent = create_deep_agent(output_type=CodeReview)

result = await agent.run(
    "Review this code: def add(a, b): return a + b",
    deps=deps
)

print(f"Found {len(result.output.issues)} issues")
print(f"Score: {result.output.score}/10")
```

### 子代理委托

```python
result = await agent.run(
    "Research the latest Python async features and summarize them",
    deps=deps
)
# 如果配置了子代理，代理会自动委托
```

### 技能使用

```python
# 代理自动从配置的目录中发现技能
result = await agent.run(
    "Load the data-analysis skill and analyze the uploaded CSV",
    deps=deps
)
```

### 人在回路

```python
agent = create_deep_agent(
    interrupt_on={"execute": True}
)

result = await agent.run(
    "Run this potentially dangerous command: rm -rf /",
    deps=deps
)

# 如果需要审批，result.output 将是 DeferredToolRequests
if isinstance(result.output, DeferredToolRequests):
    # 向用户显示审批 UI
    approvals = {}
    for call in result.output.approvals:
        if user_approves(call):
            approvals[call.tool_call_id] = ToolApproved()
    
    # 继续审批
    from pydantic_ai.tools import DeferredToolResults
    result = await agent.run(
        None,  # 无新消息
        deps=deps,
        message_history=result.all_messages(),
        deferred_tool_results=DeferredToolResults(approvals=approvals),
    )
```

### 上下文摘要

```python
from pydantic_deep.processors import create_summarization_processor

processor = create_summarization_processor(
    trigger=("messages", 50),  # 50 条消息后摘要
    keep=("messages", 10),     # 保留最后 10 条消息
    max_input_tokens=200000,   # 模型的最大输入令牌数
)

agent = create_deep_agent(history_processors=[processor])

# 长对话自动摘要
for i in range(100):
    result = await agent.run(f"Message {i}", deps=deps)
```

## CLI / API 示例

### Python API

所有功能都通过 Python API 提供。没有独立的 CLI 工具。

### 示例应用

完整示例应用提供 Web 界面：

```bash
cd examples/full_app
uvicorn app:app --reload --port 8080
```

然后在浏览器中打开 http://localhost:8080。

## 示例场景

### 场景 1：代码生成和执行

```python
agent = create_deep_agent()
deps = DeepAgentDeps(backend=DockerSandbox())

# 生成代码
result = await agent.run(
    "Write a Python function that calculates fibonacci numbers",
    deps=deps
)

# 执行代码
result = await agent.run(
    "Create a script that uses the fibonacci function and prints first 10 numbers",
    deps=deps
)

result = await agent.run(
    "Execute the script",
    deps=deps
)
```

### 场景 2：数据分析

```python
agent = create_deep_agent()
deps = DeepAgentDeps(backend=StateBackend())

# 上传数据
with open("sales.csv", "rb") as f:
    deps.upload_file("sales.csv", f.read())

# 分析
result = await agent.run(
    "Analyze the sales.csv file. Find the top 5 products by revenue.",
    deps=deps
)
```

### 场景 3：带规划的多步骤任务

```python
agent = create_deep_agent(include_todo=True)
deps = DeepAgentDeps(backend=FilesystemBackend("/tmp/workspace"))

# 代理自动创建 TODO 列表
result = await agent.run(
    "Create a web scraper that fetches data from example.com and saves to JSON",
    deps=deps
)

# 检查 todos
todos = deps.todos
for todo in todos:
    print(f"{todo.status}: {todo.content}")
```

### 场景 4：自定义工具集成

```python
from pydantic_ai import Tool
from pydantic_deep import create_deep_agent

@Tool
async def get_weather(ctx, location: str) -> str:
    """Get weather for a location."""
    # 实现代码
    return f"Weather in {location}: Sunny, 72°F"

agent = create_deep_agent(
    tools=[get_weather],
)

result = await agent.run(
    "What's the weather in San Francisco?",
    deps=deps
)
```

### 场景 5：Web 应用集成

查看 `examples/full_app/app.py` 了解完整的 FastAPI 应用，包括：
- WebSocket 流式传输
- 文件上传
- 多用户会话
- 人在回路审批
- 实时 TODO 更新
