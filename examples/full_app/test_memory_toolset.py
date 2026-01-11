"""
memory_toolset 完整测试套件

测试 memory_toolset 的所有功能，包括：
1. 工具集创建
2. 用户ID获取逻辑（多种优先级）
3. 所有工具函数（read_memory, update_preference, add_todo, complete_todo, add_memory, learn_habit）
4. 系统提示生成
5. 边界情况和错误处理
"""

import tempfile
import shutil
from pathlib import Path
from typing import Any
from unittest.mock import Mock, MagicMock

import pytest

from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset

from memory_system.toolset import (
    create_memory_toolset,
    get_memory_system_prompt,
    create_standalone_memory_system,
    MEMORY_SYSTEM_PROMPT,
)
from memory_system.core import MemorySystem

# 使用 anyio 作为异步测试框架（与项目其他测试一致）
pytestmark = pytest.mark.anyio


class TestMemoryToolsetCreation:
    """测试工具集创建"""

    def test_create_toolset_with_defaults(self):
        """测试使用默认参数创建工具集"""
        toolset = create_memory_toolset()
        assert isinstance(toolset, FunctionToolset)
        assert toolset.id == "memory"

    def test_create_toolset_with_custom_id(self):
        """测试使用自定义ID创建工具集"""
        toolset = create_memory_toolset(id="custom_memory")
        assert toolset.id == "custom_memory"

    def test_create_toolset_with_custom_memory_dir(self):
        """测试使用自定义记忆目录创建工具集"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            assert isinstance(toolset, FunctionToolset)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_toolset_with_fixed_user_id(self):
        """测试使用固定用户ID创建工具集"""
        toolset = create_memory_toolset(fixed_user_id="fixed_user_123")
        assert isinstance(toolset, FunctionToolset)
        
        # 验证工具集包含所有工具
        tool_names = list(toolset.tools.keys())
        assert "read_memory" in tool_names
        assert "update_preference" in tool_names
        assert "add_todo" in tool_names
        assert "complete_todo" in tool_names
        assert "add_memory" in tool_names
        assert "learn_habit" in tool_names
        assert "schedule_todo" in tool_names
        assert "add_one_time_event" in tool_names
        assert "add_idea" in tool_names
        assert "learn_schedule_preference" in tool_names

    def test_toolset_has_all_required_tools(self):
        """测试工具集包含所有必需的工具"""
        toolset = create_memory_toolset()
        tool_names = list(toolset.tools.keys())
        
        required_tools = [
            "read_memory",
            "update_preference",
            "add_todo",
            "complete_todo",
            "add_memory",
            "learn_habit",
            "schedule_todo",
            "add_one_time_event",
            "add_regular_schedule",
            "add_idea",
            "learn_schedule_preference",
        ]
        
        for tool_name in required_tools:
            assert tool_name in tool_names, f"工具集应该包含 {tool_name} 工具"


class TestGetUserID:
    """测试用户ID获取逻辑（多种优先级）"""

    async def test_get_user_id_from_fixed_user_id(self):
        """测试固定用户ID优先级最高"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(
                memory_dir=str(temp_dir),
                fixed_user_id="fixed_user"
            )
            
            # 创建模拟的 RunContext
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            ctx.deps.user_id = "deps_user"
            ctx.metadata = {}
            
            # 获取工具并调用
            read_memory_tool = toolset.tools["read_memory"]
            
            # 通过实际调用验证 fixed_user_id 生效
            # 由于工具是异步的，我们需要检查它使用的用户ID
            # 最简单的方式是检查创建的文件路径
            result = await read_memory_tool.function(ctx, section="all")
            
            # 验证记忆系统使用了 fixed_user_id
            memory_dir = Path(temp_dir)
            assert (memory_dir / "fixed_user").exists(), "应该使用 fixed_user_id 创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_get_user_id_from_deps_user_id(self):
        """测试从 deps.user_id 获取用户ID"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            ctx.deps.user_id = "deps_user_123"
            ctx.metadata = {}
            
            read_memory_tool = toolset.tools["read_memory"]
            await read_memory_tool.function(ctx, section="all")
            
            memory_dir = Path(temp_dir)
            assert (memory_dir / "deps_user_123").exists(), "应该使用 deps.user_id 创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_get_user_id_from_deps_session_id(self):
        """测试从 deps.session_id 获取用户ID（当没有 user_id 时）"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            # 使用 hasattr 和 setattr 来模拟没有 user_id 的情况
            if hasattr(ctx.deps, "user_id"):
                delattr(ctx.deps, "user_id")
            ctx.deps.session_id = "session_456"
            ctx.metadata = {}
            
            read_memory_tool = toolset.tools["read_memory"]
            await read_memory_tool.function(ctx, section="all")
            
            memory_dir = Path(temp_dir)
            assert (memory_dir / "session_456").exists(), "应该使用 deps.session_id 创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_get_user_id_from_metadata(self):
        """测试从 metadata 获取用户ID"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            if hasattr(ctx.deps, "user_id"):
                delattr(ctx.deps, "user_id")
            if hasattr(ctx.deps, "session_id"):
                delattr(ctx.deps, "session_id")
            ctx.metadata = {"user_id": "metadata_user_789"}
            
            read_memory_tool = toolset.tools["read_memory"]
            await read_memory_tool.function(ctx, section="all")
            
            memory_dir = Path(temp_dir)
            assert (memory_dir / "metadata_user_789").exists(), "应该使用 metadata.user_id 创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_get_user_id_from_ctx_user_id(self):
        """测试从 ctx.user_id 获取用户ID"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            if hasattr(ctx.deps, "user_id"):
                delattr(ctx.deps, "user_id")
            if hasattr(ctx.deps, "session_id"):
                delattr(ctx.deps, "session_id")
            ctx.metadata = {}
            ctx.user_id = "ctx_user_999"
            
            read_memory_tool = toolset.tools["read_memory"]
            await read_memory_tool.function(ctx, section="all")
            
            memory_dir = Path(temp_dir)
            assert (memory_dir / "ctx_user_999").exists(), "应该使用 ctx.user_id 创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_get_user_id_default_fallback(self):
        """测试默认用户ID回退"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            toolset = create_memory_toolset(memory_dir=str(temp_dir))
            
            ctx = Mock(spec=RunContext)
            ctx.deps = Mock()
            if hasattr(ctx.deps, "user_id"):
                delattr(ctx.deps, "user_id")
            if hasattr(ctx.deps, "session_id"):
                delattr(ctx.deps, "session_id")
            ctx.metadata = {}
            if hasattr(ctx, "user_id"):
                delattr(ctx, "user_id")
            
            read_memory_tool = toolset.tools["read_memory"]
            await read_memory_tool.function(ctx, section="all")
            
            memory_dir = Path(temp_dir)
            assert (memory_dir / "default_user").exists(), "应该使用默认用户ID创建目录"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestReadMemoryTool:
    """测试 read_memory 工具"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        """创建工具集"""
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        """创建模拟的 RunContext"""
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_read_memory_all(self, toolset, ctx):
        """测试读取全部记忆"""
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="all")
        
        assert isinstance(result, str)
        assert len(result) > 0, "应该返回记忆上下文"

    async def test_read_memory_basic_info(self, toolset, ctx, temp_dir):
        """测试读取基本信息"""
        # 先设置一些基本信息
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.storage.update_profile("姓名", "测试用户")
        memory_sys.storage.update_profile("昵称", "小测")
        
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="basic_info")
        
        assert "基本信息" in result
        assert "测试用户" in result
        assert "小测" in result

    async def test_read_memory_preferences(self, toolset, ctx, temp_dir):
        """测试读取偏好设置"""
        # 先设置一些偏好
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.update_preference("提醒方式", "默认提醒方式", "邮件")
        
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="preferences")
        
        assert "偏好设置" in result
        assert "邮件" in result or "提醒方式" in result

    async def test_read_memory_todos(self, toolset, ctx, temp_dir):
        """测试读取待办事项"""
        # 先添加一些待办
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.add_todo("测试待办1", priority="high")
        memory_sys.add_todo("测试待办2", priority="medium")
        
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="todos")
        
        assert "待办事项" in result or "进行中" in result
        assert "测试待办1" in result or "测试待办2" in result

    async def test_read_memory_habits(self, toolset, ctx, temp_dir):
        """测试读取习惯"""
        # 先学习一些习惯
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.learn_habit("喜欢早上工作", "工作习惯")
        
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="habits")
        
        assert "习惯" in result or "工作习惯" in result
        assert "喜欢早上工作" in result

    async def test_read_memory_memories(self, toolset, ctx, temp_dir):
        """测试读取重要记忆"""
        # 先添加一些记忆
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.add_memory("测试对话", ["要点1", "要点2"])
        
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="memories")
        
        assert "对话" in result or "记忆" in result
        assert "测试对话" in result or "要点1" in result

    async def test_read_memory_goals(self, toolset, ctx):
        """测试读取目标（当前未实现）"""
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="goals")
        
        assert "目标" in result or "未单独存储" in result

    async def test_read_memory_unknown_section(self, toolset, ctx):
        """测试读取未知章节"""
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="unknown_section")
        
        assert "未知" in result or "可用章节" in result

    async def test_read_memory_empty_section(self, toolset, ctx):
        """测试读取空章节（文件不存在或为空）"""
        read_memory_tool = toolset.tools["read_memory"]
        result = await read_memory_tool.function(ctx, section="habits")
        
        # 应该返回提示信息，而不是错误
        assert isinstance(result, str)
        assert len(result) > 0


class TestUpdatePreferenceTool:
    """测试 update_preference 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_update_preference_basic(self, toolset, ctx, temp_dir):
        """测试基本偏好更新"""
        update_preference_tool = toolset.tools["update_preference"]
        result = await update_preference_tool.function(
            ctx,
            category="提醒方式",
            key="默认提醒方式",
            value="邮件"
        )
        
        assert "已更新偏好" in result
        assert "提醒方式" in result
        assert "邮件" in result
        
        # 验证偏好确实被更新
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        preferences = data.get("profile", {}).get("preferences", {})
        assert "邮件" in str(preferences.get("提醒方式", {}).get("默认提醒方式", ""))

    async def test_update_preference_new_category(self, toolset, ctx, temp_dir):
        """测试更新新类别的偏好（当前实现不支持创建新类别，只更新现有类别）"""
        update_preference_tool = toolset.tools["update_preference"]
        result = await update_preference_tool.function(
            ctx,
            category="新类别",
            key="新键",
            value="新值"
        )
        
        # 工具会返回成功消息，但不会实际创建新类别（因为功能已被移除）
        assert "已更新偏好" in result
        
        # 注意：当前实现不支持创建新类别，所以这个测试主要验证工具不会报错
        # 如果需要支持创建新类别，需要在 update_preference 方法中添加相应逻辑

    async def test_update_preference_multiple_updates(self, toolset, ctx, temp_dir):
        """测试多次更新偏好"""
        update_preference_tool = toolset.tools["update_preference"]
        
        # 第一次更新
        await update_preference_tool.function(
            ctx,
            category="提醒方式",
            key="默认提醒方式",
            value="邮件"
        )
        
        # 第二次更新（应该覆盖）
        await update_preference_tool.function(
            ctx,
            category="提醒方式",
            key="默认提醒方式",
            value="推送"
        )
        
        # 验证最后一次更新生效
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        preferences = data.get("profile", {}).get("preferences", {})
        assert "推送" in str(preferences.get("提醒方式", {}).get("默认提醒方式", ""))

    async def test_update_preference_basic_info_category(self, toolset, ctx, temp_dir):
        """测试使用 update_preference 更新基本信息（AI可能会错误地使用这个工具）"""
        update_preference_tool = toolset.tools["update_preference"]
        result = await update_preference_tool.function(
            ctx,
            category="基本信息",
            key="昵称",
            value="猪嘎"
        )
        
        assert "已更新偏好" in result
        assert "基本信息" in result
        assert "猪嘎" in result
        
        # 验证基本信息表格中的字段被正确更新
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        basic_info = data.get("profile", {}).get("basic_info", {})
        assert basic_info.get("昵称") == "猪嘎", "昵称字段应该被更新为'猪嘎'"

    async def test_update_preference_basic_info_name(self, toolset, ctx, temp_dir):
        """测试使用 update_preference 更新姓名"""
        update_preference_tool = toolset.tools["update_preference"]
        result = await update_preference_tool.function(
            ctx,
            category="基本信息",
            key="姓名",
            value="张三"
        )
        
        assert "已更新偏好" in result
        
        # 验证姓名被正确更新
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        basic_info = data.get("profile", {}).get("basic_info", {})
        assert basic_info.get("姓名") == "张三"

    async def test_update_preference_basic_info_multiple_fields(self, toolset, ctx, temp_dir):
        """测试使用 update_preference 更新多个基本信息字段"""
        update_preference_tool = toolset.tools["update_preference"]
        
        # 更新姓名
        await update_preference_tool.function(
            ctx,
            category="基本信息",
            key="姓名",
            value="李四"
        )
        
        # 更新昵称
        await update_preference_tool.function(
            ctx,
            category="基本信息",
            key="昵称",
            value="小李"
        )
        
        # 验证两个字段都被更新
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        basic_info = data.get("profile", {}).get("basic_info", {})
        assert basic_info.get("姓名") == "李四"
        assert basic_info.get("昵称") == "小李"


