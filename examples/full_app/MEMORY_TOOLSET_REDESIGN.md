# Memory Toolset 重新设计文档

## 设计目标

基于用户需求，重新设计 Memory Toolset，实现以下4个核心功能场景：

1. **个性化学习** - AI 能对用户进行个性化学习，随着使用加深越来越了解用户
2. **创意记录** - 记录每日创意想法，持久化形成每日创意记录
3. **待办管理** - 记录待办事项，自动移动未完成项，提醒和询问完成情况
4. **日程安排** - 自动安排日程到日历，智能判断紧急程度并安排时间段

**统一存储**: 所有数据持久化在 `memories/{user_id}/` 目录下，按模块拆分为多个 JSON 文件

**文件结构**:
```
memories/{user_id}/
├── profile.json          # 用户档案和偏好（小文件，经常读取）
├── todos.json            # 待办事项（中等大小）
├── schedule.json         # 日程安排（中等大小）
├── ideas.json            # 创意想法（可能很大）
├── habits.json           # 习惯（小文件）
├── conversations.json    # 对话记录（可能很大）
├── reminders.json        # 提醒（中等大小）
├── followups.json        # 询问（中等大小）
├── relationships.json    # 人际关系（小文件）
├── diary.json            # 日记（可能很大）
└── metadata.json         # 元数据（小文件）
```

**设计优势**:
- ✅ **解决 LLM 上下文溢出**: 按需加载，只读取需要的文件
- ✅ **提升性能**: 减少读取量，独立缓存
- ✅ **改善用户体验**: 文件清晰，易于管理
- ✅ **统一接口**: API 设计清晰，易于使用

详见: `MEMORY_FILE_SPLIT_DESIGN.md`

---

## 功能场景详细分析

### 场景 1: 个性化学习

**需求**:
- AI 能学习用户的使用习惯、聊天习惯、办事习惯、语言偏好
- 随着使用加深，越来越了解用户
- 不需要用户每次都说偏好

**当前状态**:
- ✅ 已有 `update_preference()` - 更新偏好
- ✅ 已有 `learn_habit()` - 学习习惯
- ✅ 已有 `learn_schedule_preference()` - 学习日程偏好
- ⚠️ 缺少自动学习机制
- ⚠️ 缺少学习置信度管理
- ⚠️ 缺少学习结果的应用机制

**需要增强**:
- 添加 `learn_user_pattern()` - 统一的学习接口
- 添加自动学习触发机制
- 添加学习结果动态注入

---

### 场景 2: 创意记录

**需求**:
- 记录用户的创意想法
- 按日期组织，形成每日创意记录
- 持久化存储

**当前状态**:
- ✅ 已有 `add_idea()` - 记录创意想法
- ✅ 数据结构支持（ideas 数组）
- ⚠️ 缺少按日期查询功能
- ⚠️ 缺少每日创意记录的展示

**需要增强**:
- 添加 `get_daily_ideas(date)` - 获取某日的创意
- 添加 `get_recent_ideas(days)` - 获取最近N天的创意
- 优化创意展示格式

---

### 场景 3: 待办管理

**需求**:
- 记录待办事项，每个待办有截止日期
- **自动移动**: 如果今天没办完，自动移动到明天
- **提醒功能**: AI 能发消息提醒用户有待办要做
- **自动询问**: 过一段时间后自动询问待办是否完成

**当前状态**:
- ✅ 已有 `add_todo()` - 添加待办
- ✅ 已有 `complete_todo()` - 完成待办
- ✅ 已有 `schedule_todo()` - 安排时间
- ✅ 已有 reminders 和 followups 数据结构
- ❌ **缺少自动移动未完成项的功能**
- ❌ **缺少提醒触发机制**
- ❌ **缺少自动询问机制**

**需要增强**:
- 添加 `auto_migrate_overdue_todos()` - 自动移动过期待办
- 添加 `create_todo_reminder()` - 创建待办提醒
- 添加 `create_todo_followup()` - 创建待办询问
- 添加 `get_pending_todo_reminders()` - 获取待触发的提醒
- 添加 `get_pending_todo_followups()` - 获取待触发的询问

---

### 场景 4: 日程安排

