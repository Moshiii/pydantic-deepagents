# 功能索引

功能与代码库实现的规范映射。

## 代理创建

### 功能：深度代理工厂

- **描述**：用于创建配置了可选工具集的代理的工厂函数
- **入口点**： 
  - Python API: `create_deep_agent()`
- **源文件**：
  - `pydantic_deep/agent.py` (第 99-335 行)
- **相关测试**：
  - `tests/test_agent.py::TestCreateDeepAgent`
- **配置标志**：
  - `include_todo` (默认: True)
  - `include_filesystem` (默认: True)
  - `include_subagents` (默认: True)
  - `include_skills` (默认: True)
  - `include_execute` (默认: None, 自动检测)
  - `include_general_purpose_subagent` (默认: True)
  - `interrupt_on` (工具名称到审批要求的字典)
  - `output_type` (用于结构化输出的 Pydantic 模型)
  - `history_processors` (历史处理器列表)
- **置信度级别**：高
- **依据**：测试 + 实现

### 功能：默认依赖工厂

- **描述**：使用合理默认值创建 DeepAgentDeps 的辅助函数
- **入口点**：
  - Python API: `create_default_deps()`
- **源文件**：
  - `pydantic_deep/agent.py` (第 338-350 行)
- **相关测试**：
  - `tests/test_agent.py::TestCreateDefaultDeps`
- **配置标志**：无
- **置信度级别**：高
- **依据**：测试 + 实现

### 功能：文件上传辅助

- **描述**：上传文件并运行代理的便捷函数
- **入口点**：
  - Python API: `run_with_files()`
- **源文件**：
  - `pydantic_deep/agent.py` (第 353-400 行)
- **相关测试**：
  - `tests/test_agent.py::TestRunWithFiles`
- **配置标志**：
  - `upload_dir` (默认: "/uploads")
- **置信度级别**：高
- **依据**：测试 + 实现

## 依赖注入

### 功能：DeepAgentDeps 容器

- **描述**：用于代理状态和资源的依赖注入容器
- **入口点**：
  - Python API: `DeepAgentDeps`
- **源文件**：
  - `pydantic_deep/deps.py` (第 18-187 行)
- **相关测试**：
  - `tests/test_agent.py::TestDeepAgentDeps`
- **配置标志**：无（数据类字段）
- **置信度级别**：高
- **依据**：测试 + 实现

### 功能：文件上传跟踪

- **描述**：上传文件到后端并跟踪元数据
- **入口点**：
  - Python API: `deps.upload_file()`
- **源文件**：
  - `pydantic_deep/deps.py` (第 87-147 行)
- **相关测试**：
  - `tests/test_agent.py::TestFileUploads`
- **配置标志**：
  - `upload_dir` (默认: "/uploads")
- **置信度级别**：高
- **依据**：测试 + 实现

## 工具集

### 功能：Todo 工具集

- **描述**：任务规划和跟踪工具 (read_todos, write_todos)
- **入口点**：
  - Python API: 通过 `create_deep_agent()` 中的 `include_todo=True` 包含
- **源文件**：
  - 外部包: `pydantic-ai-todo`
  - 集成: `pydantic_deep/agent.py` (第 203-205 行)
- **相关测试**：
  - `tests/test_toolsets.py` (如果存在)
- **配置标志**：
  - `include_todo` (默认: True)
- **置信度级别**：高
- **依据**：实现 + 外部包测试

### 功能：文件系统工具集

- **描述**：文件操作 (ls, read_file, write_file, edit_file, glob, grep, execute)
- **入口点**：
  - Python API: 通过 `create_deep_agent()` 中的 `include_filesystem=True` 包含
- **源文件**：
  - `pydantic_deep/toolsets/filesystem.py` (第 46-341 行)
- **相关测试**：
  - `tests/test_toolsets.py::TestFilesystemToolset`
- **配置标志**：
  - `include_filesystem` (默认: True)
  - `include_execute` (默认: True, 需要 SandboxProtocol 后端)
  - `require_write_approval` (默认: False)
  - `require_execute_approval` (默认: True)
- **置信度级别**：高
- **依据**：测试 + 实现

### 功能：子代理工具集

- **描述**：任务委托给专门的子代理
- **入口点**：
  - Python API: 通过 `create_deep_agent()` 中的 `include_subagents=True` 包含
  - 工具: `task(description, subagent_type)`
- **源文件**：
  - `pydantic_deep/toolsets/subagents.py` (第 54-199 行)
- **相关测试**：
  - `tests/test_toolsets.py::TestSubAgentToolset`
- **配置标志**：
  - `include_subagents` (默认: True)
  - `include_general_purpose_subagent` (默认: True)
  - `subagents` (SubAgentConfig 列表)
- **置信度级别**：高
- **依据**：测试 + 实现

### 功能：技能工具集

- **描述**：从 Markdown 文件加载和使用模块化技能包
- **入口点**：
  - Python API: 通过 `create_deep_agent()` 中的 `include_skills=True` 包含
  - 工具: `list_skills()`, `load_skill(skill_name)`, `read_skill_resource(skill_name, resource_name)`
