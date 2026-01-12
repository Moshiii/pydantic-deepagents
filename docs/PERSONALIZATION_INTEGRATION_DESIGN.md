# 个性化学习模块集成方案分析

## 问题

个性化学习模块应该如何与现有的 Agent 机制结合？
- 作为 **Skill**？
- 作为 **Toolset**？
- 作为 **提示词内置**？

## 三种方案对比

### 方案 1: 作为 Skill ❌ 不推荐（单独使用）

**实现方式**:
```markdown
---
name: user-learning
description: Learn user patterns and preferences
---

# User Learning Skill

## When to Learn
- User expresses preference → learn_user_pattern(...)
- User shows behavior pattern → learn_user_pattern(...)
```

**优点**:
- ✅ 可以按需加载
- ✅ 提供详细的学习指南
- ✅ 模块化，易于管理

**缺点**:
- ❌ **学习应该是持续性的，不应该按需加载**
- ❌ Skill 是指南，不提供工具
- ❌ 需要 Agent 主动加载，可能错过学习时机
- ❌ 不符合 Skill 的设计理念（Skill 是任务导向的）

**结论**: ❌ **不适合作为主要实现方式**

---

### 方案 2: 作为 Toolset ✅ 推荐（核心实现）

**实现方式**:
```python
# 在 memory_system/toolset.py 中添加
@toolset.tool
async def learn_user_pattern(
    ctx: RunContext[DeepAgentDeps],
    pattern_type: str,
    pattern_description: str,
    confidence: float = 0.8,
    source: str = "conversation"
) -> str:
    """学习用户的模式/习惯"""
    memory_sys = get_memory_system(ctx)
    memory_sys.update_preference(pattern_type, pattern_description, value)
    return f"已学习用户模式：{pattern_type} - {pattern_description}"
```

**优点**:
- ✅ **提供实际的学习工具**（这是必须的）
- ✅ 工具始终可用，不需要加载
- ✅ 符合 Toolset 的设计理念（提供工具）
- ✅ 与现有 Memory Toolset 完美集成
- ✅ 可以立即持久化到 memory.json

**缺点**:
- ⚠️ 需要配合系统提示指导 Agent 何时使用
- ⚠️ 需要动态注入学习结果

**结论**: ✅ **必须实现（核心）**

---

### 方案 3: 作为提示词内置 ✅ 推荐（指导学习）

**实现方式**:
```python
MAIN_INSTRUCTIONS = """
## 用户个性化学习

**CRITICAL**: 在对话中主动学习用户的习惯和偏好。

### 学习时机
当用户表现出以下行为时，主动学习：
- 用户说"我喜欢用表格展示" → learn_user_pattern("使用习惯", "偏好表格格式", 0.95)
- 用户说"直接做，不用问我" → learn_user_pattern("聊天习惯", "不喜欢频繁确认", 0.95)
...
"""
```

**优点**:
- ✅ **指导 Agent 何时学习**（这是必须的）
- ✅ 始终生效，不需要加载
- ✅ 可以明确说明学习规则和时机
- ✅ 与 Agent 的核心行为绑定

**缺点**:
- ⚠️ 提示词会变长
- ⚠️ 需要配合工具使用

**结论**: ✅ **必须实现（指导）**

---

### 方案 4: 动态注入学习结果 ✅ 推荐（应用学习）

**实现方式**:
```python
@agent.instructions
def inject_user_patterns(ctx: Any) -> str:
    """将学习到的用户模式注入系统提示"""
    memory_sys = MemorySystem(user_id=PERSONAL_USER_ID, ...)
    data = memory_sys.storage.get_all_data()
    preferences = data.get("profile", {}).get("preferences", {})
    
    parts = []
    if preferences.get("使用习惯"):
        parts.append("## 📊 用户使用习惯")
        for key, value in preferences["使用习惯"].items():
            parts.append(f"- **{key}**: {value}")
    
    return "\n".join(parts)
```

**优点**:
- ✅ **让学习结果生效**（这是必须的）
- ✅ 动态更新，实时反映学习结果
- ✅ 影响 Agent 的行为
- ✅ 符合现有的动态注入机制

**缺点**:
- ⚠️ 需要读取 memory.json（有性能开销，但可接受）

**结论**: ✅ **必须实现（应用）**

---

## 🎯 最佳实践：组合方案

### 推荐架构：三层设计

