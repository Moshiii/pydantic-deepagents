# Features

Detailed descriptions of all features in pydantic-deep.

## Agent Creation

### Deep Agent Factory

**Description**: Factory function that creates fully-configured AI agents with optional toolsets, subagents, skills, and history processors.

**User-Visible Behavior**:
- Creates an `Agent[DeepAgentDeps, OutputT]` instance
- Automatically includes selected toolsets (todo, filesystem, subagents, skills)
- Configures dynamic system prompts based on current state
- Supports structured output via Pydantic models
- Enables human-in-the-loop approval workflows

**Internal Modules Involved**:
- `pydantic_deep.agent.create_deep_agent()`: Main factory function
- `pydantic_deep.toolsets.*`: Toolset creation functions
- `pydantic_ai.Agent`: Base agent class from pydantic-ai
- `pydantic_ai_todo.create_todo_toolset()`: External todo toolset

**Error Handling Behavior**:
- Raises `ValueError` if fraction-based triggers are used without `max_input_tokens`
- Validates context size parameters (fractions must be 0-1, counts must be > 0)
- Type errors if invalid model or output_type provided

**Feature Boundaries**:
- Does NOT implement backend logic (delegated to pydantic-ai-backend)
- Does NOT implement LLM model logic (delegated to pydantic-ai)
- Does NOT persist agent state (stateless factory)

**Confidence Level**: High
**Basis**: Tests + implementation

## Dependency Injection

### DeepAgentDeps Container

**Description**: Dependency injection container that holds all runtime state and resources needed by agents and tools.

**User-Visible Behavior**:
- Provides backend for file operations
- Tracks TODO list state
- Manages uploaded file metadata
- Stores pre-compiled subagent instances
- Generates system prompt summaries for current state

**Internal Modules Involved**:
- `pydantic_deep.deps.DeepAgentDeps`: Main dataclass
- `pydantic_ai_backends.BackendProtocol`: Backend interface
- `pydantic_ai_todo.Todo`: Todo item type

**Error Handling Behavior**:
- Raises `RuntimeError` if file upload fails
- Handles encoding detection failures gracefully (falls back to binary)
- Validates file paths during upload

**Feature Boundaries**:
- Does NOT implement backend operations (delegated to backend implementations)
- Does NOT persist state across process restarts (in-memory only)
- Does NOT manage agent lifecycle (stateless container)

**Confidence Level**: High
**Basis**: Tests + implementation

### File Upload Tracking

**Description**: Upload files to backend storage and track metadata (size, encoding, line count, MIME type).

**User-Visible Behavior**:
- Uploads file content to backend at specified path
- Detects file encoding using chardet
- Calculates line count for text files
- Infers MIME type from filename
- Stores metadata in `deps.uploads` dict
- Files accessible via `/uploads/{filename}` path

**Internal Modules Involved**:
- `pydantic_deep.deps.DeepAgentDeps.upload_file()`: Upload method
- `pydantic_ai_backends.BackendProtocol.write()`: Backend write operation
- `chardet.detect()`: Encoding detection
- `mimetypes.guess_type()`: MIME type inference

**Error Handling Behavior**:
- Raises `RuntimeError` if backend write fails
- Handles UnicodeDecodeError gracefully (marks as binary)
- Returns path on success, raises exception on failure

**Feature Boundaries**:
- Does NOT validate file content (accepts any bytes)
- Does NOT limit file size (backend-dependent)
- Does NOT scan for viruses or malware
- Does NOT support streaming uploads (loads entire file into memory)

**Confidence Level**: High
**Basis**: Tests + implementation

## Toolsets

### Todo Toolset

**Description**: Task planning and tracking tools that allow agents to create, read, and update TODO lists.

**User-Visible Behavior**:
- `write_todos(todos)`: Create or update TODO list
- `read_todos()`: Get current TODO list
- Todos have status: "pending", "in_progress", "completed"
- System prompt automatically includes current todos

**Internal Modules Involved**:
- External package: `pydantic-ai-todo`
- `pydantic_deep.agent.create_deep_agent()`: Integration point
- `pydantic_deep.deps.DeepAgentDeps.todos`: State storage

**Error Handling Behavior**:
- Validates todo status values
- Handles invalid todo structures gracefully

