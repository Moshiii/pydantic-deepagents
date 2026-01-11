# 日程排期小助理 Toolset - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品定位
日程排期小助理是一个个人时间管理工具集，帮助用户记录待办事项、安排时间预算、管理周期性任务，并记录创意想法。所有数据以标准格式存储，支持导出到第三方日历软件（如 Google Calendar、Apple Calendar、Outlook 等）。

### 1.2 核心价值
- **智能排期**：根据用户需求自动安排时间段预算
- **灵活周期**：支持一次性事件和多种周期性模式（每天、每周、每月等）
- **创意记录**：快速记录突发灵感，支持日期标记
- **标准格式**：数据存储符合 iCal/ICS 标准，便于导出和同步
- **越用越懂**：自动学习用户的使用习惯和偏好，提供个性化服务

## 2. 功能需求

### 2.1 待办事项管理

#### 2.1.1 创建待办事项
**功能描述**：用户告诉助理想要办什么事，助理记录为待办事项。

**输入参数**：
- `content` (string, 必需): 待办事项内容描述
- `priority` (string, 可选): 优先级（low/medium/high），默认 medium
- `estimated_duration` (string, 可选): 预估时长（如 "30分钟"、"2小时"、"半天"）
- `due_date` (string, 可选): 截止日期（格式：YYYY-MM-DD）
- `category` (string, 可选): 分类标签（如 "工作"、"学习"、"生活"、"健康"）

**输出**：
- 返回创建成功的确认信息
- 自动生成唯一 ID

**示例**：
```
用户："我想学习 Python 的异步编程"
助理：[调用 create_todo]
返回："已创建待办：学习 Python 的异步编程（优先级：medium）"
```

#### 2.1.2 安排时间预算
**功能描述**：为待办事项安排具体的时间段预算。

**输入参数**：
- `todo_id` (string, 必需): 待办事项 ID
- `start_time` (string, 必需): 开始时间（格式：YYYY-MM-DD HH:MM 或 YYYY-MM-DDTHH:MM）
- `duration` (string, 必需): 持续时间（如 "30分钟"、"1小时"、"2小时30分钟"）
- `flexible` (boolean, 可选): 是否灵活调整（默认 false）
- `reminder_minutes` (integer, 可选): 提前提醒分钟数（默认 15）

**输出**：
- 返回时间安排确认信息
- 更新待办事项状态为 "scheduled"

**示例**：
```
用户："帮我安排明天下午2点到3点学习 Python"
助理：[调用 schedule_todo]
返回："已安排：明天（2024-01-20）14:00-15:00 学习 Python 的异步编程"
```

#### 2.1.3 查询待办事项
**功能描述**：查询用户的待办事项列表。

**输入参数**：
- `status` (string, 可选): 状态筛选（pending/scheduled/in_progress/completed/cancelled），默认 all
- `category` (string, 可选): 分类筛选
- `due_before` (string, 可选): 截止日期筛选（格式：YYYY-MM-DD）
- `limit` (integer, 可选): 返回数量限制（默认 50）

**输出**：
- 返回格式化的待办事项列表，包含 ID、内容、状态、优先级、时间安排等

### 2.2 周期性日程管理

#### 2.2.1 创建周期性日程
**功能描述**：创建重复性日程，支持多种频率模式。

**输入参数**：
- `title` (string, 必需): 日程标题
- `start_time` (string, 必需): 开始时间（格式：HH:MM，如 "10:00"）
- `duration` (string, 必需): 持续时间（如 "30分钟"、"1小时"）
- `frequency` (string, 必需): 频率模式，支持：
  - `daily`: 每天
  - `weekdays`: 工作日（周一至周五）
  - `weekends`: 周末（周六、周日）
  - `weekly_MON/TUE/WED/THU/FRI/SAT/SUN`: 每周特定日期（如 "weekly_MON" 表示每周一）
  - `monthly_DAY`: 每月特定日期（如 "monthly_1" 表示每月1号）
  - `custom`: 自定义（需要提供 `custom_pattern` 参数）
- `custom_pattern` (string, 可选): 自定义频率模式（RRULE 格式）
- `description` (string, 可选): 备注说明
- `end_date` (string, 可选): 结束日期（格式：YYYY-MM-DD），不设置则无限期
- `reminder_minutes` (integer, 可选): 提前提醒分钟数（默认 15）

**输出**：
- 返回创建成功的确认信息
- 自动生成唯一 ID

**示例**：
```
用户："每周末我想运动"
助理：[调用 create_recurring_schedule]
返回："已创建周期性日程：每周末运动，时间：周六和周日 09:00-10:00"

用户："每周二下午3点开会"
助理：[调用 create_recurring_schedule]
返回："已创建周期性日程：每周二 15:00-16:00 开会"
```

#### 2.2.2 创建一次性日程事件
**功能描述**：创建单次日程事件。

**输入参数**：
- `title` (string, 必需): 事件标题
- `start_time` (string, 必需): 开始时间（格式：YYYY-MM-DD HH:MM）
- `end_time` (string, 可选): 结束时间（格式：YYYY-MM-DD HH:MM），不设置则使用 duration
- `duration` (string, 可选): 持续时间（与 end_time 二选一）
- `description` (string, 可选): 事件描述
- `location` (string, 可选): 地点
- `reminder_minutes` (integer, 可选): 提前提醒分钟数（默认 15）

**输出**：
- 返回创建成功的确认信息
- 自动生成唯一 ID

#### 2.2.3 查询日程
**功能描述**：查询用户的日程安排。

**输入参数**：
- `start_date` (string, 可选): 开始日期（格式：YYYY-MM-DD），默认今天
- `end_date` (string, 可选): 结束日期（格式：YYYY-MM-DD），默认未来7天
- `include_recurring` (boolean, 可选): 是否包含周期性日程（默认 true）
- `include_one_time` (boolean, 可选): 是否包含一次性事件（默认 true）

**输出**：
- 返回格式化的日程列表，包含日期、时间、标题、类型（周期性/一次性）等

### 2.3 创意想法记录

#### 2.3.1 记录创意想法
**功能描述**：快速记录用户的想法和灵感，类似日记功能。

**输入参数**：
- `content` (string, 必需): 想法内容
- `date` (string, 可选): 日期（格式：YYYY-MM-DD），默认今天
- `time` (string, 可选): 时间（格式：HH:MM），默认当前时间
- `tags` (array[string], 可选): 标签列表（如 ["工作", "产品", "技术"]）
- `category` (string, 可选): 分类（如 "产品想法"、"技术灵感"、"生活感悟"）

**输出**：
- 返回创建成功的确认信息
- 自动生成唯一 ID

**示例**：
```
用户："我突然想到一个产品功能：用户可以通过语音快速记录想法"
助理：[调用 record_idea]
返回："已记录创意想法：用户可以通过语音快速记录想法（2024-01-20 15:30）"
```

#### 2.3.2 查询创意想法
**功能描述**：查询用户记录的创意想法。

**输入参数**：
- `start_date` (string, 可选): 开始日期（格式：YYYY-MM-DD）
- `end_date` (string, 可选): 结束日期（格式：YYYY-MM-DD）
- `tags` (array[string], 可选): 标签筛选
- `category` (string, 可选): 分类筛选
- `limit` (integer, 可选): 返回数量限制（默认 50）

**输出**：
- 返回格式化的想法列表，包含日期、时间、内容、标签等

### 2.4 自动学习用户偏好（核心功能）

#### 2.4.1 功能概述
**功能描述**：日程助理在每次对话中自动捕捉用户的使用习惯和偏好信息，并保存到记忆系统中。这些偏好信息会在后续的日程安排、时间建议等场景中自动应用，实现"越用越懂"的效果。

**学习机制**：
- **隐式学习**：从用户的自然语言表达和行为模式中自动提取偏好
- **显式学习**：用户明确表达偏好时立即记录
- **模式识别**：分析历史数据，识别重复出现的模式
- **偏好应用**：在安排日程、建议时间时自动应用已学习的偏好

