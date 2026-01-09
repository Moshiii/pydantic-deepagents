# 记忆系统工作流程详解

## 概述

本文档详细解释记忆系统在 `app.py` 中的工作流程，包括：
1. 如何监控用户输入
2. 更新频率
3. 何时引用记忆库

## 当前状态

**重要：** 当前 `app.py` **还没有集成记忆系统**。以下说明的是集成后的工作流程。

## 一、用户输入监控机制

### 1.1 输入接收流程

```
用户发送消息
    ↓
WebSocket 接收 (app.py:392)
    ↓
解析 JSON: {"session_id": "xxx", "message": "..."}
    ↓
调用 run_agent_with_streaming() (app.py:429)
    ↓
Agent 处理消息
```

**代码位置：** `app.py:358-427` (websocket_chat 函数)

```python
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    # 接收用户消息
    data = await websocket.receive_text()
    message_data = json.loads(data)
    
    user_message = message_data.get("message", "")
    session_id = message_data.get("session_id")
    
    # 调用 Agent 处理
    await run_agent_with_streaming(websocket, session, user_message)
```

### 1.2 记忆系统如何"监控"输入

**记忆系统不主动监控输入**，而是通过以下两种方式工作：

#### 方式 A：Agent 主动调用工具（推荐）

Agent 在理解用户意图后，**主动决定**是否需要：
- 读取记忆（`read_memory`）
- 更新记忆（`update_preference`, `add_todo`, `learn_habit` 等）

**工作流程：**
```
用户输入："我喜欢在早上工作"
    ↓
Agent 理解意图：用户表达偏好
    ↓
Agent 决定调用工具：learn_habit("喜欢在早上工作", "工作习惯")
    ↓
工具执行：更新记忆文件
    ↓
Agent 继续处理并回复
```

#### 方式 B：在系统提示中预加载（可选）

在对话开始前，将记忆上下文注入到系统提示中：

```python
async def run_agent_with_streaming(...):
    # 对话开始前
    memory_sys = MemorySystem(user_id=session.session_id)
    memory_context = memory_sys.get_context()
    
    # 注入到系统提示（需要修改 Agent 创建方式）
    enhanced_instructions = f"{MAIN_INSTRUCTIONS}\n\n{memory_context}"
```

## 二、记忆更新频率

### 2.1 更新时机

记忆系统**不是定时更新**，而是**事件驱动**的：

| 事件 | 更新时机 | 更新内容 |
|------|---------|---------|
| Agent 调用 `add_todo` | 立即 | 添加待办事项 |
| Agent 调用 `update_preference` | 立即 | 更新偏好设置 |
| Agent 调用 `learn_habit` | 立即 | 学习新习惯 |
| Agent 调用 `add_memory` | 立即 | 记录重要记忆 |
| 对话结束 | 可选 | 增加对话计数、保存摘要 |

### 2.2 具体更新流程

**代码位置：** `app.py:429-509` (run_agent_with_streaming)

```python
async def run_agent_with_streaming(...):
    # 1. Agent 运行（可能调用记忆工具）
    async with agent.iter(...) as run:
        async for node in run:
            # 如果 Agent 调用记忆工具，工具会立即更新文件
            await process_node(websocket, node, run, session)
    
    # 2. 对话结束后（可选）
    # 可以在这里添加记忆更新逻辑
    if result.output:
        # 增加对话计数
        # memory_sys.increment_conversation_count()
        
        # 可选：自动提取并保存重要记忆
        # memory_sys.add_memory(...)
```

### 2.3 更新频率总结

- **实时更新**：当 Agent 调用记忆工具时，立即写入文件
- **无定时任务**：不依赖后台定时任务
- **按需更新**：只在需要时更新，不浪费资源

## 三、何时引用记忆库

### 3.1 引用时机

记忆库在以下情况下被引用：

#### 情况 1：Agent 主动读取（最常见）

Agent 根据用户问题，决定是否需要读取记忆：

```
用户："查看我的待办事项"
    ↓
Agent 理解：需要读取待办
    ↓
Agent 调用：read_memory(section="todos")
    ↓
返回：当前待办列表
    ↓
Agent 回复用户
```

**触发条件：**
- 用户明确询问（"我的待办"、"我的偏好"）
- Agent 需要个性化信息（"根据我的习惯..."）
- Agent 需要上下文信息

#### 情况 2：对话开始时预加载（可选）

在每次对话开始前，自动加载记忆上下文：

```python
async def run_agent_with_streaming(...):
    # 对话开始前加载记忆
    memory_sys = MemorySystem(user_id=session.session_id)
    memory_context = memory_sys.get_context()
    
    # 方式 A：注入到系统提示（需要修改 Agent）
    # 方式 B：让 Agent 在需要时调用 read_memory
```

#### 情况 3：对话结束后保存（可选）

在对话结束后，自动提取并保存重要信息：

```python
async def run_agent_with_streaming(...):
    # ... Agent 运行 ...
    
    # 对话结束后
    if result.output:
        # 分析对话，提取重要信息
        # 自动保存到记忆库
        memory_sys.add_memory(...)
```

### 3.2 引用场景示例

| 用户输入 | Agent 行为 | 记忆操作 |
|---------|-----------|---------|
| "查看我的待办" | 调用 `read_memory(section="todos")` | 读取 |
| "我喜欢早上工作" | 调用 `learn_habit("早上工作", "工作习惯")` | 写入 |
| "添加待办：完成项目" | 调用 `add_todo("完成项目")` | 写入 |
| "我的偏好是什么？" | 调用 `read_memory(section="preferences")` | 读取 |
| "记住我每天8点喝咖啡" | 调用 `update_preference(...)` 或 `learn_habit(...)` | 写入 |
| "帮我写代码" | 可能调用 `read_memory()` 了解用户习惯 | 读取 |

