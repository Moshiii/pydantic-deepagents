"""
极简记忆系统 - 独立、低依赖的 Markdown 记忆管理

这个模块提供了一个完全独立的记忆系统，可以：
1. 作为工具集集成到 pydantic-deep agent
2. 独立使用，方便移植到其他 agent 框架
3. 零外部依赖（仅使用 Python 标准库）

使用示例：
    from memory_system import MemorySystem
    
    # 初始化
    memory = MemorySystem(user_id="user123", memory_dir="./memories")
    
    # 读取记忆
    context = memory.get_context()
    
    # 更新记忆
    memory.update_preference("提醒方式", "邮件")
    memory.add_todo("完成项目文档", priority="high")
    memory.add_memory("用户喜欢在早上工作", category="工作习惯")
"""

from .core import MemorySystem, MemoryParser, MemoryUpdater
from .toolset import create_memory_toolset, get_memory_system_prompt
from .categorized_storage import CategorizedMemoryStorage

__all__ = [
    "MemorySystem",
    "MemoryParser", 
    "MemoryUpdater",
    "CategorizedMemoryStorage",
    "create_memory_toolset",
    "get_memory_system_prompt",
]

__version__ = "1.0.0"
