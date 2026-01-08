# Diagrams

Visual documentation of pydantic-deep architecture and workflows using Mermaid syntax.

## System Context Diagram

```mermaid
graph TB
    User[User/Application] -->|Creates| Agent[Deep Agent]
    User -->|Provides| Deps[DeepAgentDeps]
    Agent -->|Uses| LLM[LLM Provider<br/>OpenAI/Anthropic/etc]
    Agent -->|Executes| Tools[Toolsets]
    Tools -->|Accesses| Deps
    Deps -->|Stores Files| Backend[Backend<br/>State/Filesystem/Docker]
    Agent -->|Delegates| SubAgents[SubAgents]
    SubAgents -->|Uses| Deps
    Agent -->|Loads| Skills[Skills<br/>Markdown Files]
    
    style Agent fill:#e1f5ff
    style Deps fill:#fff4e1
    style Backend fill:#e8f5e9
    style Tools fill:#f3e5f5
```

## Component Diagram

```mermaid
graph TB
    subgraph "pydantic-deep"
        AgentFactory[create_deep_agent<br/>Agent Factory]
        DepsContainer[DeepAgentDeps<br/>Dependency Container]
        
        subgraph "Toolsets"
            TodoToolset[TodoToolset<br/>Task Planning]
            FilesystemToolset[FilesystemToolset<br/>File Operations]
            SubAgentToolset[SubAgentToolset<br/>Task Delegation]
            SkillsToolset[SkillsToolset<br/>Modular Skills]
        end
        
        Processor[SummarizationProcessor<br/>Context Management]
    end
    
    subgraph "External Packages"
        PydanticAI[pydantic-ai<br/>Core Framework]
        BackendPackage[pydantic-ai-backend<br/>Backend Implementations]
        TodoPackage[pydantic-ai-todo<br/>Todo Toolset]
    end
    
    AgentFactory -->|Creates| PydanticAI
    AgentFactory -->|Configures| TodoToolset
    AgentFactory -->|Configures| FilesystemToolset
    AgentFactory -->|Configures| SubAgentToolset
    AgentFactory -->|Configures| SkillsToolset
    AgentFactory -->|Uses| Processor
    
    TodoToolset -->|Uses| TodoPackage
    FilesystemToolset -->|Uses| BackendPackage
    SubAgentToolset -->|Creates| PydanticAI
    SkillsToolset -->|Reads| Skills[Skill Files]
    
    DepsContainer -->|Holds| BackendPackage
    DepsContainer -->|Tracks| TodoPackage
    
    style AgentFactory fill:#e1f5ff
    style DepsContainer fill:#fff4e1
    style Toolsets fill:#f3e5f5
```

## Agent Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Processor
    participant Model
    participant Toolset
    participant Backend
    participant Deps
    
    User->>Agent: run(query, deps)
    Agent->>Processor: Process history (if configured)
    Processor-->>Agent: Processed messages
    Agent->>Agent: Generate dynamic system prompt
    Agent->>Model: Request with tools
    Model-->>Agent: Response (may include tool calls)
    
    alt Tool calls needed
        Agent->>Toolset: Execute tool(ctx)
        Toolset->>Deps: Access ctx.deps
        Toolset->>Backend: File operations
        Backend-->>Toolset: Result
        Toolset-->>Agent: Tool result
        Agent->>Model: Tool result
        Model-->>Agent: Final response
    end
    
    alt Structured output
        Agent->>Agent: Validate output_type
    end
    
    Agent-->>User: Result
```

## File Upload Sequence

```mermaid
sequenceDiagram
    participant User
    participant Deps
    participant Backend
    participant Agent
    
    User->>Deps: upload_file(name, content)
    Deps->>Backend: write(path, content)
    Backend-->>Deps: WriteResult
    Deps->>Deps: Detect encoding (chardet)
    Deps->>Deps: Calculate line count
    Deps->>Deps: Infer MIME type
    Deps->>Deps: Store metadata in uploads dict
    Deps-->>User: File path
    
    User->>Agent: run("Process uploaded file", deps)
    Agent->>Agent: Generate system prompt with uploads
    Agent->>Agent: Execute file tools
    Agent->>Backend: read("/uploads/file.csv")
    Backend-->>Agent: File content
    Agent-->>User: Result