## 四、完整工作流程示例

### 4.1 场景：用户首次对话

```
1. 用户连接 WebSocket
   ↓
2. 创建会话 (get_or_create_session)
   ↓
3. 用户发送："你好，我是张三"
   ↓
4. Agent 运行：
   - 理解：用户自我介绍
   - 决定：需要记录基本信息
   - 调用：update_preference("基本信息", "姓名", "张三")
   - 工具执行：更新 memory_user123.md
   ↓
5. Agent 回复："你好张三，已记住你的名字"
   ↓
6. 对话结束，更新 message_history
```

### 4.2 场景：用户查询记忆

```
1. 用户发送："查看我的待办事项"
   ↓
2. Agent 运行：
   - 理解：需要读取待办
   - 调用：read_memory(section="todos")
   - 工具执行：读取 memory_user123.md，解析待办章节
   - 返回：待办列表
   ↓
3. Agent 回复："你的待办事项：1. 完成项目..."
   ↓
4. 对话结束
```

### 4.3 场景：Agent 自动学习

```
1. 用户发送："我通常早上9点开始工作"
   ↓
2. Agent 运行：
   - 理解：用户表达工作习惯
   - 决定：需要学习这个习惯
   - 调用：learn_habit("早上9点开始工作", "工作习惯")
   - 工具执行：更新 memory_user123.md
   ↓
3. Agent 回复："已记住你的工作习惯"
   ↓
4. 下次对话：
   - 用户："提醒我明天开会"
   - Agent 可以调用 read_memory() 了解用户习惯
   - Agent 知道用户9点开始工作，可以智能安排提醒时间
```

## 五、集成后的代码结构

### 5.1 修改 create_agent()

```python
def create_agent() -> Agent[DeepAgentDeps, str]:
    from memory_system import create_memory_toolset
    
    # 创建记忆工具集
    memory_toolset = create_memory_toolset(
        memory_dir=str(APP_DIR / "memories"),
        id="memory"
    )
    
    return create_deep_agent(
        model="openai:gpt-4.1",
        instructions=MAIN_INSTRUCTIONS,
        toolsets=[github_toolset, memory_toolset],  # 添加记忆工具集
        # ... 其他配置
    )
```

### 5.2 修改 run_agent_with_streaming()（可选增强）

```python
async def run_agent_with_streaming(...):
    from memory_system.core import MemorySystem
    
    # 可选：在对话开始前加载记忆上下文
    memory_sys = MemorySystem(
        user_id=session.session_id,
        memory_dir=str(APP_DIR / "memories")
    )
    
    # Agent 运行（Agent 会自己决定是否调用记忆工具）
    async with agent.iter(...) as run:
        # ... 处理节点 ...
    
    # 可选：对话结束后更新统计
    memory_sys.increment_conversation_count()
    
    # 可选：自动提取并保存重要记忆
    # if is_important_conversation(result):
    #     memory_sys.add_memory(...)
```

## 六、关键点总结

### 6.1 监控机制

❌ **不是主动监控**：记忆系统不监听所有用户输入
✅ **被动响应**：Agent 根据意图决定是否使用记忆工具
✅ **工具驱动**：通过工具调用触发记忆操作

### 6.2 更新频率

- **实时更新**：工具调用时立即写入
- **事件驱动**：不依赖定时任务
- **按需更新**：只在需要时更新

### 6.3 引用时机

1. **Agent 主动调用**：最常见，根据用户意图决定
2. **对话开始预加载**：可选，提前注入上下文
3. **对话结束保存**：可选，自动提取重要信息

### 6.4 设计优势

- ✅ **低耦合**：记忆系统独立，不影响现有流程
- ✅ **灵活性**：Agent 自主决定何时使用记忆
- ✅ **可扩展**：可以添加自动学习、自动摘要等功能
- ✅ **透明性**：所有操作通过工具调用，易于追踪

## 七、实际运行示例

### 7.1 日志输出示例

```
[14:30:00] === Starting agent run for session user123 ===
[14:30:00] User message: 查看我的待办事项
[14:30:01]   -> CallToolsNode: Agent 决定调用工具
[14:30:01]   TOOL CALL: read_memory(section="todos")
[14:30:01]   TOOL RESULT: 返回待办列表
[14:30:02] Agent finished after 3 nodes
[14:30:02] === Agent run complete ===
```

### 7.2 记忆文件变化

**调用前：**
```markdown
## ✅ 待办事项
### 进行中
- [ ] 完成项目文档
```

**调用后：**（如果 Agent 更新了待办）
```markdown
## ✅ 待办事项
### 进行中
- [ ] 完成项目文档
- [ ] 准备会议材料（优先级：高，截止：2024-01-20）
```

## 八、常见问题

### Q1: 记忆系统会监听所有用户输入吗？
**A:** 不会。记忆系统是被动的，只在 Agent 调用工具时工作。

### Q2: 更新是实时的吗？
**A:** 是的。当 Agent 调用记忆工具时，立即写入文件。

### Q3: 如何确保记忆被正确使用？
**A:** 通过系统提示指导 Agent 使用记忆工具，Agent 会根据用户意图自主决定。

### Q4: 可以添加自动学习功能吗？
**A:** 可以。在对话结束后分析对话内容，自动提取并保存重要信息。

### Q5: 记忆系统会影响性能吗？
**A:** 影响很小。文件读写操作很快，且只在工具调用时执行。

---

**总结：** 记忆系统是一个**工具驱动的被动系统**，不主动监控，不定时更新，只在 Agent 需要时通过工具调用工作。这种设计既灵活又高效。
