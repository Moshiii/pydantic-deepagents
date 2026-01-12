# AI 用户可塑性（个性化学习）系统设计

## 核心目标

让 AI 在对话中自动学习用户的：
1. **使用习惯** - 如何使用工具、偏好哪些功能
2. **聊天习惯** - 沟通风格、回复长度、语气
3. **办事习惯** - 工作方式、决策风格、优先级
4. **语言偏好** - 语言风格、专业术语、表达方式

**所有数据持久化在同一个文件**：`memories/{user_id}/memory.json`

---

## 架构设计

### 数据模型（统一存储在 memory.json）

```json
{
  "profile": {
    "basic_info": {
      "姓名": "张三",
      "昵称": "小张",
      "时区": "Asia/Shanghai (UTC+8)",
      "语言": "zh-CN"
    },
    "preferences": {
      "使用习惯": {
        "偏好功能": ["数据分析", "日程管理"],
        "常用工具": ["read_file", "write_file"],
        "工作流程": "先分析后决策",
        "信息展示偏好": "表格格式",
        "文件组织方式": "按日期分类"
      },
      "聊天习惯": {
        "回复长度": "中等（3-5句话）",
        "语气风格": "专业但友好",
        "使用表情": false,
        "称呼方式": "直接称呼名字",
        "确认频率": "低（直接执行）",
        "解释详细程度": "适中"
      },
      "办事习惯": {
        "决策风格": "快速决策，少确认",
        "优先级偏好": "重要性 > 紧急性",
        "工作节奏": "高效，不喜欢拖延",
        "任务分解": "喜欢详细步骤",
        "反馈方式": "实时反馈，不要等完成"
      },
      "语言偏好": {
        "语言风格": "简洁专业",
        "专业术语": "使用技术术语",
        "表达方式": "直接，少客套",
        "数字格式": "中文数字（一、二、三）",
        "时间格式": "24小时制"
      },
      "工作习惯": {
        "工作日": "周一至周五",
        "工作时间": "09:00 - 18:00",
        "午休时间": "12:00 - 13:00"
      },
      "日程偏好": {},
      "询问偏好": {}
    }
  },
  "habits": {
    "工作习惯": [
      {
        "habit": "喜欢早上处理重要任务",
        "learned_at": "2024-01-15 10:30:00",
        "confidence": 0.9,
        "source": "behavior_pattern",
        "evidence_count": 5
      }
    ],
    "沟通习惯": [
      {
        "habit": "不喜欢频繁确认，直接执行",
        "learned_at": "2024-01-10 14:20:00",
        "confidence": 0.95,
        "source": "explicit",
        "evidence_count": 3
      }
    ],
    "生活习惯": []
  },
  "conversations": [
    {
      "topic": "数据分析任务",
      "summary": [
        "用户偏好使用表格格式展示结果",
        "用户希望立即看到结果，不需要等待",
        "用户喜欢详细的步骤说明"
      ],
      "timestamp": "2024-01-15 10:30:00"
    }
  ]
}
```

---

## 实现方案

### 方案 1: 被动学习（推荐）

**原理**: Agent 在对话中识别用户特征，主动调用学习工具

**优点**:
- ✅ 不需要修改核心架构
- ✅ 灵活，可以根据上下文学习
- ✅ 可以设置置信度

**实现**:

#### 1.1 扩展 Memory Toolset

添加新的学习工具：

```python
@toolset.tool
async def learn_user_pattern(
    ctx: RunContext[DeepAgentDeps],
    pattern_type: str,  # "使用习惯", "聊天习惯", "办事习惯", "语言偏好"
    pattern_description: str,
    confidence: float = 0.8,
    source: str = "conversation",
    evidence: str | None = None
) -> str:
    """学习用户的模式/习惯
    
    Args:
        pattern_type: 模式类型
        pattern_description: 模式描述
        confidence: 置信度 (0-1)
        source: 来源 ("explicit", "behavior_pattern", "inference")
        evidence: 证据（可选）
    """
    memory_sys = get_memory_system(ctx)
    
    if pattern_type == "使用习惯":
        # 保存到 preferences["使用习惯"]
        memory_sys.update_preference("使用习惯", pattern_description, evidence or "")
    elif pattern_type == "聊天习惯":
        memory_sys.update_preference("聊天习惯", pattern_description, evidence or "")
    elif pattern_type == "办事习惯":
        memory_sys.update_preference("办事习惯", pattern_description, evidence or "")
    elif pattern_type == "语言偏好":
        memory_sys.update_preference("语言偏好", pattern_description, evidence or "")
    else:
        # 作为习惯保存
        category_map = {
            "使用习惯": "工作习惯",
            "聊天习惯": "沟通习惯",
            "办事习惯": "工作习惯",
            "语言偏好": "沟通习惯"
        }
        category = category_map.get(pattern_type, "工作习惯")
        memory_sys.learn_habit(pattern_description, category)
    
    return f"已学习用户模式：{pattern_type} - {pattern_description}（置信度：{confidence}）"
```