**需求**:
- 用户告诉 AI 什么时间有什么事情 → 自动安排到日历
- 用户说待办事项 → AI 自动判断紧急程度和需要的时间
- AI 自动安排待办事项在一周内的时间段

**当前状态**:
- ✅ 已有 `add_one_time_event()` - 添加一次性事件
- ✅ 已有 `add_regular_schedule()` - 添加定期日程
- ✅ 已有 `schedule_todo()` - 为待办安排时间
- ⚠️ 缺少智能判断紧急程度的功能
- ⚠️ 缺少自动安排时间段的功能
- ⚠️ 缺少时间冲突检测的应用

**需要增强**:
- 添加 `auto_schedule_todo()` - 智能安排待办时间段
- 添加 `assess_todo_urgency()` - 评估待办紧急程度
- 添加 `find_available_time_slot()` - 查找可用时间段
- 增强时间冲突检测的使用

---

## 架构设计

### 模块划分

```
Memory Toolset
├── 1. Personalization Module (个性化学习模块)
│   ├── learn_user_pattern() - 学习用户模式
│   ├── get_learned_patterns() - 获取学习到的模式
│   └── apply_learned_patterns() - 应用学习结果（通过动态注入）
│
├── 2. Idea Management Module (创意管理模块)
│   ├── add_idea() - 记录创意（已有）
│   ├── get_daily_ideas() - 获取每日创意
│   ├── get_recent_ideas() - 获取最近创意
│   └── search_ideas() - 搜索创意
│
├── 3. Todo Management Module (待办管理模块)
│   ├── add_todo() - 添加待办（已有）
│   ├── auto_migrate_overdue_todos() - 自动移动过期待办
│   ├── create_todo_reminder() - 创建待办提醒
│   ├── create_todo_followup() - 创建待办询问
│   ├── get_pending_todo_reminders() - 获取待触发提醒
│   └── get_pending_todo_followups() - 获取待触发询问
│
└── 4. Schedule Management Module (日程管理模块)
    ├── add_one_time_event() - 添加一次性事件（已有）
    ├── add_regular_schedule() - 添加定期日程（已有）
    ├── auto_schedule_todo() - 智能安排待办时间段
    ├── assess_todo_urgency() - 评估待办紧急程度
    └── find_available_time_slot() - 查找可用时间段
```

---

## 数据模型设计

### 统一存储结构（拆分文件）

**注意**: 数据已拆分为多个文件，以下结构仅用于说明数据模型。

#### profile.json

```json
{
    "basic_info": {
      "姓名": "",
      "昵称": "",
      "时区": "Asia/Shanghai (UTC+8)",
      "语言": "zh-CN"
    },
    "preferences": {
      "使用习惯": {
        "偏好功能": [],
        "常用工具": [],
        "信息展示偏好": "",
        "工作流程": ""
      },
      "聊天习惯": {
        "回复长度": "",
        "语气风格": "",
        "确认频率": "",
        "解释详细程度": ""
      },
      "办事习惯": {
        "决策风格": "",
        "优先级偏好": "",
        "工作节奏": "",
        "任务分解": ""
      },
      "语言偏好": {
        "语言风格": "",
        "专业术语": "",
        "表达方式": "",
        "数字格式": "",
        "时间格式": ""
      },
      "工作习惯": {
        "工作日": "周一至周五",
        "工作时间": "09:00 - 18:00",
        "午休时间": "12:00 - 13:00"
      },
      "日程偏好": {},
      "询问偏好": {
        "任务完成询问": "after_task_time",
        "进度检查频率": "weekly",
        "最小询问间隔小时数": 4
      }
    }
  }
}
```

#### todos.json

```json
{
    "pending": [
      {
        "id": "todo_xxx",
        "content": "完成项目文档",
        "priority": "high",
        "due_date": "2024-01-20",
        "category": "工作",
        "estimated_duration": "2小时",
        "status": "pending",
        "scheduled_time": null,
        "reminder_minutes": 30,
        "created_at": "2024-01-15 10:00:00",
        "updated_at": "2024-01-15 10:00:00",
        "completed_at": null,
        "auto_migrated": false,
        "migration_history": []
      }
    ],
    "scheduled": [],
    "in_progress": [],
    "completed": []
  }
}
```

