# 快速集成指南

## 在 app.py 中集成记忆系统（3 步）

### 步骤 1: 导入模块

```python
from memory_system import create_memory_toolset
from memory_system.core import MemorySystem
```

### 步骤 2: 创建工具集并添加到 Agent

```python
def create_agent() -> Agent[DeepAgentDeps, str]:
    # 创建记忆工具集
    memory_toolset = create_memory_toolset(
        memory_dir=str(APP_DIR / "memories"),
        template_path=str(APP_DIR / "memory_template.md"),
        id="memory"
    )
    
    # 创建 Agent，包含记忆工具集
    return create_deep_agent(
        model="openai:gpt-4.1",
        instructions=MAIN_INSTRUCTIONS,
        toolsets=[memory_toolset],  # 添加这里
        # ... 其他配置
    )
```

### 步骤 3: 在会话中初始化记忆系统（可选）

```python
@dataclass
class UserSession:
    session_id: str
    deps: DeepAgentDeps
    message_history: list[ModelMessage] = field(default_factory=list)
    memory: MemorySystem = field(init=False)
    
    def __post_init__(self):
        self.memory = MemorySystem(
            user_id=self.session_id,
            memory_dir=str(APP_DIR / "memories")
        )
```

完成！现在 Agent 可以使用记忆工具了。

## Agent 如何使用记忆

Agent 会自动获得以下工具：

- `read_memory(section="all")` - 读取记忆
- `update_preference(category, key, value)` - 更新偏好
- `add_todo(content, priority, due_date)` - 添加待办
- `complete_todo(content)` - 完成待办
- `add_memory(topic, summary)` - 记录记忆
- `learn_habit(habit, category)` - 学习习惯

用户可以直接说：
- "查看我的待办事项"
- "记住我喜欢在早上工作"
- "添加待办：完成项目文档"
- "更新我的偏好：提醒方式改为邮件"

## 独立使用（不依赖 pydantic-deep）

```python
from memory_system import MemorySystem

# 创建记忆系统
memory = MemorySystem(user_id="user123", memory_dir="./memories")

# 使用
memory.add_todo("完成项目")
context = memory.get_context()
```

## 移植到其他框架

记忆系统完全独立，可以轻松移植：

```python
# 在任何框架中使用
from memory_system import MemorySystem

memory = MemorySystem(user_id="user123")

# 读取记忆
context = memory.get_context()

# 更新记忆
memory.add_todo("任务")
```

就这么简单！
