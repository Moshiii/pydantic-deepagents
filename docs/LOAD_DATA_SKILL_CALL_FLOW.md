# "Load Data Skill" 按钮完整调用链路分析

本文档详细解释了点击 "Load Data Skill" 按钮后的完整调用链路。

## 📍 调用链路概览

```
前端按钮点击
  ↓
React 组件处理
  ↓
WebSocket 消息发送
  ↓
后端 WebSocket 端点接收
  ↓
Agent 执行流程
  ↓
工具调用 (load_skill)
  ↓
返回 Skill 指令
  ↓
前端显示结果
```

---

## 🔍 详细调用链路

### 1️⃣ 前端：按钮点击事件

**文件**: `examples/full_app/static/src/components/ChatPanel.jsx`

**位置**: 第 251-257 行

```jsx
<button
  onClick={() => sendQuickMessage('Load the data-analysis skill')}
  className="bg-transparent border border-border-subtle ..."
>
  <i className="ri-database-2-line text-sm"></i>
  Load Data Skill
</button>
```

**说明**: 
- 点击按钮时，调用 `sendQuickMessage('Load the data-analysis skill')`
- 这个函数会将消息设置到输入框，然后自动发送

---

### 2️⃣ 前端：sendQuickMessage 函数

**文件**: `examples/full_app/static/src/components/ChatPanel.jsx`

**位置**: 第 218-221 行

```javascript
const sendQuickMessage = (message) => {
  setInputValue(message);
  setTimeout(() => sendMessage(), 0);
};
```

**说明**:
- 将消息 `'Load the data-analysis skill'` 设置到 `inputValue` 状态
- 使用 `setTimeout` 确保状态更新后立即调用 `sendMessage()`

---

### 3️⃣ 前端：sendMessage 函数

**文件**: `examples/full_app/static/src/components/ChatPanel.jsx`

**位置**: 第 188-203 行

```javascript
const sendMessage = () => {
  const message = inputValue.trim();
  if (!message || !isConnected) return;

  setInputValue('');
  setMessages(prev => [...prev, {
    type: 'user',
    content: message,
  }]);

  const payload = { message };
  if (sessionId) {
    payload.session_id = sessionId;
  }
  sendWebSocket(payload);
};
```

**说明**:
- 检查消息是否为空和 WebSocket 是否已连接
- 清空输入框
- 将用户消息添加到消息列表（显示在界面上）
- 构建 WebSocket 消息负载：`{ message: 'Load the data-analysis skill', session_id: 'xxx' }`
- 通过 `sendWebSocket` 发送消息

---

### 4️⃣ 前端：WebSocket 发送

**文件**: `examples/full_app/static/src/hooks/useWebSocket.js`

**位置**: 第 50-56 行

```javascript
const send = useCallback((message) => {
  if (wsRef.current?.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify(message));
  } else {
    console.warn('WebSocket is not connected');
  }
}, []);
```

**说明**:
- 检查 WebSocket 连接状态
- 将消息对象序列化为 JSON 字符串
- 通过 WebSocket 发送到后端 `/ws/chat` 端点

**发送的数据**:
```json
{
  "message": "Load the data-analysis skill",
  "session_id": "abc-123-def-456"
}
```

---

### 5️⃣ 后端：WebSocket 端点接收

**文件**: `examples/full_app/app.py`

**位置**: 第 598-667 行

```python
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    # ... 省略初始化代码 ...
    
    while True:
        data = await websocket.receive_text()
        message_data = json.loads(data)
        
        session_id = message_data.get("session_id")
        user_message = message_data.get("message", "")
        
        # 获取或创建会话
        if session is None:
            session = await get_or_create_session(session_id)
        
        # 运行 Agent
        await run_agent_with_streaming(websocket, session, user_message)
```

**说明**:
- 接收 WebSocket 消息
- 解析 JSON 数据
- 获取或创建用户会话（每个会话有独立的 Docker 容器和消息历史）
- 调用 `run_agent_with_streaming` 开始 Agent 执行

---

### 6️⃣ 后端：Agent 执行流程

**文件**: `examples/full_app/app.py`

**位置**: 第 669-763 行

```python
async def run_agent_with_streaming(
    websocket: WebSocket,
    session: UserSession,
    user_message: str,
    deferred_results: DeferredToolResults | None = None,
) -> None:
    # 发送开始事件
    await websocket.send_json({"type": "start"})
    
    # 使用 agent.iter() 进行流式执行
    async with agent.iter(
        user_message,
        deps=session.deps,
        message_history=session.message_history,
        deferred_tool_results=deferred_results,
    ) as run:
        async for node in run:
            await process_node(websocket, node, run, session)
    
    # 获取最终结果
    result = run.result
```

