# Skill 结果持久化存储设计指南

## 核心原则

### ✅ 原则 1: Skill 不直接操作存储

**Skill 是指南，不是实现**：
- Skill 提供指令和最佳实践
- Skill 告诉 Agent "如何使用工具"来持久化
- Skill 不包含实际的存储代码

### ✅ 原则 2: 通过 Toolset 提供的工具持久化

**使用现有的工具集**：
- FilesystemToolset → `write_file()` - 保存到文件系统
- Memory Toolset → `add_memory()`, `update_preference()` - 保存到记忆系统
- Execute Tool → 运行代码保存（如果需要）

## 设计模式

### 模式 1: 文件系统持久化（最常用）

**适用场景**：
- 生成报告、分析结果
- 创建图表、可视化
- 生成代码、文档
- 任何需要文件形式保存的内容

**实现方式**：

#### 在 Skill 中提供指南

```markdown
## Saving Results

When you generate analysis results, charts, or reports, **always save them to persistent storage**.

### File System Storage

Use the `write_file()` tool from FilesystemToolset to save results:

```python
# Save analysis report
report_content = generate_report(data)
write_file(
    path="/workspace/analysis_report.md",
    content=report_content
)

# Save chart
# Charts are automatically saved when using matplotlib.savefig()
plt.savefig('/workspace/chart.png')
```

### Best Practices

1. **Save to `/workspace/` directory**: This is the persistent workspace
2. **Use descriptive filenames**: Include date/time if needed
3. **Save immediately after generation**: Don't wait for user confirmation
4. **Inform user**: Tell them where the file was saved
```

#### 实际使用示例

**data-analysis skill** 中的实现：

```markdown
### Visualization with Matplotlib

Always save charts to `/workspace/` directory so they can be viewed in the app.

```python
plt.savefig('/workspace/bar_chart.png', dpi=150, bbox_inches='tight')
plt.close()
```
```

**Agent 执行流程**：
1. Skill 告诉 Agent：生成图表后保存到 `/workspace/`
2. Agent 执行 Python 代码生成图表
3. `plt.savefig()` 自动保存到文件系统（通过 backend）
4. 文件持久化存储

---

### 模式 2: 记忆系统持久化

**适用场景**：
- 用户偏好、设置
- 对话记忆、重要信息
- 学习到的用户习惯
- 任何需要跨会话保存的用户数据

**实现方式**：

#### 在 Skill 中提供指南

```markdown
## Saving User Preferences

When you learn something about the user, save it to memory:

```python
# Save user preference
update_preference(
    category="工作习惯",
    key="工作时间",
    value="09:00-18:00"
)

# Save important memory
add_memory(
    topic="用户喜欢的分析方式",
    summary="用户偏好使用图表展示数据，特别是柱状图和折线图"
)
```

### When to Save

- User expresses a preference → `update_preference()`
- User mentions a habit → `learn_habit()`
- Important conversation point → `add_memory()`
- User's schedule preference → `learn_schedule_preference()`
```

#### 实际使用示例

**schedule-management skill** 中的潜在使用：

```markdown
## Learning User Preferences

If the user expresses preferences about schedule display format, save it:

```python
# User says "我喜欢看周视图"
learn_schedule_preference(
    preference_type="display_format",
    value="weekly_view"
)
```
```

---

### 模式 3: 结构化数据持久化

**适用场景**：
- 需要保存结构化数据（JSON、CSV）
- 需要保存配置、设置
- 需要保存中间结果供后续使用

**实现方式**：

#### 选项 A: JSON 文件（推荐）

```markdown
## Saving Structured Data

For structured data (configs, results), save as JSON:

```python
import json
from datetime import datetime

# Prepare data
results = {
    "timestamp": datetime.now().isoformat(),
    "analysis_type": "sales_trend",
    "summary": {...},
    "charts": ["chart1.png", "chart2.png"]
}

# Save as JSON
write_file(
    path="/workspace/analysis_results.json",
    content=json.dumps(results, indent=2, ensure_ascii=False)
)
```
```