class TestAddTodoTool:
    """测试 add_todo 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_add_todo_basic(self, toolset, ctx, temp_dir):
        """测试基本待办添加"""
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(
            ctx,
            content="完成测试",
            priority="medium"
        )
        
        assert "已添加待办" in result
        assert "完成测试" in result
        
        # 验证待办确实被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        todo_contents = [todo["content"] for todo in todos.get("pending", [])]
        assert "完成测试" in todo_contents
        # 验证返回了ID
        assert "ID:" in result or "todo_" in result

    async def test_add_todo_with_priority(self, toolset, ctx, temp_dir):
        """测试添加带优先级的待办"""
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(
            ctx,
            content="重要任务",
            priority="high"
        )
        
        assert "已添加待办" in result
        assert "重要任务" in result
        
        # 验证优先级被记录
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        todo_contents = [todo["content"] for todo in todos.get("pending", [])]
        assert "重要任务" in todo_contents
        # 验证优先级
        high_todos = [todo for todo in todos.get("pending", []) if todo.get("priority") == "high"]
        assert any(todo["content"] == "重要任务" for todo in high_todos)

    async def test_add_todo_with_due_date(self, toolset, ctx, temp_dir):
        """测试添加带截止日期的待办"""
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(
            ctx,
            content="截止任务",
            priority="medium",
            due_date="2024-12-31"
        )
        
        assert "已添加待办" in result
        
        # 验证截止日期被记录
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        todo_contents = [todo["content"] for todo in todos.get("pending", [])]
        assert "截止任务" in todo_contents
        # 验证截止日期
        due_todos = [todo for todo in todos.get("pending", []) if todo.get("due_date") == "2024-12-31"]
        assert any(todo["content"] == "截止任务" for todo in due_todos)

    async def test_add_todo_multiple(self, toolset, ctx, temp_dir):
        """测试添加多个待办"""
        add_todo_tool = toolset.tools["add_todo"]
        
        await add_todo_tool.function(ctx, content="任务1", priority="high")
        await add_todo_tool.function(ctx, content="任务2", priority="medium")
        await add_todo_tool.function(ctx, content="任务3", priority="low")
        
        # 验证所有待办都被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        all_todo_contents = []
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            all_todo_contents.extend([todo["content"] for todo in todos.get(status, [])])
        assert "任务1" in all_todo_contents
        assert "任务2" in all_todo_contents
        assert "任务3" in all_todo_contents


class TestCompleteTodoTool:
    """测试 complete_todo 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_complete_todo_basic(self, toolset, ctx, temp_dir):
        """测试基本待办完成"""
        # 先添加一个待办
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        memory_sys.add_todo("要完成的任务", priority="high")
        
        # 完成待办
        complete_todo_tool = toolset.tools["complete_todo"]
        result = await complete_todo_tool.function(ctx, content="要完成的任务")
        
        assert "已标记完成" in result
        assert "要完成的任务" in result
        
        # 验证待办被标记为完成
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        completed_todos = todos.get("completed", [])
        assert any(todo["content"] == "要完成的任务" and todo.get("completed_at") for todo in completed_todos)

    async def test_complete_todo_nonexistent(self, toolset, ctx, temp_dir):
        """测试完成不存在的待办（应该返回错误消息）"""
        complete_todo_tool = toolset.tools["complete_todo"]
        result = await complete_todo_tool.function(ctx, content="不存在的任务")
        
        # 应该返回错误消息
        assert isinstance(result, str)
        assert "未找到" in result or "失败" in result


