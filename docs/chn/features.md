# 功能

pydantic-deep 中所有功能的详细描述。

## 代理创建

### 深度代理工厂

**描述**：创建完全配置的 AI 代理的工厂函数，包含可选工具集、子代理、技能和历史处理器。

**用户可见行为**：
- 创建 `Agent[DeepAgentDeps, OutputT]` 实例
- 自动包含选定的工具集（todo、filesystem、subagents、skills）
- 基于当前状态配置动态系统提示
- 通过 Pydantic 模型支持结构化输出
- 启用在回路中的人工审批工作流

**涉及的内部模块**：
- `pydantic_deep.agent.create_deep_agent()`: 主工厂函数
- `pydantic_deep.toolsets.*`: 工具集创建函数
- `pydantic_ai.Agent`: 来自 pydantic-ai 的基础代理类
- `pydantic_ai_todo.create_todo_toolset()`: 外部 todo 工具集

**错误处理行为**：
- 如果使用基于分数的触发器但未提供 `max_input_tokens`，则抛出 `ValueError`
- 验证上下文大小参数（分数必须在 0-1 之间，计数必须 > 0）
- 如果提供了无效的 model 或 output_type，则出现类型错误

**功能边界**：
- 不实现后端逻辑（委托给 pydantic-ai-backend）
- 不实现 LLM 模型逻辑（委托给 pydantic-ai）
- 不持久化代理状态（无状态工厂）

**置信度级别**：高
**依据**：测试 + 实现

## 依赖注入

### DeepAgentDeps 容器

**描述**：依赖注入容器，保存代理和工具所需的所有运行时状态和资源。

**用户可见行为**：
- 为文件操作提供后端
- 跟踪 TODO 列表状态
- 管理上传的文件元数据
- 存储预编译的子代理实例
- 为当前状态生成系统提示摘要

**涉及的内部模块**：
- `pydantic_deep.deps.DeepAgentDeps`: 主数据类
- `pydantic_ai_backends.BackendProtocol`: 后端接口
- `pydantic_ai_todo.Todo`: Todo 项类型

**错误处理行为**：
- 如果文件上传失败，则抛出 `RuntimeError`
- 优雅地处理编码检测失败（回退到二进制）
- 在上传期间验证文件路径

**功能边界**：
- 不实现后端操作（委托给后端实现）
- 不在进程重启之间持久化状态（仅内存）
- 不管理代理生命周期（无状态容器）

**置信度级别**：高
**依据**：测试 + 实现

### 文件上传跟踪

**描述**：上传文件到后端存储并跟踪元数据（大小、编码、行数、MIME 类型）。

**用户可见行为**：
- 在指定路径将文件内容上传到后端
- 使用 chardet 检测文件编码
- 计算文本文件的行数
- 从文件名推断 MIME 类型
- 在 `deps.uploads` 字典中存储元数据
- 文件可通过 `/uploads/{filename}` 路径访问

**涉及的内部模块**：
- `pydantic_deep.deps.DeepAgentDeps.upload_file()`: 上传方法
- `pydantic_ai_backends.BackendProtocol.write()`: 后端写入操作
- `chardet.detect()`: 编码检测
- `mimetypes.guess_type()`: MIME 类型推断

**错误处理行为**：
- 如果后端写入失败，则抛出 `RuntimeError`
- 优雅地处理 UnicodeDecodeError（标记为二进制）
- 成功时返回路径，失败时抛出异常

**功能边界**：
- 不验证文件内容（接受任何字节）
- 不限制文件大小（取决于后端）
- 不扫描病毒或恶意软件
- 不支持流式上传（将整个文件加载到内存）

**置信度级别**：高
**依据**：测试 + 实现

## 工具集

### Todo 工具集

**描述**：允许代理创建、读取和更新 TODO 列表的任务规划和跟踪工具。

**用户可见行为**：
- `write_todos(todos)`: 创建或更新 TODO 列表
- `read_todos()`: 获取当前 TODO 列表
- Todos 具有状态："pending"、"in_progress"、"completed"
- 系统提示自动包含当前 todos

**涉及的内部模块**：
- 外部包: `pydantic-ai-todo`
- `pydantic_deep.agent.create_deep_agent()`: 集成点
- `pydantic_deep.deps.DeepAgentDeps.todos`: 状态存储

