# Usage Guide

Installation, configuration, and common workflows for pydantic-deep.

## Installation

### Basic Installation

```bash
pip install pydantic-deep
```

### With Docker Sandbox Support

```bash
pip install pydantic-deep[sandbox]
```

### Using uv

```bash
uv add pydantic-deep
```

### Development Installation

```bash
git clone https://github.com/vstorm-co/pydantic-deepagents.git
cd pydantic-deepagents
make install
```

## Configuration

### Environment Variables

pydantic-deep uses environment variables for API keys (via pydantic-ai):

- `OPENAI_API_KEY`: OpenAI API key (for OpenAI models)
- `ANTHROPIC_API_KEY`: Anthropic API key (for Claude models)
- `GOOGLE_API_KEY`: Google API key (for Gemini models)

Load from `.env` file using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Agent Configuration

#### Basic Agent

```python
from pydantic_deep import create_deep_agent, create_default_deps

agent = create_deep_agent()
deps = create_default_deps()
```

#### Custom Model

```python
agent = create_deep_agent(model="openai:gpt-4.1")
```

#### Custom Instructions

```python
agent = create_deep_agent(
    model="openai:gpt-4.1",
    instructions="You are a specialized coding assistant."
)
```

#### Selective Toolsets

```python
agent = create_deep_agent(
    include_todo=True,
    include_filesystem=True,
    include_subagents=False,  # Disable subagents
    include_skills=False,      # Disable skills
)
```

#### Human-in-the-Loop

```python
agent = create_deep_agent(
    interrupt_on={
        "execute": True,      # Require approval for code execution
        "write_file": False, # No approval needed for file writes
    }
)
```

#### Structured Output

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    summary: str
    issues: list[str]

agent = create_deep_agent(output_type=Analysis)
```

#### History Processing

```python
from pydantic_deep.processors import create_summarization_processor

processor = create_summarization_processor(
    trigger=("tokens", 100000),  # Summarize at 100k tokens
    keep=("messages", 20),       # Keep last 20 messages
)

agent = create_deep_agent(history_processors=[processor])
```

### Backend Configuration

#### StateBackend (In-Memory)

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

#### SessionManager (Multi-User)

```python
from pydantic_ai_backends import SessionManager

session_manager = SessionManager(
    default_runtime=None,  # Uses default python:3.12-slim
    default_idle_timeout=3600,  # 1 hour
)
session_manager.start_cleanup_loop(interval=300)  # Cleanup every 5 min

# Per-session backend
sandbox = await session_manager.get_or_create(session_id)
deps = DeepAgentDeps(backend=sandbox)
```

### SubAgent Configuration

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
        model="openai:gpt-4.1",  # Optional: custom model
    ),
]

agent = create_deep_agent(subagents=subagents)
```

### Skills Configuration

#### From Directory

```python
from pydantic_deep import create_deep_agent
from pydantic_deep.types import SkillDirectory

skill_dirs = [
    SkillDirectory(path="./skills", recursive=True),
    SkillDirectory(path="~/.pydantic-deep/skills", recursive=True),
]

agent = create_deep_agent(skill_directories=skill_dirs)
```

#### Pre-Loaded Skills

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

## Common Workflows

### Basic Agent Run

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

### File Operations

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

### File Uploads

#### Using run_with_files

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

#### Using deps.upload_file

```python
with open("data.csv", "rb") as f:
    deps.upload_file("data.csv", f.read())

result = await agent.run(
    "Analyze the uploaded CSV file",
    deps=deps
)
```

### Streaming Responses

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

### Conversation History

```python
# First message
result1 = await agent.run("Create a Python script", deps=deps)

# Continue conversation
result2 = await agent.run(
    "Now add error handling to that script",
    deps=deps,
    message_history=result1.all_messages(),
)
```

### Structured Output

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

### SubAgent Delegation

```python
result = await agent.run(
    "Research the latest Python async features and summarize them",
    deps=deps
)
# Agent automatically delegates to subagent if configured
```

### Skills Usage

```python
# Agent automatically discovers skills from configured directories
result = await agent.run(
    "Load the data-analysis skill and analyze the uploaded CSV",
    deps=deps
)
```

### Human-in-the-Loop

```python
agent = create_deep_agent(
    interrupt_on={"execute": True}
)

result = await agent.run(
    "Run this potentially dangerous command: rm -rf /",
    deps=deps
)

# If approval needed, result.output will be DeferredToolRequests
if isinstance(result.output, DeferredToolRequests):
    # Show approval UI to user
    approvals = {}
    for call in result.output.approvals:
        if user_approves(call):
            approvals[call.tool_call_id] = ToolApproved()
    
    # Continue with approvals
    from pydantic_ai.tools import DeferredToolResults
    result = await agent.run(
        None,  # No new message
        deps=deps,
        message_history=result.all_messages(),
        deferred_tool_results=DeferredToolResults(approvals=approvals),
    )
```

### Context Summarization

```python
from pydantic_deep.processors import create_summarization_processor

processor = create_summarization_processor(
    trigger=("messages", 50),  # Summarize after 50 messages
    keep=("messages", 10),     # Keep last 10 messages
    max_input_tokens=200000,   # Model's max input tokens
)

agent = create_deep_agent(history_processors=[processor])

# Long conversation automatically summarized
for i in range(100):
    result = await agent.run(f"Message {i}", deps=deps)
```

## CLI / API Examples

### Python API

All functionality is available via Python API. There is no standalone CLI tool.

### Example Application

The full example application provides a web interface:

```bash
cd examples/full_app
uvicorn app:app --reload --port 8080
```

Then open http://localhost:8080 in your browser.

## Example Scenarios

### Scenario 1: Code Generation and Execution

```python
agent = create_deep_agent()
deps = DeepAgentDeps(backend=DockerSandbox())

# Generate code
result = await agent.run(
    "Write a Python function that calculates fibonacci numbers",
    deps=deps
)

# Execute code
result = await agent.run(
    "Create a script that uses the fibonacci function and prints first 10 numbers",
    deps=deps
)

result = await agent.run(
    "Execute the script",
    deps=deps
)
```

### Scenario 2: Data Analysis

```python
agent = create_deep_agent()
deps = DeepAgentDeps(backend=StateBackend())

# Upload data
with open("sales.csv", "rb") as f:
    deps.upload_file("sales.csv", f.read())

# Analyze
result = await agent.run(
    "Analyze the sales.csv file. Find the top 5 products by revenue.",
    deps=deps
)
```

### Scenario 3: Multi-Step Task with Planning

```python
agent = create_deep_agent(include_todo=True)
deps = DeepAgentDeps(backend=FilesystemBackend("/tmp/workspace"))

# Agent automatically creates TODO list
result = await agent.run(
    "Create a web scraper that fetches data from example.com and saves to JSON",
    deps=deps
)

# Check todos
todos = deps.todos
for todo in todos:
    print(f"{todo.status}: {todo.content}")
```

### Scenario 4: Custom Tools Integration

```python
from pydantic_ai import Tool
from pydantic_deep import create_deep_agent

@Tool
async def get_weather(ctx, location: str) -> str:
    """Get weather for a location."""
    # Implementation here
    return f"Weather in {location}: Sunny, 72°F"

agent = create_deep_agent(
    tools=[get_weather],
)

result = await agent.run(
    "What's the weather in San Francisco?",
    deps=deps
)
```

### Scenario 5: Web Application Integration

See `examples/full_app/app.py` for a complete FastAPI application with:
- WebSocket streaming
- File uploads
- Multi-user sessions
- Human-in-the-loop approvals
- Real-time TODO updates
