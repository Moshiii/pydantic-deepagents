# 清理旧的 Session 记忆文件

## 问题说明

在修复之前，记忆系统会为每个 `session_id` 创建独立的记忆文件，导致出现类似 `memory_a6b16142-8c39-49f0-a98f-ccffec1916b8.md` 这样的文件。

## 已修复

现在所有记忆都统一使用固定的用户 ID `"owner"`，所有记忆文件都会存储在 `memory_owner.md` 中。

## 清理步骤

### 1. 检查现有文件

```bash
cd examples/full_app/memories
ls -la
```

你应该会看到：
- `memory_owner.md` - 这是正确的文件（保留）
- `memory_*.md` - 这些是旧的 session 文件（可以删除）

### 2. 备份（可选但推荐）

如果你想保留旧记忆作为备份：

```bash
mkdir -p backups
cp memory_*.md backups/
```

### 3. 删除旧的 session 文件

**方法 1：手动删除**
```bash
# 删除所有非 owner 的记忆文件
rm memory_*.md
# 但保留 owner
mv memory_owner.md memory_owner_backup.md
rm memory_*.md
mv memory_owner_backup.md memory_owner.md
```

**方法 2：使用脚本**
```bash
# 只保留 memory_owner.md，删除其他
find . -name "memory_*.md" ! -name "memory_owner.md" -delete
```

### 4. 验证

删除后，`memories/` 目录应该只包含：
- `memory_owner.md` - 你的个人记忆文件

### 5. 重启应用

```bash
cd examples/full_app
uvicorn app:app --reload --port 8080
```

现在所有新的记忆都会写入 `memory_owner.md`，不会再创建 session 相关的文件。

## 注意事项

- 如果你在旧的 session 文件中有重要信息，可以先手动合并到 `memory_owner.md` 中
- 或者使用 Agent 的 `read_memory` 工具读取旧文件内容，然后让 Agent 帮你整理

## 代码变更说明

已修复的位置：
1. ✅ `app.py:create_agent()` - 使用 `PERSONAL_USER_ID = "owner"`
2. ✅ `app.py:run_agent_with_streaming()` - 使用 `PERSONAL_USER_ID` 而不是 `session.session_id`
3. ✅ `memory_system/toolset.py` - 支持 `fixed_user_id` 参数，优先级最高

现在所有记忆操作都会使用固定的 `"owner"` 用户 ID。