#### habits.json

```json
{
    "工作习惯": [
      {
        "habit": "喜欢早上处理重要任务",
        "learned_at": "2024-01-15 10:30:00",
        "confidence": 0.9,
        "source": "behavior_pattern",
        "evidence_count": 5
      }
    ],
    "沟通习惯": [],
    "生活习惯": []
  }
}
```

#### schedule.json

```json
{
    "regular": [
      {
        "id": "recurring_xxx",
        "title": "晨间运动",
        "time": "07:00",
        "duration": "30分钟",
        "frequency": "每天",
        "description": "每天早上运动30分钟",
        "end_date": null,
        "reminder_minutes": 15,
        "created_at": "2024-01-10 09:00:00"
      }
    ],
    "upcoming": [
      {
        "id": "event_xxx",
        "title": "项目评审会议",
        "start_time": "2024-01-20 14:00:00",
        "end_time": "2024-01-20 15:30:00",
        "duration": "1小时30分钟",
        "description": "季度项目评审",
        "location": "会议室A",
        "reminder_minutes": 30,
        "created_at": "2024-01-15 10:00:00"
      }
    ]
  }
}
```

#### ideas.json

```json
[
    {
      "id": "idea_xxx",
      "content": "用户可以通过语音快速记录想法",
      "date": "2024-01-15",
      "time": "15:30",
      "tags": ["产品", "功能"],
      "category": "产品想法",
      "created_at": "2024-01-15 15:30:00"
    }
]
```

#### reminders.json

```json
[
    {
      "id": "reminder_xxx",
      "type": "todo",
      "target_id": "todo_xxx",
      "remind_at": "2024-01-20 13:30:00",
      "reminder_minutes": 30,
      "triggered": false,
      "triggered_at": null,
      "created_at": "2024-01-15 10:00:00"
    }
]
```

#### followups.json

```json
[
    {
      "id": "followup_xxx",
      "type": "todo_completion",
      "target_id": "todo_xxx",
      "ask_at": "2024-01-20 16:00:00",
      "question": "待办事项'完成项目文档'是否已完成？",
      "asked": false,
      "asked_at": null,
      "created_at": "2024-01-15 10:00:00"
    }
]
```

#### metadata.json

```json
{
    "created_at": "2024-01-01 00:00:00",
    "last_updated": "2024-01-15 15:30:00",
    "conversation_count": 42,
    "file_structure": "split",
    "version": "3.0"
  }
}
```

---

## 工具接口设计

### 模块 1: 个性化学习模块

#### 1.1 learn_user_pattern()

```python
@toolset.tool
async def learn_user_pattern(
    ctx: RunContext[DepsType],
    pattern_type: str,  # "使用习惯", "聊天习惯", "办事习惯", "语言偏好"
    pattern_description: str,  # 模式描述，如 "偏好表格格式展示"
    confidence: float = 0.8,  # 置信度 0-1
    source: str = "conversation",  # "explicit", "behavior_pattern", "inference"
    evidence: str | None = None  # 证据描述
) -> str:
    """学习用户的模式/习惯
    
    这是统一的学习接口，用于学习用户的：
    - 使用习惯：如何使用工具、偏好哪些功能
    - 聊天习惯：沟通风格、回复长度、确认频率
    - 办事习惯：决策风格、优先级偏好、工作节奏
    - 语言偏好：语言风格、专业术语、表达方式
    
    Args:
        pattern_type: 模式类型
        pattern_description: 模式描述（格式：key: value 或 简单描述）
        confidence: 置信度（显式表达=0.95，行为模式=0.8，推断=0.7）
        source: 来源（"explicit", "behavior_pattern", "inference"）
        evidence: 证据（可选，用于记录学习依据）
    
    Returns:
        学习结果确认信息
    """
```

**使用示例**:
```python
# 显式表达
learn_user_pattern(
    pattern_type="聊天习惯",
    pattern_description="确认频率：低（直接执行）",
    confidence=0.95,
    source="explicit",
    evidence="用户明确说'直接做，不用问我'"
)

# 行为模式
learn_user_pattern(
    pattern_type="使用习惯",
    pattern_description="信息展示偏好：表格格式",
    confidence=0.8,
    source="behavior_pattern",
    evidence="用户3次要求使用表格格式"
)
```

