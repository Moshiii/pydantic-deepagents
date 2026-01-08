# 架构

pydantic-deep 中的系统组件、模块边界和架构模式。

## 系统组件

### 核心代理工厂

**位置**：`pydantic_deep/agent.py`

**职责**：创建配置了可选工具集、子代理、技能和处理器的代理实例。

**依赖项**：
- `pydantic_ai.Agent`: 基础代理类
- `pydantic_ai_todo`: Todo 工具集
- `pydantic_deep.toolsets.*`: 内部工具集
- `pydantic_deep.deps.DeepAgentDeps`: 依赖类型

**导出**：
- `create_deep_agent()`: 主工厂函数
- `create_default_deps()`: 依赖工厂
- `run_with_files()`: 文件上传辅助函数

### 依赖注入容器

**位置**：`pydantic_deep/deps.py`

**职责**：保存运行时状态和资源（后端、todos、上传文件、子代理）。

**依赖项**：
- `pydantic_ai_backends.BackendProtocol`: 后端接口
- `pydantic_ai_todo.Todo`: Todo 类型
- `pydantic_deep.types.UploadedFile`: 上传元数据类型

**导出**：
- `DeepAgentDeps`: 主数据类

### 文件系统工具集

**位置**：`pydantic_deep/toolsets/filesystem.py`

**职责**：提供文件操作（读取、写入、编辑、搜索、执行）。

**依赖项**：
- `pydantic_ai.toolsets.FunctionToolset`: 基础工具集类
- `pydantic_ai_backends.BackendProtocol`: 后端接口
- `pydantic_ai_backends.SandboxProtocol`: 执行接口
- `pydantic_deep.deps.DeepAgentDeps`: 依赖类型

**导出**：
- `create_filesystem_toolset()`: 工厂函数
- `get_filesystem_system_prompt()`: 动态提示生成器
- `FilesystemToolset`: 工厂别名

### 子代理工具集

**位置**：`pydantic_deep/toolsets/subagents.py`

**职责**：将任务委托给专门的子代理。

**依赖项**：
- `pydantic_ai.Agent`: 子代理实例
- `pydantic_ai.toolsets.FunctionToolset`: 基础工具集类
- `pydantic_deep.deps.DeepAgentDeps`: 依赖类型
- `pydantic_deep.types.SubAgentConfig`: 配置类型

**导出**：
- `create_subagent_toolset()`: 工厂函数
- `get_subagent_system_prompt()`: 动态提示生成器
- `SubAgentToolset`: 工厂别名

### 技能工具集

**位置**：`pydantic_deep/toolsets/skills.py`

**职责**：从 Markdown 文件加载和使用模块化技能包。

**依赖项**：
- `pydantic_ai.toolsets.FunctionToolset`: 基础工具集类
- `pydantic_deep.deps.DeepAgentDeps`: 依赖类型
- `pydantic_deep.types.Skill`: 技能类型定义

**导出**：
- `create_skills_toolset()`: 工厂函数
- `discover_skills()`: 技能发现函数
- `load_skill_instructions()`: 指令加载器
- `get_skills_system_prompt()`: 动态提示生成器
- `parse_skill_md()`: Markdown 解析器

### 摘要处理器

**位置**：`pydantic_deep/processors/summarization.py`

**职责**：用于令牌管理的自动对话摘要。

**依赖项**：
- `pydantic_ai.Agent`: 摘要代理
- `pydantic_ai.messages.ModelMessage`: 消息类型
- `pydantic_ai._agent_graph.HistoryProcessor`: 处理器接口

**导出**：
- `SummarizationProcessor`: 主处理器类
- `create_summarization_processor()`: 工厂函数

### 类型定义

**位置**：`pydantic_deep/types.py`

**职责**：配置和数据结构的类型定义。

**依赖项**：
- `pydantic_ai.output.OutputSpec`: 输出规范
- `pydantic_ai_backends.*`: 后端类型
- `pydantic_ai_todo.Todo`: Todo 类型

**导出**：
- `SubAgentConfig`: 子代理配置
- `CompiledSubAgent`: 预编译子代理
- `Skill`: 技能定义
- `SkillDirectory`: 技能目录配置
- `SkillFrontmatter`: 技能元数据
- `UploadedFile`: 上传元数据
- `ResponseFormat`: 输出格式类型别名

## 模块边界

### 内部 vs 外部

**内部模块**（pydantic-deep 包）：
- `pydantic_deep.agent`: 代理工厂
- `pydantic_deep.deps`: 依赖注入
- `pydantic_deep.toolsets.*`: 工具集实现
- `pydantic_deep.processors.*`: 历史处理器
- `pydantic_deep.types`: 类型定义

**外部依赖**：
- `pydantic-ai`: 核心代理框架
- `pydantic-ai-backend`: 后端实现
- `pydantic-ai-todo`: Todo 工具集
- `pydantic`: 数据验证
- `fastapi`、`uvicorn`: 示例应用（可选）

### 工具集隔离

每个工具集都是自包含的：
- 工具集不相互依赖
- 工具集仅通过 `DeepAgentDeps` 通信
- 工具集可以独立启用/禁用
- 工具集生成自己的系统提示部分

### 后端抽象

后端通过协议抽象：
- `BackendProtocol`: 文件操作接口
- `SandboxProtocol`: 代码执行接口（扩展 BackendProtocol）
- 后端实现在外部包中（`pydantic-ai-backend`）
- 代理和工具集仅依赖协议，不依赖实现

### 依赖方向规则