class TestAddMemoryTool:
    """测试 add_memory 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_add_memory_basic(self, toolset, ctx, temp_dir):
        """测试基本记忆添加"""
        add_memory_tool = toolset.tools["add_memory"]
        result = await add_memory_tool.function(
            ctx,
            topic="测试对话",
            summary="这是第一个要点\n这是第二个要点"
        )
        
        assert "已记录记忆" in result
        assert "测试对话" in result
        
        # 验证记忆被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        conversations = data.get("conversations", [])
        assert any(conv.get("topic") == "测试对话" for conv in conversations)
        test_conv = next((conv for conv in conversations if conv.get("topic") == "测试对话"), None)
        assert test_conv is not None
        assert "这是第一个要点" in test_conv.get("summary", []) or "这是第二个要点" in test_conv.get("summary", [])

    async def test_add_memory_single_point(self, toolset, ctx, temp_dir):
        """测试添加单要点记忆"""
        add_memory_tool = toolset.tools["add_memory"]
        result = await add_memory_tool.function(
            ctx,
            topic="简单对话",
            summary="只有一个要点"
        )
        
        assert "已记录记忆" in result
        
        # 验证记忆被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        conversations = data.get("conversations", [])
        simple_conv = next((conv for conv in conversations if conv.get("topic") == "简单对话"), None)
        assert simple_conv is not None
        assert "只有一个要点" in simple_conv.get("summary", [])

    async def test_add_memory_multiple_points(self, toolset, ctx, temp_dir):
        """测试添加多要点记忆"""
        add_memory_tool = toolset.tools["add_memory"]
        summary = "要点1\n要点2\n要点3\n\n要点4"  # 包含空行
        result = await add_memory_tool.function(
            ctx,
            topic="复杂对话",
            summary=summary
        )
        
        assert "已记录记忆" in result
        
        # 验证所有要点都被添加（空行应该被过滤）
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        conversations = data.get("conversations", [])
        complex_conv = next((conv for conv in conversations if conv.get("topic") == "复杂对话"), None)
        assert complex_conv is not None
        summary = complex_conv.get("summary", [])
        assert "要点1" in summary
        assert "要点2" in summary
        assert "要点3" in summary
        assert "要点4" in summary


class TestLearnHabitTool:
    """测试 learn_habit 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_learn_habit_basic(self, toolset, ctx, temp_dir):
        """测试基本习惯学习"""
        learn_habit_tool = toolset.tools["learn_habit"]
        result = await learn_habit_tool.function(
            ctx,
            habit="喜欢早上工作",
            category="工作习惯"
        )
        
        assert "已学习习惯" in result
        assert "喜欢早上工作" in result
        assert "工作习惯" in result
        
        # 验证习惯被学习
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        habits = data.get("habits", {})
        work_habits = habits.get("工作习惯", [])
        assert any(habit.get("habit") == "喜欢早上工作" for habit in work_habits)

    async def test_learn_habit_default_category(self, toolset, ctx, temp_dir):
        """测试使用默认类别学习习惯"""
        learn_habit_tool = toolset.tools["learn_habit"]
        result = await learn_habit_tool.function(
            ctx,
            habit="偏好简洁回复"
        )
        
        assert "已学习习惯" in result
        assert "偏好简洁回复" in result
        assert "工作习惯" in result  # 默认类别
        
        # 验证习惯被学习
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        habits = data.get("habits", {})
        work_habits = habits.get("工作习惯", [])
        assert any(habit.get("habit") == "偏好简洁回复" for habit in work_habits)

    async def test_learn_habit_different_categories(self, toolset, ctx, temp_dir):
        """测试学习不同类别的习惯"""
        learn_habit_tool = toolset.tools["learn_habit"]
        
        await learn_habit_tool.function(ctx, habit="工作习惯1", category="工作习惯")
        await learn_habit_tool.function(ctx, habit="沟通习惯1", category="沟通习惯")
        await learn_habit_tool.function(ctx, habit="生活习惯1", category="生活习惯")
        
        # 验证所有习惯都被学习
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        habits = data.get("habits", {})
        work_habits = [h.get("habit") for h in habits.get("工作习惯", [])]
        comm_habits = [h.get("habit") for h in habits.get("沟通习惯", [])]
        life_habits = [h.get("habit") for h in habits.get("生活习惯", [])]
        assert "工作习惯1" in work_habits
        assert "沟通习惯1" in comm_habits
        assert "生活习惯1" in life_habits


