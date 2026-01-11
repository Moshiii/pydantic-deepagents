"""
记忆系统工具集 - 用于集成到 pydantic-deep agent

这个模块提供了与 pydantic-deep 集成的工具集，但也可以独立使用。
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset

from .core import MemorySystem

# 尝试导入 DeepAgentDeps，如果不存在则使用 Any
try:
    from pydantic_deep.deps import DeepAgentDeps
    DepsType = DeepAgentDeps
except ImportError:
    DepsType = Any


MEMORY_SYSTEM_PROMPT = """
## 记忆系统工具

你可以使用以下工具来管理和查询用户的长期记忆：

- `read_memory`: 读取用户的记忆信息（基本信息、偏好、待办、日程等）
- `update_preference`: 更新用户的偏好设置
- `add_todo`: 添加待办事项到用户的记忆（一次性任务）
- `complete_todo`: 标记待办事项为已完成（通过内容匹配）
- `remove_todo`: 删除待办事项（通过内容匹配）
- `schedule_todo`: 为待办事项安排时间预算
- `add_memory`: 记录重要的对话记忆
- `learn_habit`: 学习用户的新习惯
- `add_regular_schedule`: 添加重复性日程（每天、工作日、每周X等）
- `add_one_time_event`: 添加一次性日程事件
- `add_idea`: 记录创意想法
- `learn_schedule_preference`: 学习用户的日程偏好