#### 2.4.2 可学习的偏好类型

##### A. 时间偏好
- **工作时间**：用户通常的工作时间段（如 "09:00-18:00"）
- **午休时间**：午休时间段（如 "12:00-13:00"）
- **偏好时间段**：用户喜欢安排任务的时间段（如 "上午10:00-11:00"、"下午14:00-16:00"）
- **不活跃时间**：用户不希望被打扰的时间段（如 "晚上21:00后"、"周末早上"）
- **时区偏好**：用户的时区设置

**学习示例**：
```
用户："我一般早上9点开始工作"
助理：[自动学习] → 记录偏好：工作时间 09:00-18:00

用户："我中午12点到1点要午休"
助理：[自动学习] → 记录偏好：午休时间 12:00-13:00

用户："我下午2点到4点效率最高"
助理：[自动学习] → 记录偏好：高效时间段 14:00-16:00
```

##### B. 工作习惯偏好
- **专注时间偏好**：用户喜欢在什么时间段做需要专注的任务
- **会议时间偏好**：用户偏好的会议时间段
- **任务类型时间分配**：不同类型任务偏好的时间段（如学习→上午，运动→晚上）
- **工作日定义**：用户的工作日是哪几天（如 "周一至周五"）

**学习示例**：
```
用户："我喜欢早上处理重要任务"
助理：[自动学习] → 记录习惯：重要任务偏好安排在上午

用户："我每周一到周五工作"
助理：[自动学习] → 记录偏好：工作日 周一至周五

用户："学习类的任务我一般安排在上午"
助理：[自动学习] → 记录偏好：学习任务 → 上午时间段
```

##### C. 提醒偏好
- **提醒方式**：用户偏好的提醒方式（如 "提前15分钟"、"提前30分钟"）
- **提醒时间**：不同重要程度的提醒提前时间
- **提醒频率**：是否接受频繁提醒

**学习示例**：
```
用户："重要的事情提前30分钟提醒我"
助理：[自动学习] → 记录偏好：重要事项提醒提前30分钟

用户："一般提醒提前15分钟就够了"
助理：[自动学习] → 记录偏好：默认提醒提前15分钟
```

##### D. 日程安排偏好
- **日程密度偏好**：用户喜欢紧凑还是宽松的日程安排
- **缓冲时间偏好**：是否需要在日程之间留出缓冲时间
- **周期性任务偏好**：用户创建周期性任务的常见模式

**学习示例**：
```
用户："我习惯在日程之间留15分钟缓冲"
助理：[自动学习] → 记录偏好：日程间隔缓冲时间 15分钟

用户："我每周末都会运动"
助理：[自动学习] → 记录习惯：周末运动（周期性模式）
```

##### E. 任务分类偏好
- **任务分类习惯**：用户如何分类任务（工作/学习/生活/健康等）
- **优先级习惯**：用户如何判断任务优先级
- **任务时长估算习惯**：用户对不同类型任务的时长估算模式

**学习示例**：
```
用户："学习类的任务我一般预估2小时"
助理：[自动学习] → 记录偏好：学习任务默认时长 2小时

用户："工作相关的任务优先级高"
助理：[自动学习] → 记录偏好：工作类任务默认高优先级
```

#### 2.4.3 自动学习触发场景

##### 场景1：创建待办事项时
- 检测用户提到的时间偏好（如 "早上"、"下午"、"晚上"）
- 检测任务类型和用户习惯的时间段匹配
- 自动应用已学习的偏好

**示例**：
```
用户："我想学习 Python，帮我安排一下"
助理：[检测到"学习"任务] → [查询偏好：学习任务偏好时间段] → [应用偏好：安排在上午]
返回："根据您的习惯，我建议安排在明天上午10:00-12:00，可以吗？"
```

##### 场景2：安排时间预算时
- 检测用户明确提到的时间偏好
- 检测与已有偏好的冲突
- 学习新的时间偏好模式

**示例**：
```
用户："帮我安排在下午3点"
助理：[学习] → 记录：用户偏好下午3点安排任务
返回："已安排在明天下午15:00-16:00"
```

##### 场景3：创建周期性日程时
- 检测周期性模式（如 "每周末"、"每周二"）
- 学习用户的周期性习惯
- 记录周期性任务的时间偏好

**示例**：
```
用户："每周末我想运动"
助理：[学习] → 记录：周期性习惯 - 周末运动
返回："已创建周期性日程：每周末运动"
```

##### 场景4：用户明确表达偏好时
- 直接记录用户明确表达的偏好
- 更新已有偏好（如果用户改变偏好）

**示例**：
```
用户："我改作息了，现在早上8点开始工作"
助理：[学习] → 更新偏好：工作时间 08:00-17:00（覆盖旧偏好）
返回："已更新您的工作时间偏好：08:00-17:00"
```

#### 2.4.4 偏好应用机制

##### 应用场景1：智能排期建议
当用户创建待办事项但未指定时间时，自动应用偏好：
```
用户："我想学习 Python"
助理：[查询偏好] → [应用偏好：学习任务→上午，默认时长2小时] → [建议时间：明天上午10:00-12:00]
```

##### 应用场景2：时间冲突检测
检测新安排是否与用户偏好冲突：
```
用户："帮我安排在中午12点学习"
助理：[检测冲突] → [发现偏好：午休时间12:00-13:00] → [提示冲突] → [建议调整]
返回："您通常在这个时间午休，建议调整到下午14:00，可以吗？"
```

##### 应用场景3：默认值设置
创建新日程时自动应用偏好作为默认值：
```
用户："添加一个学习任务"
助理：[应用偏好] → [默认时间段：上午] → [默认时长：2小时] → [默认提醒：提前15分钟]
```

#### 2.4.5 偏好存储与记忆系统集成

##### 存储位置
偏好信息存储在记忆系统中，与现有的 `memory.json` 和 `profile.md` 集成：

**在 memory.json 中存储**：
```json
{
  "preferences": {
    "schedule": {
      "work_hours": "09:00-18:00",
      "lunch_break": "12:00-13:00",
      "preferred_times": {
        "learning": "上午",
        "meeting": "10:00-11:00, 14:00-16:00",
        "exercise": "晚上"
      },
      "buffer_time_minutes": 15,
      "reminder_default_minutes": 15,
      "reminder_important_minutes": 30
    },
    "habits": {
      "weekend_exercise": true,
      "morning_focus": true,
      "weekdays_only": true
    }
  }
}
```

**在 profile.md 中显示**：
```markdown
### 日程偏好
- 工作时间：`09:00-18:00`
- 午休时间：`12:00-13:00`
- 学习任务偏好时间段：`上午`
- 会议偏好时间段：`10:00-11:00, 14:00-16:00`
- 日程缓冲时间：`15分钟`
- 默认提醒时间：`提前15分钟`
- 重要事项提醒时间：`提前30分钟`

### 学习到的习惯
- 每周末运动（学习时间：2024-01-15）
- 喜欢早上处理重要任务（学习时间：2024-01-10）
- 工作日安排工作，周末安排生活（学习时间：2024-01-08）
```

#### 2.4.6 工具函数设计

##### 自动学习偏好（内部函数，无需暴露给用户）
```python
async def learn_preference_from_conversation(
    ctx: RunContext,
    preference_type: str,
    preference_value: str,
    confidence: float = 1.0,  # 学习置信度（0-1）
    source: str = "conversation"  # 学习来源
) -> str:
    """从对话中自动学习偏好
    
    Args:
        preference_type: 偏好类型（如 "work_hours", "preferred_time_learning"）
        preference_value: 偏好值（如 "09:00-18:00", "上午"）
        confidence: 学习置信度（显式表达=1.0，推断=0.7）
        source: 学习来源（"conversation", "behavior_pattern", "explicit"）
    """
    # 1. 保存到记忆系统
    # 2. 更新 profile.md
    # 3. 返回确认信息
```

