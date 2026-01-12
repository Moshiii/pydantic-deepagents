# Memory Toolset 第三方集成设计

## 设计原则

### 核心原则：分层设计

```
┌─────────────────────────────────────────┐
│  Core Layer (核心层) - 必须自己实现    │
│  - 数据存储和查询（拆分文件存储）       │
│  - 业务逻辑和规则                       │
│  - 数据模型和结构                       │
└─────────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────────┐
│  Integration Layer (集成层) - 可插拔    │
│  - 第三方服务适配器                      │
│  - 统一接口抽象                          │
│  - 降级和回退机制                        │
└─────────────────────────────────────────┘
              ↓ 委托
┌─────────────────────────────────────────┐
│  External Services (外部服务) - 第三方   │
│  - Google Calendar / Apple Calendar      │
│  - Push Notification Services            │
│  - Note-taking Apps                      │
│  - Alarm/Reminder Services               │
└─────────────────────────────────────────┘
```

---

## 功能分析：自建 vs 集成

### ✅ 必须自己实现（核心层）

#### 1. 数据存储和查询
- **原因**: 需要快速访问、离线可用、数据隐私
- **实现**: 拆分文件存储（`profile.json`, `todos.json`, `schedule.json` 等）
- **功能**:
  - ✅ 存储用户偏好、习惯、记忆（按模块拆分）
  - ✅ 存储待办事项、日程、创意（独立文件）
  - ✅ 快速查询和检索（按需加载）
  - ✅ 数据持久化（避免 LLM 上下文溢出）
- **文件结构**: 详见 `MEMORY_FILE_SPLIT_DESIGN.md`

#### 2. 业务逻辑和规则
- **原因**: 核心业务逻辑，需要完全控制
- **实现**: Memory Toolset 工具
- **功能**:
  - ✅ 个性化学习逻辑
  - ✅ 待办自动移动规则
  - ✅ 紧急程度评估算法
  - ✅ 时间段查找算法

#### 3. 数据模型和结构
- **原因**: 需要统一的数据结构
- **实现**: JSON 数据模型
- **功能**:
  - ✅ 统一的数据格式
  - ✅ 数据验证和迁移
  - ✅ 版本管理

---

### 🔌 可以集成第三方（集成层）

#### 1. 推送提醒服务 ⭐ 强烈推荐集成

**为什么集成**:
- ✅ 第三方服务更成熟、稳定
- ✅ 支持多平台（桌面、移动、Web）
- ✅ 不需要自己实现推送基础设施
- ✅ 用户可以选择自己喜欢的服务

**推荐服务**:
- **ntfy** - 开源、简单、支持多平台
- **LogSnag** - 专业、功能丰富
- **Pushover** - 可靠、支持多平台
- **IFTTT Webhooks** - 灵活、可扩展

**集成方式**:
```python
# 抽象接口
class NotificationAdapter:
    async def send_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        """发送通知"""
        pass

# 实现：ntfy 适配器
class NtfyAdapter(NotificationAdapter):
    async def send_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        import requests
        requests.post(
            "https://ntfy.sh/your-topic",
            data=f"{title}\n{message}",
            headers={"Priority": priority}
        )
```

**数据流**:
```
待办提醒触发
  ↓
Memory Toolset 检查 reminders
  ↓
调用 NotificationAdapter.send_notification()
  ↓
第三方服务推送通知
```

---

#### 2. 日历同步服务 ⭐ 强烈推荐集成

**为什么集成**:
- ✅ 用户可能已有日历应用（Google Calendar, Apple Calendar）
- ✅ 双向同步，数据一致性
- ✅ 用户可以在熟悉的日历应用中查看
- ✅ 不需要自己实现日历 UI

**推荐服务**:
- **Google Calendar API** - 最流行
- **Apple Calendar (CalDAV)** - macOS/iOS 用户
- **Outlook Calendar (Microsoft Graph)** - 企业用户
- **iCal/ICS 导出** - 通用格式，可导入任何日历

**集成方式**:
```python
# 抽象接口
class CalendarAdapter:
    async def sync_event(self, event: dict) -> bool:
        """同步事件到第三方日历"""
        pass
    
    async def get_events(self, start_date: str, end_date: str) -> list:
        """从第三方日历获取事件"""
        pass

# 实现：Google Calendar 适配器
class GoogleCalendarAdapter(CalendarAdapter):
    async def sync_event(self, event: dict) -> bool:
        # 使用 Google Calendar API
        pass
```

