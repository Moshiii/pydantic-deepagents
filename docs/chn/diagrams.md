# 图表

使用 Mermaid 语法的可视化系统文档。

## 系统上下文图

```mermaid
graph TB
    User[用户/开发者] --> Agent[pydantic-deep 代理]
    Agent --> LLM[LLM 模型<br/>OpenAI/Anthropic/等]
    Agent --> Backend[后端<br/>State/Filesystem/Docker]
    Agent --> Toolsets[工具集<br/>Todo/Filesystem/SubAgent/Skills]
    Toolsets --> Backend
    SubAgent[子代理] --> LLM
    SubAgent --> Backend
    Processor[历史处理器] --> LLM
    Processor --> Agent
```

## 组件图

```mermaid
graph TB
    subgraph "pydantic-deep"
        Factory[create_deep_agent<br/>代理工厂]
        Deps[DeepAgentDeps<br/>依赖容器]
        FSToolset[FilesystemToolset]
        SubToolset[SubAgentToolset]
        SkillToolset[SkillsToolset]
        Processor[SummarizationProcessor]
    end
    
    subgraph "外部包"
        PydanticAI[pydantic-ai<br/>代理框架]
        PydanticAITodo[pydantic-ai-todo<br/>Todo 工具集]
        PydanticAIBackend[pydantic-ai-backend<br/>后端实现]
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

## 代理执行序列

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as 代理
    participant Processor as 处理器
    participant Model as 模型
    participant Toolset as 工具集
    participant Backend as 后端
    
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

## 文件上传序列

```mermaid
sequenceDiagram
    participant User as 用户
    participant App as 应用
    participant Deps as 依赖
    participant Backend as 后端
    
    User->>App: upload_file(name, content)
    App->>Deps: upload_file(name, content)
    Deps->>Backend: write(path, content)
    Backend-->>Deps: WriteResult
    Deps->>Deps: extract metadata
    Deps->>Deps: store in uploads dict
    Deps-->>App: path
    App-->>User: success
```

## 子代理委托序列

```mermaid
sequenceDiagram
    participant MainAgent as 主代理
    participant SubAgentToolset as 子代理工具集
    participant SubAgent as 子代理
    participant Backend as 后端
    
    MainAgent->>SubAgentToolset: task(description, type)
    SubAgentToolset->>SubAgentToolset: find or create subagent
    SubAgentToolset->>SubAgentToolset: clone deps
    SubAgentToolset->>SubAgent: run(description, deps)
    SubAgent->>Backend: file operations
    Backend-->>SubAgent: results
    SubAgent-->>SubAgentToolset: summary
    SubAgentToolset-->>MainAgent: summary
```

## 摘要流程

```mermaid
flowchart TD
    Start[消息历史] --> Check{检查触发<br/>条件}
    Check -->|未触发| Continue[继续正常流程]
    Check -->|触发| Cutoff[确定截止点<br/>保留工具对]
    Cutoff --> Extract[提取消息<br/>进行摘要]
    Extract --> Summarize[生成摘要<br/>通过摘要代理]
    Summarize --> Replace[用摘要替换<br/>旧消息]
    Replace --> Preserve[保留最近消息]
    Preserve --> Continue
```

## 数据流：带工具集的代理

```mermaid
flowchart LR
    Query[用户查询] --> Agent[代理]
    Agent --> Prompt[动态系统提示]
    Prompt --> Model[LLM 模型]
    Model --> Tools{工具调用?}
    Tools -->|是| Todo[Todo 工具集]
    Tools -->|是| FS[文件系统工具集]
    Tools -->|是| Sub[子代理工具集]
    Tools -->|是| Skill[技能工具集]
    Todo --> Deps[DeepAgentDeps]
    FS --> Deps
    Sub --> Deps
    Skill --> Deps
    Deps --> Backend[后端]
    Backend --> Deps
    Deps --> Tools
    Tools -->|否| Response[最终响应]
```

## 多用户应用拓扑

```mermaid
graph TB
    subgraph "FastAPI 应用"
        App[FastAPI App]
        WS[WebSocket 处理器]
        Agent[共享代理<br/>无状态]
    end
    
    subgraph "会话管理器"
        SM[SessionManager]
    end
    
    subgraph "用户会话"
        S1[会话 1<br/>DockerSandbox]
        S2[会话 2<br/>DockerSandbox]
        S3[会话 N<br/>DockerSandbox]
    end
    
    User1[用户 1] --> WS
    User2[用户 2] --> WS
    UserN[用户 N] --> WS
    WS --> Agent
    WS --> SM
    SM --> S1
    SM --> S2
    SM --> S3
    S1 --> Agent
    S2 --> Agent
    S3 --> Agent
```

## 工具集注册

```mermaid
graph LR
    Factory[create_deep_agent] --> Config{配置标志}
    Config -->|include_todo=True| Todo[TodoToolset]
    Config -->|include_filesystem=True| FS[FilesystemToolset]
    Config -->|include_subagents=True| Sub[SubAgentToolset]
    Config -->|include_skills=True| Skill[SkillsToolset]
    Config -->|toolsets=[]| Custom[自定义工具集]
    Todo --> Agent[代理实例]
    FS --> Agent
    Sub --> Agent
    Skill --> Agent
    Custom --> Agent
```

## 后端抽象

```mermaid
graph TB
    subgraph "后端协议"
        BP[BackendProtocol<br/>接口]
        SP[SandboxProtocol<br/>接口]
    end
    
    subgraph "实现"
        State[StateBackend<br/>内存]
        FS[FilesystemBackend<br/>本地文件系统]
        Docker[DockerSandbox<br/>隔离容器]
        Composite[CompositeBackend<br/>多个后端]
    end
    
    BP --> State
    BP --> FS
    BP --> Docker
    BP --> Composite
    SP --> Docker
    SP --> Composite
```