##### 查询偏好（供其他工具使用）
```python
async def get_user_preference(
    ctx: RunContext,
    preference_type: str,
    default_value: str = None
) -> str:
    """获取用户偏好
    
    Args:
        preference_type: 偏好类型
        default_value: 如果没有找到偏好，返回默认值
    """
    # 从记忆系统中查询偏好
    # 返回偏好值或默认值
```

##### 应用偏好（供排期工具使用）
```python
async def suggest_time_with_preferences(
    ctx: RunContext,
    task_type: str,
    duration: str,
    date: str = None
) -> dict:
    """根据用户偏好建议时间
    
    Args:
        task_type: 任务类型（如 "learning", "meeting", "exercise"）
        duration: 任务时长
        date: 日期（可选）
    
    Returns:
        建议的时间段字典
    """
    # 1. 查询任务类型的偏好时间段
    # 2. 查询用户的工作时间偏好
    # 3. 检测时间冲突
    # 4. 返回建议时间段
```

#### 2.4.7 学习策略与置信度

##### 学习置信度等级
1. **高置信度（1.0）**：用户明确表达的偏好
   - 示例："我早上9点开始工作"
   - 立即更新偏好

2. **中置信度（0.7-0.9）**：从行为模式推断的偏好
   - 示例：用户连续3次将学习任务安排在上午
   - 需要多次确认后才更新

3. **低置信度（0.5-0.6）**：单次行为或模糊表达
   - 示例：用户某次提到"下午也可以"
   - 仅作为临时偏好，不持久化

##### 偏好更新策略
- **覆盖策略**：用户明确改变偏好时，覆盖旧偏好
- **合并策略**：多个时间段偏好可以合并（如 "上午和下午都可以"）
- **衰减策略**：长期未使用的偏好置信度逐渐降低

#### 2.4.8 用户控制与透明度

##### 查看已学习的偏好
用户可以通过查询命令查看所有已学习的偏好：
```
用户："我的偏好是什么？"
助理：[调用 read_memory(section="preferences")] → 显示所有偏好
```

##### 修改偏好
用户可以直接修改偏好：
```
用户："我的工作时间改成8点到5点"
助理：[调用 update_preference] → 更新偏好
```

##### 删除偏好
用户可以选择删除某些偏好：
```
用户："删除我的午休时间偏好"
助理：[调用 remove_preference] → 删除偏好
```

### 2.5 主动提醒与跟进功能（核心功能）

#### 2.5.1 功能概述
**功能描述**：日程助理不仅是被动响应，还会主动提醒用户即将到来的日程和待办事项，并定期主动询问任务完成情况，帮助用户更好地管理时间和任务。

**核心价值**：
- **主动提醒**：在合适的时间主动提醒用户即将到来的日程和待办
- **任务跟进**：定期主动询问任务完成情况，帮助用户保持进度
- **智能时机**：根据用户偏好和学习到的习惯，选择最合适的提醒和询问时机
- **个性化频率**：根据任务重要性和用户习惯，调整提醒和询问的频率

#### 2.5.2 主动提醒功能

##### A. 提醒触发时机

**1. 日程开始前提醒**
- **提前时间**：根据用户偏好设置（默认15分钟，重要事项30分钟）
- **触发条件**：日程开始时间 - 提醒提前时间 = 当前时间
- **提醒内容**：日程标题、开始时间、地点（如有）、准备事项（如有）

**示例**：
```
[系统自动触发，在日程开始前15分钟]
助理："提醒：您15分钟后有一个会议'项目评审'，时间：14:00，地点：会议室A。需要准备PPT。"
```

**2. 待办事项截止日期提醒**
- **提前时间**：根据截止日期和优先级动态调整
  - 高优先级：提前1天 + 提前3小时
  - 中优先级：提前1天
  - 低优先级：提前半天
- **触发条件**：截止日期 - 提前时间 = 当前时间
- **提醒内容**：待办内容、截止时间、当前状态、建议行动

**示例**：
```
[系统自动触发，在截止日期前1天]
助理："提醒：您有一个待办事项'完成项目文档'明天（2024-01-25）截止，当前状态：进行中。建议今天完成。"
```

**3. 周期性日程提醒**
- **提醒时间**：每次周期性日程开始前，根据用户设置的提醒时间
- **提醒内容**：日程标题、时间、频率说明

**示例**：
```
[系统自动触发，每周二下午2:45]
助理："提醒：您15分钟后有周期性日程'每周二开会'，时间：15:00。"
```

**4. 日程冲突提醒**
- **触发条件**：检测到新安排的日程与已有日程冲突
- **提醒时机**：创建日程时立即提醒
- **提醒内容**：冲突的日程详情、建议解决方案

**示例**：
```
用户："帮我安排在明天下午3点学习"
助理：[检测到冲突] "提醒：明天下午3点您已有日程'团队会议'，建议调整学习时间到下午4点，可以吗？"
```

##### B. 提醒方式

**1. 对话内提醒**
- 在用户与助理对话时，主动推送提醒消息
- 适用于实时交互场景

**2. 主动发起对话**
- 在非对话时间，主动发起对话提醒用户
- 需要支持推送通知或定时任务机制

**3. 提醒优先级**
- **紧急提醒**：立即推送，多次提醒
- **重要提醒**：提前推送，单次提醒
- **一般提醒**：按时推送，单次提醒

##### C. 提醒内容模板

**日程提醒模板**：
```
提醒：您{提前时间}后有一个{日程类型}：{标题}
时间：{开始时间}
{地点：{地点}（如有）}
{准备事项：{事项}（如有）}
```

**待办提醒模板**：
```
提醒：您有一个待办事项：{内容}
截止时间：{截止日期} {截止时间}
当前状态：{状态}
{建议：{建议行动}（如有）}
```

#### 2.5.3 主动询问任务完成情况

##### A. 询问触发时机

**1. 任务时间到期后询问**
- **触发条件**：已安排的待办事项时间已过
- **询问时机**：任务时间结束后30分钟-2小时（可配置）
- **询问内容**：任务是否完成、完成情况、是否需要调整

**示例**：
```
[系统自动触发，任务时间结束后1小时]
助理："您好！您今天下午2-3点安排了'学习 Python'，请问完成得怎么样了？如果完成了，我可以帮您标记为已完成；如果还没完成，需要我重新安排时间吗？"
```

**2. 周期性任务执行情况询问**
- **触发时机**：周期性日程执行后
- **询问频率**：每次执行后询问，或每周/每月汇总询问（根据用户偏好）
- **询问内容**：是否执行、执行情况、是否需要调整

**示例**：
```
[系统自动触发，每周二会议后]
助理："您好！今天的'每周二开会'怎么样？会议顺利吗？有什么需要我帮您记录的吗？"
```

**3. 长期任务进度询问**
- **触发时机**：对于超过3天的任务，定期询问进度
- **询问频率**：
  - 3-7天任务：每2天询问一次
  - 7-30天任务：每周询问一次
  - 30天以上任务：每2周询问一次
- **询问内容**：当前进度、遇到的困难、是否需要帮助

**示例**：
```
[系统自动触发，长期任务每2天询问]
助理："您好！您正在进行的任务'完成项目文档'（截止：2024-01-25）进度如何？有什么需要我帮助的吗？"
```

**4. 截止日期临近询问**
- **触发时机**：截止日期前1-2天
- **询问内容**：任务进度、是否需要延期、是否需要帮助

**示例**：
```
[系统自动触发，截止日期前1天]
助理："您好！您的待办事项'完成项目文档'明天就要截止了，当前状态是'进行中'。请问进度如何？需要我帮您调整截止日期吗？"
```

##### B. 询问策略

**1. 询问频率控制**
- **避免打扰**：同一任务不频繁询问（至少间隔4小时）
- **智能时机**：根据用户活跃时间偏好，选择合适的时间询问
- **用户控制**：用户可以设置"免打扰时间"和"询问频率偏好"

**2. 询问方式**
- **友好开场**：使用友好的问候语
- **简洁明了**：问题清晰，不冗长
- **提供选项**：给出明确的选项（完成/未完成/需要帮助）