**数据流**:
```
用户添加日程
  ↓
保存到 memory.json (本地存储)
  ↓
调用 CalendarAdapter.sync_event() (可选)
  ↓
同步到第三方日历
```

**设计决策**:
- ✅ **主存储**: `memory.json`（始终是数据源）
- ✅ **同步**: 可选，用户可以选择是否启用
- ✅ **双向同步**: 从第三方日历读取事件（可选）

---

#### 3. 笔记应用集成 ⚠️ 可选集成

**为什么集成**:
- ✅ 用户可能已有笔记应用（Notion, Obsidian）
- ✅ 更好的编辑和查看体验
- ✅ 支持富文本、Markdown 等

**推荐服务**:
- **Notion API** - 功能强大
- **Obsidian** - Markdown 文件，易于集成
- **LogSeq** - 支持 API

**集成方式**:
```python
# 抽象接口
class NoteAdapter:
    async def create_note(self, title: str, content: str, tags: list = None) -> str:
        """创建笔记"""
        pass
    
    async def append_to_daily_note(self, date: str, content: str) -> bool:
        """追加到每日笔记"""
        pass
```

**设计决策**:
- ⚠️ **创意记录**: 可以集成，但不是必须
- ✅ **主存储**: `memory.json`（始终是数据源）
- ✅ **导出**: 可以导出到笔记应用（可选）

---

#### 4. 闹钟/提醒服务 ⚠️ 可选集成

**为什么集成**:
- ✅ 系统级提醒更可靠
- ✅ 用户可以在系统通知中心查看
- ✅ 支持声音、震动等

**推荐服务**:
- **系统通知** (macOS, Windows, Linux)
- **第三方提醒应用** (Alarmy, Any.do)

**集成方式**:
```python
# 抽象接口
class AlarmAdapter:
    async def set_alarm(self, time: str, message: str) -> str:
        """设置闹钟"""
        pass
    
    async def cancel_alarm(self, alarm_id: str) -> bool:
        """取消闹钟"""
        pass
```

**设计决策**:
- ⚠️ **可选**: 可以作为推送通知的补充
- ✅ **主机制**: 使用推送通知服务（更灵活）

---

## 架构设计：可插拔集成层

### 设计模式：适配器模式 + 策略模式

```python
# 1. 抽象接口定义
class NotificationAdapter(ABC):
    """通知适配器抽象接口"""
    
    @abstractmethod
    async def send_notification(
        self, 
        title: str, 
        message: str, 
        priority: str = "normal"
    ) -> bool:
        """发送通知"""
        pass

class CalendarAdapter(ABC):
    """日历适配器抽象接口"""
    
    @abstractmethod
    async def sync_event(self, event: dict) -> bool:
        """同步事件"""
        pass
    
    @abstractmethod
    async def get_events(self, start_date: str, end_date: str) -> list:
        """获取事件"""
        pass

# 2. 具体实现
class NtfyAdapter(NotificationAdapter):
    """ntfy 通知适配器"""
    pass

class GoogleCalendarAdapter(CalendarAdapter):
    """Google Calendar 适配器"""
    pass

# 3. 集成管理器
class IntegrationManager:
    """集成管理器 - 管理所有第三方集成"""
    
    def __init__(self):
        self.notification_adapter: NotificationAdapter | None = None
        self.calendar_adapter: CalendarAdapter | None = None
        self.note_adapter: NoteAdapter | None = None
    
    def register_notification_adapter(self, adapter: NotificationAdapter):
        """注册通知适配器"""
        self.notification_adapter = adapter
    
    def register_calendar_adapter(self, adapter: CalendarAdapter):
        """注册日历适配器"""
        self.calendar_adapter = adapter
    
    async def send_notification(self, title: str, message: str) -> bool:
        """发送通知（带降级）"""
        if self.notification_adapter:
            try:
                return await self.notification_adapter.send_notification(title, message)
            except Exception as e:
                logger.warning(f"Notification failed: {e}")
                # 降级：保存到本地，稍后重试
                return False
        return False
    
    async def sync_event(self, event: dict) -> bool:
        """同步事件（可选）"""
        if self.calendar_adapter:
            try:
                return await self.calendar_adapter.sync_event(event)
            except Exception as e:
                logger.warning(f"Calendar sync failed: {e}")
                return False
        return False
```

