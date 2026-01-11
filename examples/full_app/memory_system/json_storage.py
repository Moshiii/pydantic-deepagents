"""
基于 JSON 的记忆存储实现

使用 JSON 格式存储所有记忆数据，避免 Markdown 解析的复杂性和潜在问题。
数据结构清晰，易于读写和维护。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class JsonMemoryStorage:
    """基于 JSON 的记忆存储系统"""
    
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
        
        # 初始化 JSON 文件
        self._initialize_json()
    
    def _initialize_json(self):
        """初始化 JSON 文件（如果不存在）"""
        if not self.json_file.exists():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                        }
                    }
                },
                "todos": {
                    "in_progress": [],
                    "pending": [],
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
                "metadata": {
                    "created_at": now,
                    "last_updated": now,
                    "conversation_count": 0
                }
            }
            self._write_json(default_data)
    
    def _read_json(self) -> Dict[str, Any]:
        """读取 JSON 文件"""
        if not self.json_file.exists():
            self._initialize_json()
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 如果文件损坏，重新初始化
            self._initialize_json()
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _write_json(self, data: Dict[str, Any]):
        """写入 JSON 文件"""
        # 更新最后更新时间
        if "metadata" in data:
            data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用缩进使 JSON 文件更易读
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== Profile 操作 ==========
    
    def update_profile(self, field: str, value: str):
        """更新个人档案基本信息"""
        data = self._read_json()
        data["profile"]["basic_info"][field] = value
        self._write_json(data)
    
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好设置
        
        如果 category 是"基本信息"，则更新基本信息表格中的字段
        否则更新偏好设置中的项
        """
        # 特殊处理：如果 category 是"基本信息"，则更新基本信息
        if category == "基本信息":
            self.update_profile(key, value)
            return
        
        data = self._read_json()
        
        # 确保偏好类别存在
        if category not in data["profile"]["preferences"]:
            data["profile"]["preferences"][category] = {}
        
        # 更新偏好值
        data["profile"]["preferences"][category][key] = value
        self._write_json(data)
    
    # ========== Todos 操作 ==========
    
    def add_todo(self, content: str, priority: str = "medium", due_date: Optional[str] = None, status: str = "pending"):
        """添加待办事项"""
        data = self._read_json()
        
        todo_item = {
            "content": content,
            "priority": priority,
            "due_date": due_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到对应状态列表
        data["todos"][status].append(todo_item)
        self._write_json(data)
    
    def complete_todo(self, content: str):
        """完成待办事项"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d")
        
        # 在所有状态中查找待办
        for status in ["pending", "in_progress"]:
            for todo in data["todos"][status]:
                if todo["content"] == content:
                    # 标记为完成
                    todo["completed_at"] = now
                    # 移动到已完成列表
                    data["todos"]["completed"].append(todo)
                    data["todos"][status].remove(todo)
                    self._write_json(data)
                    return
    
    def remove_todo(self, content: str):
        """删除待办事项（用于清理重复或已转为日程的待办）"""
        data = self._read_json()
        
        # 在所有状态中查找并删除
        for status in ["pending", "in_progress", "completed"]:
            data["todos"][status] = [
                todo for todo in data["todos"][status]
                if todo["content"] != content
            ]
        
        self._write_json(data)
    
    # ========== Diary 操作 ==========
    
    def add_diary_entry(self, title: str, content: str):
        """添加日记条目"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            "title": title,
            "content": content,
            "created_at": now
        }
        
        # 添加到日记列表开头
        data["diary"].insert(0, entry)
        
        # 只保留最近 100 条日记
        if len(data["diary"]) > 100:
            data["diary"] = data["diary"][:100]
        
        self._write_json(data)
    
    # ========== Schedule 操作 ==========
    
    def add_schedule_event(self, title: str, start_time: str, end_time: Optional[str] = None, description: str = ""):
        """添加一次性日程事件"""
        data = self._read_json()
        
        event = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到即将到来的事件列表
        data["schedule"]["upcoming"].append(event)
        self._write_json(data)
    
    def add_regular_schedule(self, title: str, time: str, frequency: str, description: str = ""):
        """添加重复性日程
        
        Args:
            title: 日程标题
            time: 时间（格式：HH:MM，如 "10:00"）
            frequency: 频率（如 "每天"、"工作日"、"每周一"、"每周五"、"每月1号"等）
            description: 备注说明
        """
        data = self._read_json()
        
        event = {
            "title": title,
            "time": time,
            "frequency": frequency,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到定期日程列表
        data["schedule"]["regular"].append(event)
        self._write_json(data)
    
    # ========== Habits 操作 ==========
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习新习惯"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d")
        
        habit_item = {
            "habit": habit,
            "learned_at": now
        }
        
        # 确保类别存在
        if category not in data["habits"]:
            data["habits"][category] = []
        
        # 添加到对应类别
        data["habits"][category].append(habit_item)
        self._write_json(data)
    
    # ========== Relationships 操作 ==========
    
    def add_relationship(self, name: str, relation: str, details: str = ""):
        """添加人际关系"""
        data = self._read_json()
        
        relationship = {
            "name": name,
            "relation": relation,
            "details": details,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到常用联系人列表
        data["relationships"]["contacts"].append(relationship)
        self._write_json(data)
    
    # ========== Conversations 操作 ==========
    
    def add_conversation(self, topic: str, summary: List[str]):
        """添加对话摘要"""
        data = self._read_json()
        now = datetime.now().strftime("%Y-%m-%d")
        
        conversation = {
            "date": now,
            "topic": topic,
            "summary": summary
        }
        
        # 添加到对话列表开头
        data["conversations"].insert(0, conversation)
        
        # 只保留最近 50 条对话
        if len(data["conversations"]) > 50:
            data["conversations"] = data["conversations"][:50]
        
        self._write_json(data)
    
    # ========== 读取操作 ==========
    
    def get_context(self, sections: Optional[List[str]] = None) -> str:
        """获取记忆上下文（用于注入系统提示）"""
        data = self._read_json()
        context_parts = []
        
        if sections is None or "profile" in sections:
            context_parts.append("## 👤 个人档案")
            
            # 基本信息 - 突出显示用户名字
            basic_info = data["profile"]["basic_info"]
            user_name = basic_info.get("姓名") or basic_info.get("昵称")
            
            if user_name:
                context_parts.append(f"### ⭐ 用户姓名：**{user_name}**")
                context_parts.append("")
                context_parts.append("**重要**：这是你的主人，你必须称呼用户为：" + user_name)
                context_parts.append("")
            
            context_parts.append("### 基本信息")
            for key, value in basic_info.items():
                if value:
                    context_parts.append(f"- {key}：{value}")
            context_parts.append("")
            
            # 偏好设置（只显示前几个）
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
            # 合并所有状态的待办，优先显示进行中的
            all_todos = data["todos"].get("in_progress", []) + data["todos"].get("pending", [])
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
                        for habit_item in habit_list[-5:]:  # 最近5个
                            context_parts.append(f"- {habit_item['habit']}")
                context_parts.append("")
        
        if sections is None or "schedule" in sections:
            # 定期日程
            regular_schedules = data["schedule"].get("regular", [])
            if regular_schedules:
                context_parts.append("## 📅 定期日程")
                for schedule in regular_schedules:
                    desc_str = f"（{schedule['description']}）" if schedule.get('description') else ""
                    context_parts.append(f"- **{schedule['title']}**：{schedule['time']}，{schedule['frequency']}{desc_str}")
                context_parts.append("")
            
            # 即将到来的事件
            upcoming_events = data["schedule"].get("upcoming", [])
            if upcoming_events:
                context_parts.append("## 📅 即将到来的事件")
                for event in upcoming_events[:5]:  # 最近5个
                    end_str = f"-{event['end_time']}" if event.get('end_time') else ""
                    desc_str = f"（{event['description']}）" if event.get('description') else ""
                    context_parts.append(f"- **{event['title']}**：{event['start_time']}{end_str}{desc_str}")
                context_parts.append("")
        
        if sections is None or "conversations" in sections:
            conversations = data["conversations"]
            if conversations:
                context_parts.append("## 最近对话摘要")
                for conv in conversations[:3]:  # 最近3条
                    context_parts.append(f"### {conv['date']} - {conv['topic']}")
                    for point in conv['summary'][:3]:  # 前3个要点
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
        self._write_json(data)