**3. 询问后的处理**
- **完成确认**：用户确认完成后，自动更新任务状态
- **重新安排**：用户需要重新安排时，主动帮助调整时间
- **记录反馈**：记录用户的反馈，用于学习用户习惯

**示例交互流程**：
```
助理："您好！您今天下午2-3点安排了'学习 Python'，请问完成得怎么样了？"
用户："完成了"
助理："太好了！已帮您标记为已完成。学习效果怎么样？有什么收获吗？"
用户："还不错，理解了异步编程的基本概念"
助理："很好！已记录您的反馈。需要我帮您安排下一步的学习计划吗？"
```

#### 2.5.4 提醒和询问的个性化

##### A. 基于用户偏好的个性化

**1. 提醒时间偏好**
- 学习用户的提醒时间偏好（如"提前15分钟"、"提前30分钟"）
- 根据任务类型应用不同提醒时间

**2. 询问频率偏好**
- 学习用户喜欢的询问频率（如"每天询问"、"每周询问"、"不需要询问"）
- 根据任务重要性调整询问频率

**3. 免打扰时间**
- 学习用户的免打扰时间段（如"晚上21:00后"、"周末早上"）
- 在这些时间段不主动提醒和询问

**4. 提醒方式偏好**
- 学习用户偏好的提醒方式（如"简洁提醒"、"详细提醒"）
- 根据用户习惯调整提醒内容详细程度

##### B. 智能时机选择

**1. 用户活跃时间**
- 分析用户的历史活跃时间
- 在用户活跃时间进行提醒和询问

**2. 任务相关性**
- 在用户提到相关任务时，主动询问其他相关任务
- 在用户完成一个任务时，询问下一个任务

**示例**：
```
用户："我完成了学习 Python 的任务"
助理："太好了！已标记为已完成。您还有另一个待办'完成项目文档'，需要我帮您安排时间吗？"
```

#### 2.5.5 提醒和询问的数据模型

##### 提醒记录 (Reminder)
```json
{
  "id": "reminder_20240120_001",
  "type": "schedule",  // schedule, todo, recurring
  "target_id": "event_20240120_001",
  "remind_at": "2024-01-20T13:45:00",
  "reminded": false,
  "reminder_minutes": 15,
  "content": "提醒：您15分钟后有一个会议'项目评审'",
  "created_at": "2024-01-20T10:00:00"
}
```

##### 询问记录 (FollowUp)
```json
{
  "id": "followup_20240120_001",
  "type": "task_completion",  // task_completion, progress_check, periodic_check
  "target_id": "todo_20240120_001",
  "ask_at": "2024-01-20T16:00:00",
  "asked": false,
  "frequency": "after_task_time",  // after_task_time, daily, weekly
  "content": "您今天下午2-3点安排了'学习 Python'，请问完成得怎么样了？",
  "created_at": "2024-01-20T14:00:00"
}
```

#### 2.5.6 工具函数设计

##### 创建提醒（内部函数）
```python
async def create_reminder(
    ctx: RunContext,
    reminder_type: str,
    target_id: str,
    remind_at: str,
    reminder_minutes: int = 15,
    content: str = None
) -> str:
    """创建提醒
    
    Args:
        reminder_type: 提醒类型（schedule, todo, recurring）
        target_id: 目标ID（日程ID或待办ID）
        remind_at: 提醒时间（ISO格式）
        reminder_minutes: 提前多少分钟提醒
        content: 提醒内容（可选，自动生成）
    """
    # 1. 创建提醒记录
    # 2. 添加到提醒队列
    # 3. 返回提醒ID
```

##### 创建询问（内部函数）
```python
async def create_followup(
    ctx: RunContext,
    followup_type: str,
    target_id: str,
    ask_at: str,
    frequency: str = "after_task_time",
    content: str = None
) -> str:
    """创建询问任务
    
    Args:
        followup_type: 询问类型（task_completion, progress_check）
        target_id: 目标ID
        ask_at: 询问时间（ISO格式）
        frequency: 询问频率
        content: 询问内容（可选，自动生成）
    """
    # 1. 创建询问记录
    # 2. 添加到询问队列
    # 3. 返回询问ID
```

##### 检查并触发提醒（定时任务）
```python
async def check_and_trigger_reminders(
    ctx: RunContext
) -> list[str]:
    """检查并触发到期的提醒
    
    这个函数应该作为定时任务定期执行（如每分钟）
    
    Returns:
        已触发的提醒ID列表
    """
    # 1. 查询所有未触发的提醒
    # 2. 检查是否到期
    # 3. 触发提醒（发送消息）
    # 4. 标记为已触发
```

##### 检查并触发询问（定时任务）
```python
async def check_and_trigger_followups(
    ctx: RunContext
) -> list[str]:
    """检查并触发到期的询问
    
    这个函数应该作为定时任务定期执行（如每30分钟）
    
    Returns:
        已触发的询问ID列表
    """
    # 1. 查询所有未触发的询问
    # 2. 检查是否到期
    # 3. 触发询问（发送消息）
    # 4. 标记为已触发
```

##### 用户响应处理
```python
async def handle_reminder_response(
    ctx: RunContext,
    reminder_id: str,
    user_response: str
) -> str:
    """处理用户对提醒的响应
    
    Args:
        reminder_id: 提醒ID
        user_response: 用户响应（如"知道了"、"已完成"、"需要调整"）
    """
    # 1. 解析用户响应
    # 2. 更新相关任务状态
    # 3. 执行相应操作（如标记完成、重新安排）
```

#### 2.5.7 提醒和询问的配置

##### 用户配置项
```json
{
  "reminders": {
    "enabled": true,
    "default_minutes": 15,
    "important_minutes": 30,
    "quiet_hours": {
      "start": "21:00",
      "end": "08:00"
    },
    "quiet_days": ["周六", "周日"]  // 可选
  },
  "followups": {
    "enabled": true,
    "frequency": {
      "task_completion": "after_task_time",  // after_task_time, daily, weekly
      "progress_check": "weekly",
      "periodic_check": "after_each"
    },
    "quiet_hours": {
      "start": "21:00",
      "end": "08:00"
    },
    "min_interval_hours": 4  // 同一任务最小询问间隔
  }
}
```

#### 2.5.8 实现技术要点

##### A. 定时任务机制
- **后台任务**：需要实现后台定时任务系统
- **任务调度**：使用 `asyncio` 或 `APScheduler` 等库
- **持久化**：提醒和询问任务需要持久化存储

##### B. 消息推送机制
- **WebSocket推送**：如果用户在线，通过WebSocket实时推送
- **消息队列**：使用消息队列管理提醒和询问
- **重试机制**：如果推送失败，需要重试机制

##### C. 状态管理
- **提醒状态**：pending, triggered, cancelled
- **询问状态**：pending, asked, responded, cancelled
- **任务关联**：提醒和询问需要关联到具体的任务或日程

### 2.6 数据导出功能

#### 2.6.1 导出为 iCal/ICS 格式
**功能描述**：将所有日程数据导出为标准 iCal/ICS 格式，可导入到第三方日历软件。

**输入参数**：
- `start_date` (string, 可选): 开始日期（格式：YYYY-MM-DD），默认今天
- `end_date` (string, 可选): 结束日期（格式：YYYY-MM-DD），默认未来1年
- `include_todos` (boolean, 可选): 是否包含已安排的待办事项（默认 true）
- `include_recurring` (boolean, 可选): 是否包含周期性日程（默认 true）
- `include_one_time` (boolean, 可选): 是否包含一次性事件（默认 true）
- `include_ideas` (boolean, 可选): 是否包含创意想法（作为全天事件，默认 false）

**输出**：
- 返回 iCal/ICS 格式的字符串
- 或保存到文件并返回文件路径

**示例**：
```
用户："导出我的日程到日历文件"
助理：[调用 export_to_ical]
返回："已导出日程到文件：schedule_2024-01-20.ics，包含 15 个事件，可导入到 Google Calendar、Apple Calendar 等"
```