**说明**:
- 发送 `{"type": "start"}` 事件到前端，通知 Agent 开始执行
- 使用 `agent.iter()` 进行流式执行，逐个处理节点
- 每个节点可能是：
  - `UserPromptNode`: 用户提示节点
  - `ModelRequestNode`: 模型请求节点（LLM 生成响应）
  - `CallToolsNode`: 工具调用节点（调用工具）
  - `End`: 结束节点

---

### 7️⃣ 后端：处理节点 - ModelRequestNode

**文件**: `examples/full_app/app.py`

**位置**: 第 799-842 行

```python
async def _stream_model_request(websocket: WebSocket, node: Any, run: Any) -> None:
    """Stream text chunks from a ModelRequestNode."""
    await websocket.send_json({"type": "status", "content": "Generating response..."})
    
    async with node.stream(run.ctx) as request_stream:
        async for event in request_stream:
            if isinstance(event, PartStartEvent):
                # 工具调用开始
                if hasattr(event.part, "tool_name"):
                    await websocket.send_json({
                        "type": "tool_call_start",
                        "tool_name": event.part.tool_name,
                        "tool_call_id": event.part.tool_call_id,
                    })
            elif isinstance(event, PartDeltaEvent):
                # 流式文本或工具参数
                await _handle_part_delta(websocket, event, current_tool_name)
```

**说明**:
- Agent 分析用户消息 "Load the data-analysis skill"
- LLM 决定调用 `load_skill` 工具
- 发送 `tool_call_start` 事件，通知前端开始工具调用
- 流式发送工具参数（`tool_args_delta`）

**前端接收的事件**:
```json
{"type": "tool_call_start", "tool_name": "load_skill", "tool_call_id": "call_123"}
{"type": "tool_args_delta", "tool_name": "load_skill", "args_delta": "{\"skill_name\":\""}
{"type": "tool_args_delta", "tool_name": "load_skill", "args_delta": "data-analysis"}
{"type": "tool_args_delta", "tool_name": "load_skill", "args_delta": "\"}"}
```

---

### 8️⃣ 后端：处理节点 - CallToolsNode

**文件**: `examples/full_app/app.py`

**位置**: 第 864-903 行

```python
async def _stream_tool_calls(
    websocket: WebSocket, node: Any, run: Any, session: UserSession
) -> None:
    async with node.stream(run.ctx) as handle_stream:
        async for event in handle_stream:
            if isinstance(event, FunctionToolCallEvent):
                # 工具调用开始
                tool_name = event.part.tool_name
                tool_args = event.part.args
                await websocket.send_json({
                    "type": "tool_start",
                    "tool_name": tool_name,
                    "args": tool_args,
                })
            
            elif isinstance(event, FunctionToolResultEvent):
                # 工具执行结果
                result_content = event.result.content
                await websocket.send_json({
                    "type": "tool_output",
                    "tool_name": tool_name,
                    "output": str(result_content),
                })
```

**说明**:
- 发送 `tool_start` 事件，包含完整的工具参数
- 实际执行工具函数 `load_skill(skill_name="data-analysis")`
- 发送 `tool_output` 事件，包含工具返回的结果

**前端接收的事件**:
```json
{"type": "tool_start", "tool_name": "load_skill", "args": {"skill_name": "data-analysis"}}
{"type": "tool_output", "tool_name": "load_skill", "output": "# Skill: data-analysis\n..."}
```

---

### 9️⃣ 后端：工具执行 - load_skill

**文件**: `pydantic_deep/toolsets/skills.py`

**位置**: 第 273-322 行

```python
@toolset.tool
async def load_skill(
    ctx: RunContext[DeepAgentDeps],
    skill_name: str,
) -> str:
    """Load full instructions for a skill."""
    if skill_name not in _skills_cache:
        available = ", ".join(_skills_cache.keys())
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"
    
    skill = _skills_cache[skill_name]
    instructions = load_skill_instructions(skill["path"])
    
    # 更新缓存
    skill["instructions"] = instructions
    skill["frontmatter_loaded"] = False
    
    # 格式化返回结果
    lines = [
        f"# Skill: {skill['name']}",
        f"Version: {skill['version']}",
        f"Path: {skill['path']}",
        "",
        "## Instructions",
        "",
        instructions,
    ]
    
    return "\n".join(lines)
```

**说明**:
- 检查 skill 是否存在于缓存中（`_skills_cache`）
- 调用 `load_skill_instructions()` 从文件系统读取完整的 SKILL.md 内容
- 解析 YAML frontmatter 和 Markdown 指令
- 格式化返回结果，包含 skill 的完整信息

