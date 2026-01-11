"""
记忆系统工具函数模块

提供ID生成、时间处理、数据验证等工具函数。
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional


def generate_id(prefix: str) -> str:
    """生成唯一ID
    
    Args:
        prefix: ID前缀（如 "todo", "event", "reminder"）
    
    Returns:
        格式：{prefix}_{YYYYMMDD}_{HHMMSS}_{随机数}
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    random_suffix = str(random.randint(1000, 9999))
    return f"{prefix}_{timestamp}_{random_suffix}"


def parse_datetime(dt_str: str) -> datetime:
    """解析日期时间字符串
    
    Args:
        dt_str: ISO格式日期时间字符串（如 "2024-01-20T14:00:00"）
    
    Returns:
        datetime对象
    """
    # 支持多种格式
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"无法解析日期时间字符串: {dt_str}")


def format_datetime(dt: datetime) -> str:
    """格式化日期时间为ISO格式
    
    Args:
        dt: datetime对象
    
    Returns:
        ISO格式字符串（如 "2024-01-20T14:00:00"）
    """
    return dt.isoformat()


def parse_duration(duration_str: str) -> int:
    """解析时长字符串为分钟数
    
    Args:
        duration_str: 时长字符串（如 "30分钟", "1小时", "2小时30分钟", "半天"）
    
    Returns:
        总分钟数
    """
    duration_str = duration_str.strip()
    
    # 特殊处理
    if duration_str == "半天":
        return 240  # 4小时
    if duration_str == "一天":
        return 480  # 8小时
    
    total_minutes = 0
    
    # 提取小时数
    hour_match = None
    for pattern in [r"(\d+)\s*小时", r"(\d+)\s*h", r"(\d+)\s*hr"]:
        import re
        match = re.search(pattern, duration_str, re.IGNORECASE)
        if match:
            hour_match = match
            break
    
    if hour_match:
        total_minutes += int(hour_match.group(1)) * 60
    
    # 提取分钟数
    minute_match = None
    for pattern in [r"(\d+)\s*分钟", r"(\d+)\s*分", r"(\d+)\s*min"]:
        import re
        match = re.search(pattern, duration_str, re.IGNORECASE)
        if match:
            minute_match = match
            break
    
    if minute_match:
        total_minutes += int(minute_match.group(1))
    
    # 如果都没有匹配到，尝试解析纯数字（假设是分钟）
    if total_minutes == 0:
        import re
        numbers = re.findall(r'\d+', duration_str)
        if numbers:
            total_minutes = int(numbers[0])
    
    return total_minutes if total_minutes > 0 else 60  # 默认1小时


def format_duration(minutes: int) -> str:
    """格式化分钟数为可读字符串
    
    Args:
        minutes: 总分钟数
    
    Returns:
        可读字符串（如 "2小时30分钟"）
    """
    hours = minutes // 60
    mins = minutes % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if mins > 0:
        parts.append(f"{mins}分钟")
    
    return "".join(parts) if parts else "0分钟"


def calculate_remind_time(start_time: str, reminder_minutes: int) -> str:
    """计算提醒时间
    
    Args:
        start_time: 开始时间（ISO格式字符串）
        reminder_minutes: 提前多少分钟提醒
    
    Returns:
        提醒时间（ISO格式字符串）
    """
    dt = parse_datetime(start_time)
    remind_dt = dt - timedelta(minutes=reminder_minutes)
    return format_datetime(remind_dt)


def time_overlap(
    start1: str, end1: str,
    start2: str, end2: Optional[str] = None
) -> bool:
    """检查两个时间段是否重叠
    
    Args:
        start1: 第一个时间段的开始时间
        end1: 第一个时间段的结束时间
        start2: 第二个时间段的开始时间
        end2: 第二个时间段的结束时间（可选，如果不提供则假设为开始时间后1小时）
    
    Returns:
        如果重叠返回True，否则返回False
    """
    dt_start1 = parse_datetime(start1)
    dt_end1 = parse_datetime(end1)
    dt_start2 = parse_datetime(start2)
    
    if end2:
        dt_end2 = parse_datetime(end2)
    else:
        # 如果没有提供结束时间，假设为开始时间后1小时
        dt_end2 = dt_start2 + timedelta(hours=1)
    
    # 检查重叠：start1 < end2 and start2 < end1
    return dt_start1 < dt_end2 and dt_start2 < dt_end1


def get_current_time() -> str:
    """获取当前时间的ISO格式字符串"""
    return format_datetime(datetime.now())


def get_current_date() -> str:
    """获取当前日期的字符串（YYYY-MM-DD）"""
    return datetime.now().strftime("%Y-%m-%d")
