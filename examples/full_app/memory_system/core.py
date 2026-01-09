"""
记忆系统核心模块 - 零依赖实现

只使用 Python 标准库，不依赖任何第三方包。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class MemoryData:
    """记忆数据结构"""
    user_id: str
    basic_info: Dict[str, str] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    schedules: List[Dict[str, Any]] = field(default_factory=list)
    todos: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "in_progress": [],
        "pending": [],
        "completed": []
    })
    learned_habits: List[Dict[str, str]] = field(default_factory=list)
    important_memories: List[Dict[str, Any]] = field(default_factory=list)
    long_term_goals: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    associations: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    last_updated: Optional[str] = None
    version: str = "1.0"


class MemoryParser:
    """Markdown 记忆文件解析器 - 纯 Python 实现"""
    
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.content = self._read_file() if self.file_path.exists() else ""
    
    def _read_file(self) -> str:
        """读取文件内容"""
        try:
            return self.file_path.read_text(encoding='utf-8')
        except Exception:
            return ""
    
    def parse(self) -> MemoryData:
        """解析整个文件"""
        if not self.content:
            # 返回空记忆数据
            return MemoryData(user_id=self._extract_user_id_from_path())
        
        return MemoryData(
            user_id=self._extract_user_id_from_path(),
            basic_info=self._parse_basic_info(),
            preferences=self._parse_preferences(),
            schedules=self._parse_schedules(),
            todos=self._parse_todos(),
            learned_habits=self._parse_learned_habits(),
            important_memories=self._parse_important_memories(),
            long_term_goals=self._parse_long_term_goals(),
            statistics=self._parse_statistics(),
            associations=self._parse_associations(),
            last_updated=self._extract_last_updated(),
            version=self._extract_version()
        )
    
    def _extract_user_id_from_path(self) -> str:
        """从文件路径提取 user_id"""
        name = self.file_path.stem
        if name.startswith("memory_"):
            return name.replace("memory_", "")
        return name
    
    def _extract_last_updated(self) -> Optional[str]:
        """提取最后更新时间"""
        match = re.search(r'> 最后更新：(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', self.content)
        return match.group(1) if match else None
    
    def _extract_version(self) -> str:
        """提取版本号"""
        match = re.search(r'> 版本：([\d.]+)', self.content)
        return match.group(1) if match else "1.0"
    
    def _parse_basic_info(self) -> Dict[str, str]:
        """解析基本信息表格"""
        pattern = r'## 📋 基本信息\n\n(.*?)\n\n---'
        match = re.search(pattern, self.content, re.DOTALL)
        if not match:
            return {}
        
        table_content = match.group(1)
        info = {}
        for line in table_content.split('\n'):
            if '|' in line and not line.startswith('|--') and line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3 and parts[1] and parts[2]:
                    info[parts[1]] = parts[2]
        return info
    
    def _parse_preferences(self) -> Dict[str, Any]:
        """解析偏好设置"""
        preferences = {}
        
        # 解析提醒方式
        reminder_section = self._extract_section("提醒方式")
        if reminder_section:
            preferences["提醒方式"] = self._parse_list_items(reminder_section)
        
        # 解析工作习惯
        work_section = self._extract_section("工作习惯")
        if work_section:
            preferences["工作习惯"] = self._parse_list_items(work_section)
        
        # 解析内容偏好
        content_section = self._extract_section("内容偏好")
        if content_section:
            preferences["内容偏好"] = self._parse_list_items(content_section)
        
        # 解析其他偏好
        other_section = self._extract_section("其他偏好")
        if other_section:
            preferences["其他偏好"] = self._parse_list_items(other_section)
        
        return preferences
    
    def _extract_section(self, section_name: str) -> Optional[str]:
        """提取指定章节内容"""
        pattern = rf'### {re.escape(section_name)}\n(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, self.content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _parse_list_items(self, content: str) -> List[str]:
        """解析列表项"""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:].strip())
        return items
    
    def _parse_schedules(self) -> List[Dict[str, Any]]:
        """解析日程安排"""
        schedules = []
        
        # 解析定期日程表格
        pattern = r'### 定期日程\n\n(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, self.content, re.DOTALL)
        if match:
            table_content = match.group(1)
            for line in table_content.split('\n'):
                if '|' in line and not line.startswith('|--') and line.strip().startswith('|'):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        schedules.append({
                            "time": parts[1],
                            "event": parts[2],
                            "frequency": parts[3],
                            "note": parts[4] if len(parts) > 4 else ""
                        })
        
        return schedules
    
    def _parse_todos(self) -> Dict[str, List[Dict[str, Any]]]:
        """解析待办事项"""
        todos = {
            "in_progress": [],
            "pending": [],
            "completed": []
        }
        
        # 解析各个待办列表
        for status in ["进行中", "待开始", "已完成"]:
            pattern = rf'### {status}\n(.*?)(?=\n### |\n## |$)'
            match = re.search(pattern, self.content, re.DOTALL)
            if match:
                content = match.group(1)
                key = "in_progress" if status == "进行中" else ("pending" if status == "待开始" else "completed")
                todos[key] = self._parse_todo_items(content)
        
        return todos
    
    def _parse_todo_items(self, content: str) -> List[Dict[str, Any]]:
        """解析待办项列表"""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- ['):
                # 解析格式：- [ ] 内容（优先级：，截止：）
                # 或：- [x] 内容（完成时间：）
                checked = '[x]' in line or '[X]' in line
                content_part = re.sub(r'^- \[[xX ]\]\s*', '', line)
                
                # 提取优先级和截止日期
                priority_match = re.search(r'优先级：([^，,]+)', content_part)
                due_match = re.search(r'截止：([^，,)]+)', content_part)
                completed_match = re.search(r'完成时间：([^，,)]+)', content_part)
                
                items.append({
                    "content": re.sub(r'（.*?）', '', content_part).strip(),
                    "priority": priority_match.group(1).strip() if priority_match else "medium",
                    "due_date": due_match.group(1).strip() if due_match else None,
                    "completed_at": completed_match.group(1).strip() if completed_match else None,
                    "checked": checked
                })
        
        return items
    
    def _parse_learned_habits(self) -> List[Dict[str, str]]:
        """解析学习到的习惯"""
        habits = []
        
        for category in ["工作习惯", "沟通习惯", "生活习惯"]:
            section = self._extract_section(category)
            if section:
                for item in self._parse_list_items(section):
                    # 提取学习时间
                    time_match = re.search(r'（学习时间：([^）)]+)）', item)
                    habit_text = re.sub(r'（学习时间：.*?）', '', item).strip()
                    habits.append({
                        "category": category,
                        "habit": habit_text,
                        "learned_at": time_match.group(1) if time_match else None
                    })
        
        return habits
    
    def _parse_important_memories(self) -> List[Dict[str, Any]]:
        """解析重要记忆"""
        memories = []
        
        pattern = r'### (\d{4}-\d{2}-\d{2})\n\*\*对话主题：(.*?)\*\*\n(.*?)(?=\n### \d{4}-|\n## |$)'
        matches = re.finditer(pattern, self.content, re.DOTALL)
        
        for match in matches:
            date = match.group(1)
            topic = match.group(2).strip()
            content = match.group(3).strip()
            
            # 解析内容中的要点
            points = []
            for line in content.split('\n'):
                if line.strip().startswith('- '):
                    points.append(line.strip()[2:])
            
            memories.append({
                "date": date,
                "topic": topic,
                "points": points,
                "content": content
            })
        
        return memories
    
    def _parse_long_term_goals(self) -> List[Dict[str, Any]]:
        """解析长期目标"""
        goals = []
        
        pattern = r'### (\d{4}年目标)\n(.*?)(?=\n## |$)'
        match = re.search(pattern, self.content, re.DOTALL)
        if match:
            content = match.group(2)
            # 解析目标项
            goal_pattern = r'\d+\. \*\*(.*?)\*\*\n(.*?)(?=\d+\. |$)'
            for goal_match in re.finditer(goal_pattern, content, re.DOTALL):
                goal_name = goal_match.group(1).strip()
                goal_content = goal_match.group(2).strip()
                
                # 提取完成度
                progress_match = re.search(r'目标完成度：(\d+)%', goal_content)
                progress = int(progress_match.group(1)) if progress_match else 0
                
                goals.append({
                    "name": goal_name,
                    "content": goal_content,
                    "progress": progress
                })
        
        return goals
    
    def _parse_statistics(self) -> Dict[str, Any]:
        """解析统计数据"""
        stats = {}
        
        # 解析交互统计
        interaction_section = self._extract_section("交互统计")
        if interaction_section:
            stats["交互统计"] = self._parse_stat_items(interaction_section)
        
        # 解析任务统计
        task_section = self._extract_section("任务统计")
        if task_section:
            stats["任务统计"] = self._parse_stat_items(task_section)
        
        return stats
    
    def _parse_stat_items(self, content: str) -> Dict[str, Any]:
        """解析统计项"""
        items = {}
        for line in content.split('\n'):
            if '- ' in line:
                # 格式：- 字段：`值`
                match = re.search(r'- (.*?)：`(.*?)`', line)
                if match:
                    items[match.group(1).strip()] = match.group(2).strip()
        return items
    
    def _parse_associations(self) -> Dict[str, List[Dict[str, Any]]]:
        """解析关联信息"""
        associations = {
            "contacts": [],
            "projects": [],
            "files": []
        }
        
        # 解析联系人
        contacts_section = self._extract_section("常用联系人")
        if contacts_section:
            associations["contacts"] = self._parse_contacts(contacts_section)
        
        # 解析项目
        projects_section = self._extract_section("常用项目")
        if projects_section:
            associations["projects"] = self._parse_projects(projects_section)
        
        # 解析文件
        files_section = self._extract_section("重要文件")
        if files_section:
            associations["files"] = self._parse_files(files_section)
        
        return associations
    
    def _parse_contacts(self, content: str) -> List[Dict[str, Any]]:
        """解析联系人"""
        contacts = []
        # 简化解析，提取基本信息
        pattern = r'- \*\*(.*?)\*\* - (.*?)\n(.*?)(?=\n- \*\*|\n### |$)'
        for match in re.finditer(pattern, content, re.DOTALL):
            contacts.append({
                "name": match.group(1).strip(),
                "relation": match.group(2).strip(),
                "details": match.group(3).strip()
            })
        return contacts
    
    def _parse_projects(self, content: str) -> List[Dict[str, Any]]:
        """解析项目"""
        projects = []
        pattern = r'- \*\*(.*?)\*\* - (.*?)\n(.*?)(?=\n- \*\*|\n### |$)'
        for match in re.finditer(pattern, content, re.DOTALL):
            projects.append({
                "name": match.group(1).strip(),
                "status": match.group(2).strip(),
                "details": match.group(3).strip()
            })
        return projects
    
    def _parse_files(self, content: str) -> List[Dict[str, Any]]:
        """解析文件"""
        files = []
        for line in content.split('\n'):
            if line.strip().startswith('- '):
                files.append({"path": line.strip()[2:]})
        return files


class MemoryUpdater:
    """记忆文件更新器 - 纯 Python 实现"""
    
    def __init__(self, file_path: str | Path, template_path: Optional[str | Path] = None):
        self.file_path = Path(file_path)
        self.template_path = Path(template_path) if template_path else None
        self.parser = MemoryParser(self.file_path)
        
        # 确保目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件不存在，从模板创建
        if not self.file_path.exists():
            self._create_from_template()
    
    def _create_from_template(self):
        """从模板创建文件"""
        if self.template_path and self.template_path.exists():
            template = self.template_path.read_text(encoding='utf-8')
            # 替换 user_id
            user_id = self.parser._extract_user_id_from_path()
            content = template.replace("user_id", user_id)
            self.file_path.write_text(content, encoding='utf-8')
        else:
            # 创建最小模板
            self._create_minimal_template()
    
    def _create_minimal_template(self):
        """创建最小模板"""
        user_id = self.parser._extract_user_id_from_path()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        template = f"""# 用户记忆档案

