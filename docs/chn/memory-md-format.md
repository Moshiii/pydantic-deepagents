# 极简记忆系统：Markdown 格式设计

## 一、设计理念

使用单个 Markdown 文件存储用户的所有记忆信息，包括：
- 基本信息
- 偏好设置
- 日程安排
- 待办事项
- 历史对话摘要
- 重要事件
- 学习到的习惯

**优点：**
- ✅ 极简，无需数据库
- ✅ 人类可读，易于编辑
- ✅ 版本控制友好（Git）
- ✅ 易于备份和迁移
- ✅ 支持 Markdown 格式（列表、表格等）

## 二、Markdown 文件结构

### 2.1 文件命名规范

```
memory_{user_id}.md
# 例如：memory_user123.md
```

### 2.2 完整模板

```markdown
# 用户记忆档案

> 最后更新：2024-01-15 14:30:00
> 版本：1.0

---

## 📋 基本信息

| 字段 | 值 |
|------|-----|
| 姓名 | 张三 |
| 昵称 | 小张 |
| 时区 | Asia/Shanghai (UTC+8) |
| 语言 | zh-CN |
| 创建时间 | 2024-01-01 |
| 最后活跃 | 2024-01-15 14:30:00 |

---

## ⚙️ 偏好设置

### 提醒方式
- 默认提醒方式：`推送通知`
- 重要事项提醒：`邮件 + 推送`
- 提醒提前时间：`15分钟`

### 工作习惯
- 工作日：`周一至周五`
- 工作时间：`09:00 - 18:00`
- 午休时间：`12:00 - 13:00`
- 偏好的会议时间：`上午 10:00-11:00, 下午 14:00-16:00`

### 内容偏好
- 喜欢的主题：`技术、阅读、旅行`
- 不喜欢的主题：`无`
- 回复风格：`简洁、专业`
- 常用工具：`Python, VS Code, Git`

### 其他偏好
- 咖啡时间：`每天早上 8:00`
- 运动习惯：`每周三、周五晚上 19:00`
- 阅读时间：`每天晚上 21:00-22:00`

---

## 📅 日程安排

### 定期日程

| 时间 | 事项 | 频率 | 备注 |
|------|------|------|------|
| 08:00 | 喝咖啡 | 每天 | 早上第一件事 |
| 09:00 | 开始工作 | 工作日 | |
| 12:00 | 午餐 | 工作日 | 通常去食堂 |
| 18:00 | 下班 | 工作日 | |
| 19:00 | 运动 | 周三、周五 | 健身房 |
| 21:00 | 阅读 | 每天 | 30分钟 |

### 即将到来的事件

#### 2024-01-20 10:00
**会议：项目评审**
- 地点：会议室A
- 参与人：团队全体
- 准备事项：准备PPT

#### 2024-01-25 全天
**旅行：北京出差**
- 目的：参加技术大会
- 酒店：已预订
- 航班：CA1234, 08:00起飞

---

## ✅ 待办事项

### 进行中
- [ ] 完成项目文档编写（优先级：高，截止：2024-01-18）
- [ ] 准备下周的演讲材料（优先级：中，截止：2024-01-22）

### 待开始
- [ ] 学习新的 Python 框架（优先级：低）
- [ ] 整理书单（优先级：低）

### 已完成
- [x] 完成代码审查（完成时间：2024-01-15）
- [x] 提交月度报告（完成时间：2024-01-10）

---

## 🧠 学习到的习惯

### 工作习惯
- 喜欢在早上处理重要任务（学习时间：2024-01-05）
- 不喜欢被打断，需要专注时间（学习时间：2024-01-08）
- 习惯在任务完成后立即更新状态（学习时间：2024-01-10）

### 沟通习惯
- 偏好简洁明了的回复（学习时间：2024-01-03）
- 喜欢使用技术术语（学习时间：2024-01-05）
- 通常在晚上 21:00 后不处理工作消息（学习时间：2024-01-12）

### 生活习惯
- 每天早上 8:00 需要提醒喝咖啡（学习时间：2024-01-02）
- 周三和周五晚上会去运动（学习时间：2024-01-04）
- 周末喜欢睡懒觉，不安排早上的事情（学习时间：2024-01-06）

---

## 📝 重要记忆

### 2024-01-15
**对话主题：项目进度讨论**
- 用户提到项目需要在 1 月底前完成
- 用户担心时间紧张，需要帮助规划
- 建议：将任务分解为小步骤，每天跟踪进度

### 2024-01-10
**对话主题：学习计划**
- 用户想学习新的 Python 框架
- 偏好：通过实践项目学习，而不是只看文档
- 建议：从简单项目开始，逐步增加复杂度

### 2024-01-05
**对话主题：时间管理**
- 用户希望提高工作效率
- 发现用户喜欢使用番茄工作法
- 建议：设置 25 分钟专注时间，5 分钟休息

---

## 🎯 长期目标

### 2024年目标
1. **技术提升**
   - 学习 3 个新的 Python 框架
   - 完成 2 个开源项目贡献
   - 目标完成度：30%

2. **健康管理**
   - 每周运动 2-3 次
   - 保持规律作息
   - 目标完成度：60%

3. **阅读计划**
   - 阅读 12 本技术书籍
   - 每月 1 本
   - 目标完成度：8%

---

## 📊 统计数据

### 交互统计
- 总对话次数：`156`
- 平均每天对话：`10.4次`
- 最活跃时段：`09:00-12:00, 14:00-18:00`
- 最常用功能：`任务管理、日程查询、代码帮助`

### 任务统计
- 已完成任务：`45`
- 进行中任务：`3`
- 平均完成时间：`2.5天`
- 最常处理的任务类型：`代码开发、文档编写`

---

## 🔗 关联信息

### 常用联系人
- **李四** - 同事，技术负责人
  - 联系方式：lisi@example.com
  - 关系：工作伙伴
  - 备注：经常讨论技术问题

### 常用项目
- **项目A** - 核心业务系统
  - 状态：进行中
  - 截止日期：2024-02-28
  - 相关文件：`/workspace/project_a/`

### 重要文件
- `/workspace/notes/meeting_notes.md` - 会议记录
- `/workspace/docs/project_plan.md` - 项目计划

---

## 📌 快速参考

### 常用命令
- "查看今天的日程" → 显示今日安排
- "添加待办" → 创建新任务
- "提醒我" → 设置提醒
- "我的偏好" → 显示偏好设置

### 快捷回复模板
- 确认收到：`好的，已记录`
- 需要更多信息：`请提供更多细节`
- 完成任务：`已完成，请查看`

---

## 🔄 更新日志

### 2024-01-15
- 更新了工作习惯：添加了专注时间偏好
- 新增待办：准备演讲材料
- 完成待办：代码审查

### 2024-01-10
- 新增长期目标：2024年阅读计划
- 更新统计数据：总对话次数 156

### 2024-01-05
- 学习到新习惯：喜欢使用番茄工作法
- 更新偏好：添加了会议时间偏好

---

## 💡 使用说明

### 如何更新记忆
1. Agent 在每次对话后自动更新相关部分
2. 用户可以直接编辑此文件
3. 重要变更会记录在"更新日志"中

### 如何查询记忆
- 使用 `Ctrl+F` 搜索关键词
- 查看对应的章节
- Agent 会自动检索相关内容

### 备份建议
- 定期备份此文件
- 可以使用 Git 进行版本控制
- 建议每周备份一次

---

*此文件由 AI 助手自动维护，用户可随时编辑*
```

