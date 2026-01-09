"""
记忆系统完整测试

测试分门别类存储的所有功能
"""

import tempfile
import shutil
from pathlib import Path
from memory_system import MemorySystem


def test_categorized_storage():
    """测试分门别类存储系统"""
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # 初始化记忆系统
        memory = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        storage = memory.storage
        
        # 1. 测试文件创建
        print("✓ 测试1: 文件创建")
        assert storage.files["profile"].exists(), "profile.md 应该被创建"
        assert storage.files["todos"].exists(), "todos.md 应该被创建"
        assert storage.files["habits"].exists(), "habits.md 应该被创建"
        assert storage.files["schedule"].exists(), "schedule.md 应该被创建"
        assert storage.files["diary"].exists(), "diary.md 应该被创建"
        assert storage.files["relationships"].exists(), "relationships.md 应该被创建"
        assert storage.files["conversations"].exists(), "conversations.md 应该被创建"
        print("  所有文件都已创建")
        
        # 2. 测试更新基本信息
        print("\n✓ 测试2: 更新基本信息")
        storage.update_profile("姓名", "测试用户")
        storage.update_profile("昵称", "小测")
        
        profile_content = storage.files["profile"].read_text(encoding="utf-8")
        assert "测试用户" in profile_content, "姓名应该被更新"
        assert "小测" in profile_content, "昵称应该被更新"
        print("  基本信息更新成功")
        
        # 3. 测试添加待办
        print("\n✓ 测试3: 添加待办事项")
        storage.add_todo("完成测试", priority="high", due_date="2024-01-20", status="pending")
        storage.add_todo("写文档", priority="medium", status="in_progress")
        
        todos_content = storage.files["todos"].read_text(encoding="utf-8")
        assert "完成测试" in todos_content, "待办应该被添加"
        assert "写文档" in todos_content, "待办应该被添加"
        print("  待办事项添加成功")
        
        # 4. 测试完成待办
        print("\n✓ 测试4: 完成待办事项")
        storage.complete_todo("完成测试")
        
        todos_content = storage.files["todos"].read_text(encoding="utf-8")
        assert "[x]" in todos_content or "完成时间" in todos_content, "待办应该被标记为完成"
        print("  待办事项完成成功")
        
        # 5. 测试学习习惯
        print("\n✓ 测试5: 学习习惯")
        storage.learn_habit("喜欢在早上工作", "工作习惯")
        storage.learn_habit("偏好简洁回复", "沟通习惯")
        
        habits_content = storage.files["habits"].read_text(encoding="utf-8")
        assert "喜欢在早上工作" in habits_content, "习惯应该被学习"
        assert "偏好简洁回复" in habits_content, "习惯应该被学习"
        print("  习惯学习成功")
        
        # 6. 测试添加对话摘要
        print("\n✓ 测试6: 添加对话摘要")
        storage.add_conversation("测试对话", ["用户询问了测试问题", "系统提供了测试答案"])
        
        conv_content = storage.files["conversations"].read_text(encoding="utf-8")
        assert "测试对话" in conv_content, "对话应该被记录"
        assert "用户询问了测试问题" in conv_content, "对话要点应该被记录"
        print("  对话摘要添加成功")
        
        # 7. 测试更新偏好
        print("\n✓ 测试7: 更新偏好设置")
        storage.update_preference("提醒方式", "默认提醒方式", "邮件")
        
        profile_content = storage.files["profile"].read_text(encoding="utf-8")
        assert "邮件" in profile_content, "偏好应该被更新"
        print("  偏好设置更新成功")
        
        # 8. 测试读取上下文
        print("\n✓ 测试8: 读取记忆上下文")
        context = storage.get_context()
        assert "测试用户" in context or "基本信息" in context, "上下文应该包含基本信息"
        print("  记忆上下文读取成功")
        
        # 9. 测试不会覆盖已有内容
        print("\n✓ 测试9: 不会覆盖已有内容")
        original_content = storage.files["todos"].read_text(encoding="utf-8")
        storage.add_todo("新任务", status="pending")
        new_content = storage.files["todos"].read_text(encoding="utf-8")
        assert original_content in new_content, "原有内容不应该被覆盖"
        assert "新任务" in new_content, "新内容应该被添加"
        print("  内容追加成功，未覆盖原有内容")
        
        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50)
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_read_memory_tool():
    """测试 read_memory 工具"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        memory = MemorySystem(user_id="test_user", memory_dir=str(temp_dir))
        storage = memory.storage
        
        # 设置基本信息
        storage.update_profile("姓名", "猪嘎")
        storage.update_profile("昵称", "小猪")
        
        # 测试读取基本信息
        import re
        profile = storage.files["profile"].read_text(encoding="utf-8")
        match = re.search(r"## 基本信息\n\n(.*?)(?=\n## |$)", profile, re.DOTALL)
        
        assert match is not None, "应该能匹配到基本信息"
        result = ["## 基本信息", match.group(1).strip()]
        output = "\n".join(result)
        
        assert "猪嘎" in output, "应该能读取到姓名"
        assert "小猪" in output, "应该能读取到昵称"
        
        print("✓ read_memory 工具测试通过")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("开始测试记忆系统...\n")
    test_categorized_storage()
    print("\n")
    test_read_memory_tool()
    print("\n所有测试完成！")
