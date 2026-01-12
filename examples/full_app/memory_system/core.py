"""
记忆系统核心模块（重构版本）

提供高级接口，所有操作委托给 JsonMemoryStorage。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .json_storage import JsonMemoryStorage


class MemorySystem:
    """记忆系统主类 - 提供高级接口
    
    使用 JSON 格式存储所有记忆数据：
    memories/
      owner/
        memory.json      # 所有记忆数据（JSON 格式）
    """
    
    def __init__(
        self,
        user_id: str,
        memory_dir: str | Path = "./memories"
    ):
        self.user_id = user_id
        self.memory_dir = Path(memory_dir)
        
        # 使用 JSON 存储
        self.storage = JsonMemoryStorage(user_id=user_id, memory_dir=memory_dir)
    
    def get_context(self, sections: Optional[List[str]] = None) -> str:
        """获取记忆上下文（用于注入系统提示）
        
        Args:
            sections: 要包含的章节列表，None 表示全部
        """
        return self.storage.get_context(sections)
    
    # ========== Profile 操作 ==========
    
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好"""
        self.storage.update_preference(category, key, value)
    
    def update_profile(self, field: str, value: str):
        """更新个人档案基本信息"""
        self.storage.update_profile(field, value)
    
    # ========== Todos 操作（新API：通过ID）==========
    
    def add_todo(
        self,
        content: str,
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        estimated_duration: Optional[str] = None,
        status: str = "pending"
    ) -> str:
        """添加待办，返回ID"""
        return self.storage.add_todo(
            content, priority, due_date, category, estimated_duration, status
        )
    
    def get_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取待办"""
        return self.storage.get_todo(todo_id)
    
    def find_todo_by_content(self, content: str) -> Optional[str]:
        """通过content查找ID（仅用于查询）"""
        return self.storage.find_todo_by_content(content)
    
    def update_todo(self, todo_id: str, **kwargs) -> bool:
        """更新待办（通过ID）"""
        return self.storage.update_todo(todo_id, **kwargs)
    
    def complete_todo(self, todo_id: str) -> bool:
        """完成待办（通过ID）"""
        return self.storage.complete_todo(todo_id)
    
    def remove_todo(self, todo_id: str) -> bool:
        """删除待办（通过ID）"""
        return self.storage.remove_todo(todo_id)
    
    def update_todo_status(self, todo_id: str, status: str) -> bool:
        """更新待办状态"""
        return self.storage.update_todo_status(todo_id, status)
    
    def schedule_todo(
        self,
        todo_id: str,
        start_time: str,
        duration: str,
        reminder_minutes: int = 15
    ) -> bool:
        """为待办安排时间预算"""
        return self.storage.schedule_todo(todo_id, start_time, duration, reminder_minutes)
    
    def query_todos(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        due_before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询待办"""
        return self.storage.query_todos(status, category, due_before)
    
    # ========== Schedule 操作（扩展）==========
    
    def add_one_time_event(
        self,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        duration: Optional[str] = None,
        description: str = "",
        location: Optional[str] = None,
        reminder_minutes: int = 15
    ) -> str:
        """添加一次性事件，返回ID"""
        return self.storage.add_one_time_event(
            title, start_time, end_time, duration, description, location, reminder_minutes
        )
    
    def add_recurring_schedule(
        self,
        title: str,
        start_time: str,
        duration: str,
        frequency: str,
        description: str = "",
        end_date: Optional[str] = None,
        reminder_minutes: int = 15
    ) -> str:
        """添加周期性日程，返回ID"""
        return self.storage.add_recurring_schedule(
            title, start_time, duration, frequency, description, end_date, reminder_minutes
        )
    
    def get_schedule_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取日程事件"""
        return self.storage.get_schedule_event(event_id)
    
    def check_time_conflict(
        self,
        start_time: str,
        end_time: str,
        exclude_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """检测时间冲突"""
        return self.storage.check_time_conflict(start_time, end_time, exclude_id)
    
    # ========== 新增功能 ==========
    
    def add_idea(
        self,
        content: str,
        date: Optional[str] = None,
        time: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> str:
        """添加创意想法，返回ID"""
        return self.storage.add_idea(content, date, time, tags, category)
    
    def learn_schedule_preference(
        self,
        preference_type: str,
        value: str,
        confidence: float = 1.0,
        source: str = "explicit"
    ):
        """学习日程偏好"""
        self.storage.learn_schedule_preference(preference_type, value, confidence, source)
    
    def get_pending_reminders(self, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取待触发的提醒"""
        return self.storage.get_pending_reminders(before)
    
    def get_pending_followups(self, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取待触发的询问"""
        return self.storage.get_pending_followups(before)
    
    def mark_reminder_triggered(self, reminder_id: str):
        """标记提醒已触发"""
        self.storage.mark_reminder_triggered(reminder_id)
    
    def mark_followup_asked(self, followup_id: str):
        """标记询问已询问"""
        self.storage.mark_followup_asked(followup_id)
    
    # ========== 其他操作 ==========
    
    def add_memory(self, topic: str, points: List[str]):
        """添加记忆（对话摘要）"""
        self.storage.add_conversation(topic, points)
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习习惯"""
        self.storage.learn_habit(habit, category)
    
    def add_regular_schedule(
        self,
        title: str,
        time: str,
        frequency: str,
        description: str = "",
        duration: str = "1小时"
    ) -> str:
        """添加重复性日程"""
        return self.storage.add_recurring_schedule(
            title, time, duration, frequency, description
        )
    
    def increment_conversation_count(self):
        """增加对话计数"""
        self.storage.increment_conversation_count()
    
    # ========== 便捷访问 ==========
    
    @property
    def json_path(self) -> Path:
        """获取 JSON 文件路径"""
        return self.storage.json_path
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据"""
        return self.storage.get_all_data()
