# Feature Index

Canonical mapping between features and their implementation in the codebase.

## Agent Creation

### Feature: Deep Agent Factory

- **Description**: Factory function for creating configured agents with optional toolsets
- **Entry Points**: 
  - Python API: `create_deep_agent()`
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 99-335)
- **Related Tests**:
  - `tests/test_agent.py::TestCreateDeepAgent`
- **Configuration Flags**:
  - `include_todo` (default: True)
  - `include_filesystem` (default: True)
  - `include_subagents` (default: True)
  - `include_skills` (default: True)
  - `include_execute` (default: None, auto-detected)
  - `include_general_purpose_subagent` (default: True)
  - `interrupt_on` (dict of tool names to approval requirements)
  - `output_type` (Pydantic model for structured output)
  - `history_processors` (list of history processors)
- **Confidence Level**: High
- **Basis**: Tests + implementation

### Feature: Default Dependencies Factory

- **Description**: Helper function to create DeepAgentDeps with sensible defaults
- **Entry Points**:
  - Python API: `create_default_deps()`
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 338-350)
- **Related Tests**:
  - `tests/test_agent.py::TestCreateDefaultDeps`
- **Configuration Flags**: None
- **Confidence Level**: High
- **Basis**: Tests + implementation

### Feature: File Upload Helper

- **Description**: Convenience function to upload files and run agent
- **Entry Points**:
  - Python API: `run_with_files()`
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 353-400)
- **Related Tests**:
  - `tests/test_agent.py::TestRunWithFiles`
- **Configuration Flags**:
  - `upload_dir` (default: "/uploads")
- **Confidence Level**: High
- **Basis**: Tests + implementation

## Dependency Injection

### Feature: DeepAgentDeps Container

- **Description**: Dependency injection container for agent state and resources
- **Entry Points**:
  - Python API: `DeepAgentDeps`
- **Source Files**:
  - `pydantic_deep/deps.py` (lines 18-187)
- **Related Tests**:
  - `tests/test_agent.py::TestDeepAgentDeps`
- **Configuration Flags**: None (dataclass fields)
- **Confidence Level**: High
- **Basis**: Tests + implementation

### Feature: File Upload Tracking

- **Description**: Upload files to backend with metadata tracking
- **Entry Points**:
  - Python API: `deps.upload_file()`
- **Source Files**:
  - `pydantic_deep/deps.py` (lines 87-147)
- **Related Tests**:
  - `tests/test_agent.py::TestFileUploads`
- **Configuration Flags**:
  - `upload_dir` (default: "/uploads")
- **Confidence Level**: High
- **Basis**: Tests + implementation

## Toolsets

### Feature: Todo Toolset

- **Description**: Task planning and tracking tools (read_todos, write_todos)
- **Entry Points**:
  - Python API: Included via `include_todo=True` in `create_deep_agent()`
- **Source Files**:
  - External package: `pydantic-ai-todo`
  - Integration: `pydantic_deep/agent.py` (lines 203-205)
- **Related Tests**:
  - `tests/test_toolsets.py` (if present)
- **Configuration Flags**:
  - `include_todo` (default: True)
- **Confidence Level**: High
- **Basis**: Implementation + external package tests

### Feature: Filesystem Toolset

- **Description**: File operations (ls, read_file, write_file, edit_file, glob, grep, execute)
- **Entry Points**:
  - Python API: Included via `include_filesystem=True` in `create_deep_agent()`
- **Source Files**:
  - `pydantic_deep/toolsets/filesystem.py` (lines 46-341)
- **Related Tests**:
  - `tests/test_toolsets.py::TestFilesystemToolset`
- **Configuration Flags**:
  - `include_filesystem` (default: True)
  - `include_execute` (default: True, requires SandboxProtocol backend)
  - `require_write_approval` (default: False)
  - `require_execute_approval` (default: True)
- **Confidence Level**: High
- **Basis**: Tests + implementation

### Feature: SubAgent Toolset

- **Description**: Task delegation to specialized subagents
- **Entry Points**:
  - Python API: Included via `include_subagents=True` in `create_deep_agent()`
  - Tool: `task(description, subagent_type)`
- **Source Files**:
  - `pydantic_deep/toolsets/subagents.py` (lines 54-199)
- **Related Tests**:
  - `tests/test_toolsets.py::TestSubAgentToolset`
- **Configuration Flags**:
  - `include_subagents` (default: True)
  - `include_general_purpose_subagent` (default: True)
  - `subagents` (list of SubAgentConfig)
- **Confidence Level**: High
- **Basis**: Tests + implementation

### Feature: Skills Toolset

- **Description**: Load and use modular skill packages from markdown files
- **Entry Points**:
  - Python API: Included via `include_skills=True` in `create_deep_agent()`
  - Tools: `list_skills()`, `load_skill(skill_name)`, `read_skill_resource(skill_name, resource_name)`
- **Source Files**:
  - `pydantic_deep/toolsets/skills.py` (lines 216-363)
