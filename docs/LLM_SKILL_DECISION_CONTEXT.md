# LLM 如何根据上下文决定加载哪个 Skill

本文档详细解释 LLM（大语言模型）如何根据上下文信息决定加载哪个 skill。

---

## 📋 上下文信息来源

LLM 决定加载哪个 skill 时，会参考以下几个方面的上下文：

### 1️⃣ **静态系统提示（System Instructions）**

**位置**: `examples/full_app/app.py` 第 146-320 行

在创建 Agent 时，会设置固定的系统提示，其中明确提到了 skills 的使用：

```python
MAIN_INSTRUCTIONS = """
## Your Capabilities
...
3. **Data Analysis**: Load the 'data-analysis' skill for comprehensive CSV analysis
...
## Guidelines
...
- When asked to analyze data, first load the 'data-analysis' skill for best practices
...
"""
```

**关键信息**:
- 明确告诉 LLM：当用户要求分析数据时，应该加载 `data-analysis` skill
- 提供了具体的使用场景指导

**示例**:
当用户说 "Load the data-analysis skill" 时，LLM 会：
1. 识别这是一个明确的 skill 加载请求
2. 从系统提示中知道 `data-analysis` 是用于数据分析的 skill
3. 直接调用 `load_skill(skill_name="data-analysis")`

---

### 2️⃣ **动态系统提示（Dynamic System Prompt）**

**位置**: `pydantic_deep/agent.py` 第 294-325 行

每次 Agent 执行时，会动态生成系统提示，包含当前可用的 skills 列表：

```python
@agent.instructions
def dynamic_instructions(ctx: Any) -> str:
    """Generate dynamic instructions based on current state."""
    parts = []
    
    # ... 其他动态内容 ...
    
    if include_skills and loaded_skills:
        skills_prompt = get_skills_system_prompt(ctx.deps, loaded_skills)
        if skills_prompt:
            parts.append(skills_prompt)
    
    return "\n\n".join(parts) if parts else ""
```

**关键函数**: `get_skills_system_prompt()`

**位置**: `pydantic_deep/toolsets/skills.py` 第 178-207 行

```python
def get_skills_system_prompt(
    deps: DeepAgentDeps,
    skills: list[Skill] | None = None,
) -> str:
    """Generate system prompt for skills."""
    if not skills:
        return ""
    
    lines = [
        "## Available Skills",
        "",
        "You have access to skills that extend your capabilities. "
        "Use `list_skills` to see available skills and `load_skill` to load instructions.",
        "",
    ]
    
    for skill in skills:
        tags_str = ", ".join(skill["tags"]) if skill["tags"] else ""
        tags_part = f" [{tags_str}]" if tags_str else ""
        lines.append(f"- **{skill['name']}**{tags_part}: {skill['description']}")
    
    return "\n".join(lines)
```

**生成的动态提示示例**:
```
## Available Skills

You have access to skills that extend your capabilities. 
Use `list_skills` to see available skills and `load_skill` to load instructions.

- **data-analysis** [python, pandas, data-analysis, visualization]: Comprehensive data analysis skill for CSV files using Python and pandas
```

**关键信息**:
- 列出所有可用的 skills
- 每个 skill 包含：名称、标签、描述
- 告诉 LLM 可以使用 `list_skills` 查看详情，使用 `load_skill` 加载指令

---

### 3️⃣ **Skills 发现机制**

**位置**: `pydantic_deep/toolsets/skills.py` 第 95-155 行

在 Agent 创建时，系统会扫描指定的目录，发现所有可用的 skills：