**错误处理行为**：
- 验证 todo 状态值
- 优雅地处理无效的 todo 结构

**功能边界**：
- 不在代理重启之间持久化 todos（仅内存）
- 不提供调度或提醒
- 不支持 todos 之间的依赖关系
- 不提供时间跟踪

**置信度级别**：高
**依据**：外部包测试 + 集成测试

### 文件系统工具集

**描述**：全面的文件操作，包括读取、写入、编辑、搜索和代码执行。

**用户可见行为**：
- `ls(path)`: 列出目录内容
- `read_file(path, offset, limit)`: 带行号读取文件
- `write_file(path, content)`: 创建或覆盖文件
- `edit_file(path, old_string, new_string, replace_all)`: 字符串替换
- `glob(pattern, path)`: 查找匹配模式的文件
- `grep(pattern, path, glob_pattern, output_mode)`: 搜索模式
- `execute(command, timeout)`: 执行 shell 命令（需要 SandboxProtocol）

**涉及的内部模块**：
- `pydantic_deep.toolsets.filesystem.create_filesystem_toolset()`: 工厂
- `pydantic_ai_backends.BackendProtocol`: 后端接口
- `pydantic_ai_backends.SandboxProtocol`: 执行接口

**错误处理行为**：
- 为失败的操作返回错误字符串
- 验证路径（不允许 '..' 或 '~'）
- 优雅地处理文件未找到
- 报告失败命令的退出代码
- 如果输出太长则截断

**功能边界**：
- 不支持文件权限或所有权更改
- 不支持符号链接或硬链接
- 不支持文件监视或事件
- 不支持并发文件访问锁定
- Execute 工具仅在 SandboxProtocol 后端可用

**置信度级别**：高
**依据**：测试 + 实现

### 子代理工具集

**描述**：任务委托系统，允许代理生成专门的子代理以进行自主工作。

**用户可见行为**：
- `task(description, subagent_type)`: 使用任务描述启动子代理
- 子代理具有隔离的上下文（无对话历史）
- 子代理共享文件系统后端
- 子代理返回其工作摘要
- 支持自定义子代理配置
- 包含可选的通用子代理

**涉及的内部模块**：
- `pydantic_deep.toolsets.subagents.create_subagent_toolset()`: 工厂
- `pydantic_deep.deps.DeepAgentDeps.clone_for_subagent()`: 上下文隔离
- `pydantic_ai.Agent`: 子代理实例
- `pydantic_deep.types.SubAgentConfig`: 配置类型

**错误处理行为**：
- 如果未找到子代理类型，则返回错误消息
- 捕获并报告子代理执行异常
- 优雅地处理缺失的子代理配置

**功能边界**：
- 不支持嵌套子代理委托（子代理不能生成子代理）
- 不支持子代理到子代理的通信
- 不在调用之间持久化子代理状态
- 不支持子代理取消或超时
- 不支持并行子代理执行

**置信度级别**：高
**依据**：测试 + 实现

### 技能工具集

**描述**：从 Markdown 文件加载指令和资源的模块化技能系统。

**用户可见行为**：
- `list_skills()`: 显示带元数据的可用技能
- `load_skill(skill_name)`: 加载完整技能指令
- `read_skill_resource(skill_name, resource_name)`: 读取技能资源文件
- 从包含 SKILL.md 文件的目录中发现技能
- 渐进式披露：首先加载 frontmatter，按需加载完整指令

**涉及的内部模块**：
- `pydantic_deep.toolsets.skills.create_skills_toolset()`: 工厂
- `pydantic_deep.toolsets.skills.discover_skills()`: 发现函数
- `pydantic_deep.toolsets.skills.parse_skill_md()`: Markdown 解析器
- `pydantic_deep.types.Skill`: 技能类型定义

**错误处理行为**：
- 如果未找到技能，则返回错误消息
- 优雅地处理无效的 SKILL.md 文件（跳过）
- 验证资源路径以防止目录遍历
- 如果未找到资源文件，则返回错误

**功能边界**：
- 不支持技能版本控制或更新
- 不支持技能依赖关系
- 不支持技能执行或沙箱化
- 不支持技能市场或分发
- 不验证技能指令语法

**置信度级别**：高
**依据**：测试 + 实现

## 历史处理

### 摘要处理器

**描述**：自动对话摘要，用于管理长时间运行会话中的令牌限制。

