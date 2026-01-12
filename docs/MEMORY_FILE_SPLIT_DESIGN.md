# Memory 文件拆分设计

## 问题分析

### 当前问题

1. **LLM 上下文溢出**
   - 单个 `memory.json` 文件可能很大（包含所有数据）
   - 读取整个文件会占用大量 token
   - 影响 LLM 的上下文窗口使用效率

2. **用户管理困难**
   - 文件太大，难以查看和编辑
   - 所有数据混在一起，不够清晰
   - 难以定位特定类型的数据

3. **性能问题**
   - 每次读取都要加载整个文件
   - 写入时需要序列化整个 JSON
   - 缓存失效影响范围大

---

## 解决方案：按模块拆分文件

### 文件结构设计

```
memories/
  owner/
    profile.json          # 用户档案和偏好（小文件，经常读取）
    todos.json            # 待办事项（中等大小）
    schedule.json         # 日程安排（中等大小）
    ideas.json            # 创意想法（可能很大）
    habits.json           # 习惯（小文件）
    conversations.json    # 对话记录（可能很大）
    reminders.json        # 提醒（中等大小）
    followups.json        # 询问（中等大小）
    relationships.json    # 人际关系（小文件）
    diary.json            # 日记（可能很大）
    metadata.json         # 元数据（小文件）
```

### 文件大小估算

| 文件 | 预估大小 | 读取频率 | 说明 |
|------|---------|---------|------|
| `profile.json` | ~2-5 KB | 高（每次对话） | 基本信息 + 偏好 |
| `todos.json` | ~10-50 KB | 中 | 待办事项（按状态分组） |
| `schedule.json` | ~10-50 KB | 中 | 日程安排（定期 + 一次性） |
| `ideas.json` | ~5-100 KB | 低 | 创意想法（按日期组织） |
| `habits.json` | ~2-10 KB | 低 | 习惯（按类别分组） |
| `conversations.json` | ~20-200 KB | 低 | 对话记录（保留最近N条） |
| `reminders.json` | ~5-20 KB | 高（定时检查） | 提醒任务 |
| `followups.json` | ~5-20 KB | 高（定时检查） | 询问任务 |
| `relationships.json` | ~2-10 KB | 低 | 人际关系 |
| `diary.json` | ~10-100 KB | 低 | 日记（按日期组织） |
| `metadata.json` | ~1 KB | 中 | 元数据（版本、更新时间等） |

**总计**: ~62-585 KB（相比单个文件，拆分后可以按需加载）

---

## 数据拆分方案

### 1. profile.json - 用户档案

```json
{
  "basic_info": {
    "姓名": "",
    "昵称": "",
    "时区": "Asia/Shanghai (UTC+8)",
    "语言": "zh-CN"
  },
  "preferences": {
    "提醒方式": {...},
    "工作习惯": {...},
    "内容偏好": {...},
    "日程偏好": {...},
    "询问偏好": {...},
    "使用习惯": {...},
    "聊天习惯": {...},
    "办事习惯": {...},
    "语言偏好": {...}
  }
}
```

**特点**:
- ✅ 小文件，经常读取
- ✅ 每次对话都需要读取（用于个性化）
- ✅ 更新频率中等

---

### 2. todos.json - 待办事项

```json
{
  "pending": [...],
  "scheduled": [...],
  "in_progress": [...],
  "completed": [...]
}
```

**特点**:
- ✅ 中等大小
- ✅ 读取频率中等（查询待办时）
- ✅ 更新频率高（添加、完成、移动）

---

### 3. schedule.json - 日程安排

```json
{
  "regular": [...],
  "upcoming": [...]
}
```

**特点**:
- ✅ 中等大小
- ✅ 读取频率中等（查询日程时）
- ✅ 更新频率中等（添加、修改日程）

---

### 4. ideas.json - 创意想法

```json
[
  {
    "id": "idea_xxx",
    "content": "...",
    "date": "2024-01-15",
    "time": "15:30",
    "tags": [...],
    "category": "...",
    "created_at": "..."
  }
]
```

**特点**:
- ⚠️ 可能很大（累积很多创意）
- ✅ 读取频率低（查询创意时）
- ✅ 更新频率低（添加创意时）
- ✅ 可以按日期查询，不需要加载全部

---

### 5. habits.json - 习惯