## 三、字段说明

### 3.1 基本信息（必需）
- **姓名/昵称**：用户称呼
- **时区**：用于时间相关功能
- **语言**：界面语言偏好
- **创建时间/最后活跃**：元数据

### 3.2 偏好设置（重要）
- **提醒方式**：如何提醒用户
- **工作习惯**：工作时间、会议偏好
- **内容偏好**：喜欢/不喜欢的主题
- **其他偏好**：个性化习惯

### 3.3 日程安排（动态）
- **定期日程**：重复性事件
- **即将到来的事件**：具体日期的事件

### 3.4 待办事项（动态）
- **进行中**：当前任务
- **待开始**：计划中的任务
- **已完成**：历史记录（可定期清理）

### 3.5 学习到的习惯（自动更新）
- Agent 从对话中学习到的用户习惯
- 包含学习时间，便于追溯

### 3.6 重要记忆（摘要）
- 关键对话的摘要
- 按时间倒序排列
- 保留最近 20-30 条

### 3.7 长期目标（可选）
- 用户的年度/月度目标
- 跟踪完成进度

### 3.8 统计数据（自动计算）
- 交互统计
- 任务统计
- 帮助了解用户行为模式

### 3.9 关联信息（可选）
- 常用联系人
- 常用项目
- 重要文件路径

### 3.10 快速参考（辅助）
- 常用命令
- 快捷回复模板

### 3.11 更新日志（自动维护）
- 记录重要变更
- 便于追踪历史