**用户可见行为**：
- 监控消息令牌计数
- 达到阈值时触发摘要
- 保留最近的消息（可配置）
- 用摘要替换旧消息
- 维护工具调用/响应对（安全截止点）

**涉及的内部模块**：
- `pydantic_deep.processors.summarization.SummarizationProcessor`: 主类
- `pydantic_deep.processors.summarization.create_summarization_processor()`: 工厂
- `pydantic_ai.Agent`: 摘要代理
- `pydantic_ai.messages.ModelMessage`: 消息类型

**错误处理行为**：
- 如果摘要失败，则回退到错误消息
- 优雅地处理令牌计数错误
- 验证 trigger 和 keep 参数
- 对于无效配置抛出 ValueError

**功能边界**：
- 不支持每个代理的自定义摘要模型
- 不支持增量摘要（完全替换）
- 不支持仅对工具结果进行摘要
- 不支持多种摘要策略
- 令牌计数是近似的（基于字符的启发式）

**置信度级别**：高
**依据**：测试 + 实现

## 结构化输出

### 类型安全输出

**描述**：使用 Pydantic 模型返回结构化数据，而不是纯字符串。

**用户可见行为**：
- 代理输出是经过验证的 Pydantic 模型实例
- 如果模型验证失败，则在运行时出现类型错误
- 支持 Pydantic 模型、数据类、TypedDict
- 可以与 DeferredToolRequests 结合用于审批工作流

**涉及的内部模块**：
- `pydantic_deep.agent.create_deep_agent()`: 输出类型配置
- `pydantic_ai.output.OutputSpec`: 输出规范
- `pydantic.BaseModel`: Pydantic 模型基类

**错误处理行为**：
- 如果输出与模型不匹配，则抛出验证错误
- 如果提供了无效的 output_type，则出现类型错误

**功能边界**：
- 不支持流式结构化输出
- 不支持部分模型验证
- 不支持超出 Pydantic 的自定义验证逻辑
- 不支持多种输出类型（单一类型或联合）

**置信度级别**：高
**依据**：测试 + 实现

## 人在回路

### 工具审批工作流

**描述**：在执行特定工具之前需要人工审批（例如，execute、write_file）。

**用户可见行为**：
- 需要审批时，代理返回 `DeferredToolRequests`
- 前端接收带有工具名称和参数的审批请求
- 用户批准/拒绝每个请求
- 代理仅继续使用已批准的工具
- 被拒绝的工具被跳过

**涉及的内部模块**：
- `pydantic_deep.agent.create_deep_agent()`: 中断配置
- `pydantic_ai.tools.DeferredToolRequests`: 审批请求类型
- `pydantic_ai.tools.DeferredToolResults`: 审批响应类型
- `pydantic_ai.tools.ToolApproved`: 审批标记

**错误处理行为**：
- 被拒绝的工具向代理返回错误
- 代理可以使用不同方法重试
- 审批无超时（无限期等待）

**功能边界**：
- 不支持审批超时
- 不支持批量审批（每个工具调用一个请求）
- 不支持条件审批（如果满足条件则批准）
- 不支持审批委托
- 不持久化审批历史

**置信度级别**：高
**依据**：测试 + 实现

## 动态系统提示

### 上下文感知指令

**描述**：基于当前代理状态自动生成系统提示部分。

**用户可见行为**：
- 系统提示包含上传文件摘要
- 系统提示包含当前 TODO 列表
- 系统提示包含文件系统状态
- 系统提示包含可用子代理
- 系统提示包含可用技能
- 随着状态变化动态更新

**涉及的内部模块**：
- `pydantic_deep.agent.create_deep_agent()`: 动态指令装饰器
- `pydantic_deep.deps.DeepAgentDeps.get_uploads_summary()`: 上传摘要
- `pydantic_ai_todo.get_todo_system_prompt()`: Todo 摘要
- `pydantic_deep.toolsets.*.get_*_system_prompt()`: 工具集摘要

**错误处理行为**：
- 优雅地处理缺失状态（空摘要）
- 如果状态为空，则无错误

**功能边界**：
- 不支持自定义提示模板
- 不支持提示版本控制
- 不支持条件提示部分
- 不缓存提示生成

**置信度级别**：中
**依据**：实现（有限的测试覆盖）