```json
{
  "工作习惯": [...],
  "沟通习惯": [...],
  "生活习惯": [...]
}
```

**特点**:
- ✅ 小文件
- ✅ 读取频率低（查询习惯时）
- ✅ 更新频率低（学习新习惯时）

---

### 6. conversations.json - 对话记录

```json
[
  {
    "id": "conv_xxx",
    "date": "2024-01-15",
    "summary": "...",
    "topics": [...],
    "created_at": "..."
  }
]
```

**特点**:
- ⚠️ 可能很大（保留很多对话）
- ✅ 读取频率低（查询历史对话时）
- ✅ 更新频率中等（每次重要对话）
- ✅ 可以只保留最近N条

---

### 7. reminders.json - 提醒

```json
[
  {
    "id": "reminder_xxx",
    "type": "todo",
    "target_id": "todo_xxx",
    "remind_at": "...",
    "triggered": false,
    ...
  }
]
```

**特点**:
- ✅ 中等大小
- ✅ 读取频率高（定时检查）
- ✅ 更新频率高（创建、触发、删除）

---

### 8. followups.json - 询问

```json
[
  {
    "id": "followup_xxx",
    "type": "todo_completion",
    "target_id": "todo_xxx",
    "ask_at": "...",
    "asked": false,
    ...
  }
]
```

**特点**:
- ✅ 中等大小
- ✅ 读取频率高（定时检查）
- ✅ 更新频率高（创建、询问、删除）

---

### 9. relationships.json - 人际关系

```json
{
  "contacts": [...],
  "important": [...]
}
```

**特点**:
- ✅ 小文件
- ✅ 读取频率低（查询联系人时）
- ✅ 更新频率低（添加联系人时）

---

### 10. diary.json - 日记

```json
[
  {
    "id": "diary_xxx",
    "date": "2024-01-15",
    "content": "...",
    "mood": "...",
    "tags": [...],
    "created_at": "..."
  }
]
```

**特点**:
- ⚠️ 可能很大（累积很多日记）
- ✅ 读取频率低（查询日记时）
- ✅ 更新频率低（添加日记时）
- ✅ 可以按日期查询，不需要加载全部

---

### 11. metadata.json - 元数据

```json
{
  "version": "3.0",
  "created_at": "2024-01-01 00:00:00",
  "last_updated": "2024-01-15 15:30:00",
  "conversation_count": 42,
  "file_structure": "split"  // 标识文件结构版本
}
```

**特点**:
- ✅ 小文件
- ✅ 读取频率中等（检查版本、更新时间）
- ✅ 更新频率中等（每次更新时）

---

## 架构设计：按需加载

### 核心设计原则

1. **按需加载**: 只读取需要的文件
2. **缓存机制**: 每个文件独立缓存
3. **统一接口**: API 保持不变，底层实现改变

### 存储层设计

```python
class SplitJsonMemoryStorage:
    """拆分文件存储系统"""
    
    def __init__(self, user_id: str, memory_dir: str | Path):
        self.user_id = user_id
        self.user_dir = Path(memory_dir) / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件路径映射
        self.files = {
            "profile": self.user_dir / "profile.json",
            "todos": self.user_dir / "todos.json",
            "schedule": self.user_dir / "schedule.json",
            "ideas": self.user_dir / "ideas.json",
            "habits": self.user_dir / "habits.json",
            "conversations": self.user_dir / "conversations.json",
            "reminders": self.user_dir / "reminders.json",
            "followups": self.user_dir / "followups.json",
            "relationships": self.user_dir / "relationships.json",
            "diary": self.user_dir / "diary.json",
            "metadata": self.user_dir / "metadata.json",
        }
        
        # 独立缓存（每个文件）
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl: float = 60.0
    
    def _read_file(self, section: str, use_cache: bool = True) -> Any:
        """读取单个文件（带缓存）"""
        file_path = self.files[section]
        
        # 检查缓存
        if use_cache and section in self._cache:
            if time.time() - self._cache_timestamp[section] < self._cache_ttl:
                return self._cache[section]
        
        # 读取文件
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = self._get_default_data(section)
            self._write_file(section, data)
        
        # 更新缓存
        self._cache[section] = data
        self._cache_timestamp[section] = time.time()
        
        return data
    
    def _write_file(self, section: str, data: Any):
        """写入单个文件"""
        file_path = self.files[section]
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新缓存
        self._cache[section] = data
        self._cache_timestamp[section] = time.time()
        
        # 更新 metadata
        self._update_metadata()
    
    def _get_default_data(self, section: str) -> Any:
        """获取默认数据"""
        defaults = {
            "profile": {
                "basic_info": {...},
                "preferences": {...}
            },
            "todos": {
                "pending": [],
                "scheduled": [],
                "in_progress": [],
                "completed": []
            },
            "schedule": {
                "regular": [],
                "upcoming": []
            },
            "ideas": [],
            "habits": {
                "工作习惯": [],
                "沟通习惯": [],
                "生活习惯": []
            },
            "conversations": [],
            "reminders": [],
            "followups": [],
            "relationships": {
                "contacts": [],
                "important": []
            },
            "diary": [],
            "metadata": {
                "version": "3.0",
                "created_at": get_current_time(),
                "last_updated": get_current_time(),
                "file_structure": "split",
                "conversation_count": 0
            }
        }
        return defaults.get(section, {})
```