#### 1.2 在系统提示中指导 Agent

```python
MAIN_INSTRUCTIONS = """
## 用户个性化学习

**CRITICAL**: 在对话中主动学习用户的习惯和偏好，让 AI 越来越懂用户。

### 学习时机

当用户表现出以下行为时，主动学习：

1. **使用习惯**:
   - 用户说"我喜欢用表格展示" → 学习：偏好表格格式
   - 用户说"先分析再决定" → 学习：工作流程偏好
   - 用户频繁使用某个功能 → 学习：常用工具偏好

2. **聊天习惯**:
   - 用户说"直接做，不用问我" → 学习：不喜欢频繁确认
   - 用户回复简短 → 学习：偏好简洁回复
   - 用户使用专业术语 → 学习：语言风格偏好

3. **办事习惯**:
   - 用户说"越快越好" → 学习：决策风格（快速决策）
   - 用户说"按重要性排序" → 学习：优先级偏好
   - 用户要求详细步骤 → 学习：任务分解偏好

4. **语言偏好**:
   - 用户使用特定表达方式 → 学习：语言风格
   - 用户偏好某种格式 → 学习：格式偏好

### 学习方法

使用 `learn_user_pattern()` 工具：

```python
# 显式表达（高置信度）
learn_user_pattern(
    pattern_type="聊天习惯",
    pattern_description="不喜欢频繁确认",
    confidence=0.95,
    source="explicit",
    evidence="用户明确说'直接做，不用问我'"
)

# 行为模式（中等置信度）
learn_user_pattern(
    pattern_type="使用习惯",
    pattern_description="偏好表格格式展示",
    confidence=0.8,
    source="behavior_pattern",
    evidence="用户3次要求使用表格格式"
)

# 推断（低置信度）
learn_user_pattern(
    pattern_type="语言偏好",
    pattern_description="偏好简洁专业",
    confidence=0.7,
    source="inference",
    evidence="用户回复简短，使用专业术语"
)
```

### 应用学习到的模式

在后续对话中，根据学习到的模式调整行为：

- 如果用户偏好表格格式 → 使用表格展示结果
- 如果用户不喜欢确认 → 直接执行，少问问题
- 如果用户偏好简洁 → 回复简短，重点突出
- 如果用户偏好详细 → 提供详细步骤和说明
"""
```

#### 1.3 动态注入用户模式到系统提示

```python
@agent.instructions
def inject_user_patterns(ctx: Any) -> str:
    """注入学习到的用户模式到系统提示"""
    try:
        memory_sys = MemorySystem(
            user_id=PERSONAL_USER_ID,
            memory_dir=str(MEMORY_DIR),
        )
        
        data = memory_sys.storage.get_all_data()
        preferences = data.get("profile", {}).get("preferences", {})
        habits = data.get("habits", {})
        
        parts = []
        
        # 使用习惯
        usage_habits = preferences.get("使用习惯", {})
        if usage_habits:
            parts.append("## 📊 用户使用习惯")
            for key, value in usage_habits.items():
                parts.append(f"- **{key}**: {value}")
            parts.append("")
        
        # 聊天习惯
        chat_habits = preferences.get("聊天习惯", {})
        if chat_habits:
            parts.append("## 💬 用户聊天习惯")
            parts.append("**重要**: 根据这些习惯调整你的回复风格")
            for key, value in chat_habits.items():
                parts.append(f"- **{key}**: {value}")
            parts.append("")
        
        # 办事习惯
        work_habits = preferences.get("办事习惯", {})
        if work_habits:
            parts.append("## ⚙️ 用户办事习惯")
            parts.append("**重要**: 根据这些习惯调整你的工作方式")
            for key, value in work_habits.items():
                parts.append(f"- **{key}**: {value}")
            parts.append("")
        
        # 语言偏好
        language_prefs = preferences.get("语言偏好", {})
        if language_prefs:
            parts.append("## 🗣️ 用户语言偏好")
            parts.append("**重要**: 根据这些偏好调整你的表达方式")
            for key, value in language_prefs.items():
                parts.append(f"- **{key}**: {value}")
            parts.append("")
        
        # 学习到的习惯
        learned_habits = []
        for category, habit_list in habits.items():
            for habit in habit_list:
                learned_habits.append(f"- **{habit['habit']}** ({category})")
        
        if learned_habits:
            parts.append("## 📝 学习到的用户习惯")
            parts.extend(learned_habits)
            parts.append("")
        
        return "\n".join(parts)
    except Exception as e:
        logger.warning(f"Failed to inject user patterns: {e}")
        return ""
```