#### 1.2 get_learned_patterns()

```python
@toolset.tool
async def get_learned_patterns(
    ctx: RunContext[DepsType],
    pattern_type: str | None = None  # None 表示获取所有
) -> str:
    """获取学习到的用户模式
    
    Args:
        pattern_type: 模式类型（可选），None 表示获取所有
    
    Returns:
        格式化的模式列表
    """
```

---

### 模块 2: 创意管理模块

#### 2.1 add_idea() - 已有，保持不变

#### 2.2 get_daily_ideas()

```python
@toolset.tool
async def get_daily_ideas(
    ctx: RunContext[DepsType],
    date: str | None = None  # YYYY-MM-DD，None 表示今天
) -> str:
    """获取某日的创意想法
    
    Args:
        date: 日期（格式：YYYY-MM-DD），None 表示今天
    
    Returns:
        格式化的每日创意记录
    """
```

**返回格式**:
```
## 📝 2024-01-15 的创意记录

1. **15:30** - 用户可以通过语音快速记录想法
   - 标签: 产品, 功能
   - 分类: 产品想法

2. **16:45** - 添加日程冲突检测功能
   - 标签: 技术, 功能
   - 分类: 技术灵感
```

#### 2.3 get_recent_ideas()

```python
@toolset.tool
async def get_recent_ideas(
    ctx: RunContext[DepsType],
    days: int = 7  # 最近N天
) -> str:
    """获取最近N天的创意想法
    
    Args:
        days: 天数，默认7天
    
    Returns:
        格式化的创意记录（按日期分组）
    """
```

---

### 模块 3: 待办管理模块

#### 3.1 add_todo() - 已有，需要增强

**增强点**:
- 自动创建提醒（如果 due_date 存在）
- 自动创建询问（根据用户偏好）

#### 3.2 auto_migrate_overdue_todos()

```python
@toolset.tool
async def auto_migrate_overdue_todos(
    ctx: RunContext[DepsType]
) -> str:
    """自动移动过期的待办事项到明天
    
    检查所有 pending/in_progress/scheduled 状态的待办：
    - 如果 due_date < 今天 → 移动到明天（due_date = 今天+1）
    - 记录迁移历史
    - 更新 auto_migrated 标志
    
    Returns:
        迁移结果摘要
    """
```

**迁移规则**:
- 只迁移 `pending`, `in_progress`, `scheduled` 状态的待办
- 不迁移 `completed` 状态的待办
- 更新 `due_date` 为明天
- 在 `migration_history` 中记录迁移历史
- 设置 `auto_migrated = true`

#### 3.3 create_todo_reminder()

```python
@toolset.tool
async def create_todo_reminder(
    ctx: RunContext[DepsType],
    todo_id: str,
    reminder_minutes: int = 30  # 提前多少分钟提醒
) -> str:
    """为待办事项创建提醒
    
    在 reminders 数组中添加提醒记录
    
    Args:
        todo_id: 待办ID
        reminder_minutes: 提前提醒分钟数
    
    Returns:
        提醒创建确认信息
    """
```

#### 3.4 create_todo_followup()

```python
@toolset.tool
async def create_todo_followup(
    ctx: RunContext[DepsType],
    todo_id: str,
    ask_after_hours: int = 4  # 多少小时后询问
) -> str:
    """为待办事项创建完成情况询问
    
    在 followups 数组中添加询问记录
    
    Args:
        todo_id: 待办ID
        ask_after_hours: 多少小时后询问（默认4小时）
    
    Returns:
        询问创建确认信息
    """
```

#### 3.5 get_pending_todo_reminders()

```python
@toolset.tool
async def get_pending_todo_reminders(
    ctx: RunContext[DepsType],
    before: str | None = None  # YYYY-MM-DD HH:MM，None 表示现在
) -> str:
    """获取待触发的待办提醒
    
    检查 reminders 数组：
    - type == "todo"
    - triggered == false
    - remind_at <= before（或现在）
    
    Returns:
        待触发的提醒列表（用于 Agent 主动提醒用户）
    """
```