## 3. 数据模型设计

### 3.1 待办事项 (Todo)
```json
{
  "id": "todo_20240120_001",
  "content": "学习 Python 的异步编程",
  "priority": "medium",
  "status": "pending",  // pending, scheduled, in_progress, completed, cancelled
  "estimated_duration": "2小时",
  "due_date": "2024-01-25",
  "category": "学习",
  "scheduled_time": {
    "start": "2024-01-20T14:00:00",
    "end": "2024-01-20T16:00:00",
    "duration": "2小时"
  },
  "reminder_minutes": 15,
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:00:00"
}
```

### 3.2 周期性日程 (RecurringSchedule)
```json
{
  "id": "recurring_20240120_001",
  "title": "每周二开会",
  "start_time": "15:00",
  "duration": "1小时",
  "frequency": "weekly_TUE",
  "description": "团队周会",
  "end_date": null,  // null 表示无限期
  "reminder_minutes": 15,
  "created_at": "2024-01-20T10:00:00"
}
```

### 3.3 一次性事件 (OneTimeEvent)
```json
{
  "id": "event_20240120_001",
  "title": "项目评审会议",
  "start_time": "2024-01-25T10:00:00",
  "end_time": "2024-01-25T11:30:00",
  "description": "项目进度评审",
  "location": "会议室A",
  "reminder_minutes": 30,
  "created_at": "2024-01-20T10:00:00"
}
```

### 3.4 创意想法 (Idea)
```json
{
  "id": "idea_20240120_001",
  "content": "用户可以通过语音快速记录想法",
  "date": "2024-01-20",
  "time": "15:30",
  "tags": ["产品", "功能"],
  "category": "产品想法",
  "created_at": "2024-01-20T15:30:00"
}
```

### 3.5 提醒记录 (Reminder)
```json
{
  "id": "reminder_20240120_001",
  "type": "schedule",
  "target_id": "event_20240120_001",
  "remind_at": "2024-01-20T13:45:00",
  "reminded": false,
  "reminder_minutes": 15,
  "content": "提醒：您15分钟后有一个会议'项目评审'",
  "created_at": "2024-01-20T10:00:00"
}
```

### 3.6 询问记录 (FollowUp)
```json
{
  "id": "followup_20240120_001",
  "type": "task_completion",
  "target_id": "todo_20240120_001",
  "ask_at": "2024-01-20T16:00:00",
  "asked": false,
  "frequency": "after_task_time",
  "content": "您今天下午2-3点安排了'学习 Python'，请问完成得怎么样了？",
  "created_at": "2024-01-20T14:00:00",
  "last_asked_at": null,
  "response_count": 0
}
```

### 3.7 用户偏好 (UserPreferences)
```json
{
  "schedule": {
    "work_hours": "09:00-18:00",
    "lunch_break": "12:00-13:00",
    "preferred_times": {
      "learning": "上午",
      "meeting": "10:00-11:00, 14:00-16:00",
      "exercise": "晚上",
      "focus_work": "上午"
    },
    "buffer_time_minutes": 15,
    "reminder_default_minutes": 15,
    "reminder_important_minutes": 30
  },
  "habits": {
    "weekend_exercise": {
      "value": true,
      "learned_at": "2024-01-15",
      "confidence": 1.0,
      "source": "explicit"
    },
    "morning_focus": {
      "value": true,
      "learned_at": "2024-01-10",
      "confidence": 0.9,
      "source": "behavior_pattern"
    }
  },
  "task_preferences": {
    "learning": {
      "default_duration": "2小时",
      "preferred_time": "上午",
      "default_priority": "medium"
    },
    "work": {
      "default_duration": "1小时",
      "preferred_time": "工作日",
      "default_priority": "high"
    }
  },
  "last_updated": "2024-01-20T15:30:00"
}
```

## 4. 存储设计（与现有记忆系统集成）

### 4.1 集成架构

日程排期功能**完全集成到现有的记忆系统**中，使用相同的存储机制和数据结构。

**核心原则**：
- ✅ 复用现有的 `JsonMemoryStorage` 存储系统
- ✅ 扩展 `memory.json` 数据结构，不创建新文件
- ✅ 通过 `MemorySystem` 类统一管理所有记忆数据
- ✅ 与现有的待办、日程、偏好系统无缝整合

### 4.2 文件结构

```
memories/
  {user_id}/
    memory.json         # 所有记忆数据（包含日程排期功能）
                        # - profile: 基本信息和偏好（扩展日程偏好）
                        # - todos: 待办事项（扩展时间预算字段）
                        # - schedule: 日程（扩展详细字段）
                        # - preferences: 新增日程偏好学习
                        # - reminders: 新增提醒任务
                        # - followups: 新增询问任务
                        # - ideas: 新增创意想法
    schedule.ics        # 导出的 iCal 文件（可选，按需生成）
```

**不再需要单独的 schedules/ 目录**，所有数据统一存储在 `memory.json` 中。

### 4.3 扩展的 memory.json 数据结构

#### 4.3.1 扩展 profile.preferences（添加日程偏好）

```json
{
  "profile": {
    "preferences": {
      "提醒方式": {
        "默认提醒方式": "推送通知",
        "重要事项提醒": "邮件 + 推送",
        "提醒提前时间": "15分钟"
      },
      "工作习惯": {
        "工作日": "周一至周五",
        "工作时间": "09:00 - 18:00",
        "午休时间": "12:00 - 13:00"
      },
      "日程偏好": {
        "工作时间": "09:00-18:00",
        "午休时间": "12:00-13:00",
        "偏好时间段": {
          "learning": "上午",
          "meeting": "10:00-11:00, 14:00-16:00",
          "exercise": "晚上",
          "focus_work": "上午"
        },
        "缓冲时间分钟数": 15,
        "默认提醒分钟数": 15,
        "重要事项提醒分钟数": 30,
        "免打扰时间": {
          "开始": "21:00",
          "结束": "08:00"
        }
      },
      "询问偏好": {
        "任务完成询问": "after_task_time",
        "进度检查频率": "weekly",
        "最小询问间隔小时数": 4
      }
    }
  }
}
```

#### 4.3.2 扩展 todos（添加时间预算）

```json
{
  "todos": {
    "in_progress": [
      {
        "content": "学习 Python 的异步编程",
        "priority": "medium",
        "due_date": "2024-01-25",
        "category": "学习",
        "estimated_duration": "2小时",
        "scheduled_time": {
          "start": "2024-01-20T14:00:00",
          "end": "2024-01-20T16:00:00",
          "duration": "2小时"
        },
        "reminder_minutes": 15,
        "created_at": "2024-01-20T10:00:00",
        "updated_at": "2024-01-20T10:00:00"
      }
    ],
    "pending": [],
    "completed": []
  }
}
```

#### 4.3.3 扩展 schedule（添加详细字段）

```json
{
  "schedule": {
    "regular": [
      {
        "id": "recurring_20240120_001",
        "title": "每周二开会",
        "time": "15:00",
        "duration": "1小时",
        "frequency": "weekly_TUE",
        "description": "团队周会",
        "end_date": null,
        "reminder_minutes": 15,
        "created_at": "2024-01-20T10:00:00"
      }
    ],
    "upcoming": [
      {
        "id": "event_20240120_001",
        "title": "项目评审会议",
        "start_time": "2024-01-25T10:00:00",
        "end_time": "2024-01-25T11:30:00",
        "description": "项目进度评审",
        "location": "会议室A",
        "reminder_minutes": 30,
        "created_at": "2024-01-20T10:00:00"
      }
    ]
  }
}
```

#### 4.3.4 新增 reminders（提醒任务）

```json
{
  "reminders": [
    {
      "id": "reminder_20240120_001",
      "type": "schedule",
      "target_id": "event_20240120_001",
      "remind_at": "2024-01-25T09:30:00",
      "reminded": false,
      "reminder_minutes": 30,
      "content": "提醒：您30分钟后有一个会议'项目评审'",
      "created_at": "2024-01-20T10:00:00"
    }
  ]
}
```