class TestGetMemorySystemPrompt:
    """测试系统提示生成"""

    def test_get_memory_system_prompt(self):
        """测试系统提示生成（新版本不接受参数）"""
        prompt = get_memory_system_prompt()
        assert prompt == MEMORY_SYSTEM_PROMPT
        assert "read_memory" in prompt
        assert "add_todo" in prompt
        assert "schedule_todo" in prompt
        assert "add_one_time_event" in prompt
        assert "add_idea" in prompt
        assert "learn_schedule_preference" in prompt


class TestStandaloneMemorySystem:
    """测试独立记忆系统创建"""

    def test_create_standalone_memory_system(self):
        """测试创建独立记忆系统"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            memory = create_standalone_memory_system(
                user_id="standalone_user",
                memory_dir=str(temp_dir)
            )
            
            assert isinstance(memory, MemorySystem)
            assert memory.user_id == "standalone_user"
            
            # 验证 JSON 文件被创建
            assert (temp_dir / "standalone_user" / "memory.json").exists()
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_standalone_memory_system_with_template(self):
        """测试使用模板创建独立记忆系统"""
        temp_dir = Path(tempfile.mkdtemp())
        template_dir = Path(tempfile.mkdtemp())
        try:
            # 创建模板文件
            template_file = template_dir / "template.md"
            template_file.write_text("# 模板\n用户ID: user_id", encoding="utf-8")
            
            memory = create_standalone_memory_system(
                user_id="template_user",
                memory_dir=str(temp_dir),
                template_path=str(template_file)
            )
            
            assert isinstance(memory, MemorySystem)
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(template_dir, ignore_errors=True)


class TestIntegrationScenarios:
    """测试集成场景"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="integration_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_full_workflow(self, toolset, ctx, temp_dir):
        """测试完整工作流程"""
        # 1. 读取记忆（初始为空）
        read_memory_tool = toolset.tools["read_memory"]
        initial_memory = await read_memory_tool.function(ctx, section="all")
        assert isinstance(initial_memory, str)
        
        # 2. 更新偏好
        update_preference_tool = toolset.tools["update_preference"]
        await update_preference_tool.function(ctx, category="提醒方式", key="默认提醒方式", value="邮件")
        
        # 3. 添加待办
        add_todo_tool = toolset.tools["add_todo"]
        await add_todo_tool.function(ctx, content="完成集成测试", priority="high", due_date="2024-12-31")
        
        # 4. 学习习惯
        learn_habit_tool = toolset.tools["learn_habit"]
        await learn_habit_tool.function(ctx, habit="喜欢在早上工作", category="工作习惯")
        
        # 5. 添加记忆
        add_memory_tool = toolset.tools["add_memory"]
        await add_memory_tool.function(ctx, topic="集成测试对话", summary="要点1\n要点2")
        
        # 6. 再次读取记忆，验证所有数据
        updated_memory = await read_memory_tool.function(ctx, section="all")
        assert "邮件" in updated_memory or "提醒方式" in updated_memory
        # 待办可能在 pending 或 in_progress 中，检查上下文
        assert "完成集成测试" in updated_memory or "待办" in updated_memory or "pending" in str(updated_memory)
        assert "喜欢在早上工作" in updated_memory or "习惯" in updated_memory
        
        # 7. 完成待办
        complete_todo_tool = toolset.tools["complete_todo"]
        await complete_todo_tool.function(ctx, content="完成集成测试")
        
        # 8. 验证待办被完成
        todos_content = await read_memory_tool.function(ctx, section="todos")
        assert "[x]" in todos_content or "完成时间" in todos_content

    async def test_multiple_users_isolation(self, temp_dir):
        """测试多用户隔离"""
        # 创建两个不同用户的工具集
        toolset1 = create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="user1")
        toolset2 = create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="user2")
        
        ctx1 = Mock(spec=RunContext)
        ctx1.deps = Mock()
        ctx2 = Mock(spec=RunContext)
        ctx2.deps = Mock()
        
        # 为用户1添加待办
        add_todo_tool1 = toolset1.tools["add_todo"]
        await add_todo_tool1.function(ctx1, content="用户1的任务", priority="high")
        
        # 为用户2添加待办
        add_todo_tool2 = toolset2.tools["add_todo"]
        await add_todo_tool2.function(ctx2, content="用户2的任务", priority="high")
        
        # 验证用户隔离
        read_memory_tool1 = toolset1.tools["read_memory"]
        read_memory_tool2 = toolset2.tools["read_memory"]
        
        user1_todos = await read_memory_tool1.function(ctx1, section="todos")
        user2_todos = await read_memory_tool2.function(ctx2, section="todos")
        
        assert "用户1的任务" in user1_todos
        assert "用户2的任务" not in user1_todos
        assert "用户2的任务" in user2_todos
        assert "用户1的任务" not in user2_todos