#### 3.6 get_pending_todo_followups()

```python
@toolset.tool
async def get_pending_todo_followups(
    ctx: RunContext[DepsType],
    before: str | None = None
) -> str:
    """获取待触发的待办询问
    
    检查 followups 数组：
    - type == "todo_completion"
    - asked == false
    - ask_at <= before（或现在）
    
    Returns:
        待触发的询问列表（用于 Agent 主动询问用户）
    """
```

---

### 模块 4: 日程管理模块

#### 4.1 add_one_time_event() - 已有，保持不变

#### 4.2 add_regular_schedule() - 已有，保持不变

#### 4.3 auto_schedule_todo()

```python
@toolset.tool
async def auto_schedule_todo(
    ctx: RunContext[DepsType],
    todo_id: str,
    preferred_date: str | None = None,  # YYYY-MM-DD，None 表示本周内
    preferred_time: str | None = None  # HH:MM，None 表示根据偏好自动选择
) -> str:
    """智能安排待办事项到时间段
    
    流程：
    1. 获取待办信息（estimated_duration, priority, category）
    2. 评估紧急程度（assess_todo_urgency）
    3. 查找可用时间段（find_available_time_slot）
    4. 安排时间（schedule_todo）
    5. 创建提醒（create_todo_reminder）
    
    Args:
        todo_id: 待办ID
        preferred_date: 偏好日期（可选）
        preferred_time: 偏好时间（可选）
    
    Returns:
        安排结果
    """
```

#### 4.4 assess_todo_urgency()

```python
@toolset.tool
async def assess_todo_urgency(
    ctx: RunContext[DepsType],
    todo_id: str
) -> dict:
    """评估待办事项的紧急程度
    
    考虑因素：
    - due_date（截止日期）
    - priority（优先级）
    - estimated_duration（预估时长）
    - category（分类）
    
    返回：
    {
        "urgency": "high" | "medium" | "low",
        "urgency_score": 0-100,
        "recommended_schedule_date": "YYYY-MM-DD",
        "reason": "原因说明"
    }
    """
```

#### 4.5 find_available_time_slot()

```python
@toolset.tool
async def find_available_time_slot(
    ctx: RunContext[DepsType],
    duration: str,  # 如 "1小时", "30分钟"
    date_range: str = "week",  # "today", "week", "month"
    preferred_time: str | None = None  # HH:MM，偏好时间段
) -> str:
    """查找可用时间段
    
    流程：
    1. 读取用户的工作时间偏好
    2. 读取现有日程（regular + upcoming）
    3. 查找空闲时间段
    4. 考虑用户偏好（如学习任务偏好上午）
    
    Returns:
        推荐的可用时间段列表
    """
```

---

## 工作流程设计

### 流程 1: 个性化学习流程

```
用户对话
  ↓
Agent 识别学习时机
  ↓
调用 learn_user_pattern()
  ↓
保存到 memory.json (preferences 或 habits)
  ↓
下次对话时动态注入到系统提示
  ↓
影响 Agent 行为
```

### 流程 2: 创意记录流程

```
用户说："我有一个想法..."
  ↓
Agent 识别为创意想法
  ↓
调用 add_idea()
  ↓
保存到 memory.json (ideas 数组)
  ↓
用户查询："今天的创意"
  ↓
调用 get_daily_ideas()
  ↓
展示每日创意记录
```

### 流程 3: 待办管理流程

#### 3.1 添加待办流程

```
用户说："我要完成项目文档，截止日期是明天"
  ↓
Agent 调用 add_todo(content, due_date="2024-01-20")
  ↓
自动创建提醒（due_date 前30分钟）
  ↓
自动创建询问（due_date 后4小时）
  ↓
保存到 memory.json
```

#### 3.2 自动移动流程

```
每天开始时（或定期检查）
  ↓
Agent 调用 auto_migrate_overdue_todos()
  ↓
检查所有待办：
  - due_date < 今天
  - status != completed
  ↓
移动到明天（due_date = 今天+1）
  ↓
记录迁移历史
  ↓
更新 memory.json
```

#### 3.3 提醒流程