#### 4.3.5 新增 followups（询问任务）

```json
{
  "followups": [
    {
      "id": "followup_20240120_001",
      "type": "task_completion",
      "target_id": "todo_20240120_001",
      "ask_at": "2024-01-20T16:00:00",
      "asked": false,
      "frequency": "after_task_time",
      "content": "您今天下午2-3点安排了'学习 Python'，请问完成得怎么样了？",
      "created_at": "2024-01-20T14:00:00",
      "last_asked_at": null,
      "response_count": 0
    }
  ]
}
```

#### 4.3.6 新增 ideas（创意想法）

```json
{
  "ideas": [
    {
      "id": "idea_20240120_001",
      "content": "用户可以通过语音快速记录想法",
      "date": "2024-01-20",
      "time": "15:30",
      "tags": ["产品", "功能"],
      "category": "产品想法",
      "created_at": "2024-01-20T15:30:00"
    }
  ]
}
```

### 4.4 与现有记忆系统的集成方式

#### 4.4.1 扩展 JsonMemoryStorage 类

在 `examples/full_app/memory_system/json_storage.py` 中添加新方法：

```python
class JsonMemoryStorage:
    # ... 现有方法 ...
    
    # ========== 日程排期扩展方法 ==========
    
    def add_todo_with_schedule(self, content: str, priority: str = "medium", 
                              due_date: Optional[str] = None,
                              scheduled_time: Optional[Dict] = None,
                              category: Optional[str] = None,
                              estimated_duration: Optional[str] = None):
        """添加待办事项（扩展版本，支持时间预算）"""
        data = self._read_json()
        
        todo_item = {
            "content": content,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "estimated_duration": estimated_duration,
            "scheduled_time": scheduled_time,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        status = "scheduled" if scheduled_time else "pending"
        if status not in data["todos"]:
            data["todos"][status] = []
        data["todos"][status].append(todo_item)
        self._write_json(data)
    
    def schedule_todo(self, content: str, start_time: str, duration: str,
                     reminder_minutes: int = 15):
        """为待办事项安排时间预算"""
        # 查找待办并更新 scheduled_time
        # 创建提醒任务
        pass
    
    def add_one_time_event(self, title: str, start_time: str, 
                          end_time: Optional[str] = None,
                          duration: Optional[str] = None,
                          description: str = "",
                          location: Optional[str] = None,
                          reminder_minutes: int = 15):
        """添加一次性事件（扩展版本）"""
        data = self._read_json()
        
        event = {
            "id": f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "description": description,
            "location": location,
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data["schedule"]["upcoming"].append(event)
        
        # 自动创建提醒
        self._create_reminder("schedule", event["id"], start_time, reminder_minutes)
        
        self._write_json(data)
    
    def add_recurring_schedule_extended(self, title: str, start_time: str,
                                       duration: str, frequency: str,
                                       description: str = "",
                                       end_date: Optional[str] = None,
                                       reminder_minutes: int = 15):
        """添加周期性日程（扩展版本）"""
        data = self._read_json()
        
        event = {
            "id": f"recurring_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "time": start_time,
            "duration": duration,
            "frequency": frequency,
            "description": description,
            "end_date": end_date,
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data["schedule"]["regular"].append(event)
        self._write_json(data)
    
    def add_idea(self, content: str, date: Optional[str] = None,
                 time: Optional[str] = None, tags: Optional[List[str]] = None,
                 category: Optional[str] = None):
        """添加创意想法"""
        data = self._read_json()
        
        if "ideas" not in data:
            data["ideas"] = []
        
        idea = {
            "id": f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": content,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "time": time or datetime.now().strftime("%H:%M"),
            "tags": tags or [],
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data["ideas"].append(idea)
        self._write_json(data)
    
    def _create_reminder(self, reminder_type: str, target_id: str,
                        remind_at: str, reminder_minutes: int):
        """创建提醒任务（内部方法）"""
        data = self._read_json()
        
        if "reminders" not in data:
            data["reminders"] = []
        
        reminder = {
            "id": f"reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": reminder_type,
            "target_id": target_id,
            "remind_at": remind_at,
            "reminded": False,
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        data["reminders"].append(reminder)
        self._write_json(data)
    
    def _create_followup(self, followup_type: str, target_id: str,
                        ask_at: str, frequency: str = "after_task_time"):
        """创建询问任务（内部方法）"""
        data = self._read_json()
        
        if "followups" not in data:
            data["followups"] = []
        
        followup = {
            "id": f"followup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": followup_type,
            "target_id": target_id,
            "ask_at": ask_at,
            "asked": False,
            "frequency": frequency,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_asked_at": None,
            "response_count": 0
        }
        
        data["followups"].append(followup)
        self._write_json(data)
    
    def learn_schedule_preference(self, preference_type: str, value: str,
                                 confidence: float = 1.0, source: str = "explicit"):
        """学习日程偏好"""
        data = self._read_json()
        
        if "日程偏好" not in data["profile"]["preferences"]:
            data["profile"]["preferences"]["日程偏好"] = {}
        
        # 存储偏好及其元数据
        if preference_type not in data["profile"]["preferences"]["日程偏好"]:
            data["profile"]["preferences"]["日程偏好"][preference_type] = {
                "value": value,
                "confidence": confidence,
                "source": source,
                "learned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # 更新现有偏好（如果置信度更高）
            existing = data["profile"]["preferences"]["日程偏好"][preference_type]
            if confidence >= existing.get("confidence", 0):
                existing["value"] = value
                existing["confidence"] = confidence
                existing["source"] = source
                existing["learned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._write_json(data)
```

#### 4.4.2 扩展 MemorySystem 类

在 `examples/full_app/memory_system/core.py` 中添加便捷方法：

```python
class MemorySystem:
    # ... 现有方法 ...
    
    # 日程排期扩展方法
    def schedule_todo(self, content: str, start_time: str, duration: str,
                     reminder_minutes: int = 15):
        """为待办事项安排时间预算"""
        self.storage.schedule_todo(content, start_time, duration, reminder_minutes)
    
    def add_one_time_event(self, title: str, start_time: str, **kwargs):
        """添加一次性事件"""
        self.storage.add_one_time_event(title, start_time, **kwargs)
    
    def add_recurring_schedule_extended(self, title: str, start_time: str,
                                      duration: str, frequency: str, **kwargs):
        """添加周期性日程（扩展版本）"""
        self.storage.add_recurring_schedule_extended(
            title, start_time, duration, frequency, **kwargs
        )
    
    def add_idea(self, content: str, **kwargs):
        """添加创意想法"""
        self.storage.add_idea(content, **kwargs)
    
    def learn_schedule_preference(self, preference_type: str, value: str,
                                 confidence: float = 1.0):
        """学习日程偏好"""
        self.storage.learn_schedule_preference(
            preference_type, value, confidence
        )
```

### 4.5 数据迁移和兼容性

#### 4.5.1 向后兼容
- 现有的 `memory.json` 文件无需修改即可使用
- 新字段在首次使用时自动初始化
- 旧数据格式自动转换为新格式

#### 4.5.2 初始化新字段
在 `JsonMemoryStorage._initialize_json()` 中添加新字段的初始化：

```python
def _initialize_json(self):
    """初始化 JSON 文件（如果不存在）"""
    if not self.json_file.exists():
        # ... 现有初始化代码 ...
        
        # 添加新字段
        default_data["reminders"] = []
        default_data["followups"] = []
        default_data["ideas"] = []
        
        # 扩展 preferences
        if "日程偏好" not in default_data["profile"]["preferences"]:
            default_data["profile"]["preferences"]["日程偏好"] = {}
        if "询问偏好" not in default_data["profile"]["preferences"]:
            default_data["profile"]["preferences"]["询问偏好"] = {}
```

### 4.6 导出功能