**Feature Boundaries**:
- Does NOT persist todos across agent restarts (in-memory only)
- Does NOT provide scheduling or reminders
- Does NOT support dependencies between todos
- Does NOT provide time tracking

**Confidence Level**: High
**Basis**: External package tests + integration tests

### Filesystem Toolset

**Description**: Comprehensive file operations including read, write, edit, search, and code execution.

**User-Visible Behavior**:
- `ls(path)`: List directory contents
- `read_file(path, offset, limit)`: Read file with line numbers
- `write_file(path, content)`: Create or overwrite file
- `edit_file(path, old_string, new_string, replace_all)`: String replacement
- `glob(pattern, path)`: Find files matching pattern
- `grep(pattern, path, glob_pattern, output_mode)`: Search for patterns
- `execute(command, timeout)`: Execute shell commands (requires SandboxProtocol)

**Internal Modules Involved**:
- `pydantic_deep.toolsets.filesystem.create_filesystem_toolset()`: Factory
- `pydantic_ai_backends.BackendProtocol`: Backend interface
- `pydantic_ai_backends.SandboxProtocol`: Execution interface

**Error Handling Behavior**:
- Returns error strings for failed operations
- Validates paths (no '..' or '~' allowed)
- Handles file not found gracefully
- Reports exit codes for failed commands
- Truncates output if too long

**Feature Boundaries**:
- Does NOT support file permissions or ownership changes
- Does NOT support symbolic links or hard links
- Does NOT support file watching or events
- Does NOT support concurrent file access locking
- Execute tool only available with SandboxProtocol backends

**Confidence Level**: High
**Basis**: Tests + implementation

### SubAgent Toolset

**Description**: Task delegation system that allows agents to spawn specialized subagents for autonomous work.

**User-Visible Behavior**:
- `task(description, subagent_type)`: Launch subagent with task description
- Subagents have isolated context (no conversation history)
- Subagents share filesystem backend
- Subagents return summary of their work
- Supports custom subagent configurations
- Includes optional general-purpose subagent

**Internal Modules Involved**:
- `pydantic_deep.toolsets.subagents.create_subagent_toolset()`: Factory
- `pydantic_deep.deps.DeepAgentDeps.clone_for_subagent()`: Context isolation
- `pydantic_ai.Agent`: Subagent instances
- `pydantic_deep.types.SubAgentConfig`: Configuration type

**Error Handling Behavior**:
- Returns error message if subagent type not found
- Catches and reports subagent execution exceptions
- Handles missing subagent configs gracefully

**Feature Boundaries**:
- Does NOT support nested subagent delegation (subagents cannot spawn subagents)
- Does NOT support subagent-to-subagent communication
- Does NOT persist subagent state across calls
- Does NOT support subagent cancellation or timeout
- Does NOT support parallel subagent execution

**Confidence Level**: High
**Basis**: Tests + implementation

### Skills Toolset

**Description**: Modular skill system that loads instructions and resources from markdown files.

**User-Visible Behavior**:
- `list_skills()`: Show available skills with metadata
- `load_skill(skill_name)`: Load full skill instructions
- `read_skill_resource(skill_name, resource_name)`: Read skill resource files
- Skills discovered from directories containing SKILL.md files
- Progressive disclosure: frontmatter loaded first, full instructions on demand

**Internal Modules Involved**:
- `pydantic_deep.toolsets.skills.create_skills_toolset()`: Factory
- `pydantic_deep.toolsets.skills.discover_skills()`: Discovery function
- `pydantic_deep.toolsets.skills.parse_skill_md()`: Markdown parser
- `pydantic_deep.types.Skill`: Skill type definition

**Error Handling Behavior**:
- Returns error message if skill not found
- Handles invalid SKILL.md files gracefully (skips)
- Validates resource paths to prevent directory traversal
- Returns error if resource file not found

**Feature Boundaries**:
- Does NOT support skill versioning or updates
- Does NOT support skill dependencies
- Does NOT support skill execution or sandboxing
- Does NOT support skill marketplace or distribution
- Does NOT validate skill instructions syntax

**Confidence Level**: High
**Basis**: Tests + implementation

## History Processing

### Summarization Processor

**Description**: Automatic conversation summarization to manage token limits in long-running sessions.

