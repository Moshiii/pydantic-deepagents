# 分门别类的记忆存储结构

## 文件结构

所有记忆文件都存储在 `memories/owner/` 目录下，按类型分类：

```
memories/
  owner/
    profile.md         # 基本信息和偏好设置
    todos.md           # 待办事项（进行中/待开始/已完成）
    diary.md           # 日记和心情记录
    schedule.md        # 日程安排和重要事件
    habits.md          # 学习到的习惯（工作/沟通/生活）
    relationships.md   # 人际关系和常用联系人
    conversations.md   # 最近对话摘要（保留最近50条）
```

## 各文件说明

### profile.md - 个人档案
- **基本信息**：姓名、昵称、时区、语言等
- **偏好设置**：提醒方式、工作习惯、内容偏好等
- **更新方式**：`update_preference()`, `update_profile()`

### todos.md - 待办事项
- **进行中**：当前正在处理的任务
- **待开始**：计划中的任务
- **已完成**：已完成的任务记录
- **更新方式**：`add_todo()`, `complete_todo()`

### diary.md - 日记
- **用途**：记录想法、心情、重要事件
- **格式**：按日期组织的条目
- **更新方式**：`add_diary_entry()`

### schedule.md - 日程安排
- **定期日程**：重复性事件（表格格式）
- **即将到来的事件**：具体日期的事件
- **更新方式**：`add_schedule_event()`

### habits.md - 生活习惯
- **工作习惯**：工作相关的习惯
- **沟通习惯**：沟通相关的习惯
- **生活习惯**：日常生活的习惯
- **更新方式**：`learn_habit()`

### relationships.md - 人际关系
- **常用联系人**：经常联系的人
- **重要关系**：重要的人际关系
- **更新方式**：`add_relationship()`

### conversations.md - 最近对话
- **用途**：记录重要对话的摘要
- **格式**：按日期组织的对话摘要
- **保留策略**：只保留最近50条
- **更新方式**：`add_conversation()` 或 `add_memory()`

## 使用方式

### 在代码中使用

```python
from memory_system import MemorySystem

# 初始化（自动创建 owner/ 目录和所有文件）
memory = MemorySystem(user_id="owner", memory_dir="./memories")

# 添加待办
memory.add_todo("完成项目文档", priority="high", due_date="2024-01-20")

# 学习习惯
memory.learn_habit("喜欢在早上工作", category="工作习惯")

# 记录对话
memory.add_memory("项目讨论", ["用户担心时间不够", "需要拆解任务"])

# 获取上下文（给 Agent 看）
context = memory.get_context()
```

### 手动编辑

所有文件都是 Markdown 格式，你可以直接编辑：

```bash
# 编辑待办事项
vim memories/owner/todos.md

# 编辑日记
vim memories/owner/diary.md

# 查看所有文件
ls -la memories/owner/
```

## 优势

1. **分门别类**：每种类型的记忆都有独立的文件，易于管理
2. **人类可读**：所有文件都是 Markdown，可以直接查看和编辑
3. **易于备份**：整个 `owner/` 目录可以轻松备份和迁移
4. **版本控制友好**：每个文件独立，Git 可以更好地跟踪变更
5. **低依赖**：只使用 Python 标准库，无需数据库

## 迁移旧数据

如果你有旧的 `memory_owner.md` 文件，可以：

1. 手动将内容分类复制到对应的新文件中
2. 或者让 Agent 帮你整理（使用 `read_memory` 读取旧文件，然后分类保存）

## 注意事项

- 所有文件都会自动创建（如果不存在）
- 每次更新会自动更新文件的"最后更新"时间戳
- `conversations.md` 会自动限制为最近50条，避免文件过大
- 所有操作都是追加式的，不会覆盖已有内容（除了更新特定字段）