iCal/ICS 导出功能可以：
- 读取 `memory.json` 中的 `schedule` 和 `todos` 数据
- 生成标准 iCal 文件
- 保存到 `memories/{user_id}/schedule.ics`（可选）

## 5. 技术实现要点（与现有系统集成）

### 5.1 集成原则
- **复用现有存储**：使用 `JsonMemoryStorage` 类，不创建新的存储系统
- **扩展数据结构**：在 `memory.json` 中添加新字段，保持向后兼容
- **统一API**：通过 `MemorySystem` 类提供统一的接口
- **无缝整合**：与现有的待办、日程、偏好系统无缝整合

### 5.2 实现步骤

#### Step 1: 扩展 JsonMemoryStorage
在 `examples/full_app/memory_system/json_storage.py` 中：
1. 添加新字段的初始化逻辑
2. 实现日程排期的扩展方法
3. 实现偏好学习方法
4. 实现提醒和询问的创建方法

#### Step 2: 扩展 MemorySystem
在 `examples/full_app/memory_system/core.py` 中：
1. 添加便捷方法委托给 storage
2. 保持 API 一致性

#### Step 3: 创建 ScheduleToolset
创建 `examples/full_app/memory_system/schedule_toolset.py`：
1. 基于 `FunctionToolset` 创建工具集
2. 提供日程排期的所有工具函数
3. 集成到现有的 `create_memory_toolset` 或创建独立的 toolset

#### Step 4: 实现定时任务
在 `examples/full_app/app.py` 中：
1. 添加后台定时任务检查提醒和询问
2. 实现消息推送机制

### 5.3 频率模式解析
- 支持标准 RRULE 格式（RFC 5545）
- 提供友好的中文频率描述（如 "每周二"、"每周末"）
- 自动转换为 RRULE 格式用于导出
- **复用现有**：`add_regular_schedule` 已支持频率，只需扩展字段

### 5.4 时间处理
- 使用 Python `datetime` 和 `dateutil` 库处理时间
- 支持时区（从 `profile.basic_info.时区` 读取）
- 自动计算周期性日程的具体日期实例
- **复用现有**：使用记忆系统中已有的时间处理逻辑

### 5.5 iCal/ICS 导出
- 使用 `icalendar` 库生成标准 iCal 文件
- 支持 VEVENT（事件）和 VTODO（待办）组件
- 周期性日程使用 RRULE 规则
- 包含提醒（VALARM）信息
- **数据来源**：从 `memory.json` 的 `schedule` 和 `todos` 读取

### 5.6 偏好学习机制
- **自然语言理解**：使用 LLM 从用户对话中提取偏好信息
- **模式识别**：分析历史行为数据，识别重复模式
- **置信度评估**：根据学习来源（显式/隐式）设置置信度
- **偏好应用**：在排期、建议等场景中自动应用已学习偏好
- **存储位置**：偏好存储在 `profile.preferences.日程偏好` 中
- **与现有整合**：使用 `update_preference` 方法，扩展 `preferences` 结构

### 5.7 提醒和询问机制
- **定时任务**：使用 `asyncio` 或 `APScheduler` 实现后台定时任务
- **数据存储**：提醒和询问存储在 `memory.json` 的 `reminders` 和 `followups` 字段
- **消息推送**：通过 WebSocket 或消息队列推送提醒和询问
- **状态管理**：跟踪提醒和询问的状态（pending, triggered, responded）

## 6. 用户体验设计

### 6.1 交互流程（与记忆系统集成）

1. **创建待办**：
   - 用户描述任务 → 助理调用 `add_todo()` → 记录到 `memory.json` → 询问是否需要安排时间
   - **自动学习**：从对话中提取偏好信息 → 调用 `learn_schedule_preference()`

2. **安排时间**：
   - 用户提供时间信息 → 助理调用 `schedule_todo()` → 更新 `todos` 中的 `scheduled_time` → 确认
   - **自动创建提醒**：调用 `_create_reminder()` → 添加到 `reminders` 列表
   - **自动创建询问**：调用 `_create_followup()` → 添加到 `followups` 列表

3. **周期性任务**：
   - 用户描述任务和频率 → 助理调用 `add_recurring_schedule_extended()` → 添加到 `schedule.regular` → **自动创建周期性提醒**

4. **记录想法**：
   - 用户描述想法 → 助理调用 `add_idea()` → 添加到 `ideas` 列表 → 添加标签（可选）

5. **主动提醒**：
   - 系统定时任务检查 `reminders` → 到期提醒 → 通过 WebSocket 推送 → 用户响应 → 更新状态

6. **主动询问**：
   - 系统定时任务检查 `followups` → 到期询问 → 通过 WebSocket 推送 → 用户反馈 → 更新任务状态

7. **偏好学习**：
   - 对话中检测到偏好表达 → 调用 `learn_schedule_preference()` → 更新 `profile.preferences.日程偏好` → 后续自动应用

### 6.2 智能建议
- 根据待办事项的截止日期和优先级，建议安排时间
- 检测时间冲突并提醒用户
- **根据用户的工作时间偏好，推荐合适的时间段**（自动应用已学习偏好）
- **根据任务类型，自动匹配用户偏好的时间段**（如学习→上午，运动→晚上）
- **检测与用户习惯的冲突**（如午休时间、不活跃时间）

### 6.3 错误处理
- 时间格式错误：提示正确格式
- 时间冲突：列出冲突的日程，询问是否调整
- 频率格式错误：提供示例和说明

## 7. 后续扩展功能（可选）

### 7.1 时间冲突检测
自动检测新安排的日程是否与已有日程冲突。

### 7.2 智能排期建议
根据用户的工作习惯和已有日程，智能推荐合适的时间段。
**已实现**：通过自动学习用户偏好，在排期时自动应用偏好。

### 7.3 日程同步
支持与第三方日历服务（Google Calendar、Outlook）双向同步。

### 7.4 统计分析
- 时间使用统计
- 任务完成率
- 周期性任务执行情况

### 7.5 主动提醒和询问（已实现）
- ✅ 主动提醒即将到来的日程和待办
- ✅ 主动询问任务完成情况
- ✅ 智能时机选择（基于用户偏好）
- ✅ 个性化提醒频率和方式

## 8. 验收标准

### 8.1 功能完整性
- ✅ 能够创建、查询、更新、删除待办事项（**集成到现有记忆系统**）
- ✅ 能够为待办事项安排时间预算（**扩展 todos 数据结构**）
- ✅ 能够创建周期性日程（支持多种频率模式）（**扩展 schedule.regular**）
- ✅ 能够创建一次性事件（**扩展 schedule.upcoming**）
- ✅ 能够记录和查询创意想法（**新增 ideas 字段**）
- ✅ 能够导出为标准 iCal/ICS 格式（**从 memory.json 读取数据**）
- ✅ **能够自动学习用户偏好和习惯**（**存储到 profile.preferences.日程偏好**）
- ✅ **能够在排期时自动应用已学习偏好**（**从 preferences 读取并应用**）
- ✅ **能够查询和管理已学习的偏好**（**通过 read_memory(section="preferences")**）
- ✅ **能够主动提醒用户即将到来的日程和待办**（**使用 reminders 字段**）
- ✅ **能够主动询问任务完成情况和进度**（**使用 followups 字段**）
- ✅ **能够根据用户偏好智能选择提醒和询问时机**（**从 preferences 读取配置**）

### 8.4 系统集成完整性
- ✅ **与现有记忆系统无缝集成**：所有数据存储在 `memory.json` 中
- ✅ **复用现有存储机制**：使用 `JsonMemoryStorage` 类
- ✅ **统一API接口**：通过 `MemorySystem` 类访问
- ✅ **向后兼容**：现有数据无需迁移即可使用
- ✅ **数据一致性**：与待办、日程、偏好系统共享同一数据源

### 8.2 数据格式标准性
- ✅ 导出的 iCal 文件能够被 Google Calendar、Apple Calendar、Outlook 正确导入
- ✅ 周期性日程使用标准 RRULE 格式
- ✅ 时间格式符合 ISO 8601 标准