1. **代理工厂 → 工具集**：工厂创建和配置工具集
2. **工具集 → 依赖**：工具集从 `DeepAgentDeps` 读取
3. **依赖 → 后端**：依赖保存后端实例
4. **后端 → 外部**：后端是外部实现
5. **处理器 → 代理**：处理器包装代理以进行摘要
6. **类型 → 所有**：类型在所有模块间共享

**无循环依赖**：依赖图是无环的。

## 数据流

### 代理执行流程

```
用户查询
    ↓
Agent.run(query, deps)
    ↓
历史处理器（如果配置）
    ↓
动态系统提示生成
    ↓
模型请求（带工具）
    ↓
工具执行（如果需要）
    ↓
    ├─→ 文件系统工具集 → 后端
    ├─→ 子代理工具集 → 子代理
    ├─→ 技能工具集 → 技能文件
    └─→ Todo 工具集 → DeepAgentDeps.todos
    ↓
模型响应
    ↓
输出验证（如果结构化）
    ↓
结果
```

### 文件上传流程

```
用户上传文件
    ↓
deps.upload_file(name, content)
    ↓
Backend.write(path, content)
    ↓
元数据提取（编码、MIME 类型、行数）
    ↓
存储在 deps.uploads
    ↓
系统提示包含上传摘要
    ↓
代理可以通过工具访问文件
```

### 子代理委托流程

```
主代理调用 task(description, subagent_type)
    ↓
查找或创建子代理
    ↓
克隆 deps（隔离上下文）
    ↓
Subagent.run(description, deps=cloned_deps)
    ↓
子代理执行（使用自己的工具集）
    ↓
返回摘要给主代理
    ↓
主代理继续
```

### 摘要流程

```
消息历史累积
    ↓
处理器检查触发条件
    ↓
如果触发：
    ├─→ 确定截止点（工具对安全）
    ├─→ 提取要摘要的消息
    ├─→ 通过摘要代理生成摘要
    └─→ 用摘要替换旧消息
    ↓
继续使用摘要后的历史
```

## 外部集成

### pydantic-ai 集成

- **Agent 类**：基础代理实现
- **工具系统**：工具注册和执行
- **消息类型**：ModelMessage、ModelRequest、ModelResponse
- **历史处理器**：处理器接口
- **输出规范**：结构化输出支持

### pydantic-ai-backend 集成

- **BackendProtocol**：文件操作接口
- **SandboxProtocol**：代码执行接口
- **后端实现**：StateBackend、FilesystemBackend、DockerSandbox
- **SessionManager**：多用户容器管理

### pydantic-ai-todo 集成

- **Todo 工具集**：任务规划工具
- **Todo 类型**：Todo 数据结构
- **系统提示**：动态 TODO 提示生成

## 运行时拓扑

### 单代理实例

```
代理（无状态）
    ↓
DeepAgentDeps（每次运行的状态）
    ├─→ 后端（文件存储）
    ├─→ todos（任务列表）
    ├─→ uploads（文件元数据）
    └─→ subagents（缓存的实例）
```

### 多用户应用

```
FastAPI 应用
    ├─→ 代理（共享，无状态）
    └─→ SessionManager
        ├─→ 会话 1 → DockerSandbox → DeepAgentDeps
        ├─→ 会话 2 → DockerSandbox → DeepAgentDeps
        └─→ 会话 N → DockerSandbox → DeepAgentDeps
```

### 工具集注册

```
代理
    ├─→ TodoToolset（来自 pydantic-ai-todo）
    ├─→ FilesystemToolset（内部）
    ├─→ SubAgentToolset（内部）
    ├─→ SkillsToolset（内部）
    └─→ 自定义工具集（用户提供）
```

## 设计模式

### 工厂模式

- `create_deep_agent()`: 代理创建的工厂
- `create_filesystem_toolset()`: 工具集创建的工厂
- `create_summarization_processor()`: 处理器创建的工厂

### 依赖注入

- `DeepAgentDeps`: 运行时依赖的容器
- 传递给每次执行的 agent.run()
- 工具集通过 RunContext 访问依赖

### 策略模式

- 后端抽象：不同的后端实现相同的协议
- 工具集选择：通过标志启用/禁用工具集
- 历史处理：可插拔处理器

### 装饰器模式

- `@agent.instructions`: 动态系统提示生成
- `@toolset.tool`: 工具注册

### 单例模式

- 代理实例通常共享（无状态）
- 子代理缓存在 `deps.subagents` 中

## 扩展点

### 自定义工具集

通过实现 `AbstractToolset[DeepAgentDeps]` 创建自定义工具集：

```python
from pydantic_ai.toolsets import FunctionToolset
from pydantic_deep.deps import DeepAgentDeps

toolset = FunctionToolset[DeepAgentDeps](id="custom")
@toolset.tool
async def my_tool(ctx, arg: str) -> str:
    # 通过 ctx.deps 访问 deps
    return "result"

agent = create_deep_agent(toolsets=[toolset])
```

### 自定义后端

实现 `BackendProtocol` 或 `SandboxProtocol`：

```python
from pydantic_ai_backends import BackendProtocol

class MyBackend(BackendProtocol):
    # 实现必需的方法
    pass

deps = DeepAgentDeps(backend=MyBackend())
```

### 自定义处理器

实现 `HistoryProcessor[DeepAgentDeps]`：

```python
from pydantic_ai._agent_graph import HistoryProcessor
from pydantic_ai.messages import ModelMessage

class MyProcessor(HistoryProcessor[DeepAgentDeps]):
    async def __call__(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        # 处理消息
        return messages

agent = create_deep_agent(history_processors=[MyProcessor()])
```