---

### 方案 2: 主动学习（高级）

**原理**: 在对话处理流程中自动提取用户特征

**实现**: 添加对话分析处理器

```python
async def analyze_conversation_for_patterns(
    user_message: str,
    agent_response: str,
    memory_sys: MemorySystem
):
    """分析对话，提取用户模式"""
    
    # 分析回复长度偏好
    if len(user_message) < 20:
        # 用户回复简短，可能偏好简洁
        memory_sys.update_preference(
            "聊天习惯", 
            "回复长度", 
            "简短",
            confidence=0.7
        )
    
    # 分析确认频率
    if "直接" in user_message or "不用问我" in user_message:
        memory_sys.update_preference(
            "聊天习惯",
            "确认频率",
            "低（直接执行）",
            confidence=0.9,
            source="explicit"
        )
    
    # 分析格式偏好
    if "表格" in user_message or "表格格式" in user_message:
        memory_sys.update_preference(
            "使用习惯",
            "信息展示偏好",
            "表格格式",
            confidence=0.85,
            source="explicit"
        )
```

---

## 具体实现步骤

### 步骤 1: 扩展 JSON 存储结构

在 `json_storage.py` 中添加新的偏好类别：

```python
def _initialize_json(self):
    default_data = {
        "profile": {
            "preferences": {
                # ... 现有偏好 ...
                "使用习惯": {},
                "聊天习惯": {},
                "办事习惯": {},
                "语言偏好": {}
            }
        }
    }
```

### 步骤 2: 添加学习工具

在 `toolset.py` 中添加：

```python
@toolset.tool
async def learn_user_pattern(...):
    """学习用户模式"""
    ...
```

### 步骤 3: 更新系统提示

在 `app.py` 中：
1. 添加学习指导到 `MAIN_INSTRUCTIONS`
2. 添加动态注入函数 `inject_user_patterns()`

### 步骤 4: 创建学习 Skill（可选）

创建一个专门的 skill 来指导 Agent 如何学习：

```markdown
---
name: user-learning
description: Learn user patterns and preferences from conversations
---

# User Learning Skill

## When to Learn

Learn user patterns when:
- User explicitly expresses preference
- User shows consistent behavior (3+ times)
- User corrects your behavior

## Learning Categories

1. **使用习惯**: How user uses tools and features
2. **聊天习惯**: Communication style preferences
3. **办事习惯**: Work style and decision-making
4. **语言偏好**: Language and expression preferences

## Examples

### Learning Usage Habits

User: "我喜欢用表格展示数据"
→ learn_user_pattern(
    pattern_type="使用习惯",
    pattern_description="偏好表格格式展示",
    confidence=0.95,
    source="explicit"
)
```

---

## 使用示例

### 示例 1: 学习使用习惯

```
用户: "帮我分析数据，用表格展示结果"

Agent 执行:
1. 分析数据
2. 使用表格格式展示
3. 学习用户偏好:
   learn_user_pattern(
       pattern_type="使用习惯",
       pattern_description="偏好表格格式展示数据",
       confidence=0.9,
       source="explicit"
   )

后续对话:
用户: "分析这个文件"
Agent: [自动使用表格格式展示，因为知道用户偏好]
```

### 示例 2: 学习聊天习惯