```

## SubAgent Delegation Sequence

```mermaid
sequenceDiagram
    participant MainAgent
    participant SubAgentToolset
    participant SubAgent
    participant Deps
    participant Backend
    
    MainAgent->>SubAgentToolset: task(description, type)
    SubAgentToolset->>Deps: Check cached subagents
    alt Not cached
        SubAgentToolset->>SubAgentToolset: Create subagent
        SubAgentToolset->>Deps: Cache subagent
    end
    SubAgentToolset->>Deps: clone_for_subagent()
    Deps-->>SubAgentToolset: Cloned deps (isolated)
    SubAgentToolset->>SubAgent: run(description, deps=cloned)
    SubAgent->>Backend: File operations (shared)
    Backend-->>SubAgent: Results
    SubAgent-->>SubAgentToolset: Summary
    SubAgentToolset-->>MainAgent: Subagent result
    MainAgent->>MainAgent: Continue with result
```

## Summarization Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Processor
    participant Messages
    participant Summarizer
    participant Model
    
    Agent->>Processor: Process messages
    Processor->>Processor: Count tokens
    Processor->>Processor: Check trigger conditions
    
    alt Triggered
        Processor->>Processor: Determine cutoff (safe for tool pairs)
        Processor->>Messages: Split: old vs recent
        Processor->>Summarizer: Create summary agent
        Processor->>Summarizer: Format messages for summary
        Summarizer->>Model: Generate summary
        Model-->>Summarizer: Summary text
        Summarizer-->>Processor: Summary
        Processor->>Messages: Replace old with summary
        Processor->>Messages: Keep recent messages
    end
    
    Processor-->>Agent: Processed messages
    Agent->>Agent: Continue with summarized history
```

## Human-in-the-Loop Approval Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Tool
    participant ApprovalUI
    
    User->>Agent: run("Execute command", deps)
    Agent->>Tool: execute(command)
    Tool->>Tool: Check requires_approval
    Tool-->>Agent: DeferredToolRequests
    Agent-->>User: Result with DeferredToolRequests
    
    User->>ApprovalUI: Show approval requests
    ApprovalUI->>User: Display tool name, args
    User->>ApprovalUI: Approve/Deny
    ApprovalUI->>User: DeferredToolResults
    
    User->>Agent: run(None, deferred_tool_results)
    Agent->>Tool: Execute approved tools
    Tool-->>Agent: Tool results
    Agent-->>User: Final result
```

## Skills Loading Sequence

```mermaid
sequenceDiagram
    participant Agent
    participant SkillsToolset
    participant FileSystem
    participant SkillCache
    
    Agent->>SkillsToolset: list_skills()
    SkillsToolset->>FileSystem: Discover SKILL.md files
    FileSystem-->>SkillsToolset: Skill directories
    SkillsToolset->>FileSystem: Read SKILL.md (frontmatter only)
    FileSystem-->>SkillsToolset: YAML frontmatter
    SkillsToolset->>SkillsToolset: Parse frontmatter
    SkillsToolset->>SkillCache: Store skill metadata
    SkillsToolset-->>Agent: List of skills
    
    Agent->>SkillsToolset: load_skill(skill_name)
    SkillsToolset->>SkillCache: Get skill path
    SkillsToolset->>FileSystem: Read full SKILL.md
    FileSystem-->>SkillsToolset: Full markdown
    SkillsToolset->>SkillsToolset: Parse instructions
    SkillsToolset-->>Agent: Full skill instructions