## 四、解析与更新规范

### 4.1 文件结构解析

```python
# memory_parser.py
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class UserMemory:
    """用户记忆数据结构"""
    user_id: str
    basic_info: Dict[str, str]
    preferences: Dict[str, any]
    schedules: List[Dict]
    todos: Dict[str, List[Dict]]
    learned_habits: List[Dict]
    important_memories: List[Dict]
    long_term_goals: List[Dict]
    statistics: Dict[str, any]
    associations: Dict[str, List[Dict]]
    last_updated: datetime

class MemoryParser:
    """Markdown 记忆文件解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self._read_file()
    
    def _read_file(self) -> str:
        """读取文件内容"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse(self) -> UserMemory:
        """解析整个文件"""
        return UserMemory(
            user_id=self._extract_user_id(),
            basic_info=self._parse_basic_info(),
            preferences=self._parse_preferences(),
            schedules=self._parse_schedules(),
            todos=self._parse_todos(),
            learned_habits=self._parse_learned_habits(),
            important_memories=self._parse_important_memories(),
            long_term_goals=self._parse_long_term_goals(),
            statistics=self._parse_statistics(),
            associations=self._parse_associations(),
            last_updated=self._extract_last_updated()
        )
    
    def _parse_basic_info(self) -> Dict[str, str]:
        """解析基本信息表格"""
        # 使用正则表达式提取表格内容
        pattern = r'## 📋 基本信息\n\n(.*?)\n\n---'
        match = re.search(pattern, self.content, re.DOTALL)
        if not match:
            return {}
        
        table_content = match.group(1)
        info = {}
        for line in table_content.split('\n'):
            if '|' in line and not line.startswith('|--'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    info[parts[1]] = parts[2]
        return info
    
    def _parse_preferences(self) -> Dict[str, any]:
        """解析偏好设置"""
        preferences = {}
        # 解析各个子章节
        # ... 实现细节
        return preferences
    
    def _parse_todos(self) -> Dict[str, List[Dict]]:
        """解析待办事项"""
        todos = {
            'in_progress': [],
            'pending': [],
            'completed': []
        }
        # 解析各个待办列表
        # ... 实现细节
        return todos
    
    # ... 其他解析方法
```

### 4.2 更新操作

```python
class MemoryUpdater:
    """记忆文件更新器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parser = MemoryParser(file_path)
    
    def update_preference(self, key: str, value: any):
        """更新偏好设置"""
        # 1. 解析文件
        # 2. 找到对应位置
        # 3. 更新值
        # 4. 写回文件
        pass
    
    def add_todo(self, todo: Dict):
        """添加待办事项"""
        pass
    
    def complete_todo(self, todo_id: str):
        """完成待办事项"""
        pass
    
    def add_memory(self, memory: Dict):
        """添加重要记忆"""
        pass
    
    def learn_habit(self, habit: str, category: str):
        """学习新习惯"""
        pass
    
    def update_statistics(self):
        """更新统计数据"""
        pass
```

## 五、与 Agent 集成

### 5.1 工具集设计

```python
# memory_toolset.py
from pydantic_ai.toolsets import FunctionToolset
from pydantic_deep.deps import DeepAgentDeps

memory_toolset = FunctionToolset[DeepAgentDeps](id="memory")

@memory_toolset.tool
async def read_memory(ctx, section: str = "all") -> str:
    """读取用户记忆
    
    Args:
        section: 要读取的部分 (all, basic_info, preferences, todos, etc.)
    """
    parser = MemoryParser(f"memory_{ctx.deps.user_id}.md")
    memory = parser.parse()
    
    if section == "all":
        return memory.to_markdown()
    elif section == "preferences":
        return format_preferences(memory.preferences)
    # ... 其他部分
    
    return "未找到指定部分"

@memory_toolset.tool
async def update_preference(ctx, key: str, value: str) -> str:
    """更新用户偏好"""
    updater = MemoryUpdater(f"memory_{ctx.deps.user_id}.md")
    updater.update_preference(key, value)
    return f"已更新偏好：{key} = {value}"

@memory_toolset.tool
async def add_todo(ctx, content: str, priority: str = "medium", due_date: str = None) -> str:
    """添加待办事项"""
    updater = MemoryUpdater(f"memory_{ctx.deps.user_id}.md")
    updater.add_todo({
        "content": content,
        "priority": priority,
        "due_date": due_date,
        "status": "pending"
    })
    return f"已添加待办：{content}"

@memory_toolset.tool
async def learn_habit(ctx, habit: str, category: str) -> str:
    """学习用户习惯"""
    updater = MemoryUpdater(f"memory_{ctx.deps.user_id}.md")
    updater.learn_habit(habit, category)
    return f"已学习习惯：{habit}（类别：{category}）"

@memory_toolset.tool
async def add_memory(ctx, topic: str, summary: str) -> str:
    """添加重要记忆"""
    updater = MemoryUpdater(f"memory_{ctx.deps.user_id}.md")
    updater.add_memory({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "summary": summary
    })
    return f"已记录记忆：{topic}"
```