### 8.3 用户体验
- ✅ 交互自然流畅，助理能够理解用户的自然语言描述
- ✅ 错误提示清晰，能够指导用户正确使用
- ✅ 查询结果格式清晰易读

## 9. 开发优先级

### Phase 1（核心功能 - 集成到记忆系统）
1. **扩展 JsonMemoryStorage**：
   - 扩展 `memory.json` 数据结构（添加 reminders, followups, ideas）
   - 扩展 `todos` 支持时间预算字段
   - 扩展 `schedule` 支持详细字段
   - 扩展 `preferences` 添加日程偏好

2. **扩展 MemorySystem**：
   - 添加日程排期的便捷方法
   - 添加偏好学习方法
   - 添加提醒和询问创建方法

3. **创建 ScheduleToolset**：
   - 基于 `FunctionToolset` 创建工具集
   - 实现所有日程排期工具函数
   - 集成到 agent 系统

4. **基础功能实现**：
   - 待办事项管理（扩展现有功能）
   - 周期性日程创建（扩展现有功能）
   - 一次性事件创建（扩展现有功能）
   - 创意想法记录（新增）
   - 自动学习用户偏好（基础版本）
   - 主动提醒功能（基础版本）
   - 主动询问功能（基础版本）

### Phase 2（完善功能）
1. **数据导出（iCal/ICS）**：
   - 从 `memory.json` 读取数据
   - 生成标准 iCal 文件

2. **时间冲突检测**：
   - 基于 `schedule` 和 `todos` 数据检测冲突

3. **更多频率模式支持**：
   - 扩展 `add_regular_schedule` 的频率解析

4. **偏好应用机制**：
   - 在排期时从 `preferences.日程偏好` 读取并应用

5. **偏好查询和管理功能**：
   - 通过 `read_memory(section="preferences")` 查询
   - 通过 `update_preference` 管理

6. **智能提醒时机选择**：
   - 从 `preferences.日程偏好` 读取配置
   - 基于用户偏好选择时机

7. **提醒和询问的个性化配置**：
   - 从 `preferences.询问偏好` 读取配置

### Phase 3（增强功能）
1. **智能排期建议（基于偏好）**：
   - 从 `preferences.日程偏好` 读取偏好
   - 智能推荐时间段

2. **行为模式识别（高级学习）**：
   - 分析 `todos` 和 `schedule` 历史数据
   - 识别行为模式并学习

3. **高级提醒策略**：
   - 多级提醒、智能重试
   - 基于 `reminders` 数据管理

4. **任务进度跟踪和可视化**：
   - 基于 `todos` 和 `followups` 数据

5. **统计分析**：
   - 基于 `memory.json` 所有数据

6. **第三方日历同步**：
   - 导出 iCal 文件供同步

7. **偏好置信度管理和衰减机制**：
   - 管理 `preferences.日程偏好` 中的置信度字段

## 10. 与现有记忆系统整合总结

### 10.1 整合架构

日程排期功能**完全集成到现有的记忆系统**中，采用以下架构：

```
MemorySystem (统一入口)
    ↓
JsonMemoryStorage (存储层)
    ↓
memory.json (单一数据源)
    ├── profile (扩展：添加日程偏好)
    ├── todos (扩展：添加时间预算字段)
    ├── schedule (扩展：添加详细字段)
    ├── reminders (新增：提醒任务)
    ├── followups (新增：询问任务)
    ├── ideas (新增：创意想法)
    └── ... (其他现有字段)
```

### 10.2 关键整合点

#### 10.2.1 数据存储
- ✅ **单一数据源**：所有数据存储在 `memory.json` 中
- ✅ **向后兼容**：现有数据无需迁移
- ✅ **统一格式**：使用 JSON 格式，与现有系统一致

#### 10.2.2 API 设计
- ✅ **复用现有类**：扩展 `JsonMemoryStorage` 和 `MemorySystem`
- ✅ **统一接口**：通过 `MemorySystem` 提供统一访问接口
- ✅ **工具集集成**：创建 `ScheduleToolset` 集成到 agent

#### 10.2.3 功能整合
- ✅ **待办事项**：扩展现有的 `todos` 功能，添加时间预算
- ✅ **日程管理**：扩展现有的 `schedule` 功能，添加详细字段
- ✅ **偏好学习**：扩展现有的 `preferences` 功能，添加日程偏好
- ✅ **提醒询问**：新增功能，但使用相同的存储机制

### 10.3 实现优势

#### 10.3.1 开发效率
- **复用代码**：无需重新实现存储层
- **统一维护**：所有记忆数据统一管理
- **快速集成**：基于现有系统快速扩展

#### 10.3.2 用户体验
- **数据一致性**：所有数据在同一系统中
- **无缝切换**：待办、日程、偏好无缝切换
- **统一查询**：通过 `read_memory` 统一查询所有数据

#### 10.3.3 系统稳定性
- **经过验证**：复用经过验证的存储系统
- **向后兼容**：不影响现有功能
- **易于维护**：统一的代码结构

### 10.4 实施建议

#### 10.4.1 开发顺序
1. **第一步**：扩展 `JsonMemoryStorage` 的数据结构和方法
2. **第二步**：扩展 `MemorySystem` 的便捷方法
3. **第三步**：创建 `ScheduleToolset` 工具集
4. **第四步**：实现定时任务和消息推送
5. **第五步**：测试和优化

#### 10.4.2 测试策略
- **单元测试**：测试 `JsonMemoryStorage` 的新方法
- **集成测试**：测试与现有系统的集成
- **兼容性测试**：确保现有数据不受影响
- **功能测试**：测试所有新功能

#### 10.4.3 迁移方案
- **无需迁移**：现有 `memory.json` 文件可直接使用
- **自动初始化**：新字段在首次使用时自动初始化
- **渐进式部署**：可以逐步启用新功能

### 10.5 代码示例

#### 10.5.1 使用示例

```python
from examples.full_app.memory_system import MemorySystem

# 初始化记忆系统（复用现有）
memory = MemorySystem(user_id="owner", memory_dir="./memories")

# 创建待办事项（扩展现有功能）
memory.add_todo("学习 Python", priority="medium", due_date="2024-01-25")

# 安排时间预算（新功能）
memory.schedule_todo("学习 Python", "2024-01-20T14:00:00", "2小时")

# 创建周期性日程（扩展现有功能）
memory.add_recurring_schedule_extended(
    "每周二开会",
    "15:00",
    "1小时",
    "weekly_TUE"
)

# 学习偏好（新功能）
memory.learn_schedule_preference("学习任务偏好时间段", "上午", confidence=1.0)

# 记录创意想法（新功能）
memory.add_idea("用户可以通过语音快速记录想法", tags=["产品", "功能"])

# 查询所有数据（统一查询）
context = memory.get_context()  # 包含所有数据
```

#### 10.5.2 Toolset 集成示例

```python
from examples.full_app.memory_system.toolset import create_memory_toolset
from examples.full_app.memory_system.schedule_toolset import create_schedule_toolset

# 创建记忆工具集（现有）
memory_toolset = create_memory_toolset(memory_dir="./memories")

# 创建日程工具集（新增，但集成到记忆系统）
schedule_toolset = create_schedule_toolset(memory_dir="./memories")

# 在 agent 中使用
agent = Agent(
    model=model,
    toolsets=[memory_toolset, schedule_toolset],
    system_prompt=system_prompt
)
```

### 10.6 总结

通过将日程排期功能整合到现有记忆系统：

✅ **统一数据管理**：所有数据存储在 `memory.json` 中  
✅ **复用现有代码**：扩展而非重写  
✅ **无缝用户体验**：待办、日程、偏好无缝整合  
✅ **易于维护**：统一的代码结构和数据格式  
✅ **向后兼容**：现有功能不受影响  

这种整合方式确保了系统的**一致性**、**可维护性**和**可扩展性**。