```
┌─────────────────────────────────────────┐
│  1. Toolset (工具层)                    │
│     - learn_user_pattern()              │
│     - 提供学习工具                      │
│     ✅ 必须实现                          │
└─────────────────────────────────────────┘
              ↑ 被调用
              │
┌─────────────────────────────────────────┐
│  2. 系统提示 (指导层)                    │
│     - MAIN_INSTRUCTIONS                 │
│     - 指导何时学习                      │
│     ✅ 必须实现                          │
└─────────────────────────────────────────┘
              ↑ 指导
              │
┌─────────────────────────────────────────┐
│  3. 动态注入 (应用层)                    │
│     - inject_user_patterns()            │
│     - 将学习结果注入系统提示             │
│     ✅ 必须实现                          │
└─────────────────────────────────────────┘
              ↑ 可选
              │
┌─────────────────────────────────────────┐
│  4. Skill (指南层) - 可选               │
│     - user-learning skill               │
│     - 提供详细的学习指南                 │
│     ⚠️ 可选实现                          │
└─────────────────────────────────────────┘
```

---

## 具体实现方案

### 实现 1: Toolset（核心工具）

**位置**: `examples/full_app/memory_system/toolset.py`

```python
@toolset.tool
async def learn_user_pattern(
    ctx: RunContext[DepsType],
    pattern_type: str,  # "使用习惯", "聊天习惯", "办事习惯", "语言偏好"
    pattern_description: str,
    confidence: float = 0.8,
    source: str = "conversation",  # "explicit", "behavior_pattern", "inference"
    evidence: str | None = None
) -> str:
    """学习用户的模式/习惯
    
    Args:
        pattern_type: 模式类型
        pattern_description: 模式描述
        confidence: 置信度 (0-1)
        source: 来源
        evidence: 证据（可选）
    """
    memory_sys = get_memory_system(ctx)
    
    # 保存到 preferences
    if pattern_type in ["使用习惯", "聊天习惯", "办事习惯", "语言偏好"]:
        # 使用现有的 update_preference
        key = pattern_description.split("：")[0] if "：" in pattern_description else pattern_description
        value = pattern_description.split("：")[1] if "：" in pattern_description else evidence or ""
        memory_sys.update_preference(pattern_type, key, value)
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

**更新 MEMORY_SYSTEM_PROMPT**:
```python
MEMORY_SYSTEM_PROMPT = """
## 记忆系统工具

你可以使用以下工具来管理和查询用户的长期记忆：

- `read_memory`: 读取用户的记忆信息
- `update_preference`: 更新用户的偏好设置
- `learn_user_pattern`: **学习用户的模式/习惯**（使用习惯、聊天习惯、办事习惯、语言偏好）
- `learn_habit`: 学习用户的新习惯
- `add_memory`: 记录重要的对话记忆
...

使用建议：
- **在对话中主动学习用户的习惯和偏好**
- 当用户明确表达偏好时，使用 `learn_user_pattern()` 学习
- 当观察到用户的行为模式时，使用 `learn_user_pattern()` 学习
"""
```

---

### 实现 2: 系统提示（指导学习）

**位置**: `examples/full_app/app.py`

```python
MAIN_INSTRUCTIONS = """
## 用户个性化学习

**CRITICAL**: 在对话中主动学习用户的习惯和偏好，让 AI 越来越懂用户。

### 学习时机

当用户表现出以下行为时，**立即**使用 `learn_user_pattern()` 学习：

#### 1. 使用习惯
- 用户说"我喜欢用表格展示" → `learn_user_pattern("使用习惯", "偏好表格格式展示", 0.95, "explicit")`
- 用户说"先分析再决定" → `learn_user_pattern("使用习惯", "工作流程：先分析后决策", 0.9, "explicit")`
- 用户频繁使用某个功能（3+次） → `learn_user_pattern("使用习惯", "常用功能：XXX", 0.8, "behavior_pattern")`

#### 2. 聊天习惯
- 用户说"直接做，不用问我" → `learn_user_pattern("聊天习惯", "确认频率：低（直接执行）", 0.95, "explicit")`
- 用户回复简短 → `learn_user_pattern("聊天习惯", "回复长度：简短", 0.7, "behavior_pattern")`
- 用户使用专业术语 → `learn_user_pattern("语言偏好", "语言风格：专业术语", 0.8, "behavior_pattern")`

#### 3. 办事习惯
- 用户说"越快越好" → `learn_user_pattern("办事习惯", "决策风格：快速决策", 0.9, "explicit")`
- 用户说"按重要性排序" → `learn_user_pattern("办事习惯", "优先级偏好：重要性 > 紧急性", 0.9, "explicit")`
- 用户要求详细步骤 → `learn_user_pattern("办事习惯", "任务分解：偏好详细步骤", 0.85, "explicit")`

#### 4. 语言偏好
- 用户使用特定表达方式 → `learn_user_pattern("语言偏好", "表达方式：XXX", 0.8, "behavior_pattern")`
- 用户偏好某种格式 → `learn_user_pattern("语言偏好", "格式偏好：XXX", 0.85, "explicit")`

### 学习方法

**显式表达**（高置信度 0.9-0.95）:
```python
learn_user_pattern(
    pattern_type="聊天习惯",
    pattern_description="确认频率：低（直接执行）",
    confidence=0.95,
    source="explicit",
    evidence="用户明确说'直接做，不用问我'"
)
```

**行为模式**（中等置信度 0.7-0.8）:
```python
learn_user_pattern(
    pattern_type="使用习惯",
    pattern_description="偏好表格格式展示",
    confidence=0.8,
    source="behavior_pattern",
    evidence="用户3次要求使用表格格式"
)
```

**推断**（低置信度 0.6-0.7）:
```python
learn_user_pattern(
    pattern_type="语言偏好",
    pattern_description="语言风格：简洁专业",
    confidence=0.7,
    source="inference",
    evidence="用户回复简短，使用专业术语"
)
```

### 应用学习结果

学习后，在后续对话中**自动应用**学习到的模式：
- 如果用户偏好表格格式 → 使用表格展示结果
- 如果用户不喜欢确认 → 直接执行，少问问题
- 如果用户偏好简洁 → 回复简短，重点突出
- 如果用户偏好详细 → 提供详细步骤和说明
"""
```

---

### 实现 3: 动态注入（应用学习）

**位置**: `examples/full_app/app.py` (在 `create_agent()` 函数中)

```python
# Add dynamic memory context injection for personal companion AI
if MEMORY_SYSTEM_AVAILABLE:
    @agent.instructions
    def inject_user_memory_context(ctx: Any) -> str:  # pragma: no cover
        """Inject user memory context (name, preferences) into system prompt."""
        try:
            memory_sys = MemorySystem(
                user_id=PERSONAL_USER_ID,
                memory_dir=str(MEMORY_DIR),
            )
            
            data = memory_sys.storage.get_all_data()
            basic_info = data.get("profile", {}).get("basic_info", {})
            preferences = data.get("profile", {}).get("preferences", {})
            habits = data.get("habits", {})
            
            parts = []
            
            # 用户姓名
            user_name = basic_info.get("姓名") or basic_info.get("昵称")
            if user_name:
                parts.append("## 👤 当前用户")
                parts.append(f"**用户姓名：{user_name}**")
                parts.append("")
                parts.append("**⚠️ 重要指令**：")
                parts.append(f"- 你只在**打招呼**或**对话开始时**称呼用户为：**{user_name}**")
                parts.append(f"- 这是你的主人，你是专属于 **{user_name}** 的私人助理")
                parts.append("")
            
            # 注入学习到的用户模式
            pattern_sections = []
            
            # 使用习惯
            usage_habits = preferences.get("使用习惯", {})
            if usage_habits:
                pattern_sections.append("### 📊 用户使用习惯")
                pattern_sections.append("**重要**: 根据这些习惯调整你的工具使用方式")
                for key, value in usage_habits.items():
                    pattern_sections.append(f"- **{key}**: {value}")
            
            # 聊天习惯
            chat_habits = preferences.get("聊天习惯", {})
            if chat_habits:
                pattern_sections.append("### 💬 用户聊天习惯")
                pattern_sections.append("**重要**: 根据这些习惯调整你的回复风格")
                for key, value in chat_habits.items():
                    pattern_sections.append(f"- **{key}**: {value}")
            
            # 办事习惯
            work_habits = preferences.get("办事习惯", {})
            if work_habits:
                pattern_sections.append("### ⚙️ 用户办事习惯")
                pattern_sections.append("**重要**: 根据这些习惯调整你的工作方式")
                for key, value in work_habits.items():
                    pattern_sections.append(f"- **{key}**: {value}")
            
            # 语言偏好
            language_prefs = preferences.get("语言偏好", {})
            if language_prefs:
                pattern_sections.append("### 🗣️ 用户语言偏好")
                pattern_sections.append("**重要**: 根据这些偏好调整你的表达方式")
                for key, value in language_prefs.items():
                    pattern_sections.append(f"- **{key}**: {value}")
            
            if pattern_sections:
                parts.append("## 🎯 学习到的用户模式")
                parts.append("")
                parts.extend(pattern_sections)
                parts.append("")
            
            # 学习到的习惯
            learned_habits = []
            for category, habit_list in habits.items():
                for habit in habit_list:
                    if isinstance(habit, dict):
                        learned_habits.append(f"- **{habit.get('habit', '')}** ({category})")
                    else:
                        learned_habits.append(f"- **{habit}** ({category})")
            
            if learned_habits:
                parts.append("## 📝 学习到的用户习惯")
                parts.extend(learned_habits)
                parts.append("")
            
            # 其他记忆上下文
            memory_context = memory_sys.get_context(sections=["profile"])
            if memory_context:
                parts.append(memory_context)
            
            return "\n".join(parts)
        except Exception as e:
            logger.warning(f"Failed to inject user memory context: {e}")
            return ""