---

## 具体集成方案

### 方案 1: 推送提醒服务集成

#### 1.1 推荐：ntfy（开源、简单）

**优点**:
- ✅ 开源、免费
- ✅ 简单易用
- ✅ 支持多平台
- ✅ 不需要注册（可选）

**实现**:
```python
class NtfyAdapter(NotificationAdapter):
    def __init__(self, topic: str):
        self.topic = topic
        self.base_url = "https://ntfy.sh"
    
    async def send_notification(
        self, 
        title: str, 
        message: str, 
        priority: str = "normal"
    ) -> bool:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{self.topic}",
                data=f"{title}\n{message}",
                headers={"Priority": priority}
            ) as response:
                return response.status == 200
```

**使用**:
```python
# 在 Memory Toolset 中
@toolset.tool
async def create_todo_reminder(...):
    # 保存到 memory.json
    reminder_id = memory_sys.create_reminder(...)
    
    # 集成第三方推送（可选）
    if integration_manager.notification_adapter:
        await integration_manager.send_notification(
            title="待办提醒",
            message=f"您有待办事项：{todo['content']}"
        )
    
    return f"已创建提醒（ID: {reminder_id}）"
```

---

### 方案 2: 日历同步服务集成

#### 2.1 推荐：iCal/ICS 导出（通用）

**优点**:
- ✅ 通用格式，所有日历应用都支持
- ✅ 不需要 OAuth 认证
- ✅ 用户手动导入，简单可靠

**实现**:
```python
class ICalExportAdapter(CalendarAdapter):
    """iCal 导出适配器（不需要第三方服务）"""
    
    async def export_to_ical(
        self, 
        events: list, 
        output_path: str
    ) -> str:
        """导出为 iCal 文件"""
        from icalendar import Calendar, Event
        
        cal = Calendar()
        for event_data in events:
            event = Event()
            event.add('summary', event_data['title'])
            event.add('dtstart', event_data['start_time'])
            # ... 添加其他字段
            cal.add_component(event)
        
        with open(output_path, 'wb') as f:
            f.write(cal.to_ical())
        
        return output_path
```

#### 2.2 可选：Google Calendar API（双向同步）

**优点**:
- ✅ 自动同步
- ✅ 双向同步
- ✅ 用户可以在 Google Calendar 中查看

**缺点**:
- ⚠️ 需要 OAuth 认证
- ⚠️ 需要用户授权
- ⚠️ 增加复杂度

**实现**:
```python
class GoogleCalendarAdapter(CalendarAdapter):
    def __init__(self, credentials_path: str):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # 加载 OAuth 凭证
        self.service = build('calendar', 'v3', credentials=credentials)
    
    async def sync_event(self, event: dict) -> bool:
        """同步事件到 Google Calendar"""
        google_event = {
            'summary': event['title'],
            'start': {'dateTime': event['start_time']},
            'end': {'dateTime': event['end_time']},
        }
        self.service.events().insert(calendarId='primary', body=google_event).execute()
        return True
```

---

### 方案 3: 笔记应用集成（可选）

#### 3.1 推荐：Obsidian（Markdown 文件）

**优点**:
- ✅ 基于文件系统，易于集成
- ✅ Markdown 格式，易于生成
- ✅ 不需要 API

**实现**:
```python
class ObsidianAdapter(NoteAdapter):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
    
    async def append_to_daily_note(self, date: str, content: str) -> bool:
        """追加到每日笔记"""
        daily_note_path = self.vault_path / f"{date}.md"
        
        if not daily_note_path.exists():
            daily_note_path.write_text(f"# {date}\n\n")
        
        with open(daily_note_path, 'a') as f:
            f.write(f"\n## 创意想法\n{content}\n")
        
        return True
```

---

## 集成架构设计

### 完整架构图

