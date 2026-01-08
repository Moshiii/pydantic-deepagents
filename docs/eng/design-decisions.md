# Design Decisions

Architectural choices, rationale, and tradeoffs in pydantic-deep.

## Modular Architecture

### Decision: Separate Package for Backends

**Summary**: Backend implementations are in a separate package (`pydantic-ai-backend`).

**Rationale** (inferred from code):
- Backends are reusable across different agent frameworks
- Docker dependencies are optional (sandbox extra)
- Clear separation of concerns (storage vs agent logic)
- Allows independent versioning and development

**Tradeoffs**:
- ✅ Reusability across projects
- ✅ Optional Docker dependency
- ✅ Clear module boundaries
- ❌ Additional package dependency
- ❌ Potential version mismatch issues

**Alternatives Considered** (implied):
- Bundling backends in pydantic-deep: Would force Docker dependency on all users
- Multiple backend packages: Too granular, harder to maintain

**Constraints Visible**:
- Backend implementations must implement `BackendProtocol` or `SandboxProtocol`
- Backends are external dependencies, not part of core package

### Decision: Separate Package for Todo Toolset

**Summary**: Todo toolset is in a separate package (`pydantic-ai-todo`).

**Rationale** (inferred from code):
- Todo functionality is useful for any pydantic-ai agent, not just pydantic-deep
- Allows independent development and versioning
- Can be used standalone without pydantic-deep

**Tradeoffs**:
- ✅ Reusability
- ✅ Independent versioning
- ✅ Standalone usage
- ❌ Additional dependency
- ❌ Potential API drift

**Alternatives Considered** (implied):
- Bundling in pydantic-deep: Would limit reusability
- Not providing todo functionality: Would reduce framework value

**Constraints Visible**:
- Must integrate with pydantic-ai's toolset system
- Must work with `DeepAgentDeps` for state management

## Dependency Injection

### Decision: DeepAgentDeps as Runtime Container

**Summary**: All runtime state is passed via `DeepAgentDeps` dataclass.

**Rationale** (inferred from code):
- Stateless agent design (agent can be shared across sessions)
- Clear separation of configuration (agent creation) and state (runtime)
- Type-safe dependency access
- Easy to clone for subagents

**Tradeoffs**:
- ✅ Stateless agents (thread-safe, shareable)
- ✅ Clear state boundaries
- ✅ Type safety
- ✅ Easy testing (mock deps)
- ❌ Must pass deps to every agent.run() call
- ❌ No global state (explicit passing required)

**Alternatives Considered** (implied):
- Global state: Would break multi-user scenarios
- Per-agent state: Would prevent agent sharing
- Context managers: More complex, less explicit

**Constraints Visible**:
- `DeepAgentDeps` must be passed to `agent.run()`
- Toolsets access deps via `RunContext[DeepAgentDeps]`
- Subagents get cloned deps (isolated context)

### Decision: Backend Abstraction via Protocols

**Summary**: Backends implement protocols (`BackendProtocol`, `SandboxProtocol`) rather than inheritance.

**Rationale** (inferred from code):
- Protocol-based design allows multiple backend types
- Clear interface contracts
- Easy to swap implementations
- Supports duck typing

**Tradeoffs**:
- ✅ Flexible implementation
- ✅ Clear contracts
- ✅ Easy testing (mock backends)
- ❌ No shared implementation (code duplication possible)
- ❌ Runtime type checking (not compile-time)

**Alternatives Considered** (implied):
- Abstract base classes: Less flexible, more rigid
- Concrete base class: Would force implementation details

**Constraints Visible**:
- Backends must implement protocol methods
- Type checking happens at runtime
- No shared base implementation

## Toolset Design

### Decision: Optional Toolsets via Flags

**Summary**: Toolsets can be enabled/disabled via boolean flags in `create_deep_agent()`.

**Rationale** (inferred from code):
- Users may not need all toolsets
- Reduces token usage (fewer tools = smaller prompts)
- Allows minimal agent configurations
- Clear opt-in/opt-out model

**Tradeoffs**:
- ✅ Flexibility
- ✅ Reduced token usage
- ✅ Minimal configurations
- ❌ More configuration options (complexity)
- ❌ Must know which toolsets to enable