```

---

### 实现 4: Skill（可选，提供详细指南）

**位置**: `examples/full_app/skills/user-learning/SKILL.md`

```markdown
---
name: user-learning
description: Detailed guide for learning user patterns and preferences
tags:
  - personalization
  - learning
  - user-adaptation
version: "1.0"
author: pydantic-deep
---

# User Learning Skill

This skill provides detailed guidance on how to learn user patterns.

## Learning Categories

1. **使用习惯** (Usage Habits)
2. **聊天习惯** (Chat Habits)
3. **办事习惯** (Work Habits)
4. **语言偏好** (Language Preferences)

## Detailed Examples

[提供详细的学习示例和最佳实践]
```

**注意**: 这个 Skill 是可选的，主要用于提供详细的学习指南。核心功能通过 Toolset + 系统提示实现。

---

## 完整集成流程

### 数据流

```
用户对话
  ↓
Agent 分析（系统提示指导）
  ↓
识别学习时机
  ↓
调用 learn_user_pattern() (Toolset)
  ↓
保存到 memory.json (统一存储)
  ↓
下次对话时动态注入 (inject_user_patterns)
  ↓
影响 Agent 行为
```

### 执行流程

```
1. 用户说："我喜欢用表格展示数据"
   ↓
2. Agent 识别：这是使用习惯的显式表达
   ↓
