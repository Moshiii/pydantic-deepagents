# 极简记忆系统

一个独立、低依赖的 Markdown 记忆管理系统，可以轻松集成到任何 AI Agent 框架中。

## 特点

- ✅ **零外部依赖**：只使用 Python 标准库
- ✅ **独立使用**：不绑定任何特定框架
- ✅ **易于集成**：提供工具集包装器，方便集成到 pydantic-deep
- ✅ **人类可读**：使用 Markdown 格式，可直接编辑
- ✅ **版本控制友好**：纯文本文件，适合 Git 跟踪

## 快速开始

### 1. 独立使用（不依赖任何框架）

```python
from memory_system import MemorySystem

# 创建记忆系统
memory = MemorySystem(
    user_id="user123",
    memory_dir="./memories"
)

# 读取记忆上下文
context = memory.get_context()
print(context)

# 更新记忆
memory.add_todo("完成项目文档", priority="high", due_date="2024-01-20")
memory.update_preference("提醒方式", "默认提醒方式", "邮件")
memory.learn_habit("喜欢在早上处理重要任务", category="工作习惯")
memory.add_memory("项目讨论", ["用户提到项目需要在月底完成", "需要帮助规划时间"])

# 增加统计
memory.increment_conversation_count()
```

### 2. 集成到 pydantic-deep Agent

```python
from pydantic_deep import create_deep_agent
from memory_system import create_memory_toolset

# 创建记忆工具集
memory_toolset = create_memory_toolset(
    memory_dir="./memories",
    id="memory"
)

# 创建 Agent 时包含记忆工具集
agent = create_deep_agent(
    model="openai:gpt-4.1",
    toolsets=[memory_toolset],
    # ... 其他配置
)

# Agent 现在可以使用记忆工具了
result = await agent.run(
    "查看我的待办事项",
    deps=deps
)
```

### 3. 在 app.py 中集成

```python
# 在 examples/full_app/app.py 中

from memory_system import create_memory_toolset, get_memory_system_prompt
from memory_system.core import MemorySystem

# 创建记忆工具集
memory_toolset = create_memory_toolset(
    memory_dir=str(APP_DIR / "memories"),
    template_path=str(APP_DIR / "memory_template.md")
)

def create_agent() -> Agent[DeepAgentDeps, str]:
    """Create the shared agent with memory system."""
    github_toolset = create_github_toolset(id="github")
    
    return create_deep_agent(
        model="openai:gpt-4.1",
        instructions=MAIN_INSTRUCTIONS.format(github_prompt=GITHUB_SYSTEM_PROMPT),
        toolsets=[github_toolset, memory_toolset],  # 添加记忆工具集
        # ... 其他配置
    )

# 在对话开始时加载记忆上下文
async def run_agent_with_streaming(...):
    # 获取用户记忆
    memory_sys = MemorySystem(
        user_id=session.session_id,
        memory_dir=str(APP_DIR / "memories")
    )
    
    # 获取记忆上下文
    memory_context = memory_sys.get_context()
    
    # 可以注入到系统提示中，或让 Agent 通过工具读取
    # ...
    
    # 对话结束后更新记忆
    memory_sys.increment_conversation_count()
```

## API 文档

### MemorySystem

主类，提供高级接口。

```python
memory = MemorySystem(
    user_id: str,                    # 用户 ID
    memory_dir: str | Path = "./memories",  # 记忆文件目录
    template_path: str | Path = None  # 模板文件路径（可选）
)
```

**方法：**

- `get_memory() -> MemoryData`: 获取完整记忆数据
- `get_context(sections: List[str] = None) -> str`: 获取记忆上下文（用于系统提示）
- `update_preference(category: str, key: str, value: str)`: 更新偏好
- `add_todo(content: str, priority: str = "medium", due_date: str = None)`: 添加待办
- `complete_todo(content: str)`: 完成待办
- `add_memory(topic: str, points: List[str])`: 添加记忆
- `learn_habit(habit: str, category: str = "工作习惯")`: 学习习惯
- `increment_conversation_count()`: 增加对话计数

### 工具集函数

```python
# 创建工具集（用于 pydantic-deep）
toolset = create_memory_toolset(
    memory_dir: str = "./memories",
    template_path: str | None = None,
    id: str | None = "memory"
) -> FunctionToolset

# 创建独立实例（用于其他框架）
memory = create_standalone_memory_system(
    user_id: str,
    memory_dir: str = "./memories",
    template_path: str | None = None
) -> MemorySystem
```

## 文件结构

```
memory_system/
├── __init__.py          # 模块导出
├── core.py              # 核心实现（零依赖）
├── toolset.py           # 工具集包装器
└── README.md            # 本文档
```

## 记忆文件格式

记忆文件使用 Markdown 格式，存储在 `memory_{user_id}.md`。

包含以下章节：
- 📋 基本信息
- ⚙️ 偏好设置
- 📅 日程安排
- ✅ 待办事项
- 🧠 学习到的习惯
- 📝 重要记忆
- 🎯 长期目标
- 📊 统计数据
- 🔗 关联信息

详细格式说明请参考 `memory_template.md`。

## 移植到其他框架

由于这个系统是独立的，可以轻松移植到其他 Agent 框架：

### LangChain

```python
from langchain.tools import Tool
from memory_system import MemorySystem

memory = MemorySystem(user_id="user123")

def read_memory_tool(query: str) -> str:
    return memory.get_context()

tool = Tool(
    name="read_memory",
    func=read_memory_tool,
    description="读取用户记忆"
)
```

### LlamaIndex

```python
from llama_index.tools import FunctionTool
from memory_system import MemorySystem

memory = MemorySystem(user_id="user123")

def read_memory(query: str) -> str:
    return memory.get_context()

tool = FunctionTool.from_defaults(fn=read_memory)
```

### 自定义框架

```python
from memory_system import MemorySystem

class MyAgent:
    def __init__(self, user_id: str):
        self.memory = MemorySystem(user_id=user_id)
    
    def get_context(self):
        return self.memory.get_context()
    
    def update_memory(self, action: str, **kwargs):
        if action == "add_todo":
            self.memory.add_todo(**kwargs)
        # ...
```

## 依赖

**无外部依赖**，只使用 Python 标准库：
- `dataclasses`
- `pathlib`
- `re`
- `datetime`
- `typing`

## 许可证

与主项目相同。