```

## Multi-User Session Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        App[FastAPI App]
        Agent[Shared Agent<br/>Stateless]
        SessionMgr[SessionManager]
    end
    
    subgraph "User Sessions"
        Session1[Session 1<br/>session_id: abc123]
        Session2[Session 2<br/>session_id: def456]
        SessionN[Session N<br/>session_id: xyz789]
    end
    
    subgraph "Docker Containers"
        Container1[DockerSandbox 1<br/>Isolated]
        Container2[DockerSandbox 2<br/>Isolated]
        ContainerN[DockerSandbox N<br/>Isolated]
    end
    
    subgraph "Dependencies"
        Deps1[DeepAgentDeps 1]
        Deps2[DeepAgentDeps 2]
        DepsN[DeepAgentDeps N]
    end
    
    App -->|Uses| Agent
    App -->|Manages| SessionMgr
    SessionMgr -->|Creates| Session1
    SessionMgr -->|Creates| Session2
    SessionMgr -->|Creates| SessionN
    Session1 -->|Gets| Container1
    Session2 -->|Gets| Container2
    SessionN -->|Gets| ContainerN
    Session1 -->|Creates| Deps1
    Session2 -->|Creates| Deps2
    SessionN -->|Creates| DepsN
    Deps1 -->|Uses| Container1
    Deps2 -->|Uses| Container2
    DepsN -->|Uses| ContainerN
    
    style Agent fill:#e1f5ff
    style SessionMgr fill:#fff4e1
    style Container1 fill:#e8f5e9
    style Container2 fill:#e8f5e9
    style ContainerN fill:#e8f5e9
```

## Data Flow: Agent State

```mermaid
graph LR
    subgraph "Agent Creation"
        Factory[create_deep_agent]
        Config[Configuration<br/>toolsets, subagents, skills]
    end
    
    subgraph "Runtime State"
        Deps[DeepAgentDeps]
        Backend[Backend Instance]
        Todos[Todo List]
        Uploads[Upload Metadata]
        SubAgents[SubAgent Cache]
    end
    
    subgraph "Tool Execution"
        Tools[Toolsets]
        Context[RunContext]
    end
    
    Factory -->|Creates| Agent[Agent Instance]
    Config -->|Configures| Agent
    Agent -->|Uses| Deps
    Deps -->|Contains| Backend
    Deps -->|Contains| Todos
    Deps -->|Contains| Uploads
    Deps -->|Contains| SubAgents
    Agent -->|Executes| Tools
    Tools -->|Accesses| Context
    Context -->|Provides| Deps
    
    style Agent fill:#e1f5ff
    style Deps fill:#fff4e1
    style Tools fill:#f3e5f5
```

## Toolset Registration Flow

```mermaid
graph TD
    Start[create_deep_agent called] --> CheckTodo{include_todo?}
    CheckTodo -->|Yes| AddTodo[Add TodoToolset]
    CheckTodo -->|No| CheckFS
    AddTodo --> CheckFS{include_filesystem?}
    CheckFS -->|Yes| AddFS[Add FilesystemToolset]
    CheckFS -->|No| CheckSub{include_subagents?}
    AddFS --> CheckSub
    CheckSub -->|Yes| AddSub[Add SubAgentToolset]
    CheckSub -->|No| CheckSkills{include_skills?}
    AddSub --> CheckSkills
    CheckSkills -->|Yes| AddSkills[Add SkillsToolset]
    CheckSkills -->|No| CheckCustom{Custom toolsets?}
    AddSkills --> CheckCustom
    CheckCustom -->|Yes| AddCustom[Add Custom Toolsets]
    CheckCustom -->|No| CreateAgent[Create Agent with Toolsets]
    AddCustom --> CreateAgent
    CreateAgent --> AddInstructions[Add Dynamic Instructions]
    AddInstructions --> Done[Return Agent]
    
    style CreateAgent fill:#e1f5ff
    style Done fill:#e8f5e9
```