```
┌─────────────────────────────────────────────────────────┐
│  Memory Toolset (核心层)                                │
│  - learn_user_pattern()                                 │
│  - add_todo()                                           │
│  - add_one_time_event()                                 │
│  - create_todo_reminder()                               │
└─────────────────────────────────────────────────────────┘
              ↓ 可选调用
┌─────────────────────────────────────────────────────────┐
│  Integration Manager (集成管理器)                        │
│  - register_notification_adapter()                      │
│  - register_calendar_adapter()                         │
│  - send_notification()                                  │
│  - sync_event()                                         │
└─────────────────────────────────────────────────────────┘
              ↓ 委托
    ┌─────────┴─────────┬───────────┐
    ↓                   ↓           ↓
┌──────────┐    ┌──────────┐  ┌──────────┐
│ Ntfy     │    │ Google   │  │ Obsidian │
│ Adapter  │    │ Calendar │  │ Adapter  │
└──────────┘    │ Adapter  │  └──────────┘
                └──────────┘
```

### 配置方式

```python
# 在 app.py 中配置
integration_manager = IntegrationManager()

# 可选：启用推送通知
if os.getenv("NTFY_TOPIC"):
    integration_manager.register_notification_adapter(
        NtfyAdapter(topic=os.getenv("NTFY_TOPIC"))
    )

# 可选：启用日历同步
if os.getenv("GOOGLE_CALENDAR_CREDENTIALS"):
    integration_manager.register_calendar_adapter(
        GoogleCalendarAdapter(credentials_path=os.getenv("GOOGLE_CALENDAR_CREDENTIALS"))
    )

# 传递给 Memory Toolset
memory_toolset = create_memory_toolset(
    integration_manager=integration_manager
)
```

---

## 功能分类总结

### ✅ 必须自己实现

| 功能 | 原因 | 实现方式 |
|------|------|---------|
| **数据存储** | 需要快速访问、离线可用 | `memory.json` |
| **个性化学习** | 核心业务逻辑 | Memory Toolset |
| **待办管理逻辑** | 业务规则 | Memory Toolset |
| **日程安排逻辑** | 业务规则 | Memory Toolset |
| **数据查询** | 需要快速检索 | Memory Toolset |

### 🔌 强烈推荐集成第三方

| 功能 | 推荐服务 | 集成方式 |
|------|---------|---------|
| **推送提醒** | ntfy, LogSnag, Pushover | NotificationAdapter |
| **日历同步** | Google Calendar, iCal 导出 | CalendarAdapter |
| **系统通知** | 系统通知 API | SystemNotificationAdapter |

### ⚠️ 可选集成第三方

| 功能 | 推荐服务 | 集成方式 |
|------|---------|---------|
| **笔记应用** | Obsidian, Notion | NoteAdapter |
| **闹钟服务** | 系统闹钟 API | AlarmAdapter |

---

## 推荐实现方案

### 方案 A: 最小集成（推荐）

**集成**:
- ✅ **推送通知**: ntfy（简单、开源）
- ✅ **日历导出**: iCal/ICS 文件导出（通用格式）

**不集成**:
- ❌ Google Calendar API（需要 OAuth，增加复杂度）
- ❌ 笔记应用（不是核心功能）
- ❌ 系统闹钟（推送通知已足够）

**优点**:
- ✅ 简单、可靠
- ✅ 不需要用户授权
- ✅ 用户可以选择自己喜欢的服务

### 方案 B: 完整集成（高级）

**集成**:
- ✅ 推送通知（ntfy）
- ✅ 日历同步（Google Calendar API）
- ✅ 笔记应用（Obsidian）
- ✅ 系统通知（macOS/Windows）

**优点**:
- ✅ 功能完整
- ✅ 用户体验好

**缺点**:
- ⚠️ 复杂度高
- ⚠️ 需要用户配置和授权

---

## 实现优先级

### P0（必须实现）

1. ✅ **数据存储** - `memory.json`（自己实现）
2. ✅ **业务逻辑** - Memory Toolset（自己实现）
3. 🔌 **推送通知** - 集成 ntfy（推荐）

### P1（推荐实现）

1. 🔌 **日历导出** - iCal/ICS 导出（推荐）
2. 🔌 **系统通知** - 系统通知 API（可选）

### P2（可选实现）

1. 🔌 **日历同步** - Google Calendar API（可选）
2. 🔌 **笔记应用** - Obsidian/Notion（可选）

---

## 代码结构设计

### 目录结构