**实际执行的代码路径**:
1. `load_skill_instructions(skill["path"])` → 读取 `examples/full_app/skills/data-analysis/SKILL.md`
2. `parse_skill_md(content)` → 解析 YAML frontmatter 和 Markdown 内容
3. 返回完整的 skill 指令（包含数据分析和可视化的详细指南）

---

### 🔟 后端：读取 Skill 文件

**文件**: `pydantic_deep/toolsets/skills.py`

**位置**: 第 158-175 行

```python
def load_skill_instructions(skill_path: str) -> str:
    """Load full instructions for a skill."""
    skill_file = Path(skill_path) / "SKILL.md"
    
    if not skill_file.exists():
        return f"Error: SKILL.md not found at {skill_path}"
    
    content = skill_file.read_text()
    _, instructions = parse_skill_md(content)
    
    return instructions
```

**说明**:
- 读取 `examples/full_app/skills/data-analysis/SKILL.md` 文件
- 解析文件内容，分离 YAML frontmatter 和 Markdown 指令
- 返回纯 Markdown 指令部分（不包含 frontmatter）

**实际文件内容**:
- 文件路径: `examples/full_app/skills/data-analysis/SKILL.md`
- 包含数据分析和可视化的完整指南（226 行）
- 包括代码模板、最佳实践、输出格式等

---

### 1️⃣1️⃣ 后端：Agent 继续处理

**文件**: `examples/full_app/app.py`

**位置**: 第 669-763 行

```python
# Agent 收到工具返回结果后，继续处理
# LLM 会分析返回的 skill 指令，并生成响应给用户

# 发送最终响应
await websocket.send_json({
    "type": "response",
    "content": str(result.output),
})

# 发送完成事件
await websocket.send_json({"type": "done"})
```

**说明**:
- Agent 收到 `load_skill` 的返回结果（完整的 skill 指令）
- LLM 分析这些指令，理解如何使用 data-analysis skill
- 生成响应，告知用户 skill 已加载，并简要说明如何使用
- 发送 `response` 事件（最终文本响应）
- 发送 `done` 事件（执行完成）

---

### 1️⃣2️⃣ 前端：接收并显示结果

**文件**: `examples/full_app/static/src/components/ChatPanel.jsx`

**位置**: 第 27-164 行（handleWebSocketMessage 函数）

```javascript
const handleWebSocketMessage = useCallback((data) => {
  switch (data.type) {
    case 'start':
      // 创建新的 assistant 消息
      currentMessageRef.current = {
        type: 'assistant',
        content: '',
        tools: [],
      };
      setMessages(prev => [...prev, currentMessageRef.current]);
      break;
    
    case 'tool_call_start':
      // 添加工具调用到消息
      const streamingTool = {
        name: data.tool_name,
        tool_call_id: data.tool_call_id,
        status: 'streaming',
        args: '',
      };
      currentMessageRef.current.tools.push(streamingTool);
      setMessages(prev => [...prev]);
      break;
    
    case 'tool_start':
      // 更新工具状态为运行中
      currentToolsRef.current.status = 'running';
      currentToolsRef.current.args = data.args;
      setMessages(prev => [...prev]);
      break;
    
    case 'tool_output':
      // 显示工具输出
      currentToolsRef.current.output = data.output;
      currentToolsRef.current.status = 'done';
      setMessages(prev => [...prev]);
      break;
    
    case 'text_delta':
      // 流式显示文本
      streamedTextRef.current += data.content;
      currentMessageRef.current.content = streamedTextRef.current;
      setMessages(prev => [...prev]);
      break;
    
    case 'response':
      // 最终响应
      currentMessageRef.current.content = data.content;
      setMessages(prev => [...prev]);
      break;
    
    case 'done':
      // 完成
      currentMessageRef.current = null;
      currentToolsRef.current = null;
      break;
  }
}, [sessionId]);
```

**说明**:
- 根据事件类型更新 UI
- `tool_start`: 显示工具调用卡片，显示工具名称和参数
- `tool_output`: 显示工具返回的结果（完整的 skill 指令）
- `text_delta`: 流式显示 Agent 的文本响应
- `response`: 显示最终响应
- `done`: 标记消息完成

---

## 📊 完整数据流图