- **Related Tests**:
  - `tests/test_skills.py`
- **Configuration Flags**:
  - `include_skills` (default: True)
  - `skill_directories` (list of SkillDirectory)
  - `skills` (pre-loaded list of Skill)
- **Confidence Level**: High
- **Basis**: Tests + implementation

## History Processing

### Feature: Summarization Processor

- **Description**: Automatic conversation summarization for token management
- **Entry Points**:
  - Python API: `create_summarization_processor()` or `SummarizationProcessor`
- **Source Files**:
  - `pydantic_deep/processors/summarization.py` (lines 152-484)
- **Related Tests**:
  - `tests/test_processors.py`
- **Configuration Flags**:
  - `trigger` (ContextSize: messages/tokens/fraction threshold)
  - `keep` (ContextSize: how much context to preserve)
  - `max_input_tokens` (required for fraction-based triggers)
  - `token_counter` (custom token counting function)
  - `summary_prompt` (custom summarization prompt)
- **Confidence Level**: High
- **Basis**: Tests + implementation

## Backends

### Feature: StateBackend

- **Description**: In-memory file storage backend
- **Entry Points**:
  - Python API: `StateBackend()` from `pydantic_ai_backends`
- **Source Files**:
  - External package: `pydantic-ai-backend`
- **Related Tests**:
  - External package tests
- **Configuration Flags**: None
- **Confidence Level**: High
- **Basis**: External package implementation

### Feature: FilesystemBackend

- **Description**: Local filesystem operations backend
- **Entry Points**:
  - Python API: `FilesystemBackend(path)` from `pydantic_ai_backends`
- **Source Files**:
  - External package: `pydantic-ai-backend`
- **Related Tests**:
  - External package tests
- **Configuration Flags**:
  - `path` (filesystem root directory)
- **Confidence Level**: High
- **Basis**: External package implementation

### Feature: DockerSandbox

- **Description**: Isolated Docker container for code execution
- **Entry Points**:
  - Python API: `DockerSandbox()` from `pydantic_ai_backends`
- **Source Files**:
  - External package: `pydantic-ai-backend`
- **Related Tests**:
  - External package tests
- **Configuration Flags**:
  - `runtime` (RuntimeConfig)
  - `default_runtime` (default runtime configuration)
- **Confidence Level**: High
- **Basis**: External package implementation

### Feature: SessionManager

- **Description**: Per-session Docker container management with auto-cleanup
- **Entry Points**:
  - Python API: `SessionManager()` from `pydantic_ai_backends`
- **Source Files**:
  - External package: `pydantic-ai-backend`
- **Related Tests**:
  - External package tests
- **Configuration Flags**:
  - `default_runtime` (RuntimeConfig)
  - `default_idle_timeout` (seconds)
- **Confidence Level**: High
- **Basis**: External package implementation

## Structured Output

### Feature: Type-Safe Output

- **Description**: Return structured data using Pydantic models
- **Entry Points**:
  - Python API: `create_deep_agent(output_type=Model)`
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 273-281)
- **Related Tests**:
  - `tests/test_agent.py` (structured output tests)
- **Configuration Flags**:
  - `output_type` (OutputSpec or Pydantic model)
- **Confidence Level**: High
- **Basis**: Tests + implementation

## Human-in-the-Loop

### Feature: Tool Approval Workflow

- **Description**: Require human approval before executing specific tools
- **Entry Points**:
  - Python API: `create_deep_agent(interrupt_on={"execute": True})`
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 208-225, 271-281)
- **Related Tests**:
  - `tests/test_agent.py::TestCreateDeepAgent::test_create_with_interrupt_on`
- **Configuration Flags**:
  - `interrupt_on` (dict mapping tool names to boolean approval requirements)
- **Confidence Level**: High
- **Basis**: Tests + implementation

## Dynamic System Prompts

### Feature: Context-Aware Instructions

- **Description**: Dynamic system prompts based on current state (uploads, todos, files, subagents, skills)
- **Entry Points**:
  - Python API: Automatic via `@agent.instructions` decorator
- **Source Files**:
  - `pydantic_deep/agent.py` (lines 295-325)
- **Related Tests**:
  - Integration tests in `tests/test_agent.py`
- **Configuration Flags**: None (automatic)
- **Confidence Level**: Medium
- **Basis**: Implementation

## Example Applications

### Feature: Full App Example

- **Description**: Complete FastAPI application demonstrating all features
- **Entry Points**:
  - CLI: `cd examples/full_app && uvicorn app:app --reload --port 8080`
  - Web UI: http://localhost:8080
- **Source Files**:
  - `examples/full_app/app.py` (1077 lines)
  - `examples/full_app/github_tools.py`
  - `examples/full_app/static/` (frontend files)
- **Related Tests**: None (example only)
- **Configuration Flags**:
  - Environment variables (API keys)
  - Docker availability (auto-detected)
- **Confidence Level**: High
- **Basis**: Implementation