使用建议：
- 在对话开始时，使用 `read_memory` 了解用户的基本信息和偏好
- 当用户提到偏好时，使用 `update_preference` 或 `learn_schedule_preference` 更新
- 当用户提到一次性任务时，使用 `add_todo` 记录
- 当用户提到重复性任务时，使用 `add_regular_schedule` 添加到日程
- 当用户需要为待办安排时间时，使用 `schedule_todo`
- 在重要对话后，使用 `add_memory` 保存关键信息
- 当发现用户的行为模式时，使用 `learn_habit` 学习
- 当用户表达时间偏好时，使用 `learn_schedule_preference` 学习
"""


def get_memory_system_prompt() -> str:
    """生成记忆系统的系统提示"""
    return MEMORY_SYSTEM_PROMPT


def create_memory_toolset(
    memory_dir: str = "./memories",
    template_path: Optional[str] = None,
    id: str | None = "memory",
    fixed_user_id: Optional[str] = None,
) -> FunctionToolset[DepsType]:
    """创建记忆系统工具集
    
    Args:
        memory_dir: 记忆文件存储目录
        template_path: 模板文件路径（可选）
        id: 工具集 ID
    
    Returns:
        FunctionToolset 实例
    """
    toolset: FunctionToolset[DepsType] = FunctionToolset(id=id)
    
    def get_user_id(ctx: RunContext[DepsType]) -> str:
        """获取 user_id

        优先级：
        1. fixed_user_id（用于单用户私人助手）
        2. ctx.deps.user_id
        3. ctx.deps.session_id
        4. ctx.metadata 中的 user_id / session_id
        5. ctx.user_id
        6. 默认值 "default_user"
        """
        # 1. 固定用户 ID（用于私人陪伴型 AI）
        if fixed_user_id:
            return fixed_user_id

        # 2. 尝试从 deps 获取 user_id
        if hasattr(ctx.deps, "user_id"):
            return getattr(ctx.deps, "user_id")

        # 3. 尝试从 session_id 获取（如果 deps 有 session_id 属性）
        if hasattr(ctx.deps, "session_id"):
            return getattr(ctx.deps, "session_id")

        # 4. 尝试从 run context 的 metadata 获取
        if hasattr(ctx, "metadata") and isinstance(ctx.metadata, dict):
            if "user_id" in ctx.metadata:
                return ctx.metadata["user_id"]
            if "session_id" in ctx.metadata:
                return ctx.metadata["session_id"]

        # 5. 尝试从 run context 直接获取
        if hasattr(ctx, "user_id"):
            return getattr(ctx, "user_id")

        # 6. 默认值
        return "default_user"
    
    def get_memory_system(ctx: RunContext[DepsType]) -> MemorySystem:
        """获取或创建记忆系统实例"""
        user_id = get_user_id(ctx)
        return MemorySystem(
            user_id=user_id,
            memory_dir=memory_dir,
            template_path=template_path
        )
    
    @toolset.tool
    async def read_memory(
        ctx: RunContext[DepsType],
        section: str = "all"
    ) -> str:
        """读取用户的记忆信息
        
        Args:
            section: 要读取的部分，可选值：
                - "all": 全部信息
                - "basic_info": 基本信息
                - "preferences": 偏好设置
                - "todos": 待办事项
                - "habits": 学习到的习惯
                - "memories": 重要记忆
                - "goals": 长期目标
                - "schedule": 日程安排（定期日程和即将到来的事件）
        """
        memory_sys = get_memory_system(ctx)

        # 全部上下文（给模型看）
        if section == "all":
            return memory_sys.get_context()

        # 以下分支使用 JSON 存储来读取对应数据
        storage = memory_sys.storage  # JsonMemoryStorage
        data = storage.get_all_data()

        if section == "basic_info":
            # 直接从 profile.md 中提取“基本信息”表格
            # 从 JSON 中提取基本信息
            basic_info = data.get("profile", {}).get("basic_info", {})
            if basic_info:
                result = ["## 基本信息", ""]
                result.append("| 字段 | 值 |")
                result.append("|------|-----|")
                for key, value in basic_info.items():
                    result.append(f"| {key} | {value} |")
                return "\n".join(result)
            return "暂无基本信息"

        if section == "preferences":
            # 从 JSON 中提取偏好设置
            preferences = data.get("profile", {}).get("preferences", {})
            if preferences:
                result = ["## 偏好设置", ""]
                for category, items in preferences.items():
                    result.append(f"### {category}")
                    for key, value in items.items():
                        result.append(f"- {key}：`{value}`")
                    result.append("")
                return "\n".join(result)
            return "暂无偏好设置"

        if section == "todos":
            # 从 JSON 中提取待办事项
            todos = data.get("todos", {})
            if todos:
                result = ["# 待办事项", ""]
                status_map = {
                    "in_progress": "进行中",
                    "pending": "待开始",
                    "completed": "已完成"
                }
                for status_key, status_name in status_map.items():
                    todo_list = todos.get(status_key, [])
                    if todo_list:
                        result.append(f"### {status_name}")
                        for todo in todo_list:
                            priority_str = f"，优先级：{todo.get('priority', 'medium')}" if todo.get('priority') != 'medium' else ""
                            due_str = f"，截止：{todo.get('due_date')}" if todo.get('due_date') else ""
                            completed_str = f"，完成时间：{todo.get('completed_at')}" if todo.get('completed_at') else ""
                            checkbox = "[x]" if status_key == "completed" else "[ ]"
                            result.append(f"- {checkbox} {todo['content']}{priority_str}{due_str}{completed_str}")
                        result.append("")
                return "\n".join(result)
            return "暂无待办事项"

        if section == "habits":
            # 从 JSON 中提取习惯
            habits = data.get("habits", {})
            if habits:
                result = ["# 生活习惯", ""]
                for category, habit_list in habits.items():
                    if habit_list:
                        result.append(f"## {category}")
                        for habit_item in habit_list:
                            learned_at = habit_item.get('learned_at', '')
                            learned_str = f"（学习时间：{learned_at}）" if learned_at else ""
                            result.append(f"- {habit_item['habit']}{learned_str}")
                        result.append("")
                return "\n".join(result)
            return "暂无学习到的习惯"

        if section == "memories":
            # 从 JSON 中提取对话记忆
            conversations = data.get("conversations", [])
            if conversations:
                result = ["# 最近对话摘要", ""]
                for conv in conversations:
                    result.append(f"### {conv.get('date', '')} - {conv.get('topic', '')}")
                    for point in conv.get('summary', []):
                        result.append(f"- {point}")
                    result.append("")
                return "\n".join(result)
            return "暂无重要记忆"

        if section == "schedule":
            # 从 JSON 中提取日程安排
            schedule_data = data.get("schedule", {})
            result = ["# 日程安排", ""]
            
            # 定期日程
            regular = schedule_data.get("regular", [])
            if regular:
                result.append("## 定期日程")
                for sched in regular:
                    desc_str = f"（{sched['description']}）" if sched.get('description') else ""
                    result.append(f"- **{sched['title']}**：{sched['time']}，{sched['frequency']}{desc_str}")
                result.append("")
            
            # 即将到来的事件
            upcoming = schedule_data.get("upcoming", [])
            if upcoming:
                result.append("## 即将到来的事件")
                for event in upcoming:
                    end_str = f"-{event['end_time']}" if event.get('end_time') else ""
                    desc_str = f"（{event['description']}）" if event.get('description') else ""
                    result.append(f"- **{event['title']}**：{event['start_time']}{end_str}{desc_str}")
                result.append("")
            
            if not regular and not upcoming:
                return "暂无日程安排"
            
            return "\n".join(result)

        if section == "goals":
            # 当前未单独实现 goals，返回提示
            return "当前记忆系统未单独存储长期目标，如需请在 diary 中记录。"

        return f"未知的章节：{section}。可用章节：all, basic_info, preferences, todos, habits, memories, goals, schedule"
    
    @toolset.tool
    async def update_preference(
        ctx: RunContext[DepsType],
        category: str,
        key: str,
        value: str
    ) -> str:
        """更新用户的偏好设置
        
        Args:
            category: 偏好类别（如"提醒方式"、"工作习惯"、"内容偏好"）
            key: 偏好键名
            value: 偏好值
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.update_preference(category, key, value)
        return f"已更新偏好：{category} - {key} = {value}"
    
    @toolset.tool
    async def add_todo(
        ctx: RunContext[DepsType],
        content: str,
        priority: str = "medium",
        due_date: str | None = None,
        category: str | None = None,
        estimated_duration: str | None = None
    ) -> str:
        """添加待办事项到用户的记忆
        
        Args:
            content: 待办内容
            priority: 优先级（low, medium, high）
            due_date: 截止日期（格式：YYYY-MM-DD）
            category: 分类标签（如 "工作"、"学习"、"生活"）
            estimated_duration: 预估时长（如 "30分钟"、"2小时"）
        """
        memory_sys = get_memory_system(ctx)
        todo_id = memory_sys.add_todo(content, priority, due_date, category, estimated_duration)
        return f"已添加待办：{content}（ID: {todo_id}，优先级：{priority}）"
    
    @toolset.tool
    async def complete_todo(
        ctx: RunContext[DepsType],
        content: str
    ) -> str:
        """标记待办事项为已完成
        
        Args:
            content: 待办内容（通过内容匹配查找待办）
        """
        memory_sys = get_memory_system(ctx)
        # 先通过content查找ID
        todo_id = memory_sys.find_todo_by_content(content)
        if not todo_id:
            return f"未找到待办事项：{content}"
        
        success = memory_sys.complete_todo(todo_id)
        if success:
            return f"已标记完成：{content}"
        else:
            return f"标记完成失败：{content}"
    
    @toolset.tool
    async def remove_todo(
        ctx: RunContext[DepsType],
        content: str
    ) -> str:
        """删除待办事项（用于清理重复或已转为日程的待办）
        
        Args:
            content: 待办内容（通过内容匹配查找待办）
        """
        memory_sys = get_memory_system(ctx)
        # 先通过content查找ID
        todo_id = memory_sys.find_todo_by_content(content)
        if not todo_id:
            return f"未找到待办事项：{content}"
        
        success = memory_sys.remove_todo(todo_id)
        if success:
            return f"已删除待办：{content}"
        else:
            return f"删除失败：{content}"
    
    @toolset.tool
    async def add_memory(
        ctx: RunContext[DepsType],
        topic: str,
        summary: str
    ) -> str:
        """记录重要的对话记忆
        
        Args:
            topic: 对话主题
            summary: 记忆摘要（可以包含多个要点，用换行分隔）
        """
        memory_sys = get_memory_system(ctx)
        points = [p.strip() for p in summary.split('\n') if p.strip()]
        memory_sys.add_memory(topic, points)
        return f"已记录记忆：{topic}"
    
    @toolset.tool
    async def learn_habit(
        ctx: RunContext[DepsType],
        habit: str,
        category: str = "工作习惯"
    ) -> str:
        """学习用户的新习惯
        
        Args:
            habit: 习惯描述
            category: 习惯类别（工作习惯、沟通习惯、生活习惯）
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.learn_habit(habit, category)
        return f"已学习习惯：{habit}（类别：{category}）"
    
    @toolset.tool
    async def schedule_todo(
        ctx: RunContext[DepsType],
        content: str,
        start_time: str,
        duration: str,
        reminder_minutes: int = 15
    ) -> str:
        """为待办事项安排时间预算
        
        Args:
            content: 待办内容（通过内容匹配查找待办）
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM 或 YYYY-MM-DDTHH:MM）
            duration: 持续时间（如 "30分钟"、"1小时"、"2小时30分钟"）
            reminder_minutes: 提前提醒分钟数（默认 15）
        """
        memory_sys = get_memory_system(ctx)
        # 先通过content查找ID
        todo_id = memory_sys.find_todo_by_content(content)
        if not todo_id:
            return f"未找到待办事项：{content}"
        
        success = memory_sys.schedule_todo(todo_id, start_time, duration, reminder_minutes)
        if success:
            return f"已安排：{content}，时间：{start_time}，时长：{duration}"
        else:
            return f"安排失败：{content}"
    
    @toolset.tool
    async def add_regular_schedule(
        ctx: RunContext[DepsType],
        title: str,
        time: str,
        frequency: str,
        duration: str = "1小时",
        description: str = "",
        reminder_minutes: int = 15
    ) -> str:
        """添加重复性日程到用户的日历
        
        Args:
            title: 日程标题（如"学习30分钟新技能"）
            time: 时间（格式：HH:MM，如 "10:00" 或 "14:30"）
            frequency: 频率，可选值：
                - "每天"：每天重复
                - "工作日"：周一至周五重复
                - "每周一"、"每周二"等：每周特定日期重复
                - "每月1号"等：每月特定日期重复
            duration: 持续时间（如 "30分钟"、"1小时"）
            description: 备注说明（可选）
            reminder_minutes: 提前提醒分钟数（默认 15）
        """
        memory_sys = get_memory_system(ctx)
        schedule_id = memory_sys.add_recurring_schedule(
            title, time, duration, frequency, description, None, reminder_minutes
        )
        return f"已添加重复性日程：{title}，时间：{time}，频率：{frequency}（ID: {schedule_id}）"
    
    @toolset.tool
    async def add_one_time_event(
        ctx: RunContext[DepsType],
        title: str,
        start_time: str,
        end_time: str | None = None,
        duration: str | None = None,
        description: str = "",
        location: str | None = None,
        reminder_minutes: int = 15
    ) -> str:
        """添加一次性日程事件
        
        Args:
            title: 事件标题
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM）
            end_time: 结束时间（格式：YYYY-MM-DD HH:MM），不设置则使用 duration
            duration: 持续时间（与 end_time 二选一）
            description: 事件描述
            location: 地点
            reminder_minutes: 提前提醒分钟数（默认 15）
        """
        memory_sys = get_memory_system(ctx)
        event_id = memory_sys.add_one_time_event(
            title, start_time, end_time, duration, description, location, reminder_minutes
        )
        return f"已添加一次性事件：{title}，时间：{start_time}（ID: {event_id}）"
    
    @toolset.tool
    async def add_idea(
        ctx: RunContext[DepsType],
        content: str,
        date: str | None = None,
        time: str | None = None,
        tags: list[str] | None = None,
        category: str | None = None
    ) -> str:
        """记录创意想法
        
        Args:
            content: 想法内容
            date: 日期（格式：YYYY-MM-DD），默认今天
            time: 时间（格式：HH:MM），默认当前时间
            tags: 标签列表（如 ["工作", "产品", "技术"]）
            category: 分类（如 "产品想法"、"技术灵感"、"生活感悟"）
        """
        memory_sys = get_memory_system(ctx)
        idea_id = memory_sys.add_idea(content, date, time, tags, category)
        return f"已记录创意想法：{content}（ID: {idea_id}）"
    
    @toolset.tool
    async def learn_schedule_preference(
        ctx: RunContext[DepsType],
        preference_type: str,
        value: str,
        confidence: float = 1.0
    ) -> str:
        """学习用户的日程偏好
        
        Args:
            preference_type: 偏好类型（如 "工作时间"、"偏好时间段_学习"、"午休时间"）
            value: 偏好值（如 "09:00-18:00"、"上午"、"12:00-13:00"）
            confidence: 学习置信度（0-1，默认1.0表示用户明确表达）
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.learn_schedule_preference(preference_type, value, confidence)
        return f"已学习偏好：{preference_type} = {value}（置信度：{confidence}）"
    
    return toolset


# 独立使用时的辅助函数
def create_standalone_memory_system(
    user_id: str,
    memory_dir: str = "./memories",
    template_path: Optional[str] = None
) -> MemorySystem:
    """创建独立的记忆系统实例（不依赖 pydantic-deep）
    
    这个函数允许在其他框架中使用记忆系统。
    
    Args:
        user_id: 用户 ID
        memory_dir: 记忆文件存储目录
        template_path: 模板文件路径
    
    Returns:
        MemorySystem 实例
    
    Example:
        ```python
        # 在任何 Python 应用中使用
        memory = create_standalone_memory_system("user123")
        
        # 读取记忆
        context = memory.get_context()
        
        # 更新记忆
        memory.add_todo("完成项目文档")
        memory.update_preference("提醒方式", "默认提醒方式", "邮件")
        ```
    """
    return MemorySystem(
        user_id=user_id,
        memory_dir=memory_dir,
        template_path=template_path
    )
