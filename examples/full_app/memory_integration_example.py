"""
记忆系统集成示例

展示如何将记忆系统集成到现有的 app.py 中。
"""

from pathlib import Path
from memory_system import create_memory_toolset, MemorySystem
from memory_system.core import get_memory_system_prompt

# 假设这是你的应用目录
APP_DIR = Path(__file__).parent
MEMORY_DIR = APP_DIR / "memories"
TEMPLATE_PATH = APP_DIR / "memory_template.md"

# ============================================
# 方式 1: 作为工具集集成（推荐）
# ============================================

def create_agent_with_memory():
    """创建包含记忆系统的 Agent"""
    from pydantic_deep import create_deep_agent
    
    # 创建记忆工具集
    memory_toolset = create_memory_toolset(
        memory_dir=str(MEMORY_DIR),
        template_path=str(TEMPLATE_PATH),
        id="memory"
    )
    
    # 创建 Agent，包含记忆工具集
    agent = create_deep_agent(
        model="openai:gpt-4.1",
        instructions="你是一个智能助手，可以使用记忆系统来记住用户信息。",
        toolsets=[memory_toolset],  # 添加记忆工具集
        # ... 其他配置
    )
    
    return agent


# ============================================
# 方式 2: 在系统提示中注入记忆上下文
# ============================================

def create_agent_with_memory_context(session_id: str):
    """创建 Agent，并在系统提示中注入记忆上下文"""
    from pydantic_deep import create_deep_agent
    
    # 获取用户记忆
    memory_sys = MemorySystem(
        user_id=session_id,
        memory_dir=str(MEMORY_DIR),
        template_path=str(TEMPLATE_PATH)
    )
    
    # 获取记忆上下文
    memory_context = memory_sys.get_context()
    
    # 构建增强的系统提示
    enhanced_instructions = f"""
你是一个智能助手，具有以下用户记忆：

{memory_context}

请根据这些记忆信息为用户提供个性化服务。
"""
    
    # 创建 Agent
    agent = create_deep_agent(
        model="openai:gpt-4.1",
        instructions=enhanced_instructions,
        # ... 其他配置
    )
    
    return agent, memory_sys


# ============================================
# 方式 3: 在对话流程中集成
# ============================================

async def run_conversation_with_memory(session_id: str, user_message: str):
    """运行对话，集成记忆系统"""
    from pydantic_deep import create_deep_agent, DeepAgentDeps
    from pydantic_ai_backends import StateBackend
    
    # 创建记忆系统
    memory_sys = MemorySystem(
        user_id=session_id,
        memory_dir=str(MEMORY_DIR),
        template_path=str(TEMPLATE_PATH)
    )
    
    # 创建 Agent（包含记忆工具集）
    memory_toolset = create_memory_toolset(
        memory_dir=str(MEMORY_DIR),
        id="memory"
    )
    
    agent = create_deep_agent(
        model="openai:gpt-4.1",
        toolsets=[memory_toolset],
    )
    
    # 创建 deps（可以添加 user_id 到 deps）
    deps = DeepAgentDeps(backend=StateBackend())
    # 如果 deps 支持，可以设置 user_id
    # deps.user_id = session_id  # 需要扩展 DeepAgentDeps
    
    # 运行 Agent
    result = await agent.run(
        user_message,
        deps=deps
    )
    
    # 对话结束后更新记忆
    memory_sys.increment_conversation_count()
    
    # 可以分析对话内容，提取重要信息
    # 例如：如果用户提到偏好，自动更新
    # if "喜欢" in user_message or "偏好" in user_message:
    #     memory_sys.learn_habit(extracted_habit, "工作习惯")
    
    return result


# ============================================
# 方式 4: 修改 UserSession 以包含记忆系统
# ============================================

from dataclasses import dataclass, field
from typing import Any

@dataclass
class UserSessionWithMemory:
    """带记忆系统的用户会话"""
    session_id: str
    deps: Any  # DeepAgentDeps
    message_history: list = field(default_factory=list)
    pending_approval_state: dict[str, Any] = field(default_factory=dict)
    memory: MemorySystem = field(init=False)
    
    def __post_init__(self):
        """初始化记忆系统"""
        self.memory = MemorySystem(
            user_id=self.session_id,
            memory_dir=str(MEMORY_DIR),
            template_path=str(TEMPLATE_PATH)
        )


async def get_or_create_session_with_memory(session_id: str) -> UserSessionWithMemory:
    """获取或创建带记忆的会话"""
    # ... 创建 deps 的逻辑 ...
    
    session = UserSessionWithMemory(
        session_id=session_id,
        deps=deps  # 你的 deps
    )
    
    return session


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    # 示例：独立使用记忆系统
    memory = MemorySystem(
        user_id="test_user",
        memory_dir="./memories"
    )
    
    # 读取记忆
    context = memory.get_context()
    print("记忆上下文：")
    print(context)
    
    # 更新记忆
    memory.add_todo("测试待办", priority="high")
    memory.update_preference("提醒方式", "默认提醒方式", "邮件")
    
    print("\n记忆已更新")