```
examples/full_app/
├── memory_system/
│   ├── core.py              # 核心逻辑（自己实现）
│   ├── json_storage.py      # 数据存储（自己实现）
│   ├── toolset.py           # 工具集（自己实现）
│   └── integrations/        # 第三方集成（新增）
│       ├── __init__.py
│       ├── base.py          # 抽象接口
│       ├── notification.py  # 通知适配器
│       ├── calendar.py     # 日历适配器
│       └── notes.py        # 笔记适配器
```

### 抽象接口定义

```python
# integrations/base.py
from abc import ABC, abstractmethod

class NotificationAdapter(ABC):
    """通知适配器抽象接口"""
    
    @abstractmethod
    async def send_notification(
        self, 
        title: str, 
        message: str, 
        priority: str = "normal"
    ) -> bool:
        """发送通知"""
        pass

class CalendarAdapter(ABC):
    """日历适配器抽象接口"""
    
    @abstractmethod
    async def sync_event(self, event: dict) -> bool:
        """同步事件到第三方日历"""
        pass
    
    @abstractmethod
    async def get_events(self, start_date: str, end_date: str) -> list:
        """从第三方日历获取事件"""
        pass
    
    @abstractmethod
    async def export_to_ical(self, events: list, output_path: str) -> str:
        """导出为 iCal 文件"""
        pass
```

### 具体实现示例

```python
# integrations/notification.py
class NtfyAdapter(NotificationAdapter):
    """ntfy 通知适配器"""
    pass

class LogSnagAdapter(NotificationAdapter):
    """LogSnag 通知适配器"""
    pass

# integrations/calendar.py
class ICalExportAdapter(CalendarAdapter):
    """iCal 导出适配器"""
    pass

class GoogleCalendarAdapter(CalendarAdapter):
    """Google Calendar 适配器"""
    pass
```

---

## 使用示例

### 示例 1: 集成推送通知

```python
# 在 toolset.py 中
@toolset.tool
async def create_todo_reminder(
    ctx: RunContext[DepsType],
    todo_id: str,
    reminder_minutes: int = 30
) -> str:
    """创建待办提醒"""
    memory_sys = get_memory_system(ctx)
    
    # 1. 保存到本地（必须）
    reminder_id = memory_sys.create_reminder(...)
    
    # 2. 发送推送通知（可选，如果配置了）
    if hasattr(ctx.deps, 'integration_manager'):
        integration_manager = ctx.deps.integration_manager
        if integration_manager.notification_adapter:
            todo = memory_sys.get_todo(todo_id)
            await integration_manager.send_notification(
                title="待办提醒",
                message=f"您有待办事项：{todo['content']}",
                priority="high"
            )
    
    return f"已创建提醒（ID: {reminder_id}）"
```

### 示例 2: 集成日历同步

```python
@toolset.tool
async def add_one_time_event(...):
    """添加一次性事件"""
    memory_sys = get_memory_system(ctx)
    
    # 1. 保存到本地（必须）
    event_id = memory_sys.add_one_time_event(...)
    
    # 2. 同步到第三方日历（可选）
    if hasattr(ctx.deps, 'integration_manager'):
        integration_manager = ctx.deps.integration_manager
        if integration_manager.calendar_adapter:
            event_data = memory_sys.get_schedule_event(event_id)
            await integration_manager.sync_event(event_data)
    
    return f"已添加事件（ID: {event_id}）"
```

---

## 总结

### 核心设计原则

1. ✅ **数据主权**: `memory.json` 始终是数据源
2. ✅ **可选集成**: 第三方集成是可选的，不影响核心功能
3. ✅ **降级机制**: 第三方服务失败时，核心功能仍然可用
4. ✅ **统一接口**: 使用适配器模式，易于扩展

### 推荐方案

**最小可行方案**:
- ✅ 自己实现：数据存储、业务逻辑
- ✅ 集成：推送通知（ntfy）
- ✅ 集成：日历导出（iCal/ICS）

**完整方案**（可选）:
- ✅ 集成：推送通知（ntfy）
- ✅ 集成：日历同步（Google Calendar）
- ✅ 集成：笔记应用（Obsidian）
- ✅ 集成：系统通知（macOS/Windows）

### 关键优势

1. ✅ **不重复造轮子**: 推送、日历等使用成熟服务
2. ✅ **保持核心控制**: 数据存储和业务逻辑自己实现
3. ✅ **灵活可扩展**: 用户可以按需启用集成
4. ✅ **降级可靠**: 第三方服务失败不影响核心功能