---

## API 设计：保持兼容

### 读取接口（按需加载）

```python
# 读取单个 section
def read_memory(self, section: str) -> Any:
    """读取指定 section（只加载需要的文件）"""
    return self._read_file(section)

# 读取多个 sections
def read_memory_sections(self, sections: List[str]) -> Dict[str, Any]:
    """读取多个 sections（只加载需要的文件）"""
    result = {}
    for section in sections:
        result[section] = self._read_file(section)
    return result

# 获取上下文（用于 LLM 注入）
def get_context(self, sections: Optional[List[str]] = None) -> str:
    """获取记忆上下文（只加载需要的文件）"""
    if sections is None:
        # 默认只加载常用的小文件
        sections = ["profile", "todos", "schedule", "reminders", "followups"]
    
    data = {}
    for section in sections:
        data[section] = self._read_file(section)
    
    # 格式化为字符串
    return self._format_context(data)
```

### 写入接口（只更新相关文件）

```python
def update_preference(self, category: str, key: str, value: str):
    """更新偏好（只更新 profile.json）"""
    profile = self._read_file("profile")
    profile["preferences"][category][key] = value
    self._write_file("profile", profile)

def add_todo(self, content: str, ...):
    """添加待办（只更新 todos.json）"""
    todos = self._read_file("todos")
    todos["pending"].append({...})
    self._write_file("todos", todos)
```

---

## 性能优化

### 1. 按需加载

**场景**: 查询待办事项
- ❌ **旧方式**: 读取整个 `memory.json` (~500 KB)
- ✅ **新方式**: 只读取 `todos.json` (~50 KB)
- **节省**: ~90% 的读取量

**场景**: 获取用户偏好（每次对话）
- ❌ **旧方式**: 读取整个 `memory.json` (~500 KB)
- ✅ **新方式**: 只读取 `profile.json` (~5 KB)
- **节省**: ~99% 的读取量

### 2. 独立缓存

**优势**:
- ✅ 每个文件独立缓存，失效范围小
- ✅ 更新 `todos.json` 不影响 `profile.json` 的缓存
- ✅ 缓存命中率更高

### 3. 批量操作优化

```python
def batch_update(self, updates: Dict[str, Any]):
    """批量更新多个文件"""
    for section, data in updates.items():
        self._write_file(section, data)
    # 只更新一次 metadata
    self._update_metadata()
```

---

## LLM 上下文优化

### 默认加载策略

```python
def get_context(self, sections: Optional[List[str]] = None) -> str:
    """获取记忆上下文（智能加载）"""
    if sections is None:
        # 默认只加载小文件和常用文件
        sections = [
            "profile",      # 必须：用户偏好
            "todos",        # 常用：待办事项
            "schedule",     # 常用：日程安排
            "reminders",    # 常用：提醒
            "followups"     # 常用：询问
        ]
        # 不加载大文件：
        # - ideas（按需查询）
        # - conversations（按需查询）
        # - diary（按需查询）
    
    data = {}
    for section in sections:
        data[section] = self._read_file(section)
    
    return self._format_context(data)
```

### 按需查询大文件