- **源文件**：
  - `pydantic_deep/toolsets/skills.py` (第 216-363 行)
- **相关测试**：
  - `tests/test_skills.py`
- **配置标志**：
  - `include_skills` (默认: True)
  - `skill_directories` (SkillDirectory 列表)
  - `skills` (预加载的 Skill 列表)
- **置信度级别**：高
- **依据**：测试 + 实现

## 历史处理

### 功能：摘要处理器

- **描述**：用于令牌管理的自动对话摘要
- **入口点**：
  - Python API: `create_summarization_processor()` 或 `SummarizationProcessor`
- **源文件**：
  - `pydantic_deep/processors/summarization.py` (第 152-484 行)
- **相关测试**：
  - `tests/test_processors.py`
- **配置标志**：
  - `trigger` (ContextSize: messages/tokens/fraction 阈值)
  - `keep` (ContextSize: 保留多少上下文)
  - `max_input_tokens` (基于分数的触发器必需)
  - `token_counter` (自定义令牌计数函数)
  - `summary_prompt` (自定义摘要提示)
- **置信度级别**：高
- **依据**：测试 + 实现

## 后端

### 功能：StateBackend

- **描述**：内存文件存储后端
- **入口点**：
  - Python API: 来自 `pydantic_ai_backends` 的 `StateBackend()`
- **源文件**：
  - 外部包: `pydantic-ai-backend`
- **相关测试**：
  - 外部包测试
- **配置标志**：无
- **置信度级别**：高
- **依据**：外部包实现

### 功能：FilesystemBackend

- **描述**：本地文件系统操作后端
- **入口点**：
  - Python API: 来自 `pydantic_ai_backends` 的 `FilesystemBackend(path)`
- **源文件**：
  - 外部包: `pydantic-ai-backend`
- **相关测试**：
  - 外部包测试
- **配置标志**：
  - `path` (文件系统根目录)
- **置信度级别**：高
- **依据**：外部包实现

### 功能：DockerSandbox

- **描述**：用于代码执行的隔离 Docker 容器
- **入口点**：
  - Python API: 来自 `pydantic_ai_backends` 的 `DockerSandbox()`
- **源文件**：
  - 外部包: `pydantic-ai-backend`
- **相关测试**：
  - 外部包测试
- **配置标志**：
  - `runtime` (RuntimeConfig)
  - `default_runtime` (默认运行时配置)
- **置信度级别**：高
- **依据**：外部包实现

### 功能：SessionManager

- **描述**：每会话 Docker 容器管理，带自动清理
- **入口点**：
  - Python API: 来自 `pydantic_ai_backends` 的 `SessionManager()`
- **源文件**：
  - 外部包: `pydantic-ai-backend`
- **相关测试**：
  - 外部包测试
- **配置标志**：
  - `default_runtime` (RuntimeConfig)
  - `default_idle_timeout` (秒)
- **置信度级别**：高
- **依据**：外部包实现

## 结构化输出

### 功能：类型安全输出

- **描述**：使用 Pydantic 模型返回结构化数据
- **入口点**：
  - Python API: `create_deep_agent(output_type=Model)`
- **源文件**：
  - `pydantic_deep/agent.py` (第 273-281 行)
- **相关测试**：
  - `tests/test_agent.py` (结构化输出测试)
- **配置标志**：
  - `output_type` (OutputSpec 或 Pydantic 模型)
- **置信度级别**：高
- **依据**：测试 + 实现

## 人在回路

### 功能：工具审批工作流

- **描述**：在执行特定工具之前需要人工审批
- **入口点**：
  - Python API: `create_deep_agent(interrupt_on={"execute": True})`
- **源文件**：
  - `pydantic_deep/agent.py` (第 208-225, 271-281 行)
- **相关测试**：
  - `tests/test_agent.py::TestCreateDeepAgent::test_create_with_interrupt_on`
- **配置标志**：
  - `interrupt_on` (工具名称到布尔审批要求的映射字典)
- **置信度级别**：高
- **依据**：测试 + 实现

## 动态系统提示

### 功能：上下文感知指令

- **描述**：基于当前状态的动态系统提示（上传、待办事项、文件、子代理、技能）
- **入口点**：
  - Python API: 通过 `@agent.instructions` 装饰器自动
- **源文件**：
  - `pydantic_deep/agent.py` (第 295-325 行)
- **相关测试**：
  - `tests/test_agent.py` 中的集成测试
- **配置标志**：无（自动）
- **置信度级别**：中
- **依据**：实现

## 示例应用

### 功能：完整应用示例

- **描述**：展示所有功能的完整 FastAPI 应用
- **入口点**：
  - CLI: `cd examples/full_app && uvicorn app:app --reload --port 8080`
  - Web UI: http://localhost:8080
- **源文件**：
  - `examples/full_app/app.py` (1077 行)
  - `examples/full_app/github_tools.py`
  - `examples/full_app/static/` (前端文件)
- **相关测试**：无（仅示例）
- **配置标志**：
  - 环境变量（API 密钥）
  - Docker 可用性（自动检测）
- **置信度级别**：高
- **依据**：实现