> 最后更新：{now}
> 版本：1.0

---

## 📋 基本信息

| 字段 | 值 |
|------|-----|
| 姓名 |  |
| 昵称 |  |
| 时区 | Asia/Shanghai (UTC+8) |
| 语言 | zh-CN |
| 创建时间 | {datetime.now().strftime("%Y-%m-%d")} |
| 最后活跃 | {now} |

---

## ⚙️ 偏好设置

### 提醒方式
- 默认提醒方式：`推送通知`
- 重要事项提醒：`邮件 + 推送`
- 提醒提前时间：`15分钟`

### 工作习惯
- 工作日：`周一至周五`
- 工作时间：`09:00 - 18:00`

### 内容偏好
- 喜欢的主题：``
- 回复风格：`简洁、专业`

---

## 📅 日程安排

### 定期日程

| 时间 | 事项 | 频率 | 备注 |
|------|------|------|------|
|  |  |  |  |

---

## ✅ 待办事项

### 进行中
- [ ] 

### 待开始
- [ ] 

### 已完成
- [x] 

---

## 🧠 学习到的习惯

### 工作习惯
- 

### 沟通习惯
- 

### 生活习惯
- 

---

## 📝 重要记忆

---

## 🎯 长期目标

---

## 📊 统计数据

### 交互统计
- 总对话次数：`0`
- 平均每天对话：`0次`