```
每次对话开始时
  ↓
Agent 调用 get_pending_todo_reminders()
  ↓
检查 reminders：
  - remind_at <= 现在
  - triggered == false
  ↓
如果有待触发提醒：
  - 主动提醒用户
  - 标记 triggered = true
```

#### 3.4 询问流程

```
每次对话开始时
  ↓
Agent 调用 get_pending_todo_followups()
  ↓
检查 followups：
  - ask_at <= 现在
  - asked == false
  ↓
如果有待触发询问：
  - 主动询问用户："待办事项'XXX'是否已完成？"
  - 标记 asked = true
```

### 流程 4: 日程安排流程

#### 4.1 用户明确时间

```
用户说："明天下午2点有会议"
  ↓
Agent 调用 add_one_time_event(
    title="会议",
    start_time="2024-01-20 14:00:00"
)
  ↓
保存到 schedule.upcoming
```

#### 4.2 用户说待办，AI 自动安排

```
用户说："我要完成项目文档"
  ↓
Agent 调用 add_todo(content="完成项目文档")
  ↓
Agent 调用 assess_todo_urgency() 评估紧急程度
  ↓
Agent 调用 find_available_time_slot() 查找可用时间
  ↓
Agent 调用 auto_schedule_todo() 安排时间段
  ↓
Agent 调用 create_todo_reminder() 创建提醒
  ↓
保存到 memory.json
```

---

## 系统提示集成

### 在 MAIN_INSTRUCTIONS 中添加

```python
MAIN_INSTRUCTIONS = """
## 个性化学习

**CRITICAL**: 在对话中主动学习用户的习惯和偏好。

### 学习时机

当用户表现出以下行为时，**立即**使用 `learn_user_pattern()` 学习：

1. **使用习惯**: 用户说"我喜欢用表格展示" → learn_user_pattern("使用习惯", "信息展示偏好：表格格式", 0.95)
2. **聊天习惯**: 用户说"直接做，不用问我" → learn_user_pattern("聊天习惯", "确认频率：低", 0.95)
3. **办事习惯**: 用户说"越快越好" → learn_user_pattern("办事习惯", "决策风格：快速决策", 0.9)
4. **语言偏好**: 用户使用专业术语 → learn_user_pattern("语言偏好", "专业术语：使用", 0.8)

## 创意记录

当用户表达创意想法时：
- **立即**使用 `add_idea()` 记录
- 自动提取标签和分类
- 按日期组织，形成每日创意记录

## 待办管理

### 添加待办

当用户提到待办事项时：
1. 使用 `add_todo()` 记录
2. 如果有截止日期，自动创建提醒和询问
3. 如果用户没有说截止日期，根据内容推断

### 自动移动

**每天开始时**（或定期）：
- 调用 `auto_migrate_overdue_todos()` 移动过期待办

### 提醒和询问

**每次对话开始时**：
1. 调用 `get_pending_todo_reminders()` 检查待触发提醒
2. 调用 `get_pending_todo_followups()` 检查待触发询问
3. 如果有，主动提醒/询问用户

## 日程安排

### 用户明确时间

当用户说"X时间有Y事情"：
- 使用 `add_one_time_event()` 添加到日历

### 用户说待办，AI 自动安排

当用户说待办事项时：
1. 使用 `add_todo()` 记录
2. 使用 `assess_todo_urgency()` 评估紧急程度
3. 使用 `find_available_time_slot()` 查找可用时间
4. 使用 `auto_schedule_todo()` 安排时间段
5. 创建提醒和询问

**智能安排规则**：
- 高优先级 → 安排在最近的工作日
- 中等优先级 → 安排在本周
- 低优先级 → 安排在下周
- 考虑用户的工作时间偏好
- 避免时间冲突
"""
```

---

## 动态注入设计

### 注入学习结果

