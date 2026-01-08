# Architecture

System components, module boundaries, and architectural patterns in pydantic-deep.

## System Components

### Core Agent Factory

**Location**: `pydantic_deep/agent.py`

**Responsibility**: Creates configured Agent instances with optional toolsets, subagents, skills, and processors.

**Dependencies**:
- `pydantic_ai.Agent`: Base agent class
- `pydantic_ai_todo`: Todo toolset
- `pydantic_deep.toolsets.*`: Internal toolsets
- `pydantic_deep.deps.DeepAgentDeps`: Dependency type

**Exports**:
- `create_deep_agent()`: Main factory function
- `create_default_deps()`: Dependency factory
- `run_with_files()`: File upload helper

### Dependency Injection Container

**Location**: `pydantic_deep/deps.py`

**Responsibility**: Holds runtime state and resources (backend, todos, uploads, subagents).

**Dependencies**:
- `pydantic_ai_backends.BackendProtocol`: Backend interface
- `pydantic_ai_todo.Todo`: Todo type
- `pydantic_deep.types.UploadedFile`: Upload metadata type

**Exports**:
- `DeepAgentDeps`: Main dataclass

### Filesystem Toolset

**Location**: `pydantic_deep/toolsets/filesystem.py`

**Responsibility**: Provides file operations (read, write, edit, search, execute).

**Dependencies**:
- `pydantic_ai.toolsets.FunctionToolset`: Base toolset class
- `pydantic_ai_backends.BackendProtocol`: Backend interface
- `pydantic_ai_backends.SandboxProtocol`: Execution interface
- `pydantic_deep.deps.DeepAgentDeps`: Dependency type

**Exports**:
- `create_filesystem_toolset()`: Factory function
- `get_filesystem_system_prompt()`: Dynamic prompt generator
- `FilesystemToolset`: Alias for factory

### SubAgent Toolset

**Location**: `pydantic_deep/toolsets/subagents.py`

**Responsibility**: Task delegation to specialized subagents.

**Dependencies**:
- `pydantic_ai.Agent`: Subagent instances
- `pydantic_ai.toolsets.FunctionToolset`: Base toolset class
- `pydantic_deep.deps.DeepAgentDeps`: Dependency type
- `pydantic_deep.types.SubAgentConfig`: Configuration type

**Exports**:
- `create_subagent_toolset()`: Factory function
- `get_subagent_system_prompt()`: Dynamic prompt generator
- `SubAgentToolset`: Alias for factory

### Skills Toolset

**Location**: `pydantic_deep/toolsets/skills.py`

**Responsibility**: Load and use modular skill packages from markdown files.

**Dependencies**:
- `pydantic_ai.toolsets.FunctionToolset`: Base toolset class
- `pydantic_deep.deps.DeepAgentDeps`: Dependency type
- `pydantic_deep.types.Skill`: Skill type definition

**Exports**:
- `create_skills_toolset()`: Factory function
- `discover_skills()`: Skill discovery function
- `load_skill_instructions()`: Instruction loader
- `get_skills_system_prompt()`: Dynamic prompt generator
- `parse_skill_md()`: Markdown parser

### Summarization Processor

**Location**: `pydantic_deep/processors/summarization.py`

**Responsibility**: Automatic conversation summarization for token management.

**Dependencies**:
- `pydantic_ai.Agent`: Summarization agent
- `pydantic_ai.messages.ModelMessage`: Message types
- `pydantic_ai._agent_graph.HistoryProcessor`: Processor interface

**Exports**:
- `SummarizationProcessor`: Main processor class
- `create_summarization_processor()`: Factory function

### Type Definitions

**Location**: `pydantic_deep/types.py`

**Responsibility**: Type definitions for configuration and data structures.

**Dependencies**:
- `pydantic_ai.output.OutputSpec`: Output specification
- `pydantic_ai_backends.*`: Backend types
- `pydantic_ai_todo.Todo`: Todo type

**Exports**:
- `SubAgentConfig`: Subagent configuration
- `CompiledSubAgent`: Pre-compiled subagent
- `Skill`: Skill definition
- `SkillDirectory`: Skill directory configuration
- `SkillFrontmatter`: Skill metadata
- `UploadedFile`: Upload metadata
- `ResponseFormat`: Output format type alias

## Module Boundaries

### Internal vs External

**Internal Modules** (pydantic-deep package):
- `pydantic_deep.agent`: Agent factory
- `pydantic_deep.deps`: Dependency injection
- `pydantic_deep.toolsets.*`: Toolset implementations
- `pydantic_deep.processors.*`: History processors
- `pydantic_deep.types`: Type definitions

**External Dependencies**:
- `pydantic-ai`: Core agent framework
- `pydantic-ai-backend`: Backend implementations
- `pydantic-ai-todo`: Todo toolset
- `pydantic`: Data validation
- `fastapi`, `uvicorn`: Example application (optional)

### Toolset Isolation

Each toolset is self-contained:
- Toolsets do not depend on each other
- Toolsets communicate only through `DeepAgentDeps`
- Toolsets can be enabled/disabled independently
- Toolsets generate their own system prompt sections

### Backend Abstraction

Backends are abstracted via protocols:
- `BackendProtocol`: File operations interface
- `SandboxProtocol`: Code execution interface (extends BackendProtocol)
- Backend implementations are in external package (`pydantic-ai-backend`)
- Agents and toolsets depend only on protocols, not implementations

### Dependency Direction Rules

