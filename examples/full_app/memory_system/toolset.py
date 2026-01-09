"""
记忆系统工具集 - 用于集成到 pydantic-deep agent

这个模块提供了与 pydantic-deep 集成的工具集，但也可以独立使用。
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset

from .core import MemorySystem, MemoryData

# 尝试导入 DeepAgentDeps，如果不存在则使用 Any
try:
    from pydantic_deep.deps import DeepAgentDeps
    DepsType = DeepAgentDeps
except ImportError:
    DepsType = Any


MEMORY_SYSTEM_PROMPT = """
## 记忆系统工具

你可以使用以下工具来管理和查询用户的长期记忆：

- `read_memory`: 读取用户的记忆信息（基本信息、偏好、待办等）
- `update_preference`: 更新用户的偏好设置
- `add_todo`: 添加待办事项到用户的记忆
- `complete_todo`: 标记待办事项为已完成
- `add_memory`: 记录重要的对话记忆
- `learn_habit`: 学习用户的新习惯

使用建议：
- 在对话开始时，使用 `read_memory` 了解用户的基本信息和偏好
- 当用户提到偏好时，使用 `update_preference` 更新
- 当用户提到任务时，使用 `add_todo` 记录
- 在重要对话后，使用 `add_memory` 保存关键信息
- 当发现用户的行为模式时，使用 `learn_habit` 学习
"""


def get_memory_system_prompt(memory: Optional[MemoryData] = None) -> str:
    """生成记忆系统的系统提示"""
    if not memory:
        return MEMORY_SYSTEM_PROMPT
    
    parts = [MEMORY_SYSTEM_PROMPT]
    
    # 添加当前记忆摘要
    if memory.basic_info:
        parts.append("\n## 当前用户信息")
        for key, value in memory.basic_info.items():
            if value:
                parts.append(f"- {key}：{value}")
    
    if memory.preferences:
        parts.append("\n## 用户偏好")
        for category, items in memory.preferences.items():
            if items:
                parts.append(f"### {category}")
                for item in items[:3]:  # 只显示前3个
                    parts.append(f"  - {item}")
    
    todos = memory.todos.get("in_progress", [])
    if todos:
        parts.append("\n## 当前待办")
        for todo in todos[:5]:
            parts.append(f"- {todo.get('content', '')}")
    
    return "\n".join(parts)


def create_memory_toolset(
    memory_dir: str = "./memories",
    template_path: Optional[str] = None,
    id: str | None = "memory",
    fixed_user_id: Optional[str] = None,
) -> FunctionToolset[DepsType]:
    """创建记忆系统工具集
    
    Args:
        memory_dir: 记忆文件存储目录
        template_path: 模板文件路径（可选）
        id: 工具集 ID
    
    Returns:
        FunctionToolset 实例
    """
    toolset: FunctionToolset[DepsType] = FunctionToolset(id=id)
    
    def get_user_id(ctx: RunContext[DepsType]) -> str:
        """获取 user_id

        优先级：
        1. fixed_user_id（用于单用户私人助手）
        2. ctx.deps.user_id
        3. ctx.deps.session_id
        4. ctx.metadata 中的 user_id / session_id
        5. ctx.user_id
        6. 默认值 "default_user"
        """
        # 1. 固定用户 ID（用于私人陪伴型 AI）
        if fixed_user_id:
            return fixed_user_id

        # 2. 尝试从 deps 获取 user_id
        if hasattr(ctx.deps, "user_id"):
            return getattr(ctx.deps, "user_id")

        # 3. 尝试从 session_id 获取（如果 deps 有 session_id 属性）
        if hasattr(ctx.deps, "session_id"):
            return getattr(ctx.deps, "session_id")

        # 4. 尝试从 run context 的 metadata 获取
        if hasattr(ctx, "metadata") and isinstance(ctx.metadata, dict):
            if "user_id" in ctx.metadata:
                return ctx.metadata["user_id"]
            if "session_id" in ctx.metadata:
                return ctx.metadata["session_id"]

        # 5. 尝试从 run context 直接获取
        if hasattr(ctx, "user_id"):
            return getattr(ctx, "user_id")

        # 6. 默认值
        return "default_user"
    
    def get_memory_system(ctx: RunContext[DepsType]) -> MemorySystem:
        """获取或创建记忆系统实例"""
        user_id = get_user_id(ctx)
        return MemorySystem(
            user_id=user_id,
            memory_dir=memory_dir,
            template_path=template_path
        )
    
    @toolset.tool
    async def read_memory(
        ctx: RunContext[DepsType],
        section: str = "all"
    ) -> str:
        """读取用户的记忆信息
        
        Args:
            section: 要读取的部分，可选值：
                - "all": 全部信息
                - "basic_info": 基本信息
                - "preferences": 偏好设置
                - "todos": 待办事项
                - "habits": 学习到的习惯
                - "memories": 重要记忆
                - "goals": 长期目标
        """
        memory_sys = get_memory_system(ctx)

        # 全部上下文（给模型看）
        if section == "all":
            return memory_sys.get_context()

        # 以下分支使用新的分类存储来读取对应文件
        storage = memory_sys.storage  # CategorizedMemoryStorage

        if section == "basic_info":
            # 直接从 profile.md 中提取“基本信息”表格
            profile = storage.files["profile"].read_text(encoding="utf-8") if storage.files["profile"].exists() else ""
            import re
            match = re.search(r"## 基本信息\n\n(.*?)(?=\n## |$)", profile, re.DOTALL)
            if match:
                result = ["## 基本信息", match.group(1).strip()]
                return "\n".join(result)
            return "暂无基本信息"

        if section == "preferences":
            # 返回 profile.md 中的偏好设置部分
            profile = storage.files["profile"].read_text(encoding="utf-8") if storage.files["profile"].exists() else ""
            import re
            match = re.search(r"## 偏好设置\n(.*?)(?=\n---|$)", profile, re.DOTALL)
            if match:
                result = ["## 偏好设置", match.group(1).strip()]
                return "\n".join(result)
            return "暂无偏好设置"

        if section == "todos":
            # 直接返回 todos.md 的内容
            if storage.files["todos"].exists():
                return storage.files["todos"].read_text(encoding="utf-8")
            return "暂无待办事项"

        if section == "habits":
            if storage.files["habits"].exists():
                return storage.files["habits"].read_text(encoding="utf-8")
            return "暂无学习到的习惯"

        if section == "memories":
            if storage.files["conversations"].exists():
                return storage.files["conversations"].read_text(encoding="utf-8")
            return "暂无重要记忆"

        if section == "goals":
            # 当前未单独实现 goals 文件，返回 profile 中可能的目标信息或占位
            return "当前记忆系统未单独存储长期目标，如需请在 profile 或 diary 中记录。"

        return f"未知的章节：{section}。可用章节：all, basic_info, preferences, todos, habits, memories, goals"
    
    @toolset.tool
    async def update_preference(
        ctx: RunContext[DepsType],
        category: str,
        key: str,
        value: str
    ) -> str:
        """更新用户的偏好设置
        
        Args:
            category: 偏好类别（如"提醒方式"、"工作习惯"、"内容偏好"）
            key: 偏好键名
            value: 偏好值
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.update_preference(category, key, value)
        return f"已更新偏好：{category} - {key} = {value}"
    
    @toolset.tool
    async def add_todo(
        ctx: RunContext[DepsType],
        content: str,
        priority: str = "medium",
        due_date: str | None = None
    ) -> str:
        """添加待办事项到用户的记忆
        
        Args:
            content: 待办内容
            priority: 优先级（low, medium, high）
            due_date: 截止日期（格式：YYYY-MM-DD）
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.add_todo(content, priority, due_date)
        return f"已添加待办：{content}（优先级：{priority}）"
    
    @toolset.tool
    async def complete_todo(
        ctx: RunContext[DepsType],
        content: str
    ) -> str:
        """标记待办事项为已完成
        
        Args:
            content: 待办内容（需要与添加时完全匹配）
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.complete_todo(content)
        return f"已标记完成：{content}"
    
    @toolset.tool
    async def add_memory(
        ctx: RunContext[DepsType],
        topic: str,
        summary: str
    ) -> str:
        """记录重要的对话记忆
        
        Args:
            topic: 对话主题
            summary: 记忆摘要（可以包含多个要点，用换行分隔）
        """
        memory_sys = get_memory_system(ctx)
        points = [p.strip() for p in summary.split('\n') if p.strip()]
        memory_sys.add_memory(topic, points)
        return f"已记录记忆：{topic}"
    
    @toolset.tool
    async def learn_habit(
        ctx: RunContext[DepsType],
        habit: str,
        category: str = "工作习惯"
    ) -> str:
        """学习用户的新习惯
        
        Args:
            habit: 习惯描述
            category: 习惯类别（工作习惯、沟通习惯、生活习惯）
        """
        memory_sys = get_memory_system(ctx)
        memory_sys.learn_habit(habit, category)
        return f"已学习习惯：{habit}（类别：{category}）"
    
    return toolset


# 独立使用时的辅助函数
def create_standalone_memory_system(
    user_id: str,
    memory_dir: str = "./memories",
    template_path: Optional[str] = None
) -> MemorySystem:
    """创建独立的记忆系统实例（不依赖 pydantic-deep）
    
    这个函数允许在其他框架中使用记忆系统。
    
    Args:
        user_id: 用户 ID
        memory_dir: 记忆文件存储目录
        template_path: 模板文件路径
    
    Returns:
        MemorySystem 实例
    
    Example:
        ```python
        # 在任何 Python 应用中使用
        memory = create_standalone_memory_system("user123")
        
        # 读取记忆
        context = memory.get_context()
        
        # 更新记忆
        memory.add_todo("完成项目文档")
        memory.update_preference("提醒方式", "默认提醒方式", "邮件")
        ```
    """
    return MemorySystem(
        user_id=user_id,
        memory_dir=memory_dir,
        template_path=template_path
    )