**Alternatives Considered** (implied):
- Always include all toolsets: Would increase token usage and complexity
- Explicit toolset list: More verbose, less convenient

**Constraints Visible**:
- Default is to include all toolsets (`include_* = True`)
- Toolsets are independent (can mix and match)
- Toolsets generate their own system prompt sections

### Decision: Dynamic System Prompts

**Summary**: System prompts are generated dynamically based on current state.

**Rationale** (inferred from code):
- Context-aware prompts (uploads, todos, files visible to agent)
- Reduces token usage (only include relevant information)
- Better agent performance (relevant context)
- Automatic updates as state changes

**Tradeoffs**:
- ✅ Context-aware
- ✅ Reduced tokens
- ✅ Better performance
- ❌ More complex prompt generation
- ❌ Potential prompt inconsistency

**Alternatives Considered** (implied):
- Static prompts: Would include irrelevant information, waste tokens
- Manual prompt updates: Error-prone, easy to forget

**Constraints Visible**:
- Prompts generated via `@agent.instructions` decorator
- Each toolset provides its own prompt section
- Prompts update automatically on each agent run

## SubAgent Design

### Decision: Isolated SubAgent Context

**Summary**: Subagents get cloned deps with empty todos and no nested subagents.

**Rationale** (inferred from code):
- Prevents infinite recursion (subagents can't spawn subagents)
- Isolated task execution (no conversation history)
- Shared filesystem (subagents can read/write files)
- Clear task boundaries

**Tradeoffs**:
- ✅ Prevents recursion
- ✅ Clear isolation
- ✅ Shared filesystem (useful for coordination)
- ❌ No conversation context (subagents start fresh)
- ❌ No nested delegation

**Alternatives Considered** (implied):
- Full context sharing: Would allow recursion, complexity
- Complete isolation: Would prevent file coordination

**Constraints Visible**:
- `clone_for_subagent()` creates new deps with empty todos/subagents
- Subagents share backend and uploads (file access)
- Subagents don't share message history

### Decision: On-Demand SubAgent Creation

**Summary**: Subagents are created on first use and cached in `deps.subagents`.

**Rationale** (inferred from code):
- Lazy initialization (only create when needed)
- Caching reduces creation overhead
- Stateless subagent creation (can recreate if needed)

**Tradeoffs**:
- ✅ Lazy initialization
- ✅ Performance (caching)
- ✅ Stateless creation
- ❌ Memory usage (cached instances)
- ❌ Potential stale configurations

**Alternatives Considered** (implied):
- Pre-create all subagents: Would waste resources if unused
- No caching: Would recreate on every call (inefficient)

**Constraints Visible**:
- Subagents created in `task()` tool implementation
- Cached in `ctx.deps.subagents` dict
- Can be pre-created and passed in deps

## Skills Design

### Decision: Progressive Disclosure

**Summary**: Skills load frontmatter first, full instructions on demand.

**Rationale** (inferred from code):
- Reduces initial load time (don't parse all skills)
- Saves tokens (only load instructions when needed)
- Faster skill discovery (just metadata)
- Better scalability (many skills, few used)

**Tradeoffs**:
- ✅ Fast discovery
- ✅ Reduced tokens
- ✅ Scalability
- ❌ Extra step to load instructions
- ❌ Potential inconsistency (frontmatter vs instructions)

**Alternatives Considered** (implied):
- Load all instructions upfront: Would be slow and wasteful
- No frontmatter: Would require loading full instructions for discovery

**Constraints Visible**:
- `discover_skills()` loads only frontmatter
- `load_skill()` loads full instructions
- Skills stored with `frontmatter_loaded` flag

### Decision: Markdown-Based Skill Format

**Summary**: Skills are defined in SKILL.md files with YAML frontmatter.

**Rationale** (inferred from code):
- Human-readable format
- Easy to version control
- Familiar format (Markdown + YAML)
- Supports rich formatting in instructions

**Tradeoffs**:
- ✅ Human-readable
- ✅ Version control friendly
- ✅ Rich formatting
- ❌ Manual parsing (not using full YAML parser)
- ❌ Limited validation

**Alternatives Considered** (implied):
- JSON format: Less readable, harder to edit
- Python modules: More complex, requires execution
- Full YAML parser: Would add dependency, overkill for simple format

**Constraints Visible**:
- Custom YAML frontmatter parser (simple key:value format)
- Markdown instructions after frontmatter
- Resources stored as files in skill directory

## History Processing

### Decision: Approximate Token Counting

**Summary**: Token counting uses character-based heuristic (~4 chars per token).

**Rationale** (inferred from code):
- No tokenizer dependency
- Fast calculation
- Good enough for threshold detection
- Works across all models

**Tradeoffs**:
- ✅ No dependencies
- ✅ Fast
- ✅ Model-agnostic
- ❌ Not exact (approximation)
- ❌ May trigger early/late

**Alternatives Considered** (implied):
- Model-specific tokenizers: Would require dependencies, model-specific code
- Exact counting: Would be slower, require tokenizer

**Constraints Visible**:
- `_count_tokens_approximately()` uses character count / 4
- Custom token counter can be provided
- Approximation is acceptable for threshold detection

### Decision: Safe Cutoff Points

**Summary**: Summarization preserves tool call/response pairs (doesn't split them).

**Rationale** (inferred from code):
- Tool calls need their responses for context
- Prevents broken tool execution chains
- Maintains conversation coherence

**Tradeoffs**:
- ✅ Preserves tool context
- ✅ Maintains coherence
- ❌ May keep more messages than requested
- ❌ More complex cutoff logic

**Alternatives Considered** (implied):
- Simple message count cutoff: Would break tool pairs
- Always keep tool pairs: Would be simpler but less flexible

**Constraints Visible**:
- `_is_safe_cutoff_point()` checks for tool call/response pairs
- Searches around cutoff point for tool pairs
- Adjusts cutoff to preserve pairs

## Human-in-the-Loop

### Decision: DeferredToolRequests for Approvals

**Summary**: Tools return `DeferredToolRequests` when approval needed, agent output type includes it.

**Rationale** (inferred from code):
- Integrates with pydantic-ai's approval system
- Type-safe approval workflow
- Can combine with structured output (union types)
- Clear separation of approval and execution

**Tradeoffs**:
- ✅ Type-safe
- ✅ Integrated with pydantic-ai
- ✅ Flexible (can combine with output_type)
- ❌ More complex output types (union)
- ❌ Must handle DeferredToolRequests in code

**Alternatives Considered** (implied):
- Callback-based: Would be less type-safe
- Exception-based: Would break control flow

**Constraints Visible**:
- `output_type` becomes union when `interrupt_on` is used
- Must check `isinstance(result.output, DeferredToolRequests)`
- Approval results passed via `deferred_tool_results` parameter

## File Uploads

### Decision: Metadata Tracking

**Summary**: Uploaded files have metadata tracked (size, encoding, line count, MIME type).

**Rationale** (inferred from code):
- Helps agent understand file contents
- Enables better file handling decisions
- Provides context in system prompts
- Improves user experience

**Tradeoffs**:
- ✅ Better agent understanding
- ✅ Rich metadata
- ✅ Better prompts
- ❌ Extra processing overhead
- ❌ May fail for some file types

**Alternatives Considered** (implied):
- No metadata: Would reduce agent capabilities
- Full file analysis: Would be too slow

**Constraints Visible**:
- Encoding detection via `chardet` (may fail)
- Line count only for text files
- MIME type from filename (may be inaccurate)

## Structured Output

### Decision: Pydantic Model Integration

**Summary**: Structured output uses Pydantic models via `output_type` parameter.

**Rationale** (inferred from code):
- Type-safe responses
- Validation built-in
- Familiar to Python developers
- Integrates with pydantic-ai

**Tradeoffs**:
- ✅ Type safety
- ✅ Validation
- ✅ Familiar API
- ❌ Pydantic dependency
- ❌ Must define models upfront

**Alternatives Considered** (implied):
- JSON schema: Less type-safe, more verbose
- Dataclasses: Less validation features
- TypedDict: Less validation

**Constraints Visible**:
- Must use Pydantic models or compatible types
- Validation happens at runtime
- Type errors if validation fails