```python
def discover_skills(
    directories: list[SkillDirectory],
    backend: Any | None = None,
) -> list[Skill]:
    """Discover skills from the filesystem."""
    skills: list[Skill] = []
    
    for skill_dir in directories:
        dir_path = Path(skill_dir["path"]).expanduser()
        # 查找所有 SKILL.md 文件
        pattern = "**/SKILL.md" if recursive else "*/SKILL.md"
        for skill_file in dir_path.glob(pattern):
            # 解析 frontmatter
            content = skill_file.read_text()
            frontmatter, _ = parse_skill_md(content)
            
            # 创建 Skill 对象
            skill: Skill = {
                "name": frontmatter.get("name", skill_folder.name),
                "description": frontmatter.get("description", ""),
                "path": str(skill_folder),
                "tags": frontmatter.get("tags", []),
                "version": frontmatter.get("version", "1.0.0"),
                ...
            }
            skills.append(skill)
    
    return skills
```

**在 app.py 中的配置**:

```python
agent = create_deep_agent(
    ...
    skill_directories=[{"path": str(SKILLS_DIR), "recursive": True}],
    # SKILLS_DIR = examples/full_app/skills
    ...
)
```

**发现的 skills**:
- 扫描 `examples/full_app/skills/` 目录
- 找到 `data-analysis/SKILL.md`
- 解析 frontmatter，提取：
  - name: "data-analysis"
  - description: "Comprehensive data analysis skill for CSV files using Python and pandas"
  - tags: ["python", "pandas", "data-analysis", "visualization"]

---

### 4️⃣ **工具可用性信息**

LLM 知道有以下工具可用：

**工具**: `list_skills`
- **功能**: 列出所有可用的 skills
- **返回**: 详细的 skill 列表（名称、描述、标签、版本、路径）

**工具**: `load_skill`
- **功能**: 加载指定 skill 的完整指令
- **参数**: `skill_name: str`
- **返回**: 完整的 SKILL.md 内容

**工具**: `read_skill_resource`
- **功能**: 读取 skill 的资源文件
- **参数**: `skill_name: str`, `resource_name: str`

这些工具的信息通过 pydantic-ai 的工具系统自动注入到 LLM 的上下文中。

---

## 🧠 LLM 决策流程

### 场景 1: 用户明确请求加载 skill

**用户消息**: "Load the data-analysis skill"

**LLM 决策过程**:

1. **解析用户意图**
   - 识别关键词：`Load` + `data-analysis` + `skill`
   - 这是一个明确的 skill 加载请求

2. **匹配可用 skills**
   - 从动态系统提示中看到：`**data-analysis**: Comprehensive data analysis skill...`
   - 确认 `data-analysis` 是一个可用的 skill

3. **调用工具**
   - 直接调用 `load_skill(skill_name="data-analysis")`
   - 不需要先调用 `list_skills`（因为已经知道 skill 名称）

---

### 场景 2: 用户请求数据分析任务

**用户消息**: "Analyze the uploaded CSV file"

**LLM 决策过程**:

1. **解析用户意图**
   - 识别任务类型：数据分析
   - 识别数据源：CSV 文件

2. **参考系统提示**
   - 从静态系统提示中看到：
     - "When asked to analyze data, first load the 'data-analysis' skill for best practices"
     - "Load the 'data-analysis' skill for comprehensive CSV analysis"

3. **决策**
   - 根据系统提示，应该先加载 `data-analysis` skill
   - 然后使用 skill 中的指令来指导分析过程

4. **执行流程**
   ```
   1. load_skill(skill_name="data-analysis")
      → 获取完整的数据分析指南
   
   2. 根据 skill 指令执行分析：
      - 读取 CSV 文件
      - 探索数据（shape, dtypes, missing values）
      - 执行分析
      - 创建可视化
      - 生成报告
   ```

---

### 场景 3: 用户请求未知任务类型

**用户消息**: "Help me with code review"

**LLM 决策过程**:

1. **解析用户意图**
   - 识别任务类型：代码审查
   - 不确定是否有对应的 skill

2. **查看可用 skills**
   - 从动态系统提示中看到可用 skills 列表
   - 如果没有匹配的 skill，LLM 可能：
     - 调用 `list_skills` 查看所有可用 skills
     - 或者直接使用通用能力处理任务

