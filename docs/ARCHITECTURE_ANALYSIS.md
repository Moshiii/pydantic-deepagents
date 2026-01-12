# 记忆系统与日程管理 Skill 架构分析

## 当前架构

### 1. Memory System (Toolset) - 数据层
**位置**: `examples/full_app/memory_system/toolset.py`

**职责**: 提供数据操作工具
- `read_memory()` - 读取记忆数据
- `add_todo()` - 添加待办
- `add_regular_schedule()` - 添加定期日程
- `add_one_time_event()` - 添加一次性事件
- `update_preference()` - 更新偏好
- 等等...

**特点**:
- ✅ 提供实际的工具函数（可调用的 API）
- ✅ 负责数据的 CRUD 操作
- ✅ 数据持久化（JSON 存储）
- ✅ 基础设施层

### 2. Schedule Management Skill - 展示层
**位置**: `examples/full_app/skills/schedule-management/SKILL.md`

**职责**: 提供展示和使用的指南
- 告诉 Agent 如何使用 `read_memory()` 读取日程
- 告诉 Agent 如何格式化展示（日历表格）
- 告诉 Agent 何时使用哪些工具
- 提供最佳实践和工作流程

**特点**:
- ✅ 提供指导性指令（知识/指南）
- ✅ 不包含实际代码实现
- ✅ 告诉 Agent "如何做"，而不是"做什么"
- ✅ 应用层

## 架构对比分析

### 方案 A: 分离架构（当前设计）✅

```
┌─────────────────────────────────────┐
│  Memory System (Toolset)            │
│  - read_memory()                    │
│  - add_regular_schedule()           │
│  - add_one_time_event()             │
│  提供数据操作工具                    │
└─────────────────────────────────────┘
              ↑ 被使用
              │
┌─────────────────────────────────────┐
│  Schedule Management Skill          │
│  - 如何使用 read_memory()            │
│  - 如何格式化展示日程                │
│  - 何时加载此 skill                  │
│  提供使用指南                         │
└─────────────────────────────────────┘
```

**优点**:
1. ✅ **职责清晰**: Toolset 负责数据，Skill 负责展示
2. ✅ **可复用性**: Memory toolset 可以被其他 skills 使用
   - 例如：可以创建 "todo-management" skill 使用同样的 memory toolset
3. ✅ **灵活性**: 可以有多个展示方式
   - `schedule-management` skill - 日历表格展示
   - 未来可以创建 `schedule-analytics` skill - 数据分析展示
4. ✅ **符合单一职责原则**: 每个组件只做一件事
5. ✅ **易于测试**: 数据层和展示层可以独立测试
6. ✅ **符合 pydantic-deep 架构**: Toolset 提供工具，Skill 提供指南

**缺点**:
1. ⚠️ 需要理解两个概念（Toolset vs Skill）
2. ⚠️ 可能感觉有些分离（但实际上这是好的设计）

### 方案 B: 合并架构（不推荐）❌

```
┌─────────────────────────────────────┐
│  Memory + Schedule Management       │
│  - read_memory()                    │
│  - add_regular_schedule()           │
│  - display_schedule()               │
│  - format_calendar_table()          │
│  数据和展示混在一起                  │
└─────────────────────────────────────┘
```

**缺点**:
1. ❌ **违反单一职责原则**: 一个组件做太多事情
2. ❌ **难以复用**: 展示逻辑和数据操作耦合
3. ❌ **难以扩展**: 如果要添加新的展示方式，需要修改核心工具集
4. ❌ **违反关注点分离**: 数据层和展示层混在一起
5. ❌ **不符合 pydantic-deep 架构**: Toolset 应该只提供工具，不包含展示逻辑

## Toolset vs Skill 的区别

### Toolset（工具集）
- **是什么**: 提供实际可调用的工具函数
- **职责**: 数据操作、业务逻辑
- **位置**: Python 代码（`.py` 文件）
- **示例**: `read_memory()`, `add_todo()`, `write_file()`

### Skill（技能）
- **是什么**: 提供指导性指令和最佳实践
- **职责**: 告诉 Agent 如何使用工具、何时使用、如何展示
- **位置**: Markdown 文件（`SKILL.md`）
- **示例**: "使用日历表格格式展示日程"、"先读取数据再格式化"

## 类比理解

### 类比 1: 数据库和查询工具

```
Memory System (Toolset) = 数据库
- 提供数据存储和查询 API
- read_memory() = SELECT
- add_schedule() = INSERT

Schedule Management Skill = SQL 查询优化指南
- 告诉如何写高效的查询
- 告诉如何格式化结果
- 提供最佳实践
```

### 类比 2: API 和 SDK 文档

```
Memory System (Toolset) = REST API
- 提供实际的 API 端点
- POST /api/schedule
- GET /api/schedule

Schedule Management Skill = SDK 使用文档
- 告诉如何使用 API
- 提供代码示例
- 说明最佳实践
```

### 类比 3: 工具和说明书

