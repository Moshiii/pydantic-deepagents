# 术语表

pydantic-deep 中使用的领域术语、内部命名约定和缩写。

## 核心概念

### Agent（代理）

基于 pydantic-ai 构建的自主 AI 系统，可以使用工具、维护对话历史并产生结构化输出。在 pydantic-deep 中，代理通过 `create_deep_agent()` 创建。

### DeepAgentDeps

依赖注入容器，保存代理执行所需的运行时状态和资源。包含后端、todos、上传文件和子代理。

### Backend（后端）

存储和执行抽象。实现 `BackendProtocol` 用于文件操作，或 `SandboxProtocol` 用于代码执行。示例：StateBackend、FilesystemBackend、DockerSandbox。

### Toolset（工具集）

扩展代理功能的相关工具集合。工具集是模块化的，可以独立启用/禁用。示例：TodoToolset、FilesystemToolset、SubAgentToolset、SkillsToolset。

### Tool（工具）

代理在执行期间可以调用的单个函数。工具通过工具集注册，可以访问 `RunContext[DeepAgentDeps]`。

### SubAgent（子代理）

可以由主代理委托任务的专门代理实例。子代理具有隔离的上下文，但共享文件系统后端。

### Skill（技能）

包含指令和资源的模块化包，用于扩展代理功能。技能在带有 YAML frontmatter 的 SKILL.md 文件中定义。

## 类型和数据结构

### Todo

用于规划和跟踪的任务项。包含 `content`（描述）、`status`（pending/in_progress/completed）和 `active_form`（现在进行时形式）。

### SubAgentConfig

子代理的配置。包含 `name`、`description`、`instructions`、可选的 `model` 和可选的 `tools`。

### Skill

已加载的技能定义。包含 `name`、`description`、`path`、`tags`、`version`、`author`，以及可选的 `instructions` 和 `resources`。

### SkillDirectory

用于发现技能的配置。包含 `path`（目录路径）和可选的 `recursive`（布尔值）。

### UploadedFile

上传文件的元数据。包含 `name`、`path`、`size`、`line_count`、`mime_type` 和 `encoding`。

### FileData

文件内容的存储格式。包含 `content`（行列表）、`created_at` 和 `modified_at` 时间戳。

### FileInfo

目录列表的文件元数据。包含 `name`、`path`、`is_dir` 和可选的 `size`。

### WriteResult

文件写入操作的结果。包含 `path` 和可选的 `error`。

### EditResult

文件编辑操作的结果。包含 `path`、可选的 `error` 和 `occurrences`（替换次数）。

### ExecuteResponse

命令执行的结果。包含 `output`、可选的 `exit_code` 和 `truncated` 标志。

### GrepMatch

单个 grep 搜索结果。包含 `path`、`line_number` 和 `line` 内容。

## 缩写

- **LLM**: 大语言模型（Large Language Model）
- **API**: 应用程序编程接口（Application Programming Interface）
- **CLI**: 命令行界面（Command Line Interface）
- **UI**: 用户界面（User Interface）
- **FS**: 文件系统（Filesystem）
- **Deps**: 依赖项（Dependencies，DeepAgentDeps）
- **SKILL.md**: 技能定义文件（带 YAML frontmatter 的 Markdown）

## 协议名称

### BackendProtocol

文件存储后端的接口。定义方法：`read()`、`write()`、`edit()`、`ls_info()`、`glob_info()`、`grep_raw()`。

### SandboxProtocol

代码执行后端的接口。扩展 `BackendProtocol` 并添加 `execute()` 方法。

## 函数名称

### create_deep_agent()

创建配置代理的主工厂函数。返回 `Agent[DeepAgentDeps, OutputT]`。

### create_default_deps()

使用合理默认值创建 `DeepAgentDeps` 的辅助函数。

### run_with_files()

在一次调用中上传文件并运行代理的便捷函数。

### create_filesystem_toolset()

创建带文件操作的文件系统工具集的工厂函数。

### create_subagent_toolset()

创建用于任务委托的子代理工具集的工厂函数。

### create_skills_toolset()

创建用于加载技能包的技能工具集的工厂函数。

### create_summarization_processor()

创建用于摘要对话的历史处理器的工厂函数。

### discover_skills()

从包含 SKILL.md 文件的目录中发现技能的函数。

### load_skill_instructions()

从技能的 SKILL.md 文件加载完整指令的函数。

## 内部命名约定

### 模块名称

- `pydantic_deep.agent`: 代理工厂模块
- `pydantic_deep.deps`: 依赖注入模块
- `pydantic_deep.toolsets.*`: 工具集实现
- `pydantic_deep.processors.*`: 历史处理器
- `pydantic_deep.types`: 类型定义

### 变量名称

- `deps`: `DeepAgentDeps` 实例的简写
- `backend`: 后端实例（StateBackend、FilesystemBackend 等）
- `agent`: 代理实例
- `ctx`: 工具实现中的 RunContext
- `run`: 流式传输中的代理运行上下文

### 配置标志

- `include_todo`: 启用/禁用 todo 工具集
- `include_filesystem`: 启用/禁用文件系统工具集
- `include_subagents`: 启用/禁用子代理工具集
- `include_skills`: 启用/禁用技能工具集
- `include_execute`: 启用/禁用执行工具
- `interrupt_on`: 工具名称到审批要求的映射
- `output_type`: 结构化输出类型规范

## 状态值

### Todo 状态

- `pending`: 任务尚未开始
- `in_progress`: 当前正在处理的任务
- `completed`: 已完成的任务

### 上下文大小类型

- `messages`: 基于计数（消息数量）
- `tokens`: 基于令牌（近似令牌计数）
- `fraction`: 基于分数（max_input_tokens 的百分比）

## 文件路径

### 默认路径

- `/uploads`: 上传文件的默认目录
- `/workspace`: 后端中的默认工作空间目录
- `~/.pydantic-deep/skills`: 默认技能目录

### 技能文件结构

```
skill-name/
  ├── SKILL.md          # 技能定义（必需）
  └── resource.*        # 附加资源（可选）
```

## 外部包名称

- `pydantic-ai`: 核心代理框架
- `pydantic-ai-backend`: 后端实现
- `pydantic-ai-todo`: Todo 工具集包