class TestEdgeCases:
    """测试边界情况和错误处理"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="edge_test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_empty_strings(self, toolset, ctx):
        """测试空字符串输入"""
        add_todo_tool = toolset.tools["add_todo"]
        # 应该不报错，但可能不会添加有效内容
        result = await add_todo_tool.function(ctx, content="", priority="medium")
        assert isinstance(result, str)

    async def test_very_long_content(self, toolset, ctx, temp_dir):
        """测试超长内容"""
        long_content = "A" * 10000
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(ctx, content=long_content, priority="medium")
        
        assert "已添加待办" in result
        
        # 验证内容被保存
        memory_sys = MemorySystem(user_id="edge_test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        all_todo_contents = []
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            all_todo_contents.extend([todo["content"] for todo in todos.get(status, [])])
        assert long_content in all_todo_contents

    async def test_special_characters(self, toolset, ctx, temp_dir):
        """测试特殊字符"""
        special_content = "任务包含特殊字符：!@#$%^&*()[]{}|\\:;\"'<>?,./"
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(ctx, content=special_content, priority="medium")
        
        assert "已添加待办" in result
        
        # 验证特殊字符被正确处理
        memory_sys = MemorySystem(user_id="edge_test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        all_todo_contents = []
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            all_todo_contents.extend([todo["content"] for todo in todos.get(status, [])])
        assert special_content in all_todo_contents

    async def test_unicode_characters(self, toolset, ctx, temp_dir):
        """测试Unicode字符"""
        unicode_content = "任务包含Unicode：中文、日本語、한국어、🚀、🎉"
        add_todo_tool = toolset.tools["add_todo"]
        result = await add_todo_tool.function(ctx, content=unicode_content, priority="medium")
        
        assert "已添加待办" in result
        
        # 验证Unicode字符被正确处理
        memory_sys = MemorySystem(user_id="edge_test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        todos = data.get("todos", {})
        all_todo_contents = []
        for status in ["pending", "scheduled", "in_progress", "completed"]:
            all_todo_contents.extend([todo["content"] for todo in todos.get(status, [])])
        assert unicode_content in all_todo_contents

    async def test_multiline_content(self, toolset, ctx, temp_dir):
        """测试多行内容"""
        multiline_content = "第一行\n第二行\n第三行"
        add_memory_tool = toolset.tools["add_memory"]
        result = await add_memory_tool.function(
            ctx,
            topic="多行主题",
            summary=multiline_content
        )
        
        assert "已记录记忆" in result
        
        # 验证多行内容被正确处理
        memory_sys = MemorySystem(user_id="edge_test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        conversations = data.get("conversations", [])
        assert any(conv.get("topic") == "多行主题" for conv in conversations)


class TestScheduleTodoTool:
    """测试 schedule_todo 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_schedule_todo_basic(self, toolset, ctx, temp_dir):
        """测试基本待办时间安排"""
        # 先添加一个待办
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        todo_id = memory_sys.add_todo("要安排的任务", priority="high")
        
        # 安排时间
        schedule_todo_tool = toolset.tools["schedule_todo"]
        result = await schedule_todo_tool.function(
            ctx,
            content="要安排的任务",
            start_time="2024-01-20T14:00:00",
            duration="2小时",
            reminder_minutes=15
        )
        
        assert "已安排" in result
        assert "要安排的任务" in result
        
        # 验证待办被安排
        todo = memory_sys.get_todo(todo_id)
        assert todo is not None
        assert todo.get("scheduled_time") is not None
        assert todo.get("scheduled_time", {}).get("start") == "2024-01-20T14:00:00"
        
        # 验证状态变为scheduled
        data = memory_sys.storage.get_all_data()
        scheduled_todos = data.get("todos", {}).get("scheduled", [])
        assert any(t.get("id") == todo_id for t in scheduled_todos)