3. **如果发现匹配的 skill**
   - 例如：如果有 `code-review` skill
   - 调用 `load_skill(skill_name="code-review")`
   - 使用 skill 指令指导代码审查过程

---

## 📊 上下文信息的优先级

LLM 在决策时，会按以下优先级考虑：

### 1. **用户明确指令** (最高优先级)
- 如果用户明确说 "Load X skill"，直接执行
- 如果用户说 "Use Y skill for Z task"，按用户指示执行

### 2. **静态系统提示中的指导**
- 系统提示中明确提到的使用场景
- 例如："When asked to analyze data, first load the 'data-analysis' skill"

### 3. **动态系统提示中的可用 skills 列表**
- 当前可用的 skills 及其描述和标签
- 帮助 LLM 了解有哪些选项

### 4. **工具调用能力**
- 可以通过 `list_skills` 主动查询
- 可以通过 `load_skill` 加载指令

### 5. **通用能力**
- 如果没有匹配的 skill，使用通用能力处理任务

---

## 🔍 实际示例分析

### 示例 1: "Load the data-analysis skill"

**上下文信息**:
1. ✅ 静态系统提示：提到 `data-analysis` skill 用于数据分析
2. ✅ 动态系统提示：列出 `data-analysis` skill 及其描述
3. ✅ 用户明确请求：直接指定 skill 名称

**决策**: 直接调用 `load_skill(skill_name="data-analysis")`

---

### 示例 2: "Analyze this CSV file"

**上下文信息**:
1. ✅ 静态系统提示："When asked to analyze data, first load the 'data-analysis' skill"
2. ✅ 动态系统提示：列出 `data-analysis` skill
3. ✅ 用户任务：数据分析任务

**决策流程**:
```
1. 识别任务类型：数据分析
2. 参考系统提示：应该先加载 data-analysis skill
3. 调用 load_skill(skill_name="data-analysis")
4. 使用 skill 指令指导分析过程
```

---

### 示例 3: "What skills are available?"

**上下文信息**:
1. ✅ 动态系统提示：已列出可用 skills
2. ✅ 用户询问：想知道有哪些 skills
3. ✅ 工具可用：`list_skills` 可以提供详细信息

**决策**: 
- 可以直接回答（基于动态系统提示）
- 或者调用 `list_skills` 获取更详细的信息

---

## 🎯 关键设计特点

### 1. **渐进式披露（Progressive Disclosure）**

- **初始阶段**: 只加载 frontmatter（名称、描述、标签）
- **按需加载**: 当需要时，才加载完整的 SKILL.md 内容
- **优势**: 节省 token，提高效率

### 2. **动态上下文注入**

- 每次请求时，动态生成系统提示
- 包含当前可用的 skills 列表
- 确保 LLM 始终知道最新的可用选项

### 3. **明确的指导原则**

- 静态系统提示提供明确的使用场景指导
- 告诉 LLM 在什么情况下应该使用哪个 skill
- 减少 LLM 的决策负担

### 4. **灵活的查询机制**

- LLM 可以主动调用 `list_skills` 查询
- 支持探索性使用场景
- 不强制 LLM 必须记住所有 skills

---

## 📝 总结

LLM 决定加载哪个 skill 时，主要依赖以下上下文：

1. **静态系统提示**: 提供使用场景指导
2. **动态系统提示**: 列出当前可用的 skills（名称、描述、标签）
3. **用户消息**: 明确请求或任务类型
4. **工具能力**: `list_skills` 和 `load_skill` 工具

**决策流程**:
- 用户明确请求 → 直接执行
- 任务类型匹配 → 参考系统提示 → 加载对应 skill
- 不确定 → 查询 `list_skills` → 选择合适的 skill

这种设计既提供了明确的指导，又保持了灵活性，让 LLM 能够智能地选择合适的 skill 来处理用户任务。