```
用户: "直接帮我做，不用问我"

Agent 执行:
1. 直接执行任务
2. 学习用户偏好:
   learn_user_pattern(
       pattern_type="聊天习惯",
       pattern_description="不喜欢频繁确认，直接执行",
       confidence=0.95,
       source="explicit"
   )

后续对话:
Agent: [自动执行，少问问题，因为知道用户偏好]
```

### 示例 3: 学习办事习惯

```
用户: "越快越好，不用太详细"

Agent 执行:
1. 快速完成任务
2. 简洁回复
3. 学习用户偏好:
   learn_user_pattern(
       pattern_type="办事习惯",
       pattern_description="快速决策，偏好简洁",
       confidence=0.9,
       source="explicit"
   )
```

---

## 数据持久化

### 统一存储位置

**所有数据存储在**: `memories/{user_id}/memory.json`

**数据结构**:
```json
{
  "profile": {
    "preferences": {
      "使用习惯": {
        "偏好功能": "...",
        "常用工具": "...",
        "信息展示偏好": "..."
      },
      "聊天习惯": {
        "回复长度": "...",
        "语气风格": "...",
        "确认频率": "..."
      },
      "办事习惯": {
        "决策风格": "...",
        "优先级偏好": "...",
        "工作节奏": "..."
      },
      "语言偏好": {
        "语言风格": "...",
        "专业术语": "...",
        "表达方式": "..."
      }
    }
  },
  "habits": {
    "工作习惯": [...],
    "沟通习惯": [...],
    "生活习惯": [...]
  }
}
```

### 更新机制

- **实时更新**: 每次学习立即写入 JSON
- **缓存机制**: 60秒缓存，减少文件读写
- **原子操作**: 使用文件锁确保数据一致性

---

## 最佳实践

### ✅ DO（推荐）

1. **显式学习优先**
   ```python
   # 用户明确表达 → 高置信度
   learn_user_pattern(..., confidence=0.95, source="explicit")
   ```

2. **行为模式学习**
   ```python
   # 用户多次表现 → 中等置信度
   learn_user_pattern(..., confidence=0.8, source="behavior_pattern")
   ```

3. **渐进式学习**
   ```python
   # 多次观察后提高置信度
   if evidence_count >= 3:
       confidence = min(0.95, confidence + 0.1)
   ```

4. **应用学习结果**
   ```python
   # 在后续对话中应用学习到的模式
   if user_prefers_table_format:
       display_as_table()
   ```

### ❌ DON'T（避免）

1. **不要过度学习**
   ```python
   # ❌ WRONG - 一次行为就学习
   if user_says_once("表格"):
       learn_pattern(confidence=0.95)
   
   # ✅ RIGHT - 多次确认后学习
   if user_says_multiple_times("表格", count>=3):
       learn_pattern(confidence=0.8)
   ```

2. **不要忽略用户纠正**
   ```python
   # ✅ RIGHT - 用户纠正时更新
   if user_corrects_behavior:
       update_pattern(new_value, confidence=0.95)
   ```

3. **不要学习临时偏好**
   ```python
   # ❌ WRONG - 临时需求
   if user_says("这次用图表"):
       # 这是临时需求，不要学习
   
   # ✅ RIGHT - 持续偏好
   if user_says_multiple_times("我喜欢图表"):
       learn_pattern(...)
   ```

---

## 总结

### 核心设计

1. ✅ **统一存储**: 所有数据在 `memory.json`
2. ✅ **分类学习**: 4个类别（使用、聊天、办事、语言）
3. ✅ **置信度机制**: 显式 > 行为模式 > 推断
4. ✅ **动态应用**: 在系统提示中注入，影响 Agent 行为
5. ✅ **实时更新**: 学习后立即持久化

### 实现路径

1. **扩展存储结构** - 添加新的偏好类别
2. **添加学习工具** - `learn_user_pattern()`
3. **更新系统提示** - 指导 Agent 学习
4. **动态注入** - 将学习结果注入系统提示
5. **创建学习 Skill** - 提供详细的学习指南（可选）

### 效果

- ✅ AI 越来越懂用户
- ✅ 回复风格自动调整
- ✅ 工作方式自动适配
- ✅ 语言风格自动匹配
- ✅ 所有数据统一管理