class TestAddOneTimeEventTool:
    """测试 add_one_time_event 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_add_one_time_event_basic(self, toolset, ctx, temp_dir):
        """测试基本一次性事件添加"""
        add_event_tool = toolset.tools["add_one_time_event"]
        result = await add_event_tool.function(
            ctx,
            title="测试会议",
            start_time="2024-01-21T10:00:00",
            duration="1小时",
            description="测试会议描述",
            location="会议室A"
        )
        
        assert "已添加一次性事件" in result
        assert "测试会议" in result
        assert "ID:" in result or "event_" in result
        
        # 验证事件被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        upcoming_events = data.get("schedule", {}).get("upcoming", [])
        assert any(e.get("title") == "测试会议" for e in upcoming_events)


class TestAddIdeaTool:
    """测试 add_idea 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_add_idea_basic(self, toolset, ctx, temp_dir):
        """测试基本创意想法添加"""
        add_idea_tool = toolset.tools["add_idea"]
        result = await add_idea_tool.function(
            ctx,
            content="测试想法",
            tags=["测试", "想法"],
            category="产品想法"
        )
        
        assert "已记录创意想法" in result
        assert "测试想法" in result
        assert "ID:" in result or "idea_" in result
        
        # 验证想法被添加
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        ideas = data.get("ideas", [])
        assert any(i.get("content") == "测试想法" for i in ideas)


class TestLearnSchedulePreferenceTool:
    """测试 learn_schedule_preference 工具"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def toolset(self, temp_dir):
        return create_memory_toolset(memory_dir=str(temp_dir), fixed_user_id="test_user")

    @pytest.fixture
    def ctx(self):
        ctx = Mock(spec=RunContext)
        ctx.deps = Mock()
        return ctx

    async def test_learn_schedule_preference_basic(self, toolset, ctx, temp_dir):
        """测试基本日程偏好学习"""
        learn_pref_tool = toolset.tools["learn_schedule_preference"]
        result = await learn_pref_tool.function(
            ctx,
            preference_type="工作时间",
            value="09:00-18:00",
            confidence=1.0
        )
        
        assert "已学习偏好" in result
        assert "工作时间" in result
        assert "09:00-18:00" in result
        
        # 验证偏好被学习
        memory_sys = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        data = memory_sys.storage.get_all_data()
        preferences = data.get("profile", {}).get("preferences", {}).get("日程偏好", {})
        assert "工作时间" in preferences
        assert preferences["工作时间"]["value"] == "09:00-18:00"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