**User-Visible Behavior**:
- Monitors message token count
- Triggers summarization when thresholds reached
- Preserves recent messages (configurable)
- Replaces old messages with summary
- Maintains tool call/response pairs (safe cutoff points)

**Internal Modules Involved**:
- `pydantic_deep.processors.summarization.SummarizationProcessor`: Main class
- `pydantic_deep.processors.summarization.create_summarization_processor()`: Factory
- `pydantic_ai.Agent`: Summarization agent
- `pydantic_ai.messages.ModelMessage`: Message types

**Error Handling Behavior**:
- Falls back to error message if summarization fails
- Handles token counting errors gracefully
- Validates trigger and keep parameters
- Raises ValueError for invalid configuration

**Feature Boundaries**:
- Does NOT support custom summarization models per agent
- Does NOT support incremental summarization (full replacement)
- Does NOT support summarization of tool results only
- Does NOT support multiple summarization strategies
- Token counting is approximate (character-based heuristic)

**Confidence Level**: High
**Basis**: Tests + implementation

## Structured Output

### Type-Safe Output

**Description**: Return structured data using Pydantic models instead of plain strings.

**User-Visible Behavior**:
- Agent output is validated Pydantic model instance
- Type errors at runtime if model validation fails
- Supports Pydantic models, dataclasses, TypedDict
- Can combine with DeferredToolRequests for approval workflows

**Internal Modules Involved**:
- `pydantic_deep.agent.create_deep_agent()`: Output type configuration
- `pydantic_ai.output.OutputSpec`: Output specification
- `pydantic.BaseModel`: Pydantic model base

**Error Handling Behavior**:
- Raises validation errors if output doesn't match model
- Type errors if invalid output_type provided

**Feature Boundaries**:
- Does NOT support streaming structured output
- Does NOT support partial model validation
- Does NOT support custom validation logic beyond Pydantic
- Does NOT support multiple output types (single type or union)

**Confidence Level**: High
**Basis**: Tests + implementation

## Human-in-the-Loop

### Tool Approval Workflow

**Description**: Require human approval before executing specific tools (e.g., execute, write_file).

**User-Visible Behavior**:
- Agent returns `DeferredToolRequests` when approval needed
- Frontend receives approval requests with tool name and arguments
- User approves/denies each request
- Agent continues with approved tools only
- Denied tools are skipped

**Internal Modules Involved**:
- `pydantic_deep.agent.create_deep_agent()`: Interrupt configuration
- `pydantic_ai.tools.DeferredToolRequests`: Approval request type
- `pydantic_ai.tools.DeferredToolResults`: Approval response type
- `pydantic_ai.tools.ToolApproved`: Approval marker

**Error Handling Behavior**:
- Denied tools return error to agent
- Agent can retry with different approach
- No timeout for approval (waits indefinitely)

**Feature Boundaries**:
- Does NOT support approval timeouts
- Does NOT support batch approval (one request per tool call)
- Does NOT support conditional approval (approve if condition met)
- Does NOT support approval delegation
- Does NOT persist approval history

**Confidence Level**: High
**Basis**: Tests + implementation

## Dynamic System Prompts

### Context-Aware Instructions

**Description**: Automatically generate system prompt sections based on current agent state.

**User-Visible Behavior**:
- System prompt includes uploaded files summary
- System prompt includes current TODO list
- System prompt includes filesystem state
- System prompt includes available subagents
- System prompt includes available skills
- Updates dynamically as state changes

**Internal Modules Involved**:
- `pydantic_deep.agent.create_deep_agent()`: Dynamic instructions decorator
- `pydantic_deep.deps.DeepAgentDeps.get_uploads_summary()`: Upload summary
- `pydantic_ai_todo.get_todo_system_prompt()`: Todo summary
- `pydantic_deep.toolsets.*.get_*_system_prompt()`: Toolset summaries

**Error Handling Behavior**:
- Handles missing state gracefully (empty summaries)
- No errors if state is empty

**Feature Boundaries**:
- Does NOT support custom prompt templates
- Does NOT support prompt versioning
- Does NOT support conditional prompt sections
- Does NOT cache prompt generation

**Confidence Level**: Medium
**Basis**: Implementation (limited test coverage)
