# Diagrams

Visual system documentation using Mermaid syntax.

## System Context Diagram

```mermaid
graph TB
    User[User/Developer] --> Agent[pydantic-deep Agent]
    Agent --> LLM[LLM Model<br/>OpenAI/Anthropic/etc]
    Agent --> Backend[Backend<br/>State/Filesystem/Docker]
    Agent --> Toolsets[Toolsets<br/>Todo/Filesystem/SubAgent/Skills]
    Toolsets --> Backend
    SubAgent[SubAgent] --> LLM
    SubAgent --> Backend
    Processor[History Processor] --> LLM
    Processor --> Agent
```

## Component Diagram

```mermaid
graph TB
    subgraph "pydantic-deep"
        Factory[create_deep_agent<br/>Agent Factory]
        Deps[DeepAgentDeps<br/>Dependency Container]
        FSToolset[FilesystemToolset]
        SubToolset[SubAgentToolset]
        SkillToolset[SkillsToolset]
        Processor[SummarizationProcessor]
    end
    
    subgraph "External Packages"
        PydanticAI[pydantic-ai<br/>Agent Framework]
        PydanticAITodo[pydantic-ai-todo<br/>Todo Toolset]
        PydanticAIBackend[pydantic-ai-backend<br/>Backend Implementations]
    end
    
    Factory --> PydanticAI
    Factory --> PydanticAITodo
    Factory --> FSToolset
    Factory --> SubToolset
    Factory --> SkillToolset
    Factory --> Processor
    FSToolset --> Deps
    SubToolset --> Deps
    SkillToolset --> Deps
    Deps --> PydanticAIBackend
    Processor --> PydanticAI
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
    
    User->>Agent: run(query, deps)
    Agent->>Processor: process(messages)
    Processor-->>Agent: processed messages
    Agent->>Model: request with tools
    Model-->>Agent: response with tool calls
    Agent->>Toolset: execute tool
    Toolset->>Backend: read/write/execute
    Backend-->>Toolset: result
    Toolset-->>Agent: tool result
    Agent->>Model: tool result
    Model-->>Agent: final response
    Agent-->>User: result.output
```

## File Upload Sequence

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Deps
    participant Backend
    
    User->>App: upload_file(name, content)
    App->>Deps: upload_file(name, content)
    Deps->>Backend: write(path, content)
    Backend-->>Deps: WriteResult
    Deps->>Deps: extract metadata
    Deps->>Deps: store in uploads dict
    Deps-->>App: path
    App-->>User: success
```

## SubAgent Delegation Sequence

```mermaid
sequenceDiagram
    participant MainAgent
    participant SubAgentToolset
    participant SubAgent
    participant Backend
    
    MainAgent->>SubAgentToolset: task(description, type)
    SubAgentToolset->>SubAgentToolset: find or create subagent
    SubAgentToolset->>SubAgentToolset: clone deps
    SubAgentToolset->>SubAgent: run(description, deps)
    SubAgent->>Backend: file operations
    Backend-->>SubAgent: results
    SubAgent-->>SubAgentToolset: summary
    SubAgentToolset-->>MainAgent: summary
```

## Summarization Flow

```mermaid
flowchart TD
    Start[Message History] --> Check{Check Trigger<br/>Conditions}
    Check -->|Not Triggered| Continue[Continue Normal Flow]
    Check -->|Triggered| Cutoff[Determine Cutoff Point<br/>Preserve Tool Pairs]
    Cutoff --> Extract[Extract Messages<br/>to Summarize]
    Extract --> Summarize[Generate Summary<br/>via Summarization Agent]
    Summarize --> Replace[Replace Old Messages<br/>with Summary]
    Replace --> Preserve[Preserve Recent Messages]
    Preserve --> Continue
```

## Data Flow: Agent with Toolsets

```mermaid
flowchart LR
    Query[User Query] --> Agent[Agent]
    Agent --> Prompt[Dynamic System Prompt]
    Prompt --> Model[LLM Model]
    Model --> Tools{Tool Calls?}
    Tools -->|Yes| Todo[Todo Toolset]
    Tools -->|Yes| FS[Filesystem Toolset]
    Tools -->|Yes| Sub[SubAgent Toolset]
    Tools -->|Yes| Skill[Skills Toolset]
    Todo --> Deps[DeepAgentDeps]
    FS --> Deps
    Sub --> Deps
    Skill --> Deps
    Deps --> Backend[Backend]
    Backend --> Deps
    Deps --> Tools
    Tools -->|No| Response[Final Response]
```

## Multi-User Application Topology

```mermaid
graph TB
    subgraph "FastAPI Application"
        App[FastAPI App]
        WS[WebSocket Handler]
        Agent[Shared Agent<br/>Stateless]
    end
    
    subgraph "Session Manager"
        SM[SessionManager]
    end
    
    subgraph "User Sessions"
        S1[Session 1<br/>DockerSandbox]
        S2[Session 2<br/>DockerSandbox]
        S3[Session N<br/>DockerSandbox]
    end
    
    User1[User 1] --> WS
    User2[User 2] --> WS
    UserN[User N] --> WS
    WS --> Agent
    WS --> SM
    SM --> S1
    SM --> S2
    SM --> S3
    S1 --> Agent
    S2 --> Agent
    S3 --> Agent
```

## Toolset Registration

```mermaid
graph LR
    Factory[create_deep_agent] --> Config{Configuration Flags}
    Config -->|include_todo=True| Todo[TodoToolset]
    Config -->|include_filesystem=True| FS[FilesystemToolset]
    Config -->|include_subagents=True| Sub[SubAgentToolset]
    Config -->|include_skills=True| Skill[SkillsToolset]
    Config -->|toolsets=[]| Custom[Custom Toolsets]
    Todo --> Agent[Agent Instance]
    FS --> Agent
    Sub --> Agent
    Skill --> Agent
    Custom --> Agent
```

## Backend Abstraction

```mermaid
graph TB
    subgraph "Backend Protocol"
        BP[BackendProtocol<br/>Interface]
        SP[SandboxProtocol<br/>Interface]
    end
    
    subgraph "Implementations"
        State[StateBackend<br/>In-Memory]
        FS[FilesystemBackend<br/>Local Filesystem]
        Docker[DockerSandbox<br/>Isolated Container]
        Composite[CompositeBackend<br/>Multiple Backends]
    end
    
    BP --> State
    BP --> FS
    BP --> Docker
    BP --> Composite
    SP --> Docker
    SP --> Composite
```