```python
# 查询创意想法（只加载 ideas.json）
def get_daily_ideas(self, date: str) -> List[Dict]:
    ideas = self._read_file("ideas")
    return [idea for idea in ideas if idea["date"] == date]

# 查询历史对话（只加载 conversations.json）
def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
    conversations = self._read_file("conversations")
    return conversations[-limit:]
```

---

## 文件大小控制

### 1. 对话记录限制

```python
def add_conversation(self, summary: str, ...):
    """添加对话记录（自动限制数量）"""
    conversations = self._read_file("conversations")
    
    # 只保留最近 100 条
    MAX_CONVERSATIONS = 100
    if len(conversations) >= MAX_CONVERSATIONS:
        conversations = conversations[-MAX_CONVERSATIONS+1:]
    
    conversations.append({...})
    self._write_file("conversations", conversations)
```

### 2. 已完成待办归档

```python
def archive_completed_todos(self, days: int = 30):
    """归档旧已完成待办（移动到归档文件）"""
    todos = self._read_file("todos")
    completed = todos["completed"]
    
    # 归档 30 天前的已完成待办
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    
    archived = []
    remaining = []
    for todo in completed:
        completed_at = parse_datetime(todo.get("completed_at", ""))
        if completed_at and completed_at.date() < cutoff_date:
            archived.append(todo)
        else:
            remaining.append(todo)
    
    todos["completed"] = remaining
    self._write_file("todos", todos)
    
    # 保存到归档文件
    if archived:
        archive_file = self.user_dir / "todos_archive.json"
        # ... 追加到归档文件
```

---

## 用户管理优势

### 1. 文件清晰

```
memories/owner/
├── profile.json          # 用户偏好设置
├── todos.json            # 待办事项
├── schedule.json         # 日程安排
├── ideas.json            # 创意想法
└── ...
```

**优势**:
- ✅ 每个文件职责清晰
- ✅ 易于定位和编辑
- ✅ 文件大小合理

### 2. 按需查看

**场景**: 用户想查看今天的待办
- ✅ 只需要打开 `todos.json`
- ✅ 不需要查看其他不相关的数据

**场景**: 用户想修改偏好设置
- ✅ 只需要打开 `profile.json`
- ✅ 文件小，易于编辑

### 3. 备份和恢复

**优势**:
- ✅ 可以单独备份重要文件（如 `profile.json`）
- ✅ 可以单独恢复某个模块的数据
- ✅ 文件损坏影响范围小

---

## 实现计划

### Phase 1: 核心拆分（P0）

1. ✅ 实现 `SplitJsonMemoryStorage` 类
2. ✅ 实现文件拆分逻辑
3. ✅ 实现按需加载机制
4. ✅ 实现独立缓存

### Phase 2: API 设计（P0）

1. ✅ 设计统一的读取接口
2. ✅ 设计统一的写入接口
3. ✅ 实现 `get_context()` 智能加载

### Phase 3: 功能实现（P0）

1. ✅ 实现所有 CRUD 操作
2. ✅ 实现按需查询大文件
3. ✅ 测试所有功能

### Phase 4: 优化（P1）

1. ✅ 实现文件大小控制（归档）
2. ✅ 优化默认加载策略
3. ✅ 性能测试和优化

---

## 总结

### 核心优势

1. ✅ **解决上下文溢出**: 按需加载，只读取需要的文件
2. ✅ **提升性能**: 减少读取量，独立缓存
3. ✅ **改善用户体验**: 文件清晰，易于管理
4. ✅ **统一接口**: API 设计清晰，易于使用

### 文件拆分策略

| 文件 | 大小 | 读取频率 | 拆分原因 |
|------|------|---------|---------|
| `profile.json` | 小 | 高 | 每次对话都需要 |
| `todos.json` | 中 | 中 | 独立模块，经常更新 |
| `schedule.json` | 中 | 中 | 独立模块，经常更新 |
| `ideas.json` | 大 | 低 | 可能很大，按需查询 |
| `conversations.json` | 大 | 低 | 可能很大，按需查询 |
| `diary.json` | 大 | 低 | 可能很大，按需查询 |

### 关键设计决策

1. ✅ **按需加载**: 只读取需要的文件
2. ✅ **独立缓存**: 每个文件独立缓存
3. ✅ **统一接口**: API 设计清晰，易于使用
4. ✅ **文件大小控制**: 归档旧数据