```python
@agent.instructions
def inject_user_patterns(ctx: Any) -> str:
    """注入学习到的用户模式"""
    memory_sys = MemorySystem(...)
    data = memory_sys.storage.get_all_data()
    preferences = data.get("profile", {}).get("preferences", {})
    
    parts = []
    
    # 使用习惯
    if preferences.get("使用习惯"):
        parts.append("## 📊 用户使用习惯")
        for key, value in preferences["使用习惯"].items():
            parts.append(f"- **{key}**: {value}")
    
    # 聊天习惯
    if preferences.get("聊天习惯"):
        parts.append("## 💬 用户聊天习惯")
        parts.append("**重要**: 根据这些习惯调整你的回复风格")
        for key, value in preferences["聊天习惯"].items():
            parts.append(f"- **{key}**: {value}")
    
    # ... 其他模式 ...
    
    return "\n".join(parts)
```

### 注入待办提醒和询问

```python
@agent.instructions
def inject_todo_alerts(ctx: Any) -> str:
    """注入待办提醒和询问"""
    memory_sys = MemorySystem(...)
    
    parts = []
    
    # 检查待触发提醒
    reminders = memory_sys.get_pending_reminders()
    if reminders:
        parts.append("## ⏰ 待办提醒")
        for reminder in reminders:
            if reminder["type"] == "todo":
                todo = memory_sys.get_todo(reminder["target_id"])
                if todo:
                    parts.append(f"- **提醒**: {todo['content']}（截止：{todo.get('due_date', '')}）")
    
    # 检查待触发询问
    followups = memory_sys.get_pending_followups()
    if followups:
        parts.append("## ❓ 待询问事项")
        for followup in followups:
            if followup["type"] == "todo_completion":
                todo = memory_sys.get_todo(followup["target_id"])
                if todo:
                    parts.append(f"- **询问**: {followup.get('question', '')}")
    
    return "\n".join(parts) if parts else ""
```

---

## 数据迁移设计

### 新增字段

在 `_initialize_json()` 中添加：

```python
"todos": {
    "pending": [
        {
            # ... 现有字段 ...
            "auto_migrated": false,  # 新增
            "migration_history": []  # 新增
        }
    ]
}
```

### 迁移脚本

```python
def migrate_to_v3(memory_file: Path):
    """迁移到 v3.0 格式"""
    data = json.loads(memory_file.read_text())
    
    # 添加新字段
    for status in ["pending", "scheduled", "in_progress"]:
        for todo in data["todos"].get(status, []):
            if "auto_migrated" not in todo:
                todo["auto_migrated"] = False
            if "migration_history" not in todo:
                todo["migration_history"] = []
    
    # 更新版本
    data["metadata"]["version"] = "3.0"
    
    memory_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
```

---

## 实现优先级

### P0（核心功能，必须实现）

1. ✅ **个性化学习**
   - `learn_user_pattern()` - 统一学习接口
   - 动态注入学习结果

2. ✅ **创意记录**
   - `get_daily_ideas()` - 获取每日创意
   - `get_recent_ideas()` - 获取最近创意

3. ✅ **待办管理**
   - `auto_migrate_overdue_todos()` - 自动移动过期待办
   - `get_pending_todo_reminders()` - 获取待触发提醒
   - `get_pending_todo_followups()` - 获取待触发询问

4. ✅ **日程安排**
   - `auto_schedule_todo()` - 智能安排待办
   - `assess_todo_urgency()` - 评估紧急程度
   - `find_available_time_slot()` - 查找可用时间

### P1（增强功能，推荐实现）

1. ⚠️ **学习结果应用**
   - 更智能的模式应用
   - 模式冲突检测

2. ⚠️ **创意搜索**
   - `search_ideas()` - 搜索创意

3. ⚠️ **待办分析**
   - 待办完成率统计
   - 待办时间分析

---

## 总结

### 核心设计原则

1. ✅ **统一存储** - 所有数据在 `memory.json`
2. ✅ **模块化设计** - 4个功能模块，职责清晰
3. ✅ **自动化** - 自动移动、自动提醒、自动询问、自动安排
4. ✅ **智能化** - 智能评估紧急程度、智能查找时间段
5. ✅ **可扩展** - 易于添加新功能

### 关键特性

- **个性化学习**: 统一的学习接口，支持4种模式类型
- **创意记录**: 按日期组织，形成每日创意记录
- **待办管理**: 自动移动、提醒、询问机制
- **日程安排**: 智能评估和自动安排

### 下一步

1. 实现 P0 功能
2. 添加系统提示指导
3. 实现动态注入
4. 测试和优化