```
Memory System (Toolset) = 工具箱
- 提供实际的工具（锤子、螺丝刀）
- read_memory() = 锤子
- add_schedule() = 螺丝刀

Schedule Management Skill = 使用说明书
- 告诉如何使用工具
- 提供使用场景
- 说明注意事项
```

## 实际使用场景

### 场景 1: 用户问"最近的日程安排"

```
1. Agent 识别需要展示日程
2. 加载 schedule-management skill（获得展示指南）
3. Skill 告诉 Agent: "使用 read_memory(section='schedule') 读取数据"
4. Agent 调用 Memory Toolset 的 read_memory() 工具
5. Skill 告诉 Agent: "使用日历表格格式展示结果"
6. Agent 按照 skill 的指南格式化展示
```

### 场景 2: 用户问"添加一个会议"

```
1. Agent 识别需要添加日程
2. 不需要加载 skill（直接操作数据）
3. Agent 直接调用 Memory Toolset 的 add_one_time_event() 工具
4. 完成
```

### 场景 3: 未来添加"日程分析"功能

```
1. 创建新的 schedule-analytics skill
2. 使用同样的 Memory Toolset（read_memory）
3. 但提供不同的展示方式（图表、统计）
4. 不需要修改 Memory Toolset
```

## 最佳实践建议

### ✅ 推荐：保持分离架构

**原因**:
1. **符合 pydantic-deep 的设计理念**
   - Toolset = 工具（做什么）
   - Skill = 指南（如何做）

2. **符合软件工程原则**
   - 单一职责原则
   - 关注点分离
   - 开闭原则（对扩展开放，对修改关闭）

3. **实际好处**
   - Memory toolset 可以被多个 skills 复用
   - 可以有不同的展示方式（表格、图表、列表）
   - 易于维护和扩展

### 当前设计的问题（如果有）

如果感觉有问题，可能是：

1. **文档不够清晰**
   - 解决方案：添加架构说明文档（本文档）

2. **Skill 和 Toolset 的边界不够明确**
   - 解决方案：明确职责划分
   - Toolset：提供工具函数
   - Skill：提供使用指南

3. **可能缺少一些工具**
   - 如果需要在 skill 中做复杂的数据处理，可能需要添加更多工具到 toolset

## 改进建议

### 1. 明确职责边界

**Memory Toolset 应该提供**:
- ✅ 数据 CRUD 操作
- ✅ 数据查询和过滤
- ❌ 不应该包含展示逻辑

**Schedule Management Skill 应该提供**:
- ✅ 如何使用工具的指南
- ✅ 展示格式的说明
- ✅ 最佳实践
- ❌ 不应该包含数据操作代码

### 2. 如果需要在 Skill 中做复杂处理

如果 skill 需要复杂的数据处理（比如生成日历表格），有两个选择：

**选择 A**: 在 Memory Toolset 中添加格式化工具
```python
@toolset.tool
async def format_schedule_as_calendar_table(
    ctx: RunContext[DeepAgentDeps],
    days: int = 7
) -> str:
    """Format schedule as calendar table for next N days."""
    # 实现格式化逻辑
    ...
```

**选择 B**: 在 Skill 中提供 Python 代码模板
```markdown
## Code Template

```python
from datetime import datetime, timedelta
# 读取数据
schedule_data = read_memory(section="schedule")
# 格式化展示
# ... 代码模板 ...
```
```

**推荐选择 B**，因为：
- 保持 toolset 的简洁性
- 展示逻辑可以更灵活
- 符合 skill 的定位（提供指南和模板）

### 3. 添加更多工具（如果需要）

如果发现 skill 中需要频繁使用的功能，可以考虑添加到 toolset：

```python
# 如果经常需要"获取今天的日程"
@toolset.tool
async def get_today_schedule(ctx: RunContext[DeepAgentDeps]) -> str:
    """Get today's schedule formatted."""
    ...

# 如果经常需要"获取本周日程"
@toolset.tool
async def get_week_schedule(ctx: RunContext[DeepAgentDeps]) -> str:
    """Get this week's schedule formatted."""
    ...
```

但要注意：不要过度添加工具，保持 toolset 的简洁性。

## 结论

### ✅ 当前架构是正确的！

**分离架构的优势**:
1. ✅ 职责清晰
2. ✅ 可复用性强
3. ✅ 易于扩展
4. ✅ 符合软件工程最佳实践
5. ✅ 符合 pydantic-deep 的设计理念

**建议**:
1. ✅ **保持分离架构** - 这是正确的设计
2. ✅ **明确职责边界** - Toolset 提供工具，Skill 提供指南
3. ✅ **完善文档** - 让开发者理解为什么这样设计
4. ✅ **如果需要在 skill 中做复杂处理** - 使用代码模板而不是添加过多工具

**如果感觉有问题**，可能是：
- 文档不够清晰（添加架构说明）
- 边界不够明确（明确职责划分）
- 缺少某些工具（按需添加，但保持简洁）

总的来说，**当前的设计是合理的，建议保持分离架构**。