```
┌─────────────────────────────────────────────────────────────┐
│  前端: ChatPanel.jsx                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. 用户点击按钮                                        │  │
│  │    onClick={() => sendQuickMessage('Load...')}        │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2. sendQuickMessage()                                  │  │
│  │    setInputValue(message)                              │  │
│  │    setTimeout(() => sendMessage(), 0)                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 3. sendMessage()                                       │  │
│  │    - 添加到消息列表                                    │  │
│  │    - sendWebSocket({message, session_id})             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket
                          ↓ JSON: {"message": "Load...", "session_id": "xxx"}
┌─────────────────────────────────────────────────────────────┐
│  后端: app.py                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 4. websocket_chat()                                   │  │
│  │    - 接收消息                                          │  │
│  │    - 获取/创建会话                                     │  │
│  │    - run_agent_with_streaming()                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 5. run_agent_with_streaming()                       │  │
│  │    - agent.iter(user_message, ...)                   │  │
│  │    - 流式处理节点                                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 6. process_node()                                     │  │
│  │    - ModelRequestNode → _stream_model_request()       │  │
│  │    - CallToolsNode → _stream_tool_calls()             │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 7. LLM 决定调用 load_skill("data-analysis")          │  │
│  │    - 发送 tool_call_start                            │  │
│  │    - 发送 tool_args_delta (流式参数)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 8. _stream_tool_calls()                               │  │
│  │    - 发送 tool_start                                  │  │
│  │    - 执行 load_skill()                                │  │
│  │    - 发送 tool_output                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 9. load_skill() (pydantic_deep/toolsets/skills.py)   │  │
│  │    - 检查 _skills_cache                              │  │
│  │    - load_skill_instructions()                       │  │
│  │    - 读取 SKILL.md 文件                              │  │
│  │    - 返回完整指令                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 10. Agent 生成最终响应                                │  │
│  │     - 发送 response 事件                              │  │
│  │     - 发送 done 事件                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket Events
                          ↓ {"type": "tool_output", ...}
                          ↓ {"type": "text_delta", ...}
                          ↓ {"type": "response", ...}
                          ↓ {"type": "done"}
┌─────────────────────────────────────────────────────────────┐
│  前端: ChatPanel.jsx                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 11. handleWebSocketMessage()                         │  │
│  │     - 更新消息状态                                    │  │
│  │     - 显示工具调用和结果                              │  │
│  │     - 流式显示文本                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 12. UI 更新                                           │  │
│  │     - 显示工具调用卡片                                │  │
│  │     - 显示 skill 指令内容                            │  │
│  │     - 显示 Agent 响应                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 关键概念解释

### Skills 系统

**Skills** 是模块化的能力包，用于扩展 Agent 的功能。每个 Skill 包含：

1. **SKILL.md**: 定义文件，包含：
   - YAML frontmatter（元数据：名称、描述、版本等）
   - Markdown 指令（详细的使用指南）

2. **资源文件**（可选）: 模板、脚本、文档等

### 渐进式披露（Progressive Disclosure）

Skills 系统使用渐进式披露来优化 token 使用：

1. **发现阶段**（低成本）:
   - 只加载 YAML frontmatter
   - Agent 调用 `list_skills()` 查看可用技能

2. **加载阶段**（按需）:
   - 当需要时，Agent 调用 `load_skill(skill_name)`
   - 加载完整的 SKILL.md 内容

3. **资源阶段**（按需）:
   - 如果需要，Agent 调用 `read_skill_resource()` 读取特定资源文件

### WebSocket 流式通信

整个系统使用 WebSocket 进行实时双向通信：

- **前端 → 后端**: 发送用户消息
- **后端 → 前端**: 流式发送事件：
  - `start`: Agent 开始执行
  - `tool_call_start`: 工具调用开始
  - `tool_args_delta`: 工具参数流式更新
  - `tool_start`: 工具开始执行
  - `tool_output`: 工具执行结果
  - `text_delta`: Agent 文本流式输出
  - `response`: 最终响应
  - `done`: 执行完成

### Agent 执行流程

Agent 使用图执行模型：

1. **UserPromptNode**: 处理用户输入
2. **ModelRequestNode**: LLM 生成响应（可能包含工具调用）
3. **CallToolsNode**: 执行工具调用
4. **End**: 结束节点

每个节点都可以流式处理，实现实时反馈。

---

## 📝 总结

点击 "Load Data Skill" 按钮后：

1. **前端**: 按钮点击 → 发送 WebSocket 消息
2. **后端**: 接收消息 → Agent 分析 → 决定调用 `load_skill` 工具
3. **工具执行**: 读取 `SKILL.md` 文件 → 返回完整指令
4. **Agent 响应**: 生成响应，告知用户 skill 已加载
5. **前端显示**: 流式显示工具调用过程和最终结果

整个过程是**异步流式**的，用户可以实时看到：
- 工具调用开始
- 工具参数
- 工具执行结果（完整的 skill 指令）
- Agent 的文本响应

这种设计提供了良好的用户体验，让用户能够清楚地了解 Agent 正在做什么。