#### 选项 B: CSV 文件

```markdown
## Saving Tabular Data

For tabular data, save as CSV:

```python
import pandas as pd

# Generate DataFrame
df = pd.DataFrame({
    'date': dates,
    'value': values,
    'category': categories
})

# Save as CSV
df.to_csv('/workspace/results.csv', index=False, encoding='utf-8')
```
```

---

### 模式 4: 代码执行持久化

**适用场景**：
- 需要运行脚本保存结果
- 需要调用外部 API 保存
- 需要复杂的保存逻辑

**实现方式**：

```markdown
## Saving via Code Execution

For complex saving logic, use `execute()` tool:

```python
# Save via Python script
execute(
    command="python save_results.py --output /workspace/results.json",
    timeout=30
)
```

**Note**: Only use this if simple file operations are insufficient.
```

---

## 完整示例：数据分析 Skill

### Skill 定义

```markdown
---
name: data-analysis
description: Comprehensive data analysis skill
---

# Data Analysis Skill

## Saving Results

**CRITICAL**: Always save your analysis results to persistent storage.

### 1. Save Analysis Report

After completing analysis, save a markdown report:

```python
# Generate report
report = f"""
# Data Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{summary_text}

## Key Findings
{findings_text}

## Charts Generated
- bar_chart.png
- line_chart.png
"""