1. **Agent Factory → Toolsets**: Factory creates and configures toolsets
2. **Toolsets → Dependencies**: Toolsets read from `DeepAgentDeps`
3. **Dependencies → Backends**: Dependencies hold backend instances
4. **Backends → External**: Backends are external implementations
5. **Processors → Agent**: Processors wrap agent for summarization
6. **Types → All**: Types are shared across modules

**No circular dependencies**: Dependency graph is acyclic.

## Data Flow

### Agent Execution Flow

```
User Query
    ↓
Agent.run(query, deps)
    ↓
History Processor (if configured)
    ↓
Dynamic System Prompt Generation
    ↓
Model Request (with tools)
    ↓
Tool Execution (if needed)
    ↓
    ├─→ Filesystem Toolset → Backend
    ├─→ SubAgent Toolset → Subagent Agent
    ├─→ Skills Toolset → Skill Files
    └─→ Todo Toolset → DeepAgentDeps.todos
    ↓
Model Response
    ↓
Output Validation (if structured)
    ↓
Result
```

### File Upload Flow

```
User uploads file
    ↓
deps.upload_file(name, content)
    ↓
Backend.write(path, content)
    ↓
Metadata extraction (encoding, MIME type, line count)
    ↓
Store in deps.uploads
    ↓
System prompt includes upload summary
    ↓
Agent can access file via tools
```

### SubAgent Delegation Flow

```
Main agent calls task(description, subagent_type)
    ↓
Find or create subagent
    ↓
Clone deps (isolated context)
    ↓
Subagent.run(description, deps=cloned_deps)
    ↓
Subagent execution (with own toolsets)
    ↓
Return summary to main agent
    ↓
Main agent continues
```

### Summarization Flow

```
Message history accumulates
    ↓
Processor checks trigger conditions
    ↓
If triggered:
    ├─→ Determine cutoff point (safe for tool pairs)
    ├─→ Extract messages to summarize
    ├─→ Generate summary via summarization agent
    └─→ Replace old messages with summary
    ↓
Continue with summarized history
```

## External Integrations

### pydantic-ai Integration

- **Agent Class**: Base agent implementation
- **Tool System**: Tool registration and execution
- **Message Types**: ModelMessage, ModelRequest, ModelResponse
- **History Processors**: Processor interface
- **Output Specs**: Structured output support

### pydantic-ai-backend Integration

- **BackendProtocol**: File operations interface
- **SandboxProtocol**: Code execution interface
- **Backend Implementations**: StateBackend, FilesystemBackend, DockerSandbox
- **SessionManager**: Multi-user container management

### pydantic-ai-todo Integration

- **Todo Toolset**: Task planning tools
- **Todo Type**: Todo data structure
- **System Prompt**: Dynamic TODO prompt generation

## Runtime Topology

### Single Agent Instance

```
Agent (stateless)
    ↓
DeepAgentDeps (per-run state)
    ├─→ Backend (file storage)
    ├─→ todos (task list)
    ├─→ uploads (file metadata)
    └─→ subagents (cached instances)
```

### Multi-User Application

```
FastAPI Application
    ├─→ Agent (shared, stateless)
    └─→ SessionManager
        ├─→ Session 1 → DockerSandbox → DeepAgentDeps
        ├─→ Session 2 → DockerSandbox → DeepAgentDeps
        └─→ Session N → DockerSandbox → DeepAgentDeps
```

### Toolset Registration

```
Agent
    ├─→ TodoToolset (from pydantic-ai-todo)
    ├─→ FilesystemToolset (internal)
    ├─→ SubAgentToolset (internal)
    ├─→ SkillsToolset (internal)
    └─→ Custom Toolsets (user-provided)
```

## Design Patterns

### Factory Pattern

- `create_deep_agent()`: Factory for agent creation
- `create_filesystem_toolset()`: Factory for toolset creation
- `create_summarization_processor()`: Factory for processor creation

### Dependency Injection

- `DeepAgentDeps`: Container for runtime dependencies
- Passed to agent.run() for each execution
- Toolsets access dependencies via RunContext

### Strategy Pattern

- Backend abstraction: Different backends implement same protocol
- Toolset selection: Enable/disable toolsets via flags
- History processing: Pluggable processors

### Decorator Pattern

- `@agent.instructions`: Dynamic system prompt generation
- `@toolset.tool`: Tool registration

### Singleton Pattern

- Agent instances are typically shared (stateless)
- Subagents are cached in `deps.subagents`

## Extension Points

### Custom Toolsets

Create custom toolsets by implementing `AbstractToolset[DeepAgentDeps]`:

```python
from pydantic_ai.toolsets import FunctionToolset
from pydantic_deep.deps import DeepAgentDeps

toolset = FunctionToolset[DeepAgentDeps](id="custom")
@toolset.tool
async def my_tool(ctx, arg: str) -> str:
    # Access deps via ctx.deps
    return "result"

agent = create_deep_agent(toolsets=[toolset])
```

### Custom Backends

Implement `BackendProtocol` or `SandboxProtocol`:

```python
from pydantic_ai_backends import BackendProtocol

class MyBackend(BackendProtocol):
    # Implement required methods
    pass

deps = DeepAgentDeps(backend=MyBackend())
```

### Custom Processors

Implement `HistoryProcessor[DeepAgentDeps]`:

```python
from pydantic_ai._agent_graph import HistoryProcessor
from pydantic_ai.messages import ModelMessage

class MyProcessor(HistoryProcessor[DeepAgentDeps]):
    async def __call__(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        # Process messages
        return messages

agent = create_deep_agent(history_processors=[MyProcessor()])
```