### 5.2 系统提示集成

```python
def get_memory_context(user_id: str) -> str:
    """获取记忆上下文，用于注入系统提示"""
    parser = MemoryParser(f"memory_{user_id}.md")
    memory = parser.parse()
    
    context = f"""
## 用户记忆上下文

### 基本信息
- 姓名：{memory.basic_info.get('姓名', '未知')}
- 时区：{memory.basic_info.get('时区', 'UTC')}

### 偏好设置
- 提醒方式：{memory.preferences.get('提醒方式', {}).get('默认提醒方式', '未知')}
- 工作时间：{memory.preferences.get('工作习惯', {}).get('工作时间', '未知')}

### 当前待办
{format_todos(memory.todos['in_progress'])}

### 即将到来的日程
{format_schedules(memory.schedules)}

### 最近学习到的习惯
{format_habits(memory.learned_habits[-5:])}
"""
    return context
```

## 六、使用示例

### 6.1 初始化记忆文件

```python
# 首次创建
from memory_parser import MemoryParser, MemoryUpdater

user_id = "user123"
file_path = f"memory_{user_id}.md"

# 创建模板文件
template = get_memory_template()
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(template)

# 初始化基本信息
updater = MemoryUpdater(file_path)
updater.update_preference("姓名", "张三")
updater.update_preference("时区", "Asia/Shanghai")
```

### 6.2 Agent 自动更新

```python
# 在对话结束后
async def after_conversation(user_id: str, conversation_summary: str):
    updater = MemoryUpdater(f"memory_{user_id}.md")
    
    # 添加重要记忆
    updater.add_memory({
        "topic": "对话摘要",
        "summary": conversation_summary
    })
    
    # 更新最后活跃时间
    updater.update_basic_info("最后活跃", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 更新统计数据
    updater.increment_statistic("总对话次数")
```

### 6.3 用户手动编辑

用户可以直接编辑 Markdown 文件，Agent 会在下次读取时解析更新后的内容。

## 七、最佳实践

### 7.1 文件组织
- 每个用户一个文件：`memory_{user_id}.md`
- 存储在 `./memories/` 目录下
- 定期备份（建议每天）

### 7.2 更新频率
- **实时更新**：待办事项、日程
- **对话后更新**：重要记忆、学习到的习惯
- **定期更新**：统计数据（每天）
- **手动更新**：长期目标、关联信息

### 7.3 数据清理
- **已完成待办**：保留最近 30 条
- **重要记忆**：保留最近 50 条
- **更新日志**：保留最近 100 条
- **定期归档**：每月归档一次旧数据

### 7.4 性能优化
- 使用缓存，避免频繁解析
- 增量更新，只修改变化的部分
- 异步读写，不阻塞主流程

## 八、扩展建议

### 8.1 多文件版本（如果单文件太大）
如果记忆文件超过 1000 行，可以拆分为多个文件：
- `memory_{user_id}_basic.md` - 基本信息和偏好
- `memory_{user_id}_todos.md` - 待办事项
- `memory_{user_id}_memories.md` - 重要记忆
- `memory_{user_id}_goals.md` - 长期目标

### 8.2 版本控制
- 使用 Git 跟踪变更
- 每次重要更新创建提交
- 支持回滚到历史版本

### 8.3 搜索优化
- 使用 `ripgrep` 或 `grep` 快速搜索
- 建立索引文件（JSON）用于快速查询
- 支持全文搜索功能

## 九、总结

这个极简的 Markdown 记忆系统：

✅ **优点：**
- 零依赖，无需数据库
- 人类可读，易于编辑
- 版本控制友好
- 易于备份和迁移
- 结构清晰，易于解析

⚠️ **限制：**
- 不适合大规模并发写入
- 文件过大时性能下降
- 需要手动管理文件大小

💡 **适用场景：**
- 个人助手应用
- 单用户或小规模用户
- 需要简单、透明的存储方案
- 希望用户可以手动编辑记忆

---

*此格式设计为极简方案，可根据实际需求调整和扩展*
