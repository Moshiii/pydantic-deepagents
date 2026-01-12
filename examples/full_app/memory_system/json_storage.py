"""
基于 JSON 的记忆存储实现（重构版本）

使用 JSON 格式存储所有记忆数据，所有操作通过ID进行，支持缓存和批量操作。
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .utils import (
    calculate_remind_time,
    format_datetime,
    generate_id,
    get_current_time,
    parse_datetime,
    parse_duration,
    time_overlap,
)


class JsonMemoryStorage:
    """基于 JSON 的记忆存储系统（重构版本）"""
    
    def __init__(
        self,
        user_id: str = "owner",
        memory_dir: str | Path = "./memories"
    ):
        self.user_id = user_id
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建用户专属目录：memories/owner/
        self.user_dir = self.memory_dir / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON 文件路径
        self.json_file = self.user_dir / "memory.json"
        
        # 缓存机制
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl: float = 60.0  # 缓存60秒
        
        # 初始化 JSON 文件
        self._initialize_json()
    
    def _initialize_json(self):
        """初始化 JSON 文件（如果不存在）"""
        if not self.json_file.exists():
            now = get_current_time()
            default_data = {
                "profile": {
                    "basic_info": {
                        "姓名": "",
                        "昵称": "",
                        "时区": "Asia/Shanghai (UTC+8)",
                        "语言": "zh-CN"
                    },
                    "preferences": {
                        "提醒方式": {
                            "默认提醒方式": "推送通知",
                            "重要事项提醒": "邮件 + 推送",
                            "提醒提前时间": "15分钟"
                        },
                        "工作习惯": {
                            "工作日": "周一至周五",
                            "工作时间": "09:00 - 18:00"
                        },
                        "内容偏好": {
                            "喜欢的主题": "",
                            "回复风格": "简洁、专业"
                        },
                        "日程偏好": {},
                        "询问偏好": {
                            "任务完成询问": "after_task_time",
                            "进度检查频率": "weekly",
                            "最小询问间隔小时数": 4
                        }
                    }
                },
                "todos": {
                    "pending": [],
                    "scheduled": [],
                    "in_progress": [],
                    "completed": []
                },
                "habits": {
                    "工作习惯": [],
                    "沟通习惯": [],
                    "生活习惯": []
                },
                "conversations": [],
                "diary": [],
                "schedule": {
                    "regular": [],
                    "upcoming": []
                },
                "relationships": {
                    "contacts": [],
                    "important": []
                },
                "reminders": [],
                "followups": [],
                "ideas": [],
                "metadata": {
                    "created_at": now,
                    "last_updated": now,
                    "conversation_count": 0,
                    "version": "2.0"
                }
            }
            self._write_json(default_data)
    
    def _read_json(self, use_cache: bool = True) -> Dict[str, Any]:
        """读取 JSON 文件（带缓存）"""
        if use_cache and self._cache is not None:
            if time.time() - self._cache_timestamp < self._cache_ttl:
                return self._cache
        
        if not self.json_file.exists():
            self._initialize_json()
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 如果文件损坏，重新初始化
            self._initialize_json()
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # 更新缓存
        self._cache = data
        self._cache_timestamp = time.time()
        
        return data
    
    def _write_json(self, data: Dict[str, Any], invalidate_cache: bool = True):
        """写入 JSON 文件（清除缓存）"""
        # 更新最后更新时间
        if "metadata" in data:
            data["metadata"]["last_updated"] = get_current_time()
        
        # 使用缩进使 JSON 文件更易读
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        if invalidate_cache:
            self._cache = None
            self._cache_timestamp = None
    
    def batch_update(self, operations: List[Callable[[Dict], Dict]]):
        """批量操作（原子性）
        
        Args:
            operations: 操作函数列表，每个函数接收data并返回修改后的data
        """
        data = self._read_json(use_cache=False)
        
        try:
            for op in operations:
                data = op(data)
            self._write_json(data, invalidate_cache=True)
        except Exception as e:
            # 回滚：重新读取文件
            self._cache = None
            self._cache_timestamp = None
            raise
    
    # ========== Profile 操作 ==========
    
    def update_profile(self, field: str, value: str):
        """更新个人档案基本信息"""
        data = self._read_json()
        data["profile"]["basic_info"][field] = value
        self._write_json(data)
    
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好设置"""
        if category == "基本信息":
            self.update_profile(key, value)
            return
        
        data = self._read_json()
        
        if category not in data["profile"]["preferences"]:
            data["profile"]["preferences"][category] = {}
        
        data["profile"]["preferences"][category][key] = value
        self._write_json(data)
    
    # ========== Todos 操作（重构：通过ID）==========
    
    def add_todo(
        self,
        content: str,
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        estimated_duration: Optional[str] = None,
        status: str = "pending"
    ) -> str:
        """添加待办事项，返回ID"""
        todo_id = generate_id("todo")
        now = get_current_time()
        
        data = self._read_json()
        
        todo_item = {
            "id": todo_id,
            "content": content,
            "priority": priority,
            "category": category,
            "estimated_duration": estimated_duration,
            "due_date": due_date,
            "scheduled_time": None,
            "reminder_minutes": 15,
            "created_at": now,
            "updated_at": now
        }
        
        if status not in data["todos"]:
            data["todos"][status] = []
        data["todos"][status].append(todo_item)
        self._write_json(data)
        
        return todo_id
    
    def get_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取待办"""
        data = self._read_json()
        
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            for todo in data["todos"].get(status, []):
                if todo.get("id") == todo_id:
                    return todo
        
        return None
    
    def find_todo_by_content(self, content: str) -> Optional[str]:
        """通过content查找ID（仅用于查询，不用于更新）"""
        data = self._read_json()
        
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            for todo in data["todos"].get(status, []):
                if todo.get("content") == content:
                    return todo.get("id")
        
        return None
    
    def update_todo(self, todo_id: str, **kwargs) -> bool:
        """更新待办（通过ID）"""
        data = self._read_json()
        
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            for todo in data["todos"].get(status, []):
                if todo.get("id") == todo_id:
                    # 更新字段
                    for key, value in kwargs.items():
                        if key != "id":  # 不允许修改ID
                            todo[key] = value
                    todo["updated_at"] = get_current_time()
                    self._write_json(data)
                    return True
        
        return False
    
    def complete_todo(self, todo_id: str) -> bool:
        """完成待办（通过ID）"""
        data = self._read_json()
        now = get_current_time()
        
        for status in ["pending", "scheduled", "in_progress"]:
            for todo in data["todos"].get(status, []):
                if todo.get("id") == todo_id:
                    todo["completed_at"] = now
                    todo["updated_at"] = now
                    # 移动到已完成列表
                    data["todos"]["completed"].append(todo)
                    data["todos"][status].remove(todo)
                    self._write_json(data)
                    return True
        
        return False
    
    def remove_todo(self, todo_id: str) -> bool:
        """删除待办（通过ID）"""
        data = self._read_json()
        
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            data["todos"][status] = [
                todo for todo in data["todos"].get(status, [])
                if todo.get("id") != todo_id
            ]
        
        self._write_json(data)
        return True
    
    def update_todo_status(self, todo_id: str, status: str) -> bool:
        """更新待办状态（pending/scheduled/in_progress/completed）"""
        data = self._read_json()
        
        # 找到待办
        todo = None
        old_status = None
        for s in ["pending", "scheduled", "in_progress", "completed"]:
            for t in data["todos"].get(s, []):
                if t.get("id") == todo_id:
                    todo = t
                    old_status = s
                    break
            if todo:
                break
        
        if not todo:
            return False
        
        # 移动到新状态
        if old_status:
            data["todos"][old_status].remove(todo)
        if status not in data["todos"]:
            data["todos"][status] = []
        data["todos"][status].append(todo)
        todo["updated_at"] = get_current_time()
        
        self._write_json(data)
        return True
    
    def schedule_todo(
        self,
        todo_id: str,
        start_time: str,
        duration: str,
        reminder_minutes: int = 15
    ) -> bool:
        """为待办安排时间预算"""
        data = self._read_json()
        
        # 找到待办
        todo = None
        old_status = None
        for status in ["pending", "scheduled", "in_progress"]:
            for t in data["todos"].get(status, []):
                if t.get("id") == todo_id:
                    todo = t
                    old_status = status
                    break
            if todo:
                break
        
        if not todo:
            return False
        
        # 计算结束时间
        start_dt = parse_datetime(start_time)
        duration_minutes = parse_duration(duration)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # 更新待办
        todo["scheduled_time"] = {
            "start": start_time,
            "end": format_datetime(end_dt),
            "duration": duration
        }
        todo["reminder_minutes"] = reminder_minutes
        todo["updated_at"] = get_current_time()
        
        # 移动到scheduled状态
        if old_status and old_status != "scheduled":
            data["todos"][old_status].remove(todo)
        if "scheduled" not in data["todos"]:
            data["todos"]["scheduled"] = []
        data["todos"]["scheduled"].append(todo)
        
        # 创建提醒
        self._create_reminder("todo", todo_id, start_time, reminder_minutes)
        
        # 创建询问任务
        ask_at_dt = end_dt + timedelta(hours=1)  # 任务结束后1小时询问
        self._create_followup("task_completion", todo_id, format_datetime(ask_at_dt))
        
        self._write_json(data)
        return True
    
    def query_todos(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        due_before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询待办"""
        data = self._read_json()
        
        results = []
        statuses = [status] if status else ["pending", "scheduled", "in_progress", "completed"]
        
        for s in statuses:
            for todo in data["todos"].get(s, []):
                # 过滤条件
                if category and todo.get("category") != category:
                    continue
                if due_before and todo.get("due_date"):
                    if todo["due_date"] > due_before:
                        continue
                results.append(todo)
        
        return results
    
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
        event_id = generate_id("event")
        now = get_current_time()
        
        # 计算duration或end_time
        if end_time:
            start_dt = parse_datetime(start_time)
            end_dt = parse_datetime(end_time)
            duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            duration = format_duration(duration_minutes)
        elif duration:
            start_dt = parse_datetime(start_time)
            duration_minutes = parse_duration(duration)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            end_time = format_datetime(end_dt)
        else:
            duration = "1小时"
            start_dt = parse_datetime(start_time)
            end_dt = start_dt + timedelta(hours=1)
            end_time = format_datetime(end_dt)
        
        data = self._read_json()
        
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "description": description,
            "location": location,
            "reminder_minutes": reminder_minutes,
            "created_at": now
        }
        
        data["schedule"]["upcoming"].append(event)
        
        # 自动创建提醒
        self._create_reminder("schedule", event_id, start_time, reminder_minutes)
        
        self._write_json(data)
        return event_id
    
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
        schedule_id = generate_id("recurring")
        now = get_current_time()
        
        data = self._read_json()
        
        event = {
            "id": schedule_id,
            "title": title,
            "time": start_time,
            "duration": duration,
            "frequency": frequency,
            "description": description,
            "end_date": end_date,
            "reminder_minutes": reminder_minutes,
            "created_at": now
        }
        
        data["schedule"]["regular"].append(event)
        self._write_json(data)
        return schedule_id
    
    def get_schedule_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取日程事件"""
        data = self._read_json()
        
        for event in data["schedule"].get("regular", []):
            if event.get("id") == event_id:
                return event
        
        for event in data["schedule"].get("upcoming", []):
            if event.get("id") == event_id:
                return event
        
        return None
    
    def check_time_conflict(
        self,
        start_time: str,
        end_time: str,
        exclude_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """检测时间冲突"""
        conflicts = []
        data = self._read_json()
        
        # 检查一次性事件
        for event in data["schedule"].get("upcoming", []):
            if exclude_id and event.get("id") == exclude_id:
                continue
            if time_overlap(start_time, end_time, event["start_time"], event.get("end_time")):
                conflicts.append(event)
        
        # 检查已安排的待办
        for todo in data["todos"].get("scheduled", []):
            if exclude_id and todo.get("id") == exclude_id:
                continue
            scheduled = todo.get("scheduled_time")
            if scheduled:
                if time_overlap(start_time, end_time, scheduled["start"], scheduled.get("end")):
                    conflicts.append(todo)
        
        return conflicts
    
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
        idea_id = generate_id("idea")
        now = get_current_time()
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        if not time:
            time = datetime.now().strftime("%H:%M")
        
        data = self._read_json()
        
        idea = {
            "id": idea_id,
            "content": content,
            "date": date,
            "time": time,
            "tags": tags or [],
            "category": category,
            "created_at": now
        }
        
        data["ideas"].append(idea)
        self._write_json(data)
        return idea_id
    
    def learn_schedule_preference(
        self,
        preference_type: str,
        value: str,
        confidence: float = 1.0,
        source: str = "explicit"
    ):
        """学习日程偏好"""
        data = self._read_json()
        
        if "日程偏好" not in data["profile"]["preferences"]:
            data["profile"]["preferences"]["日程偏好"] = {}
        
        preferences = data["profile"]["preferences"]["日程偏好"]
        
        if preference_type not in preferences:
            preferences[preference_type] = {
                "value": value,
                "confidence": confidence,
                "source": source,
                "learned_at": get_current_time()
            }
        else:
            # 更新现有偏好（如果置信度更高）
            existing = preferences[preference_type]
            if confidence >= existing.get("confidence", 0):
                existing["value"] = value
                existing["confidence"] = confidence
                existing["source"] = source
                existing["learned_at"] = get_current_time()
        
        self._write_json(data)
    
    def _create_reminder(
        self,
        reminder_type: str,
        target_id: str,
        remind_at: str,
        reminder_minutes: int
    ) -> str:
        """创建提醒任务（内部方法），返回ID"""
        reminder_id = generate_id("reminder")
        now = get_current_time()
        
        # 计算提醒时间
        if isinstance(remind_at, str):
            remind_dt = parse_datetime(remind_at) - timedelta(minutes=reminder_minutes)
            remind_at_str = format_datetime(remind_dt)
        else:
            remind_at_str = remind_at
        
        data = self._read_json()
        
        reminder = {
            "id": reminder_id,
            "type": reminder_type,
            "target_id": target_id,
            "remind_at": remind_at_str,
            "reminded": False,
            "reminder_minutes": reminder_minutes,
            "content": None,  # 可以后续生成
            "created_at": now
        }
        
        data["reminders"].append(reminder)
        self._write_json(data)
        return reminder_id
    
    def _create_followup(
        self,
        followup_type: str,
        target_id: str,
        ask_at: str,
        frequency: str = "after_task_time"
    ) -> str:
        """创建询问任务（内部方法），返回ID"""
        followup_id = generate_id("followup")
        now = get_current_time()
        
        data = self._read_json()
        
        followup = {
            "id": followup_id,
            "type": followup_type,
            "target_id": target_id,
            "ask_at": ask_at,
            "asked": False,
            "frequency": frequency,
            "content": None,  # 可以后续生成
            "created_at": now,
            "last_asked_at": None,
            "response_count": 0
        }
        
        data["followups"].append(followup)
        self._write_json(data)
        return followup_id
    
    def get_pending_reminders(self, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取待触发的提醒"""
        data = self._read_json()
        now = get_current_time()
        
        if before:
            before_dt = parse_datetime(before)
        else:
            before_dt = parse_datetime(now)
        
        results = []
        for reminder in data.get("reminders", []):
            if reminder.get("reminded"):
                continue
            remind_at = reminder.get("remind_at")
            if remind_at:
                remind_dt = parse_datetime(remind_at)
                if remind_dt <= before_dt:
                    results.append(reminder)
        
        return results
    
    def get_pending_followups(self, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取待触发的询问"""
        data = self._read_json()
        now = get_current_time()
        
        if before:
            before_dt = parse_datetime(before)
        else:
            before_dt = parse_datetime(now)
        
        results = []
        for followup in data.get("followups", []):
            if followup.get("asked"):
                continue
            ask_at = followup.get("ask_at")
            if ask_at:
                ask_dt = parse_datetime(ask_at)
                if ask_dt <= before_dt:
                    results.append(followup)
        
        return results
    
    def mark_reminder_triggered(self, reminder_id: str):
        """标记提醒已触发"""
        data = self._read_json()
        
        for reminder in data.get("reminders", []):
            if reminder.get("id") == reminder_id:
                reminder["reminded"] = True
                self._write_json(data)
                return
    
    def mark_followup_asked(self, followup_id: str):
        """标记询问已询问"""
        data = self._read_json()
        now = get_current_time()
        
        for followup in data.get("followups", []):
            if followup.get("id") == followup_id:
                followup["asked"] = True
                followup["last_asked_at"] = now
                followup["response_count"] = followup.get("response_count", 0) + 1
                self._write_json(data)
                return
    
    # ========== 其他操作 ==========
    
    def add_diary_entry(self, title: str, content: str):
        """添加日记条目"""
        data = self._read_json()
        now = get_current_time()
        
        entry = {
            "title": title,
            "content": content,
            "created_at": now
        }
        
        data["diary"].insert(0, entry)
        
        if len(data["diary"]) > 100:
            data["diary"] = data["diary"][:100]
        
        self._write_json(data)
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习新习惯"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d")
        
        habit_item = {
            "habit": habit,
            "learned_at": now
        }
        
        if category not in data["habits"]:
            data["habits"][category] = []
        
        data["habits"][category].append(habit_item)
        self._write_json(data)
    
    def add_relationship(self, name: str, relation: str, details: str = ""):
        """添加人际关系"""
        data = self._read_json()
        
        relationship = {
            "name": name,
            "relation": relation,
            "details": details,
            "created_at": get_current_time()
        }
        
        data["relationships"]["contacts"].append(relationship)
        self._write_json(data)
    
    def add_conversation(self, topic: str, summary: List[str]):
        """添加对话摘要"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d")
        
        conversation = {
            "date": now,
            "topic": topic,
            "summary": summary
        }
        
        data["conversations"].insert(0, conversation)
        
        if len(data["conversations"]) > 50:
            data["conversations"] = data["conversations"][:50]
        
        self._write_json(data)
    
    def get_context(self, sections: Optional[List[str]] = None) -> str:
        """获取记忆上下文（用于注入系统提示）"""
        data = self._read_json()
        context_parts = []
        
        if sections is None or "profile" in sections:
            context_parts.append("## 👤 个人档案")
            
            basic_info = data["profile"]["basic_info"]
            user_name = basic_info.get("姓名") or basic_info.get("昵称")
            
            if user_name:
                context_parts.append(f"### ⭐ 用户姓名：**{user_name}**")
                context_parts.append("")
                context_parts.append("**重要**：这是你的主人。你只在打招呼或对话开始时称呼用户为：" + user_name + "，让用户知道你记得他们。之后正常交流即可，不需要频繁提及名字。")
                context_parts.append("")
            
            context_parts.append("### 基本信息")
            for key, value in basic_info.items():
                if value:
                    context_parts.append(f"- {key}：{value}")
            context_parts.append("")
            
            preferences = data["profile"]["preferences"]
            if preferences:
                context_parts.append("### 偏好设置")
                for category, items in list(preferences.items())[:3]:
                    if items:
                        context_parts.append(f"#### {category}")
                        for key, value in list(items.items())[:3]:
                            if value:
                                context_parts.append(f"- {key}：{value}")
                context_parts.append("")
        
        if sections is None or "todos" in sections:
            all_todos = (
                data["todos"].get("in_progress", []) +
                data["todos"].get("scheduled", []) +
                data["todos"].get("pending", [])
            )
            if all_todos:
                context_parts.append("## 当前待办")
                for todo in all_todos[:5]:
                    priority_str = f"（优先级：{todo['priority']}）" if todo.get('priority') != 'medium' else ""
                    due_str = f"，截止：{todo['due_date']}" if todo.get('due_date') else ""
                    context_parts.append(f"- [ ] {todo['content']}{priority_str}{due_str}")
                context_parts.append("")
        
        if sections is None or "habits" in sections:
            habits = data["habits"]
            if any(habits.values()):
                context_parts.append("## 学习到的习惯")
                for category, habit_list in habits.items():
                    if habit_list:
                        context_parts.append(f"### {category}")
                        for habit_item in habit_list[-5:]:
                            context_parts.append(f"- {habit_item['habit']}")
                context_parts.append("")
        
        if sections is None or "schedule" in sections:
            regular_schedules = data["schedule"].get("regular", [])
            if regular_schedules:
                context_parts.append("## 📅 定期日程")
                for schedule in regular_schedules:
                    desc_str = f"（{schedule['description']}）" if schedule.get('description') else ""
                    context_parts.append(f"- **{schedule['title']}**：{schedule['time']}，{schedule['frequency']}{desc_str}")
                context_parts.append("")
            
            upcoming_events = data["schedule"].get("upcoming", [])
            if upcoming_events:
                context_parts.append("## 📅 即将到来的事件")
                for event in upcoming_events[:5]:
                    end_str = f"-{event['end_time']}" if event.get('end_time') else ""
                    desc_str = f"（{event['description']}）" if event.get('description') else ""
                    context_parts.append(f"- **{event['title']}**：{event['start_time']}{end_str}{desc_str}")
                context_parts.append("")
        
        if sections is None or "conversations" in sections:
            conversations = data["conversations"]
            if conversations:
                context_parts.append("## 最近对话摘要")
                for conv in conversations[:3]:
                    context_parts.append(f"### {conv['date']} - {conv['topic']}")
                    for point in conv['summary'][:3]:
                        context_parts.append(f"  - {point}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def increment_conversation_count(self):
        """增加对话计数"""
        data = self._read_json()
        data["metadata"]["conversation_count"] = data["metadata"].get("conversation_count", 0) + 1
        self._write_json(data)
    
    # ========== 便捷访问方法 ==========
    
    @property
    def json_path(self) -> Path:
        """获取 JSON 文件路径"""
        return self.json_file
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据（用于调试或导出）"""
        return self._read_json()
    
    def set_all_data(self, data: Dict[str, Any]):
        """设置所有数据（用于导入或迁移）"""
        self._write_json(data, invalidate_cache=True)
