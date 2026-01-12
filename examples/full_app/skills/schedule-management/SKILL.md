---
name: schedule-management
description: Expert schedule management and display skill for viewing and organizing user's calendar and schedule
tags:
  - schedule
  - calendar
  - time-management
  - productivity
version: "1.0"
author: pydantic-deep
---

# Schedule Management Skill

You are a schedule management expert. When this skill is loaded, you help users view, understand, and manage their schedules effectively.

## When to Use This Skill

Load this skill when users ask about:
- "最近的日程安排" (recent schedule)
- "我今天的日程" (today's schedule)
- "这周的安排" (this week's schedule)
- "我有什么安排" (what's scheduled)
- "查看我的日程" (view my schedule)
- "日程表" (schedule/calendar)
- Any questions about upcoming events, regular schedules, or time management

## Core Workflow

1. **Read Schedule Data**: Use `read_memory(section="schedule")` to get user's schedule
2. **Parse and Understand**: Analyze the schedule structure (regular vs upcoming events)
3. **Format for Display**: Present schedule in a clear, organized format
4. **Provide Insights**: Highlight important events, conflicts, or recommendations

## Schedule Data Structure

The schedule data from `read_memory(section="schedule")` contains:

### Regular Schedules (定期日程)
- Recurring events that happen on a regular basis
- Format: `{title, time, frequency, description}`
- Frequency types: "每天", "工作日", "每周一", "每周五", "每月1号", etc.

### Upcoming Events (即将到来的事件)
- One-time events with specific dates/times
- Format: `{title, start_time, end_time, description, location}`
- Includes both future events and today's events

## Display Formats

**IMPORTANT**: Always use professional calendar table formats for displaying schedules. This is the preferred and most professional way to present schedule information.

### Format 1: Calendar Table View (日历表格视图) - **PRIMARY FORMAT**

This is the **recommended format** for all schedule displays. Use calendar tables for professional presentation.

#### Weekly Calendar Table (周历表格)

```python
from datetime import datetime, timedelta

# Read schedule data
schedule_data = read_memory(section="schedule")

# Get current week dates
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

# Format as calendar table
print("## 📅 本周日程安排")
print("")
print("| 日期 | 时间 | 事件 | 类型 | 地点 |")
print("|------|------|------|------|------|")

# Add regular schedules (apply to appropriate days)
for schedule in regular_schedules:
    frequency = schedule.get('frequency', '')
    time = schedule.get('time', '')
    title = schedule.get('title', '')
    
    # Determine which days this applies to
    if '每天' in frequency or 'daily' in frequency.lower():
        for i, date in enumerate(week_dates):
            date_str = date.strftime("%m-%d")
            print(f"| {date_str} ({weekday_names[i]}) | {time} | **{title}** | 定期 | - |")
    elif '工作日' in frequency or 'weekdays' in frequency.lower():
        for i in range(5):  # Monday to Friday
            date_str = week_dates[i].strftime("%m-%d")
            print(f"| {date_str} ({weekday_names[i]}) | {time} | **{title}** | 定期 | - |")
    # Add more frequency handling as needed

# Add upcoming events
for event in upcoming_events:
    start_time = event.get('start_time', '')
    # Parse date from start_time
    event_date = datetime.strptime(start_time.split()[0], "%Y-%m-%d")
    
    # Check if event is in current week
    if start_of_week <= event_date < start_of_week + timedelta(days=7):
        date_str = event_date.strftime("%m-%d")
        weekday = weekday_names[event_date.weekday()]
        time_str = start_time.split()[1] if ' ' in start_time else start_time
        if event.get('end_time'):
            time_str += f" - {event['end_time'].split()[1] if ' ' in event['end_time'] else event['end_time']}"
        
        location = event.get('location', '-')
        print(f"| {date_str} ({weekday}) | {time_str} | **{event['title']}** | 事件 | {location} |")

print("")
```

#### Monthly Calendar Table (月历表格)

```python
from datetime import datetime, timedelta
from calendar import monthrange

# Get current month
today = datetime.now()
year = today.year
month = today.month
days_in_month = monthrange(year, month)[1]

# Create monthly calendar table
print("## 📅 本月日程安排")
print("")
print("| 日期 | 时间 | 事件 | 类型 | 地点 | 备注 |")
print("|------|------|------|------|------|------|")

# Group events by date
events_by_date = {}

# Add regular schedules
for schedule in regular_schedules:
    time = schedule.get('time', '')
    title = schedule.get('title', '')
    frequency = schedule.get('frequency', '')
    description = schedule.get('description', '')
    
    # Apply to appropriate dates based on frequency
    if '每天' in frequency:
        for day in range(1, days_in_month + 1):
            date_key = f"{year}-{month:02d}-{day:02d}"
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append({
                'time': time,
                'title': title,
                'type': '定期',
                'location': '-',
                'description': description
            })

# Add upcoming events
for event in upcoming_events:
    start_time = event.get('start_time', '')
    event_date = start_time.split()[0] if ' ' in start_time else start_time
    
    if event_date not in events_by_date:
        events_by_date[event_date] = []
    
    time_str = start_time.split()[1] if ' ' in start_time else ''
    if event.get('end_time'):
        end_time_str = event['end_time'].split()[1] if ' ' in event['end_time'] else event['end_time']
        time_str += f" - {end_time_str}"
    
    events_by_date[event_date].append({
        'time': time_str,
        'title': event.get('title', ''),
        'type': '事件',
        'location': event.get('location', '-'),
        'description': event.get('description', '')
    })

# Display sorted by date
for date_key in sorted(events_by_date.keys()):
    date_obj = datetime.strptime(date_key, "%Y-%m-%d")
    date_str = date_obj.strftime("%m-%d")
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
    
    for event_info in events_by_date[date_key]:
        print(f"| {date_str} ({weekday}) | {event_info['time']} | **{event_info['title']}** | {event_info['type']} | {event_info['location']} | {event_info['description']} |")

print("")
```

#### Today's Schedule Table (今日日程表格)

```python
from datetime import datetime

# Read schedule data
schedule_data = read_memory(section="schedule")

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]

print("## 📅 今天的日程安排")
print("")
print(f"**日期**: {today.strftime('%Y年%m月%d日')} ({weekday})")
print("")
print("| 时间 | 事件 | 类型 | 地点 | 备注 |")
print("|------|------|------|------|------|")

# Add regular schedules for today
for schedule in regular_schedules:
    frequency = schedule.get('frequency', '')
    # Check if this schedule applies today
    applies_today = False
    if '每天' in frequency:
        applies_today = True
    elif '工作日' in frequency and today.weekday() < 5:
        applies_today = True
    # Add more frequency checks as needed
    
    if applies_today:
        time = schedule.get('time', '')
        title = schedule.get('title', '')
        description = schedule.get('description', '')
        print(f"| {time} | **{title}** | 定期 | - | {description} |")

# Add today's events
for event in upcoming_events:
    start_time = event.get('start_time', '')
    event_date = start_time.split()[0] if ' ' in start_time else start_time
    
    if event_date == today_str:
        time_str = start_time.split()[1] if ' ' in start_time else start_time
        if event.get('end_time'):
            end_time_str = event['end_time'].split()[1] if ' ' in event['end_time'] else event['end_time']
            time_str += f" - {end_time_str}"
        
        title = event.get('title', '')
        location = event.get('location', '-')
        description = event.get('description', '')
        print(f"| {time_str} | **{title}** | 事件 | {location} | {description} |")

print("")
```

### Format 2: Upcoming Events Table (即将到来的事件表格)

For showing upcoming events in a clean table format:

```python
from datetime import datetime

# Read schedule data
schedule_data = read_memory(section="schedule")

print("## 📅 即将到来的事件")
print("")
print("| 日期 | 时间 | 事件 | 地点 | 备注 |")
print("|------|------|------|------|------|")

# Sort events by start_time
sorted_events = sorted(upcoming_events, key=lambda x: x.get('start_time', ''))

# Show next 10 events
for event in sorted_events[:10]:
    start_time = event.get('start_time', '')
    if ' ' in start_time:
        date_str = start_time.split()[0]
        time_str = start_time.split()[1]
    else:
        date_str = start_time
        time_str = ''
    
    if event.get('end_time'):
        end_time = event['end_time'].split()[1] if ' ' in event['end_time'] else event['end_time']
        time_str += f" - {end_time}"
    
    # Format date for display
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_display = date_obj.strftime("%m-%d")
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        date_display += f" ({weekday})"
    except:
        date_display = date_str
    
    title = event.get('title', '')
    location = event.get('location', '-')
    description = event.get('description', '')
    
    print(f"| {date_display} | {time_str} | **{title}** | {location} | {description} |")

print("")
```

### Format 3: Regular Schedules Table (定期日程表格)

For displaying recurring schedules:

```python
# Read schedule data
schedule_data = read_memory(section="schedule")

print("## 📅 定期日程")
print("")
print("| 时间 | 事件 | 频率 | 备注 |")
print("|------|------|------|------|")

for schedule in regular_schedules:
    time = schedule.get('time', '')
    title = schedule.get('title', '')
    frequency = schedule.get('frequency', '')
    description = schedule.get('description', '')
    
    print(f"| {time} | **{title}** | {frequency} | {description} |")

print("")
```

### Format 4: Summary Table (摘要表格)

For quick overview:

```python
print("## 📅 日程摘要")
print("")
print("| 类型 | 数量 | 说明 |")
print("|------|------|------|")
print(f"| 定期日程 | {len(regular_schedules)} | 重复性日程安排 |")
print(f"| 即将到来的事件 | {len(upcoming_events)} | 一次性事件 |")
print("")
print("### 最近3个事件")
print("")
print("| 日期 | 时间 | 事件 |")
print("|------|------|------|")
for event in sorted(upcoming_events, key=lambda x: x.get('start_time', ''))[:3]:
    start_time = event.get('start_time', '')
    date_str = start_time.split()[0] if ' ' in start_time else start_time
    time_str = start_time.split()[1] if ' ' in start_time else ''
    print(f"| {date_str} | {time_str} | {event.get('title', '')} |")
```

## Best Practices

### 1. **ALWAYS Use Calendar Tables** (最重要)

**CRITICAL**: Always display schedules in professional calendar table format. This is the standard and most professional way to present schedule information.

- ✅ **DO**: Use Markdown tables with columns: 日期, 时间, 事件, 类型, 地点, 备注
- ❌ **DON'T**: Use bullet lists or plain text for schedule display

### 2. Always Read Schedule First

```python
# Always start by reading schedule data
schedule_data = read_memory(section="schedule")
```

### 3. Handle Empty Schedules Gracefully

```python
if not regular_schedules and not upcoming_events:
    print("## 📅 日程安排")
    print("")
    print("| 状态 | 说明 |")
    print("|------|------|")
    print("| 暂无日程 | 您目前没有日程安排。需要我帮您添加一些日程吗？ |")
    return
```

### 4. Prioritize by Time

- Sort upcoming events by start_time chronologically
- Show today's events first, then future events
- Group events by date in calendar tables

### 5. Use Professional Table Format

Always use this table structure:

```python
print("| 日期 | 时间 | 事件 | 类型 | 地点 | 备注 |")
print("|------|------|------|------|------|------|")
# Add rows...
```

**Table Columns**:
- **日期**: Format as "MM-DD (周X)" for clarity
- **时间**: Show time range if available (e.g., "14:00 - 15:30")
- **事件**: Bold the event title using `**title**`
- **类型**: "定期" for recurring, "事件" for one-time
- **地点**: Show location or "-" if not available
- **备注**: Description or additional notes

### 6. Highlight Important Information

- Use emojis for visual clarity: 📅 🕐 📍 ✅
- Bold event titles in tables: `**Event Title**`
- Use consistent date formatting
- Group events by date naturally in tables

### 7. Provide Context

- Add summary row or header with total count
- Mention if schedule is empty
- Suggest adding events if needed
- Point out conflicts or overlaps if any

### 8. Use Chinese Formatting

Since the user interface is in Chinese, format all output in Chinese:

```python
# Good formatting - Calendar table
print("## 📅 今天的日程安排")
print("| 时间 | 事件 | 类型 | 地点 |")
print("|------|------|------|------|")
print(f"| 09:00 | **会议** | 定期 | 会议室A |")

# Avoid English-only formatting
# print("Today's Schedule:")  # ❌
# print("- Meeting at 9:00")  # ❌ - Use tables instead
```

### 9. Choose Appropriate Table Format

- **Today's schedule**: Use "Today's Schedule Table" format
- **This week**: Use "Weekly Calendar Table" format
- **This month**: Use "Monthly Calendar Table" format
- **Upcoming events**: Use "Upcoming Events Table" format
- **Regular schedules**: Use "Regular Schedules Table" format

## Code Templates

### Template 1: Create Weekly Calendar Table (推荐)

```python
from datetime import datetime, timedelta

# Read schedule data
schedule_result = read_memory(section="schedule")

# Parse schedule_result to extract regular_schedules and upcoming_events
# (You'll need to parse the formatted string or access raw JSON)

# Get current week
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

# Create calendar table
print("## 📅 本周日程安排")
print("")
print("| 日期 | 时间 | 事件 | 类型 | 地点 |")
print("|------|------|------|------|------|")

# Add events to table (implementation depends on data structure)
# ... add rows ...

print("")
```

### Template 2: Create Today's Schedule Table

```python
from datetime import datetime

# Read schedule
schedule_result = read_memory(section="schedule")

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]

print("## 📅 今天的日程安排")
print("")
print(f"**日期**: {today.strftime('%Y年%m月%d日')} ({weekday})")
print("")
print("| 时间 | 事件 | 类型 | 地点 | 备注 |")
print("|------|------|------|------|------|")

# Filter and add today's events
# ... implementation ...

print("")
```

### Template 3: Create Upcoming Events Table

```python
from datetime import datetime

# Read schedule
schedule_result = read_memory(section="schedule")

print("## 📅 即将到来的事件")
print("")
print("| 日期 | 时间 | 事件 | 地点 | 备注 |")
print("|------|------|------|------|------|")

# Sort and display events
sorted_events = sorted(upcoming_events, key=lambda x: x.get('start_time', ''))
for event in sorted_events[:10]:
    # Format and add row
    # ... implementation ...

print("")
```

### Template 4: Create Regular Schedules Table

```python
# Read schedule
schedule_result = read_memory(section="schedule")

print("## 📅 定期日程")
print("")
print("| 时间 | 事件 | 频率 | 备注 |")
print("|------|------|------|------|")

for schedule in regular_schedules:
    print(f"| {schedule['time']} | **{schedule['title']}** | {schedule['frequency']} | {schedule.get('description', '')} |")

print("")
```

## Response Examples

### Example 1: User asks "最近的日程安排"

```
好的，让我为您查看最近的日程安排。

[调用 read_memory(section="schedule")]

## 📅 最近的日程安排

### 定期日程

| 时间 | 事件 | 频率 | 备注 |
|------|------|------|------|
| 07:00 | **晨间运动** | 每天 | 每天早上运动30分钟 |
| 09:00 | **工作会议** | 工作日 | 每日站会 |
| 12:00 | **午休** | 每天 | 午餐和休息时间 |

### 即将到来的事件

| 日期 | 时间 | 事件 | 地点 | 备注 |
|------|------|------|------|------|
| 01-15 (周一) | 14:00 - 15:30 | **项目评审会议** | 会议室A | 季度项目评审 |
| 01-18 (周四) | 18:00 - 20:00 | **团队聚餐** | 餐厅B | 团队建设活动 |

您最近有3项定期日程和2个即将到来的事件。需要我帮您添加或调整任何日程吗？
```

### Example 2: User asks "我今天的日程"

```
让我为您查看今天的日程安排。

[调用 read_memory(section="schedule")]

## 📅 今天的日程安排

**日期**: 2024年01月15日 (周一)

| 时间 | 事件 | 类型 | 地点 | 备注 |
|------|------|------|------|------|
| 07:00 | **晨间运动** | 定期 | - | 每天早上运动30分钟 |
| 09:00 | **工作会议** | 定期 | - | 每日站会 |
| 12:00 | **午休** | 定期 | - | 午餐和休息时间 |
| 14:00 - 15:30 | **项目评审会议** | 事件 | 会议室A | 季度项目评审 |

今天您有3项定期日程和1个重要会议。记得提前准备项目评审的材料哦！
```

### Example 3: User asks "这周的安排"

```
让我为您查看本周的日程安排。

[调用 read_memory(section="schedule")]

## 📅 本周日程安排

| 日期 | 时间 | 事件 | 类型 | 地点 |
|------|------|------|------|------|
| 01-15 (周一) | 07:00 | **晨间运动** | 定期 | - |
| 01-15 (周一) | 09:00 | **工作会议** | 定期 | - |
| 01-15 (周一) | 14:00 - 15:30 | **项目评审会议** | 事件 | 会议室A |
| 01-16 (周二) | 07:00 | **晨间运动** | 定期 | - |
| 01-16 (周二) | 09:00 | **工作会议** | 定期 | - |
| 01-18 (周四) | 18:00 - 20:00 | **团队聚餐** | 事件 | 餐厅B |

本周您有多个定期日程和2个重要事件。记得准备周一的项目评审和参加周四的团队聚餐！
```

### Example 4: Empty Schedule

```
让我为您查看日程安排。

[调用 read_memory(section="schedule")]

## 📅 日程安排

| 状态 | 说明 |
|------|------|
| 暂无日程 | 您目前没有日程安排。需要我帮您添加一些日程吗？ |

我可以帮您：
- 添加定期日程（如每天的运动时间）
- 添加即将到来的事件（如会议、约会）
- 从待办事项中安排时间

需要我帮您添加一些日程吗？
```

## Integration with Memory System

This skill works seamlessly with the memory system:

- **read_memory(section="schedule")**: Read schedule data
- **add_regular_schedule()**: Add recurring schedules (use when user wants to add)
- **add_one_time_event()**: Add one-time events (use when user wants to add)

## Output Format Guidelines

1. **ALWAYS Use Calendar Tables**: This is the primary and most professional format
   - Use Markdown tables with proper columns
   - Format: `| 日期 | 时间 | 事件 | 类型 | 地点 | 备注 |`
   - Always include table header and separator row

2. **Use Clear Headers**: Use `##` for main sections, `###` for subsections
   - Example: `## 📅 今天的日程安排`

3. **Use Emojis**: 📅 for schedule, 🕐 for time, 📍 for location
   - Add emojis to headers for visual clarity

4. **Bold Important Info**: Use `**bold**` for event titles in tables
   - Example: `| 09:00 | **工作会议** | 定期 | - |`

5. **Consistent Date Formatting**: 
   - Format dates as "MM-DD (周X)" for clarity
   - Example: "01-15 (周一)"

6. **Group Related Info**: Keep related information together in tables
   - Sort by date and time chronologically

7. **Provide Action Items**: Suggest next steps when appropriate
   - Add helpful suggestions after displaying schedule

8. **Professional Appearance**:
   - Use consistent column widths
   - Align data properly in tables
   - Use "-" for empty fields

## Common User Queries

| User Query | Action | Format |
|------------|--------|--------|
| "最近的日程安排" | Read schedule, show regular + upcoming events | Regular Schedules Table + Upcoming Events Table |
| "我今天的日程" | Read schedule, filter today's events | Today's Schedule Table |
| "这周的安排" | Read schedule, format as weekly view | Weekly Calendar Table |
| "这月的安排" | Read schedule, format as monthly view | Monthly Calendar Table |
| "我有什么安排" | Read schedule, show summary | Summary Table |
| "查看我的日程" | Read schedule, display full schedule | Weekly Calendar Table |
| "日程表" | Read schedule, display in calendar format | Weekly Calendar Table |
| "定期日程" | Read schedule, show only regular schedules | Regular Schedules Table |
| "即将到来的事件" | Read schedule, show only upcoming events | Upcoming Events Table |

## Notes

- **CRITICAL**: Always use calendar table format for displaying schedules - this is the professional standard
- Always use `read_memory(section="schedule")` to get schedule data
- The schedule data includes both regular and upcoming events
- Format output in Chinese for better user experience
- Use Markdown tables with proper columns: 日期, 时间, 事件, 类型, 地点, 备注
- Sort events chronologically by date and time
- Provide helpful suggestions when schedule is empty
- Highlight important or urgent events using bold formatting
- Use consistent date formatting: "MM-DD (周X)" format
- Use "-" for empty fields in tables to maintain table structure
