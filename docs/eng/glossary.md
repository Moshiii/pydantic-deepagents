# Glossary

Domain terminology, internal naming conventions, and abbreviations used in pydantic-deep.

## Core Concepts

### Agent

An autonomous AI system built on pydantic-ai that can use tools, maintain conversation history, and produce structured outputs. In pydantic-deep, agents are created via `create_deep_agent()`.

### DeepAgentDeps

Dependency injection container that holds runtime state and resources for agent execution. Contains backend, todos, uploads, and subagents.

### Backend

Storage and execution abstraction. Implements `BackendProtocol` for file operations or `SandboxProtocol` for code execution. Examples: StateBackend, FilesystemBackend, DockerSandbox.

### Toolset

Collection of related tools that extend agent capabilities. Toolsets are modular and can be enabled/disabled independently. Examples: TodoToolset, FilesystemToolset, SubAgentToolset, SkillsToolset.

### Tool

Individual function that an agent can call during execution. Tools are registered via toolsets and have access to `RunContext[DeepAgentDeps]`.

### SubAgent

Specialized agent instance that can be delegated tasks by the main agent. Subagents have isolated context but share the filesystem backend.

### Skill

Modular package containing instructions and resources for extending agent capabilities. Skills are defined in SKILL.md files with YAML frontmatter.

## Types and Data Structures

### Todo

Task item for planning and tracking. Contains `content` (description), `status` (pending/in_progress/completed), and `active_form` (present continuous form).

### SubAgentConfig

Configuration for a subagent. Contains `name`, `description`, `instructions`, optional `model`, and optional `tools`.

### Skill

Loaded skill definition. Contains `name`, `description`, `path`, `tags`, `version`, `author`, and optional `instructions` and `resources`.

### SkillDirectory

Configuration for discovering skills. Contains `path` (directory path) and optional `recursive` (boolean).

### UploadedFile

Metadata for uploaded files. Contains `name`, `path`, `size`, `line_count`, `mime_type`, and `encoding`.

### FileData

Storage format for file contents. Contains `content` (list of lines), `created_at`, and `modified_at` timestamps.

### FileInfo

File metadata for directory listings. Contains `name`, `path`, `is_dir`, and optional `size`.

### WriteResult

Result of file write operations. Contains `path` and optional `error`.

### EditResult

Result of file edit operations. Contains `path`, optional `error`, and `occurrences` (number of replacements).

### ExecuteResponse

Result of command execution. Contains `output`, optional `exit_code`, and `truncated` flag.

### GrepMatch

Single grep search result. Contains `path`, `line_number`, and `line` content.

## Abbreviations

- **LLM**: Large Language Model
- **API**: Application Programming Interface
- **CLI**: Command Line Interface
- **UI**: User Interface
- **FS**: Filesystem
- **Deps**: Dependencies (DeepAgentDeps)
- **SKILL.md**: Skill definition file (markdown with YAML frontmatter)

## Protocol Names

### BackendProtocol

Interface for file storage backends. Defines methods: `read()`, `write()`, `edit()`, `ls_info()`, `glob_info()`, `grep_raw()`.

### SandboxProtocol

Interface for code execution backends. Extends `BackendProtocol` and adds `execute()` method.

## Function Names

### create_deep_agent()

Main factory function for creating configured agents. Returns `Agent[DeepAgentDeps, OutputT]`.

### create_default_deps()

Helper function to create `DeepAgentDeps` with sensible defaults.

### run_with_files()

Convenience function to upload files and run agent in one call.

### create_filesystem_toolset()

Factory function for creating filesystem toolset with file operations.

### create_subagent_toolset()

Factory function for creating subagent toolset for task delegation.

### create_skills_toolset()

Factory function for creating skills toolset for loading skill packages.

### create_summarization_processor()

Factory function for creating history processor that summarizes conversations.

### discover_skills()

Function to discover skills from directories containing SKILL.md files.

### load_skill_instructions()

Function to load full instructions from a skill's SKILL.md file.

## Internal Naming Conventions

### Module Names

- `pydantic_deep.agent`: Agent factory module
- `pydantic_deep.deps`: Dependency injection module
- `pydantic_deep.toolsets.*`: Toolset implementations
- `pydantic_deep.processors.*`: History processors
- `pydantic_deep.types`: Type definitions

### Variable Names

- `deps`: Short for `DeepAgentDeps` instance
- `backend`: Backend instance (StateBackend, FilesystemBackend, etc.)
- `agent`: Agent instance
- `ctx`: RunContext in tool implementations
- `run`: Agent run context in streaming

### Configuration Flags

- `include_todo`: Enable/disable todo toolset
- `include_filesystem`: Enable/disable filesystem toolset
- `include_subagents`: Enable/disable subagent toolset
- `include_skills`: Enable/disable skills toolset
- `include_execute`: Enable/disable execute tool
- `interrupt_on`: Map of tool names to approval requirements
- `output_type`: Structured output type specification

## Status Values

### Todo Status

- `pending`: Task not yet started
- `in_progress`: Task currently being worked on
- `completed`: Task finished

### Context Size Types

- `messages`: Count-based (number of messages)
- `tokens`: Token-based (approximate token count)
- `fraction`: Fraction-based (percentage of max_input_tokens)

## File Paths

### Default Paths

- `/uploads`: Default directory for uploaded files
- `/workspace`: Default workspace directory in backends
- `~/.pydantic-deep/skills`: Default skills directory

### Skill File Structure

```
skill-name/
  ├── SKILL.md          # Skill definition (required)
  └── resource.*        # Additional resources (optional)
```

## External Package Names

- `pydantic-ai`: Core agent framework
- `pydantic-ai-backend`: Backend implementations
- `pydantic-ai-todo`: Todo toolset package
