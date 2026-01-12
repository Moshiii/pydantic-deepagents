"""
Personal Assistant Toolset - 个人助手工具集

统一所有个人助手功能在一个 toolset 中：
- 个性化学习模块
- 创意记录模块
- 待办管理模块
- 日程安排模块
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset

try:
    from pydantic_deep.deps import DeepAgentDeps
    DepsType = DeepAgentDeps
except ImportError:
    DepsType = Any

from datetime import timedelta

from memory_system.core import MemorySystem
from memory_system.utils import get_current_date, get_current_time, parse_datetime, parse_duration, time_overlap


def create_personal_assistant_toolset(
    memory_dir: str = "./memories",
    id: str = "personal_assistant",
    fixed_user_id: Optional[str] = None,
) -> FunctionToolset[DepsType]:
    """创建个人助手工具集
    
    Args:
        memory_dir: 记忆文件存储目录
        id: 工具集 ID
        fixed_user_id: 固定用户 ID（用于单用户私人助手）
    
    Returns:
        FunctionToolset 实例
    """
    toolset = FunctionToolset[DepsType](id=id)
    
    def get_user_id(ctx: RunContext[DepsType]) -> str:
        """获取 user_id"""
        if fixed_user_id:
            return fixed_user_id
        if hasattr(ctx.deps, "user_id"):
            return getattr(ctx.deps, "user_id")
        if hasattr(ctx.deps, "session_id"):
            return getattr(ctx.deps, "session_id")
        if hasattr(ctx, "metadata") and isinstance(ctx.metadata, dict):
            if "user_id" in ctx.metadata:
                return ctx.metadata["user_id"]
            if "session_id" in ctx.metadata:
                return ctx.metadata["session_id"]
        if hasattr(ctx, "user_id"):
            return ctx.user_id
        return "default_user"
    
    def get_memory_system(ctx: RunContext[DepsType]) -> MemorySystem:
        """获取或创建记忆系统实例"""
        user_id = get_user_id(ctx)
        return MemorySystem(user_id=user_id, memory_dir=memory_dir)
    
    # ========== 个性化学习模块 ==========
    
    @toolset.tool
    async def learn_user_pattern(
        ctx: RunContext[DepsType],
        pattern_type: str,  # "使用习惯", "聊天习惯", "办事习惯", "语言偏好"
        pattern_description: str,
        confidence: float = 0.8,
        source: str = "conversation",  # "explicit", "behavior_pattern", "inference"
        evidence: Optional[str] = None
    ) -> str:
        """学习用户的模式/习惯
        
        Args:
            pattern_type: 模式类型（使用习惯、聊天习惯、办事习惯、语言偏好）
            pattern_description: 模式描述
            confidence: 置信度（0-1）
            source: 学习来源（explicit=显式, behavior_pattern=行为模式, inference=推断）
            evidence: 证据描述（可选）
        """
        memory_sys = get_memory_system(ctx)
        
        # 根据类型保存到不同位置
        if pattern_type == "使用习惯":
            memory_sys.update_preference("使用习惯", pattern_description, str(confidence))
        elif pattern_type == "聊天习惯":
            memory_sys.update_preference("聊天习惯", pattern_description, str(confidence))
        elif pattern_type == "办事习惯":
            memory_sys.update_preference("办事习惯", pattern_description, str(confidence))
        elif pattern_type == "语言偏好":
            memory_sys.update_preference("语言偏好", pattern_description, str(confidence))
        else:
            # 作为习惯保存
            memory_sys.learn_habit(pattern_description, pattern_type)
        
        return f"已学习用户模式：{pattern_type} - {pattern_description}（置信度：{confidence:.1%}）"
    
    @toolset.tool
    async def get_learned_patterns(
        ctx: RunContext[DepsType],
        pattern_type: Optional[str] = None
    ) -> str:
        """获取已学习的模式
        
        Args:
            pattern_type: 模式类型（可选，不指定则返回所有）
        """
        memory_sys = get_memory_system(ctx)
        data = memory_sys.get_all_data()
        
        result = []
        if pattern_type:
            # 返回特定类型
            if pattern_type in ["使用习惯", "聊天习惯", "办事习惯", "语言偏好"]:
                prefs = data.get("profile", {}).get("preferences", {}).get(pattern_type, {})
                if prefs:
                    result.append(f"## {pattern_type}")
                    for key, value in prefs.items():
                        result.append(f"- {key}: {value}")
            else:
                habits = data.get("habits", {}).get(pattern_type, [])
                if habits:
                    result.append(f"## {pattern_type}")
                    for habit in habits:
                        result.append(f"- {habit.get('habit', '')}（置信度：{habit.get('confidence', 0):.1%}）")
        else:
            # 返回所有
            prefs = data.get("profile", {}).get("preferences", {})
            for pref_type in ["使用习惯", "聊天习惯", "办事习惯", "语言偏好"]:
                if pref_type in prefs and prefs[pref_type]:
                    result.append(f"## {pref_type}")
                    for key, value in prefs[pref_type].items():
                        result.append(f"- {key}: {value}")
            
            habits = data.get("habits", {})
            for category, habit_list in habits.items():
                if habit_list:
                    result.append(f"## {category}")
                    for habit in habit_list:
                        result.append(f"- {habit.get('habit', '')}（置信度：{habit.get('confidence', 0):.1%}）")
        
        return "\n".join(result) if result else "暂无已学习的模式"
    
    # ========== 创意记录模块 ==========
    
    @toolset.tool
    async def add_idea(
        ctx: RunContext[DepsType],
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """记录创意想法
        
        Args:
            content: 创意内容
            category: 分类（可选）
            tags: 标签列表（可选）
        """
        memory_sys = get_memory_system(ctx)
        idea_id = memory_sys.add_idea(
            content=content,
            date=get_current_date(),
            time=get_current_time(),
            tags=tags,
            category=category
        )
        return f"已记录创意想法（ID: {idea_id}）"
    
    @toolset.tool
    async def get_daily_ideas(
        ctx: RunContext[DepsType],
        date: Optional[str] = None
    ) -> str:
        """获取每日创意
        
        Args:
            date: 日期（格式：YYYY-MM-DD），不指定则返回今天的
        """
        memory_sys = get_memory_system(ctx)
        data = memory_sys.get_all_data()
        ideas = data.get("ideas", [])
        
        target_date = date or get_current_date()
        daily_ideas = [idea for idea in ideas if idea.get("date") == target_date]
        
        if not daily_ideas:
            return f"{target_date} 暂无创意记录"
        
        result = [f"## {target_date} 的创意想法", ""]
        for idea in daily_ideas:
            result.append(f"### {idea.get('time', '')} - {idea.get('category', '未分类')}")
            result.append(f"{idea.get('content', '')}")
            if idea.get("tags"):
                result.append(f"标签：{', '.join(idea.get('tags', []))}")
            result.append("")
        
        return "\n".join(result)
    
    @toolset.tool
    async def search_ideas(
        ctx: RunContext[DepsType],
        query: str,
        category: Optional[str] = None
    ) -> str:
        """搜索创意
        
        Args:
            query: 搜索关键词
            category: 分类过滤（可选）
        """
        memory_sys = get_memory_system(ctx)
        data = memory_sys.get_all_data()
        ideas = data.get("ideas", [])
        
        results = []
        for idea in ideas:
            content = idea.get("content", "").lower()
            if query.lower() in content:
                if category and idea.get("category") != category:
                    continue
                results.append(idea)
        
        if not results:
            return f"未找到包含 '{query}' 的创意"
        
        result_text = [f"## 搜索结果（'{query}'）", ""]
        for idea in results[:20]:  # 限制最多20条
            result_text.append(f"### {idea.get('date', '')} {idea.get('time', '')} - {idea.get('category', '未分类')}")
            result_text.append(f"{idea.get('content', '')}")
            if idea.get("tags"):
                result_text.append(f"标签：{', '.join(idea.get('tags', []))}")
            result_text.append("")
        
        return "\n".join(result_text)
    
    # ========== 待办管理模块 ==========
    
    @toolset.tool
    async def read_memory(
        ctx: RunContext[DepsType],
        section: str = "all"
    ) -> str:
        """读取用户的记忆信息
        
        Args:
            section: 要读取的部分（all, profile, todos, schedule, ideas, habits）
        """
        memory_sys = get_memory_system(ctx)
        
        if section == "all":
            return memory_sys.get_context()
        
        data = memory_sys.get_all_data()
        
        if section == "profile":
            profile = data.get("profile", {})
            result = ["## 用户档案", ""]
            basic_info = profile.get("basic_info", {})
            if basic_info:
                result.append("### 基本信息")
                for key, value in basic_info.items():
                    result.append(f"- {key}: {value}")
                result.append("")
            
            preferences = profile.get("preferences", {})
            if preferences:
                result.append("### 偏好设置")
                for category, items in preferences.items():
                    result.append(f"#### {category}")
                    for key, value in items.items():
                        result.append(f"- {key}: {value}")
                    result.append("")
            
            return "\n".join(result)
        
        elif section == "todos":
            todos = data.get("todos", {})
            result = ["## 待办事项", ""]
            status_map = {
                "pending": "待开始",
                "scheduled": "已安排",
                "in_progress": "进行中",
                "completed": "已完成"
            }
            for status_key, status_name in status_map.items():
                todo_list = todos.get(status_key, [])
                if todo_list:
                    result.append(f"### {status_name}")
                    for todo in todo_list:
                        priority_str = f"，优先级：{todo.get('priority', 'medium')}" if todo.get('priority') != 'medium' else ""
                        due_str = f"，截止：{todo.get('due_date')}" if todo.get('due_date') else ""
                        checkbox = "[x]" if status_key == "completed" else "[ ]"
                        result.append(f"- {checkbox} {todo.get('content', '')}{priority_str}{due_str}")
                    result.append("")
            
            return "\n".join(result) if len(result) > 2 else "暂无待办事项"
        
        elif section == "schedule":
            schedule = data.get("schedule", {})
            result = ["## 日程安排", ""]
            
            regular = schedule.get("regular", [])
            if regular:
                result.append("### 定期日程")
                for event in regular:
                    result.append(f"- {event.get('title', '')} - {event.get('time', '')} ({event.get('frequency', '')})")
                result.append("")
            
            upcoming = schedule.get("upcoming", [])
            if upcoming:
                result.append("### 即将到来的事件")
                for event in upcoming:
                    result.append(f"- {event.get('title', '')} - {event.get('start_time', '')}")
                result.append("")
            
            return "\n".join(result) if len(result) > 2 else "暂无日程安排"
        
        elif section == "ideas":
            ideas = data.get("ideas", [])
            if not ideas:
                return "暂无创意记录"
            
            result = ["## 创意想法", ""]
            for idea in ideas[-20:]:  # 最近20条
                result.append(f"### {idea.get('date', '')} {idea.get('time', '')} - {idea.get('category', '未分类')}")
                result.append(f"{idea.get('content', '')}")
                result.append("")
            
            return "\n".join(result)
        
        elif section == "habits":
            habits = data.get("habits", {})
            result = ["## 学习到的习惯", ""]
            for category, habit_list in habits.items():
                if habit_list:
                    result.append(f"### {category}")
                    for habit in habit_list:
                        result.append(f"- {habit.get('habit', '')}（置信度：{habit.get('confidence', 0):.1%}）")
                    result.append("")
            
            return "\n".join(result) if len(result) > 2 else "暂无已学习的习惯"
        
        return f"未知的 section: {section}"
    
    @toolset.tool
    async def update_preference(
        ctx: RunContext[DepsType],
        category: str,
        key: str,
        value: str
    ) -> str:
        """更新用户的偏好设置
        
        Args:
            category: 偏好类别
            key: 偏好键
            value: 偏好值
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.update_preference(category, key, value)
        return f"已更新偏好：{category}.{key} = {value}"
    
    @toolset.tool
    async def add_todo(
        ctx: RunContext[DepsType],
        content: str,
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        estimated_duration: Optional[str] = None
    ) -> str:
        """添加待办事项
        
        Args:
            content: 待办内容
            priority: 优先级（low, medium, high）
            due_date: 截止日期（格式：YYYY-MM-DD）
            category: 分类
            estimated_duration: 预估时长（如 "2小时"）
        """
        memory_sys = get_memory_system(ctx)
        todo_id = memory_sys.add_todo(
            content=content,
            priority=priority,
            due_date=due_date,
            category=category,
            estimated_duration=estimated_duration
        )
        return f"已添加待办事项（ID: {todo_id}）"
    
    @toolset.tool
    async def complete_todo(
        ctx: RunContext[DepsType],
        todo_id: str
    ) -> str:
        """完成待办事项
        
        Args:
            todo_id: 待办 ID
        """
        memory_sys = get_memory_system(ctx)
        success = memory_sys.complete_todo(todo_id)
        if success:
            return f"已标记待办事项为已完成（ID: {todo_id}）"
        return f"未找到待办事项（ID: {todo_id}）"
    
    @toolset.tool
    async def remove_todo(
        ctx: RunContext[DepsType],
        todo_id: str
    ) -> str:
        """删除待办事项
        
        Args:
            todo_id: 待办 ID
        """
        memory_sys = get_memory_system(ctx)
        success = memory_sys.remove_todo(todo_id)
        if success:
            return f"已删除待办事项（ID: {todo_id}）"
        return f"未找到待办事项（ID: {todo_id}）"
    
    @toolset.tool
    async def auto_migrate_overdue_todos(
        ctx: RunContext[DepsType]
    ) -> str:
        """自动移动过期待办到明天"""
        memory_sys = get_memory_system(ctx)
        data = memory_sys.get_all_data()
        todos = data.get("todos", {})
        
        today = get_current_date()
        migrated_count = 0
        
        for status in ["pending", "scheduled", "in_progress"]:
            todo_list = todos.get(status, [])
            for todo in todo_list[:]:  # 复制列表避免修改时出错
                due_date = todo.get("due_date")
                if due_date and due_date < today:
                    # 移动到明天
                    tomorrow = (parse_datetime(today + " 00:00:00") + timedelta(days=1)).strftime("%Y-%m-%d")
                    memory_sys.update_todo(todo.get("id"), due_date=tomorrow)
                    migrated_count += 1
        
        if migrated_count > 0:
            return f"已自动移动 {migrated_count} 个过期待办到明天"
        return "没有需要移动的过期待办"
    
    @toolset.tool
    async def create_todo_reminder(
        ctx: RunContext[DepsType],
        todo_id: str,
        reminder_minutes: int = 30
    ) -> str:
        """创建待办提醒
        
        Args:
            todo_id: 待办 ID
            reminder_minutes: 提前提醒的分钟数
        """
        memory_sys = get_memory_system(ctx)
        todo = memory_sys.get_todo(todo_id)
        
        if not todo:
            return f"未找到待办事项（ID: {todo_id}）"
        
        # 获取截止日期或安排时间
        due_date = todo.get("due_date")
        scheduled_time = todo.get("scheduled_time")
        
        if scheduled_time and scheduled_time.get("start"):
            start_time = scheduled_time["start"]
        elif due_date:
            start_time = f"{due_date} 09:00:00"  # 默认上午9点
        else:
            return "待办事项没有截止日期或安排时间，无法创建提醒"
        
        # 计算提醒时间
        start_dt = parse_datetime(start_time)
        remind_dt = start_dt - timedelta(minutes=reminder_minutes)
        
        # 创建提醒
        memory_sys.storage._create_reminder("todo", todo_id, remind_dt.strftime("%Y-%m-%d %H:%M:%S"), reminder_minutes)
        
        return f"已创建待办提醒，将在 {remind_dt.strftime('%Y-%m-%d %H:%M')} 提醒"
    
    @toolset.tool
    async def create_todo_followup(
        ctx: RunContext[DepsType],
        todo_id: str,
        followup_type: str = "after_task_time"
    ) -> str:
        """创建待办询问
        
        Args:
            todo_id: 待办 ID
            followup_type: 询问类型（after_task_time=任务时间后, daily=每天, weekly=每周）
        """
        memory_sys = get_memory_system(ctx)
        todo = memory_sys.get_todo(todo_id)
        
        if not todo:
            return f"未找到待办事项（ID: {todo_id}）"
        
        # 计算询问时间
        scheduled_time = todo.get("scheduled_time")
        estimated_duration = todo.get("estimated_duration", "1小时")
        
        if scheduled_time and scheduled_time.get("end"):
            end_time = scheduled_time["end"]
        else:
            # 使用预估时长
            duration_minutes = parse_duration(estimated_duration)
            from datetime import timedelta
            end_time = (parse_datetime(get_current_time()) + timedelta(minutes=duration_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        
        end_dt = parse_datetime(end_time)
        
        if followup_type == "after_task_time":
            ask_at = end_dt + timedelta(hours=1)  # 任务结束后1小时
        elif followup_type == "daily":
            ask_at = end_dt + timedelta(days=1)
        elif followup_type == "weekly":
            ask_at = end_dt + timedelta(days=7)
        else:
            ask_at = end_dt + timedelta(hours=1)
        
        # 创建询问（_create_followup 的签名是：type, target_id, ask_at, frequency）
        memory_sys.storage._create_followup("todo_completion", todo_id, ask_at.strftime("%Y-%m-%d %H:%M:%S"), followup_type)
        
        return f"已创建待办询问，将在 {ask_at.strftime('%Y-%m-%d %H:%M')} 询问"
    
    @toolset.tool
    async def get_pending_reminders(
        ctx: RunContext[DepsType]
    ) -> str:
        """获取待触发的提醒"""
        memory_sys = get_memory_system(ctx)
        reminders = memory_sys.get_pending_reminders()
        
        if not reminders:
            return "暂无待触发的提醒"
        
        result = ["## 待触发的提醒", ""]
        for reminder in reminders:
            result.append(f"- {reminder.get('remind_at', '')}: {reminder.get('type', '')} - {reminder.get('target_id', '')}")
        
        return "\n".join(result)
    
    @toolset.tool
    async def get_pending_followups(
        ctx: RunContext[DepsType]
    ) -> str:
        """获取待触发的询问"""
        memory_sys = get_memory_system(ctx)
        followups = memory_sys.get_pending_followups()
        
        if not followups:
            return "暂无待触发的询问"
        
        result = ["## 待触发的询问", ""]
        for followup in followups:
            result.append(f"- {followup.get('ask_at', '')}: {followup.get('question', '')}")
        
        return "\n".join(result)
    
    # ========== 日程安排模块 ==========
    
    @toolset.tool
    async def add_one_time_event(
        ctx: RunContext[DepsType],
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        duration: Optional[str] = None,
        description: str = "",
        location: Optional[str] = None,
        reminder_minutes: int = 15
    ) -> str:
        """添加一次性事件
        
        Args:
            title: 事件标题
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
            end_time: 结束时间（可选）
            duration: 持续时间（如 "1小时30分钟"，如果未提供 end_time）
            description: 描述
            location: 地点
            reminder_minutes: 提前提醒的分钟数
        """
        memory_sys = get_memory_system(ctx)
        event_id = memory_sys.add_one_time_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            description=description,
            location=location,
            reminder_minutes=reminder_minutes
        )
        return f"已添加一次性事件（ID: {event_id}）"
    
    @toolset.tool
    async def add_regular_schedule(
        ctx: RunContext[DepsType],
        title: str,
        time: str,
        frequency: str,
        description: str = "",
        duration: str = "1小时",
        reminder_minutes: int = 15
    ) -> str:
        """添加定期日程
        
        Args:
            title: 日程标题
            time: 时间（格式：HH:MM）
            frequency: 频率（每天、工作日、每周一、每周五等）
            description: 描述
            duration: 持续时间（如 "30分钟"）
            reminder_minutes: 提前提醒的分钟数
        """
        memory_sys = get_memory_system(ctx)
        schedule_id = memory_sys.add_recurring_schedule(
            title=title,
            start_time=time,
            duration=duration,
            frequency=frequency,
            description=description,
            reminder_minutes=reminder_minutes
        )
        return f"已添加定期日程（ID: {schedule_id}）"
    
    @toolset.tool
    async def assess_todo_urgency(
        ctx: RunContext[DepsType],
        todo_id: str
    ) -> str:
        """评估待办紧急程度
        
        Args:
            todo_id: 待办 ID
        """
        memory_sys = get_memory_system(ctx)
        todo = memory_sys.get_todo(todo_id)
        
        if not todo:
            return f"未找到待办事项（ID: {todo_id}）"
        
        priority = todo.get("priority", "medium")
        due_date = todo.get("due_date")
        today = get_current_date()
        
        # 评估逻辑
        urgency_score = 0
        
        # 优先级
        if priority == "high":
            urgency_score += 3
        elif priority == "medium":
            urgency_score += 2
        else:
            urgency_score += 1
        
        # 截止日期
        if due_date:
            if due_date < today:
                urgency_score += 5  # 已过期
            elif due_date == today:
                urgency_score += 4  # 今天到期
            else:
                from datetime import timedelta
                days_left = (parse_datetime(due_date + " 00:00:00") - parse_datetime(today + " 00:00:00")).days
                if days_left <= 1:
                    urgency_score += 3
                elif days_left <= 3:
                    urgency_score += 2
                elif days_left <= 7:
                    urgency_score += 1
        
        # 判断紧急程度
        if urgency_score >= 7:
            urgency = "非常紧急"
        elif urgency_score >= 5:
            urgency = "紧急"
        elif urgency_score >= 3:
            urgency = "中等"
        else:
            urgency = "低"
        
        return f"待办事项 '{todo.get('content', '')}' 的紧急程度：{urgency}（评分：{urgency_score}/10）"
    
    @toolset.tool
    async def find_available_time_slot(
        ctx: RunContext[DepsType],
        duration_minutes: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """查找可用时间段
        
        Args:
            duration_minutes: 需要的时长（分钟）
            start_date: 开始日期（格式：YYYY-MM-DD），默认今天
            end_date: 结束日期（格式：YYYY-MM-DD），默认一周后
        """
        memory_sys = get_memory_system(ctx)
        data = memory_sys.get_all_data()
        
        today = get_current_date()
        start_date = start_date or today
        
        from datetime import timedelta
        if end_date:
            end_dt = parse_datetime(end_date + " 00:00:00")
        else:
            end_dt = parse_datetime(start_date + " 00:00:00") + timedelta(days=7)
        
        # 获取所有日程
        schedule = data.get("schedule", {})
        all_events = []
        
        # 定期日程（需要展开）
        for regular in schedule.get("regular", []):
            # 简化：只检查今天到结束日期之间的工作日
            # 实际应该根据 frequency 展开
            pass
        
        # 一次性事件
        for event in schedule.get("upcoming", []):
            start_time = event.get("start_time")
            end_time = event.get("end_time")
            if start_time and end_time:
                all_events.append({
                    "start": parse_datetime(start_time),
                    "end": parse_datetime(end_time)
                })
        
        # 查找可用时间段（简化版：每天9:00-18:00，每小时检查）
        current_dt = parse_datetime(start_date + " 09:00:00")
        available_slots = []
        
        while current_dt < end_dt:
            # 检查这个时间段是否可用
            slot_end = current_dt + timedelta(minutes=duration_minutes)
            
            # 检查是否在工作时间内（9:00-18:00）
            if current_dt.hour >= 9 and slot_end.hour <= 18:
                # 检查是否与已有事件冲突
                conflict = False
                for event in all_events:
                    if time_overlap(
                        current_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        slot_end.strftime("%Y-%m-%d %H:%M:%S"),
                        event["start"].strftime("%Y-%m-%d %H:%M:%S"),
                        event["end"].strftime("%Y-%m-%d %H:%M:%S")
                    ):
                        conflict = True
                        break
                
                if not conflict:
                    available_slots.append({
                        "start": current_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": slot_end.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    if len(available_slots) >= 5:  # 最多返回5个
                        break
            
            # 下一个时间段（每小时）
            current_dt += timedelta(hours=1)
            
            # 如果超过一天，重置到第二天9点
            if current_dt.hour >= 18:
                current_dt = current_dt.replace(hour=9, minute=0, second=0) + timedelta(days=1)
        
        if not available_slots:
            return f"在 {start_date} 到 {end_date or '一周后'} 之间未找到可用时间段"
        
        result = [f"找到 {len(available_slots)} 个可用时间段：", ""]
        for slot in available_slots:
            result.append(f"- {slot['start']} 到 {slot['end']}")
        
        return "\n".join(result)
    
    @toolset.tool
    async def auto_schedule_todo(
        ctx: RunContext[DepsType],
        todo_id: str
    ) -> str:
        """智能安排待办时间段
        
        Args:
            todo_id: 待办 ID
        """
        memory_sys = get_memory_system(ctx)
        todo = memory_sys.get_todo(todo_id)
        
        if not todo:
            return f"未找到待办事项（ID: {todo_id}）"
        
        # 评估紧急程度
        urgency_result = await assess_todo_urgency(ctx, todo_id)
        
        # 获取预估时长
        estimated_duration = todo.get("estimated_duration", "1小时")
        duration_minutes = parse_duration(estimated_duration)
        
        # 查找可用时间段
        slot_result = await find_available_time_slot(ctx, duration_minutes)
        
        # 选择第一个可用时间段
        if "找到" in slot_result and "可用时间段" in slot_result:
            lines = slot_result.split("\n")
            if len(lines) > 2:
                first_slot = lines[2].replace("- ", "").split(" 到 ")
                if len(first_slot) == 2:
                    start_time = first_slot[0]
                    # 安排待办
                    memory_sys.schedule_todo(todo_id, start_time, estimated_duration)
                    return f"已自动安排待办事项到 {start_time}\n{urgency_result}"
        
        return f"无法自动安排待办事项：\n{urgency_result}\n{slot_result}"
    
    return toolset