### 任务统计
- 已完成任务：`0`
- 进行中任务：`0`

---

## 🔗 关联信息

### 常用联系人
- 

### 常用项目
- 

### 重要文件
- 

---

## 🔄 更新日志

### {datetime.now().strftime("%Y-%m-%d")}
- 初始化记忆文件

---

*此文件由 AI 助手自动维护，用户可随时编辑*
"""
        self.file_path.write_text(template, encoding='utf-8')
    
    def _read_content(self) -> str:
        """读取文件内容"""
        return self.file_path.read_text(encoding='utf-8')
    
    def _write_content(self, content: str):
        """写入文件内容"""
        self.file_path.write_text(content, encoding='utf-8')
    
    def update_basic_info(self, field: str, value: str):
        """更新基本信息"""
        content = self._read_content()
        
        # 查找并更新表格中的值
        pattern = rf'\| {re.escape(field)} \| (.*?) \|'
        replacement = f'| {field} | {value} |'
        content = re.sub(pattern, replacement, content)
        
        # 更新最后更新时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now}', content)
        
        self._write_content(content)
    
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好设置"""
        content = self._read_content()
        
        # 查找对应的章节
        pattern = rf'(### {re.escape(category)}\n.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            # 查找并更新对应的项
            item_pattern = rf'- {re.escape(key)}：`(.*?)`'
            if re.search(item_pattern, section):
                new_section = re.sub(item_pattern, f'- {key}：`{value}`', section)
                content = content.replace(section, new_section)
            else:
                # 添加新项
                new_section = section.rstrip() + f'\n- {key}：`{value}`\n'
                content = content.replace(section, new_section)
        
        # 更新最后更新时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now}', content)
        
        self._write_content(content)
    
    def add_todo(self, todo_content: str, priority: str = "medium", due_date: Optional[str] = None, status: str = "pending"):
        """添加待办事项"""
        content = self._read_content()
        
        # 确定要添加到的章节
        status_map = {"pending": "待开始", "in_progress": "进行中", "completed": "已完成"}
        section_name = status_map.get(status, "待开始")
        
        # 构建待办项
        due_str = f"，截止：{due_date}" if due_date else ""
        priority_str = f"，优先级：{priority}" if priority != "medium" else ""
        todo_item = f"- [ ] {todo_content}（{priority_str}{due_str}）"
        
        # 查找对应章节并添加
        pattern = rf'(### {re.escape(section_name)}\n)(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section_header = match.group(1)
            section_content = match.group(2)
            new_content = section_header + section_content.rstrip() + f'\n{todo_item}\n'
            content = content.replace(match.group(0), new_content)
        
        # 更新最后更新时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now}', content)
        
        self._write_content(content)
    
    def complete_todo(self, todo_content: str):
        """完成待办事项"""
        content = self._read_content()
        
        # 查找待办项并标记为完成
        pattern = rf'- \[ \] {re.escape(todo_content)}.*?'
        now = datetime.now().strftime("%Y-%m-%d")
        replacement = f'- [x] {todo_content}（完成时间：{now}）'
        content = re.sub(pattern, replacement, content)
        
        # 可能需要移动到已完成章节
        # 这里简化处理，只标记为完成
        
        # 更新最后更新时间
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now_str}', content)
        
        self._write_content(content)
    
    def add_memory(self, date: str, topic: str, points: List[str]):
        """添加重要记忆"""
        content = self._read_content()
        
        # 构建记忆内容
        memory_text = f"\n### {date}\n**对话主题：{topic}**\n"
        for point in points:
            memory_text += f"- {point}\n"
        memory_text += "\n"
        
        # 插入到重要记忆章节
        pattern = r'(## 📝 重要记忆\n)(.*?)(?=\n## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            header = match.group(1)
            existing = match.group(2)
            new_section = header + memory_text + existing
            content = content.replace(match.group(0), new_section)
        
        # 更新最后更新时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now}', content)
        
        self._write_content(content)
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习新习惯"""
        content = self._read_content()
        
        now = datetime.now().strftime("%Y-%m-%d")
        habit_item = f"- {habit}（学习时间：{now}）\n"
        
        # 查找对应章节
        pattern = rf'(### {re.escape(category)}\n)(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            header = match.group(1)
            existing = match.group(2)
            new_section = header + existing.rstrip() + f'\n{habit_item}'
            content = content.replace(match.group(0), new_section)
        
        # 更新最后更新时间
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now_str}', content)
        
        self._write_content(content)
    
    def increment_statistic(self, stat_name: str, increment: int = 1):
        """增加统计值"""
        content = self._read_content()
        
        # 查找统计值并更新
        pattern = rf'- {re.escape(stat_name)}：`(\d+)`'
        match = re.search(pattern, content)
        if match:
            current_value = int(match.group(1))
            new_value = current_value + increment
            content = re.sub(pattern, f'- {stat_name}：`{new_value}`', content)
        
        # 更新最后更新时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'> 最后更新：.*?', f'> 最后更新：{now}', content)
        
        self._write_content(content)


class MemorySystem:
    """记忆系统主类 - 提供高级接口
    
    支持分门别类的存储结构：
    memories/
      owner/
        profile.md      # 基本信息和偏好
        todos.md         # 待办事项
        diary.md         # 日记
        schedule.md      # 日程安排
        habits.md        # 生活习惯
        relationships.md # 人际关系
        conversations.md # 最近对话
    """
    
    def __init__(
        self,
        user_id: str,
        memory_dir: str | Path = "./memories",
        template_path: Optional[str | Path] = None
    ):
        self.user_id = user_id
        self.memory_dir = Path(memory_dir)
        
        # 使用新的分门别类存储
        from .categorized_storage import CategorizedMemoryStorage
        self.storage = CategorizedMemoryStorage(user_id=user_id, memory_dir=memory_dir)
        
        # 保留旧的接口用于兼容
        self.template_path = Path(template_path) if template_path else None
    
    def get_memory(self) -> MemoryData:
        """获取完整记忆数据（兼容旧接口）"""
        # 返回一个空的 MemoryData，因为新系统使用分门别类的存储
        return MemoryData(user_id=self.user_id)
    
    def get_context(self, sections: Optional[List[str]] = None) -> str:
        """获取记忆上下文（用于注入系统提示）
        
        Args:
            sections: 要包含的章节列表，None 表示全部
        """
        return self.storage.get_context(sections)
    
    # 便捷方法 - 委托给新的存储系统
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好"""
        self.storage.update_preference(category, key, value)
    
    def add_todo(self, content: str, priority: str = "medium", due_date: Optional[str] = None):
        """添加待办"""
        self.storage.add_todo(content, priority, due_date)
    
    def complete_todo(self, content: str):
        """完成待办"""
        self.storage.complete_todo(content)
    
    def add_memory(self, topic: str, points: List[str]):
        """添加记忆（对话摘要）"""
        self.storage.add_conversation(topic, points)
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习习惯"""
        self.storage.learn_habit(habit, category)
    
    def increment_conversation_count(self):
        """增加对话计数"""
        self.storage.increment_conversation_count()