3. Agent 调用：learn_user_pattern("使用习惯", "偏好表格格式", 0.95, "explicit")
   ↓
4. Toolset 执行：保存到 memory.json
   ↓
5. 下次对话：inject_user_patterns() 注入学习结果
   ↓
6. Agent 行为：自动使用表格格式展示数据
```

---

## 总结

### ✅ 推荐方案：三层设计

| 层级 | 组件 | 作用 | 必须性 |
|------|------|------|--------|
| **工具层** | Toolset | 提供 `learn_user_pattern()` 工具 | ✅ 必须 |
| **指导层** | 系统提示 | 指导 Agent 何时学习 | ✅ 必须 |
| **应用层** | 动态注入 | 将学习结果注入系统提示 | ✅ 必须 |
| **指南层** | Skill | 提供详细的学习指南 | ⚠️ 可选 |

### 关键设计原则

1. ✅ **Toolset 提供工具** - 这是核心，必须实现
2. ✅ **系统提示指导学习** - 告诉 Agent 何时学习，必须实现
3. ✅ **动态注入应用结果** - 让学习生效，必须实现
4. ⚠️ **Skill 提供指南** - 可选，提供详细指南

### 为什么这样设计？

1. **Toolset 必须**：
   - 提供实际的学习工具
   - 工具始终可用，不需要加载
   - 与 Memory System 完美集成

2. **系统提示必须**：
   - 指导 Agent 何时学习
   - 始终生效，不需要加载
   - 明确学习规则

3. **动态注入必须**：
   - 让学习结果生效
   - 影响 Agent 行为
   - 符合现有架构

4. **Skill 可选**：
   - 提供详细指南
   - 可以按需加载
   - 不是核心功能

### 实现优先级

1. **P0（必须）**: Toolset + 系统提示 + 动态注入
2. **P1（推荐）**: Skill（提供详细指南）

---

## 代码位置总结

| 功能 | 文件位置 | 说明 |
|------|---------|------|
| 学习工具 | `memory_system/toolset.py` | 添加 `learn_user_pattern()` |
| 学习指导 | `app.py` (MAIN_INSTRUCTIONS) | 添加学习规则 |
| 动态注入 | `app.py` (inject_user_patterns) | 注入学习结果 |
| 学习指南 | `skills/user-learning/SKILL.md` | 可选，详细指南 |