# Save report
write_file(
    path="/workspace/analysis_report.md",
    content=report
)
```

### 2. Save Charts

Always save charts to `/workspace/`:

```python
plt.savefig('/workspace/bar_chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

### 3. Save Data

If you processed data, save the processed dataset:

```python
# Save processed data
df_processed.to_csv('/workspace/processed_data.csv', index=False)
```

### 4. Save Results Summary

Save a JSON summary for programmatic access:

```python
import json

summary = {
    "timestamp": datetime.now().isoformat(),
    "rows_analyzed": len(df),
    "charts_generated": ["bar_chart.png", "line_chart.png"],
    "key_metrics": {
        "total": total_value,
        "average": avg_value
    }
}

write_file(
    path="/workspace/analysis_summary.json",
    content=json.dumps(summary, indent=2, ensure_ascii=False)
)
```

### Best Practices

1. **Save immediately**: Don't wait for user confirmation
2. **Use `/workspace/`**: This is the persistent directory
3. **Inform user**: Tell them what was saved and where
4. **Use descriptive names**: Include analysis type and date if needed
5. **Save multiple formats**: Markdown for reading, JSON for programmatic access
```

---

## 设计决策树

```
需要持久化 Skill 的结果？
│
├─ 是什么类型的数据？
│  │
│  ├─ 文件（报告、图表、代码）
│  │  └─ 使用 FilesystemToolset.write_file()
│  │     └─ 保存到 /workspace/
│  │
│  ├─ 用户数据（偏好、记忆、习惯）
│  │  └─ 使用 Memory Toolset
│  │     ├─ update_preference() - 偏好
│  │     ├─ add_memory() - 记忆
│  │     └─ learn_habit() - 习惯
│  │
│  ├─ 结构化数据（JSON、CSV）
│  │  └─ 使用 FilesystemToolset.write_file()
│  │     └─ 保存为 JSON/CSV 文件
│  │
│  └─ 复杂逻辑（需要脚本）
│     └─ 使用 execute() 运行脚本
│        └─ 脚本内部处理保存
```

---

## 最佳实践

### ✅ DO（推荐做法）

1. **在 Skill 中明确说明保存位置**
   ```markdown
   Always save results to `/workspace/` directory.
   ```

2. **提供代码模板**
   ```markdown
   ```python
   write_file(path="/workspace/result.md", content=report)
   ```
   ```

3. **说明何时保存**
   ```markdown
   Save immediately after generating results, don't wait for confirmation.
   ```

4. **告知用户保存位置**
   ```markdown
   After saving, inform the user: "Results saved to /workspace/analysis_report.md"
   ```

5. **使用描述性文件名**
   ```markdown
   Use filenames like: `analysis_2024-01-15.md` or `sales_report_Q1.json`
   ```

### ❌ DON'T（避免的做法）

1. **不要在 Skill 中直接操作文件系统**
   ```markdown
   # ❌ WRONG - Skill 不应该包含实际代码
   import os
   with open('/workspace/file.txt', 'w') as f:
       f.write(content)
   ```

2. **不要假设存储位置**
   ```markdown
   # ❌ WRONG - 不明确
   Save to a file.
   
   # ✅ RIGHT - 明确
   Save to /workspace/result.md using write_file()
   ```

3. **不要忽略错误处理**
   ```markdown
   # ✅ GOOD - 检查结果
   result = write_file(path="/workspace/file.md", content=content)
   if "Error" in result:
       # Handle error
   ```

---

## 实际案例

### 案例 1: 数据分析 Skill

**需求**: 分析 CSV 文件后保存报告和图表

**实现**:
```markdown
## Workflow

1. Load data
2. Analyze
3. Generate charts
4. **Save everything**:
   - Report: `/workspace/analysis_report.md`
   - Charts: `/workspace/*.png`
   - Summary: `/workspace/summary.json`
```

**Agent 执行**:
```python
# Agent 根据 skill 指南执行
write_file(path="/workspace/analysis_report.md", content=report)
# Charts saved via plt.savefig()
write_file(path="/workspace/summary.json", content=json.dumps(summary))
```

### 案例 2: 日程管理 Skill

**需求**: 生成日程报告后保存

**实现**:
```markdown
## Saving Schedule Reports

If user requests a schedule report, save it:

```python
# Generate formatted schedule
schedule_report = format_schedule_as_calendar_table()

# Save report
write_file(
    path="/workspace/schedule_report.md",
    content=schedule_report
)
```
```

### 案例 3: 代码生成 Skill

**需求**: 生成代码后保存

**实现**:
```markdown
## Saving Generated Code

Always save generated code to files:

```python
# Generate code
code_content = generate_code(...)

# Save code
write_file(
    path="/workspace/generated_code.py",
    content=code_content
)
```
```

---

## 存储位置规范

### `/workspace/` - 工作空间（推荐）

**用途**: 所有 skill 生成的结果
- 报告、分析结果
- 图表、可视化
- 生成的代码、文档
- 中间结果

**特点**:
- ✅ 持久化存储（跨会话）
- ✅ 用户可见
- ✅ 可以通过文件系统工具访问

### `/uploads/` - 上传文件

**用途**: 用户上传的文件
- 不要在这里保存 skill 生成的结果
- 只读取用户上传的文件

### Memory System - 记忆系统

**用途**: 用户相关的数据
- 偏好、设置
- 对话记忆
- 学习到的习惯
- 用户信息

---

## 总结

### 核心设计原则

1. ✅ **Skill 提供指南，不直接操作存储**
2. ✅ **通过 Toolset 工具持久化**
3. ✅ **明确保存位置和格式**
4. ✅ **提供代码模板**
5. ✅ **立即保存，告知用户**

### 推荐模式

| 数据类型 | 存储方式 | 工具 | 位置 |
|---------|---------|------|------|
| 报告、文档 | 文件系统 | `write_file()` | `/workspace/` |
| 图表、图片 | 文件系统 | `plt.savefig()` | `/workspace/` |
| JSON 数据 | 文件系统 | `write_file()` | `/workspace/*.json` |
| CSV 数据 | 文件系统 | `df.to_csv()` | `/workspace/*.csv` |
| 用户偏好 | 记忆系统 | `update_preference()` | Memory System |
| 对话记忆 | 记忆系统 | `add_memory()` | Memory System |
| 用户习惯 | 记忆系统 | `learn_habit()` | Memory System |

### 关键要点

- **Skill = 指南**：告诉 Agent 如何使用工具
- **Toolset = 工具**：提供实际的存储能力
- **明确性**：在 Skill 中明确说明保存位置和方式
- **即时性**：生成后立即保存，不要等待确认
- **告知性**：保存后告知用户文件位置
