"""
分门别类的记忆存储实现

将记忆按类型存储到不同的文件中：
- profile.md: 基本信息和偏好
- todos.md: 待办事项
- diary.md: 日记
- schedule.md: 日程安排
- habits.md: 生活习惯
- relationships.md: 人际关系
- conversations.md: 最近对话
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional


class CategorizedMemoryStorage:
    """分门别类的记忆存储系统"""
    
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
        
        # 定义各类记忆文件路径
        self.files = {
            "profile": self.user_dir / "profile.md",
            "todos": self.user_dir / "todos.md",
            "diary": self.user_dir / "diary.md",
            "schedule": self.user_dir / "schedule.md",
            "habits": self.user_dir / "habits.md",
            "relationships": self.user_dir / "relationships.md",
            "conversations": self.user_dir / "conversations.md",
        }
        
        # 初始化所有文件
        self._initialize_files()
    
    def _initialize_files(self):
        """初始化所有记忆文件（如果不存在）"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Profile: 基本信息和偏好
        if not self.files["profile"].exists():
            self.files["profile"].write_text(f"""# 个人档案

> 创建时间：{now}
> 最后更新：{now}

## 基本信息

| 字段 | 值 |
|------|-----|
| 姓名 |  |
| 昵称 |  |
| 时区 | Asia/Shanghai (UTC+8) |
| 语言 | zh-CN |

## 偏好设置

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

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Todos: 待办事项
        if not self.files["todos"].exists():
            self.files["todos"].write_text(f"""# 待办事项

> 最后更新：{now}

### 进行中

- [ ] 

### 待开始

- [ ] 

### 已完成

- [x] 

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Diary: 日记
        if not self.files["diary"].exists():
            self.files["diary"].write_text(f"""# 日记

> 创建时间：{now}

---

*记录你的想法、心情和重要事件*

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Schedule: 日程安排
        if not self.files["schedule"].exists():
            self.files["schedule"].write_text(f"""# 日程安排

> 最后更新：{now}

## 定期日程

| 时间 | 事项 | 频率 | 备注 |
|------|------|------|------|
|  |  |  |  |

## 即将到来的事件

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Habits: 生活习惯
        if not self.files["habits"].exists():
            self.files["habits"].write_text(f"""# 生活习惯

> 最后更新：{now}

## 工作习惯

- 

## 沟通习惯

- 

## 生活习惯

- 

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Relationships: 人际关系
        if not self.files["relationships"].exists():
            self.files["relationships"].write_text(f"""# 人际关系

> 最后更新：{now}

## 常用联系人

- 

## 重要关系

- 

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
        
        # Conversations: 最近对话
        if not self.files["conversations"].exists():
            self.files["conversations"].write_text(f"""# 最近对话摘要

> 最后更新：{now}

---

*记录重要对话的关键信息*

---

*此文件由 AI 助手自动维护，用户可随时编辑*
""", encoding='utf-8')
    
    def _update_timestamp(self, file_path: Path):
        """更新文件的最后更新时间"""
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 更新最后更新时间
            import re
            content = re.sub(r'> 最后更新：.*', f'> 最后更新：{now}', content)
            file_path.write_text(content, encoding='utf-8')
    
    # ========== Profile 操作 ==========
    
    def update_profile(self, field: str, value: str):
        """更新个人档案"""
        content = self.files["profile"].read_text(encoding='utf-8')
        # 更新表格中的值
        import re
        pattern = rf'\| {re.escape(field)} \| (.*?) \|'
        replacement = f'| {field} | {value} |'
        content = re.sub(pattern, replacement, content)
        self.files["profile"].write_text(content, encoding='utf-8')
        self._update_timestamp(self.files["profile"])
    
    def update_preference(self, category: str, key: str, value: str):
        """更新偏好设置"""
        content = self.files["profile"].read_text(encoding='utf-8')
        import re
        # 查找对应的章节
        pattern = rf'(### {re.escape(category)}\n)(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(2)
            # 查找并更新对应的项
            item_pattern = rf'- {re.escape(key)}：`(.*?)`'
            if re.search(item_pattern, section):
                new_section = re.sub(item_pattern, f'- {key}：`{value}`', section)
                content = content.replace(section, new_section)
            else:
                # 添加新项
                new_section = section.rstrip() + f'\n- {key}：`{value}`\n'
                content = content.replace(section, new_section)
            self.files["profile"].write_text(content, encoding='utf-8')
            self._update_timestamp(self.files["profile"])
    
    # ========== Todos 操作 ==========
    
    def add_todo(self, content: str, priority: str = "medium", due_date: Optional[str] = None, status: str = "pending"):
        """添加待办事项"""
        content_text = self.files["todos"].read_text(encoding='utf-8')
        
        # 确定要添加到的章节
        status_map = {"pending": "待开始", "in_progress": "进行中", "completed": "已完成"}
        section_name = status_map.get(status, "待开始")
        
        # 构建待办项
        due_str = f"，截止：{due_date}" if due_date else ""
        priority_str = f"，优先级：{priority}" if priority != "medium" else ""
        todo_item = f"- [ ] {content}（{priority_str}{due_str}）"
        
        # 查找对应章节并添加
        import re
        pattern = rf'(### {re.escape(section_name)}\n)(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, content_text, re.DOTALL)
        if match:
            section_header = match.group(1)
            section_content = match.group(2)
            new_content = section_header + section_content.rstrip() + f'\n{todo_item}\n'
            content_text = content_text.replace(match.group(0), new_content)
            self.files["todos"].write_text(content_text, encoding='utf-8')
            self._update_timestamp(self.files["todos"])
    
    def complete_todo(self, content: str):
        """完成待办事项"""
        content_text = self.files["todos"].read_text(encoding='utf-8')
        import re
        # 查找待办项并标记为完成
        pattern = rf'- \[ \] {re.escape(content)}.*?'
        now = datetime.now().strftime("%Y-%m-%d")
        replacement = f'- [x] {content}（完成时间：{now}）'
        content_text = re.sub(pattern, replacement, content_text)
        self.files["todos"].write_text(content_text, encoding='utf-8')
        self._update_timestamp(self.files["todos"])
    
    # ========== Diary 操作 ==========
    
    def add_diary_entry(self, title: str, content: str):
        """添加日记条目"""
        diary_content = self.files["diary"].read_text(encoding='utf-8')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""
## {now} - {title}

{content}

---
"""
        # 插入到文件开头（在标题和分隔线之后）
        import re
        pattern = r'(---\n\n)(.*?)(?=\n---|$)'
        match = re.search(pattern, diary_content, re.DOTALL)
        if match:
            new_content = match.group(1) + entry + match.group(2)
            diary_content = diary_content.replace(match.group(0), new_content)
        else:
            diary_content = diary_content.rstrip() + entry
        
        self.files["diary"].write_text(diary_content, encoding='utf-8')
        self._update_timestamp(self.files["diary"])
    
    # ========== Schedule 操作 ==========
    
    def add_schedule_event(self, title: str, start_time: str, end_time: Optional[str] = None, description: str = ""):
        """添加日程事件"""
        schedule_content = self.files["schedule"].read_text(encoding='utf-8')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        event = f"""
#### {start_time}{f" - {end_time}" if end_time else ""}
**{title}**
{f"- {description}" if description else ""}
"""
        
        # 插入到"即将到来的事件"章节
        import re
        pattern = r'(## 即将到来的事件\n)(.*?)(?=\n---|$)'
        match = re.search(pattern, schedule_content, re.DOTALL)
        if match:
            new_content = match.group(1) + event + match.group(2)
            schedule_content = schedule_content.replace(match.group(0), new_content)
        else:
            schedule_content = schedule_content.rstrip() + event
        
        self.files["schedule"].write_text(schedule_content, encoding='utf-8')
        self._update_timestamp(self.files["schedule"])
    
    # ========== Habits 操作 ==========
    
    def learn_habit(self, habit: str, category: str = "工作习惯"):
        """学习新习惯"""
        habits_content = self.files["habits"].read_text(encoding='utf-8')
        now = datetime.now().strftime("%Y-%m-%d")
        habit_item = f"- {habit}（学习时间：{now}）\n"
        
        # 查找对应章节
        import re
        pattern = rf'(### {re.escape(category)}\n)(.*?)(?=\n### |\n## |$)'
        match = re.search(pattern, habits_content, re.DOTALL)
        if match:
            header = match.group(1)
            existing = match.group(2)
            new_section = header + existing.rstrip() + f'\n{habit_item}'
            habits_content = habits_content.replace(match.group(0), new_section)
            self.files["habits"].write_text(habits_content, encoding='utf-8')
            self._update_timestamp(self.files["habits"])
    
    # ========== Relationships 操作 ==========
    
    def add_relationship(self, name: str, relation: str, details: str = ""):
        """添加人际关系"""
        rel_content = self.files["relationships"].read_text(encoding='utf-8')
        
        entry = f"""
- **{name}** - {relation}
  {f"- {details}" if details else ""}
"""
        
        # 插入到"常用联系人"章节
        import re
        pattern = r'(## 常用联系人\n)(.*?)(?=\n## |$)'
        match = re.search(pattern, rel_content, re.DOTALL)
        if match:
            new_content = match.group(1) + entry + match.group(2)
            rel_content = rel_content.replace(match.group(0), new_content)
        else:
            rel_content = rel_content.rstrip() + entry
        
        self.files["relationships"].write_text(rel_content, encoding='utf-8')
        self._update_timestamp(self.files["relationships"])
    
    # ========== Conversations 操作 ==========
    
    def add_conversation(self, topic: str, summary: List[str]):
        """添加对话摘要"""
        conv_content = self.files["conversations"].read_text(encoding='utf-8')
        now = datetime.now().strftime("%Y-%m-%d")
        
        entry = f"""
### {now} - {topic}
"""
        for point in summary:
            entry += f"- {point}\n"
        entry += "\n"
        
        # 插入到文件开头（在标题和分隔线之后）
        import re
        pattern = r'(---\n\n)(.*?)(?=\n---|$)'
        match = re.search(pattern, conv_content, re.DOTALL)
        if match:
            new_content = match.group(1) + entry + match.group(2)
            conv_content = conv_content.replace(match.group(0), new_content)
        else:
            conv_content = conv_content.rstrip() + entry
        
        # 只保留最近 50 条对话
        entries = re.findall(r'### \d{4}-\d{2}-\d{2} - .*?(?=\n### |$)', conv_content, re.DOTALL)
        if len(entries) > 50:
            conv_content = conv_content.split('---\n\n')[0] + '---\n\n' + '\n'.join(entries[:50])
        
        self.files["conversations"].write_text(conv_content, encoding='utf-8')
        self._update_timestamp(self.files["conversations"])
    
    # ========== 读取操作 ==========
    
    def get_context(self, sections: Optional[List[str]] = None) -> str:
        """获取记忆上下文（用于注入系统提示）"""
        context_parts = []
        
        if sections is None or "profile" in sections:
            if self.files["profile"].exists():
                profile = self.files["profile"].read_text(encoding='utf-8')
                context_parts.append("## 个人档案")
                # 提取基本信息
                import re
                info_match = re.search(r'## 基本信息\n\n(.*?)\n\n---', profile, re.DOTALL)
                if info_match:
                    context_parts.append(info_match.group(1))
                context_parts.append("")
        
        if sections is None or "todos" in sections:
            if self.files["todos"].exists():
                todos = self.files["todos"].read_text(encoding='utf-8')
                context_parts.append("## 当前待办")
                # 提取进行中的待办
                import re
                in_progress = re.search(r'### 进行中\n(.*?)(?=\n### |\n## |$)', todos, re.DOTALL)
                if in_progress:
                    for line in in_progress.group(1).strip().split('\n'):
                        if line.strip() and line.strip().startswith('- ['):
                            context_parts.append(line.strip())
                context_parts.append("")
        
        if sections is None or "habits" in sections:
            if self.files["habits"].exists():
                habits = self.files["habits"].read_text(encoding='utf-8')
                context_parts.append("## 学习到的习惯")
                # 提取最近的习惯
                import re
                work_habits = re.search(r'### 工作习惯\n(.*?)(?=\n### |\n## |$)', habits, re.DOTALL)
                if work_habits:
                    for line in work_habits.group(1).strip().split('\n')[-5:]:
                        if line.strip():
                            context_parts.append(f"  - {line.strip()}")
                context_parts.append("")
        
        if sections is None or "conversations" in sections:
            if self.files["conversations"].exists():
                convs = self.files["conversations"].read_text(encoding='utf-8')
                context_parts.append("## 最近对话摘要")
                # 提取最近 3 条
                import re
                entries = re.findall(r'### (\d{4}-\d{2}-\d{2}) - (.*?)\n(.*?)(?=\n### |$)', convs, re.DOTALL)
                for date, topic, content in entries[:3]:
                    context_parts.append(f"### {date} - {topic}")
                    for line in content.strip().split('\n')[:3]:
                        if line.strip():
                            context_parts.append(f"  {line.strip()}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def increment_conversation_count(self):
        """增加对话计数（存储在 profile 中）"""
        # 这个可以存储在 profile 的统计部分，或者单独的文件
        # 简化处理：暂时不实现统计功能
        pass
