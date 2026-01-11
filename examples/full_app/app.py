"""Full-featured example application with FastAPI backend and WebSocket streaming.

This example demonstrates all pydantic-deep features:
- DockerSandbox for file operations and code execution
- WebSocket streaming for real-time events
- Human-in-the-loop approval for execute
- Skills (data analysis)
- Subagents (joke generator - unrelated to main task)
- File uploads (PDF/CSV)
- Multi-user support with SessionManager
- Long-term memory system (Markdown-based, persistent across sessions)

Run with:
    cd examples/full_app
    uvicorn app:app --reload --port 8080
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# NOTE: memory_system is a local module under examples/full_app/memory_system
# It is deliberately designed to be low-dependency and portable.
try:
    from memory_system import create_memory_toolset
    from memory_system.core import MemorySystem
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError:  # pragma: no cover - dev-time warning only
    MEMORY_SYSTEM_AVAILABLE = False
from pydantic_ai import (
    FinalResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ThinkingPartDelta,
    ToolCallPartDelta,
)
from pydantic_ai._agent_graph import End, UserPromptNode
from pydantic_ai.agent import Agent
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent, ModelMessage
from pydantic_ai.tools import (
    DeferredToolRequests,
    DeferredToolResults,
    ToolApproved,
)

from pydantic_deep import (
    DeepAgentDeps,
    SessionManager,
    create_deep_agent,
)
from pydantic_deep.types import SubAgentConfig
from pydantic_ai_backends import StateBackend, FilesystemBackend
from dotenv import load_dotenv

# Try to import DockerException, but it's optional
try:
    from docker.errors import DockerException
except ImportError:
    DockerException = Exception  # Fallback if docker package not installed

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Paths
APP_DIR = Path(__file__).parent
WORKSPACE_DIR = APP_DIR / "workspace"
SKILLS_DIR = APP_DIR / "skills"
STATIC_DIR = APP_DIR / "static"
MEMORY_DIR = APP_DIR / "memories"
MEMORY_TEMPLATE = APP_DIR / "memory_template.md"

# Personal Companion AI: Fixed user ID (not session-based)
# All memories are stored for this single user identity
PERSONAL_USER_ID = "owner"

# Create workspace if it doesn't exist
WORKSPACE_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)


@dataclass
class UserSession:
    """Per-user session state."""

    session_id: str
    deps: DeepAgentDeps
    message_history: list[ModelMessage] = field(default_factory=list)
    pending_approval_state: dict[str, Any] = field(default_factory=dict)


# Global state - shared agent (stateless) and session manager
agent: Agent[DeepAgentDeps, str] | None = None
session_manager: SessionManager | None = None
user_sessions: dict[str, UserSession] = {}  # session_id -> UserSession
docker_available: bool = False  # Track if Docker is available


# Subagent configurations
SUBAGENT_CONFIGS: list[SubAgentConfig] = [
    {
        "name": "joke-generator",
        "description": "Generates jokes on any topic. Use for jokes or entertainment.",
        "instructions": """You are a professional comedian and joke writer.

Your task is to generate funny, clever jokes on the requested topic.

Guidelines:
- Generate 2-3 jokes per request
- Include different styles: puns, one-liners, observational humor
- Keep it clean and appropriate
- Be creative and original

Format your response as:
1. [First joke]
2. [Second joke]
3. [Third joke]

Always end with a brief explanation of why each joke is funny (for educational purposes).
""",
    },
]

# System instructions for the main agent
MAIN_INSTRUCTIONS = """You are a personal AI assistant dedicated to serving ONE user exclusively. This is a private, personal companion AI.

## Your Core Identity

**CRITICAL**: You are a PERSONAL ASSISTANT serving only ONE user. You MUST:
- Address the user by their name ONLY when greeting them or at the start of a conversation (use their name from memory)
- After the initial greeting, you can communicate naturally without repeatedly mentioning their name
- Make the user feel that you are THEIR personal assistant, not a generic AI
- Center all your responses around the user's needs, preferences, and context
- Use a warm, personal tone as if you're their dedicated companion
- Remember: You serve ONLY this one user - everything you do is for them

## Your Capabilities

1. **File Operations**: You can read, write, edit, and search files in the workspace
2. **Code Execution**: You can execute Python code in a Docker sandbox
3. **Data Analysis**: Load the 'data-analysis' skill for comprehensive CSV analysis
4. **Entertainment**: Delegate to the 'joke-generator' subagent for humor
5. **Memory System**: Remember user preferences, todos, habits, and important information across conversations

## Task Management with TODO List

**IMPORTANT**: You MUST use the TODO list to track your progress on tasks!

When you receive a task:
1. **First**, use `write_todos` to create a task list breaking down the work into steps
2. **During work**, update todos as you complete them ("completed") or start them ("in_progress")
3. **Always** keep exactly ONE todo as "in_progress" at any time
4. **Mark completed** immediately after finishing each step - don't batch completions

Example workflow:
```
User: "Create a script that analyzes sales data"

1. write_todos([
     {{"content": "Read and understand the data file", "status": "in_progress"}},
     {{"content": "Write analysis script", "status": "pending"}},
     {{"content": "Execute and verify results", "status": "pending"}}
   ])
2. [Read the file]
3. write_todos([...first completed, second in_progress...])
4. [Write the script]
5. write_todos([...second completed, third in_progress...])
6. [Execute]
7. write_todos([...all completed...])
```

The user can see your TODO list in real-time, so keep it updated!

## Error Handling - BE AUTONOMOUS

**CRITICAL**: When something fails, FIX IT YOURSELF. Don't ask for permission to fix obvious issues.

Examples of things you should fix automatically WITHOUT asking:
- Missing Python modules → `pip install <module>` and retry
- File not found → check the path, create the file if needed
- Syntax errors in code → fix the code and retry
- Permission errors → try alternative approaches
- Command not found → install the tool or use alternatives

**NEVER** say things like:
- "Would you like me to install...?"
- "Should I fix this error?"
- "Do you want me to retry?"

**ALWAYS** just fix the problem and continue. Only ask the user if:
- You've tried multiple approaches and all failed
- The error requires a decision about business logic or design
- You need information only the user can provide (credentials, preferences, etc.)

When you encounter an error:
1. Analyze what went wrong
2. Fix it immediately (install packages, correct code, etc.)
3. Retry the operation
4. Continue with the task

## Memory System

You have access to a long-term memory system that persists across conversations:

- **read_memory(section)**: Read user's memory (basic_info, preferences, todos, habits, memories, goals, schedule)
- **update_preference(category, key, value)**: Update user preferences
- **add_todo(content, priority, due_date)**: Add a todo item (for one-time tasks)
- **complete_todo(content)**: Mark a todo as completed
- **add_memory(topic, summary)**: Record important conversation memories
- **learn_habit(habit, category)**: Learn user habits (工作习惯, 沟通习惯, 生活习惯)
- **add_regular_schedule(title, time, frequency, description)**: Add recurring schedule (daily, weekdays, weekly, monthly)

**CRITICAL - Memory Usage:**
- **ALWAYS** start conversations by reading the user's basic_info to get their name
- Address the user by their name ONLY when greeting them or at the start of a conversation to acknowledge you remember them
- After the greeting, communicate naturally without repeatedly mentioning their name
- When user asks about their preferences, todos, or habits → use `read_memory`
- When user expresses preferences or habits → use `update_preference` or `learn_habit`
- When user mentions one-time tasks → use `add_todo`
- When user mentions recurring tasks → use `add_regular_schedule` to add to calendar, then **IMMEDIATELY** use `remove_todo` to remove it from todos
- After important conversations → use `add_memory` to save key points
- **ALWAYS** personalize responses based on remembered information
- **AUTOMATIC CLEANUP**: When converting a task from todo to schedule, automatically remove the todo using `remove_todo`
- If you don't know the user's name yet, ask them: "请问我应该怎么称呼您？" and then use `update_preference("基本信息", "姓名", "他们的名字")` to save it

## Schedule Management - BE PROACTIVE AND DECISIVE

**CRITICAL**: When managing schedules, you are the user's personal assistant. Act like you're serving your boss - be proactive, decisive, and minimize confirmations.

**MINIMIZE QUESTIONS**: Don't ask unnecessary questions. When user asks you to do something, just do it. Only ask when you truly need information you cannot infer.

**Rules for Schedule Management:**

1. **DON'T ASK OPEN QUESTIONS** - Never ask "What time would you like?" or "When is convenient?"
   - ❌ WRONG: "什么时间段方便？"
   - ❌ WRONG: "几点钟可以？"
   - ✅ RIGHT: "上午10:00行不行？" or "下午2:30可以吗？"

2. **MAKE DECISIONS FIRST, THEN CONFIRM** - Always propose a specific time/arrangement, then ask "行不行" or "可以吗"
   - ✅ RIGHT: "我帮您安排在每天上午10:00-10:30，行不行？"
   - ✅ RIGHT: "每周五下午4:00可以吗？"

3. **USE CLOSED-ENDED QUESTIONS** - Only ask binary choices (yes/no) or multiple choice
   - ✅ RIGHT: "上午还是下午？"
   - ✅ RIGHT: "10:00还是14:00？"
   - ❌ WRONG: "什么时间？"

4. **AUTOMATICALLY ARRANGE** - When user says "你自己帮我安排吧" or similar:
   - **IMMEDIATELY** use `add_regular_schedule` with your best judgment
   - Consider user's work hours (usually 09:00-18:00 from preferences)
   - Choose reasonable times (avoid lunch break 12:00-13:00)
   - Don't ask for confirmation - just do it and inform the user

5. **FREQUENCY DECISIONS** - When deciding frequency:
   - Learning/skill building → "工作日" (Monday-Friday)
   - Weekly meetings → "每周五" (Friday afternoon)
   - Daily habits → "每天"
   - Make the decision based on context, then confirm with closed question if needed

**Example Workflow:**
```
User: "学习30分钟新技能" (recurring task)
You: [Think: This is learning, should be weekdays. User works 09:00-18:00. 
      Good time would be 10:00-10:30 (morning, before lunch).]
You: "猪嘎，我帮您安排在每个工作日上午10:00-10:30学习新技能，行不行？"
[If user says yes or "你自己安排吧":]
You: [IMMEDIATELY call add_regular_schedule("学习30分钟新技能", "10:00", "工作日", "每天上午学习时间")]
You: [IMMEDIATELY call remove_todo("学习30分钟新技能") to clean up]
You: "已安排好！已添加到您的日程：每个工作日上午10:00-10:30学习新技能，并已从待办中移除。"
```

**Automatic Schedule Arrangement:**
When user says "你帮我安排今天的日程吧" or "你给我排期" or similar:
- **IMMEDIATELY** read all todos using `read_memory(section="todos")`
- **AUTOMATICALLY** identify which tasks are recurring vs one-time
- **AUTOMATICALLY** convert recurring tasks to schedules using `add_regular_schedule`
- **AUTOMATICALLY** remove converted todos using `remove_todo`
- **AUTOMATICALLY** arrange remaining one-time tasks into a time schedule
- **DON'T ASK** - just do it and show the result

## Guidelines

- **PERSONALIZATION**: Use the user's name when greeting them or at conversation start to show you remember them. After that, communicate naturally without repeatedly mentioning their name.
- **BE PROACTIVE**: Don't ask for permission to do obvious things. Make decisions and execute.
- **SCHEDULE MANAGEMENT**: When arranging schedules, propose specific times and ask "行不行" (closed question), never ask open questions like "什么时间"
- When asked to analyze data, first load the 'data-analysis' skill for best practices
- When asked for jokes or entertainment, delegate to the 'joke-generator' subagent
- For code execution, write the code to a file first, then execute it
- Use the memory system to provide personalized, context-aware responses
- Briefly explain what you're doing, but don't over-explain
- Remember: You are THEIR personal assistant - everything revolves around them
- **TREAT USER AS BOSS**: Act decisively, minimize confirmations, make smart decisions on their behalf

## File Locations

- Uploaded files are in: /uploads/
- Your workspace is: /workspace/
- Save generated files (charts, reports) to /workspace/
"""


def create_agent() -> Agent[DeepAgentDeps, str]:
    """Create the shared agent (stateless - can be used by all sessions)."""
    # Create toolsets list
    toolsets = []

    # Create the memory toolset if available
    # Use fixed PERSONAL_USER_ID for personal companion AI (not session-based)
    if MEMORY_SYSTEM_AVAILABLE:
        try:
            memory_toolset = create_memory_toolset(
                memory_dir=str(MEMORY_DIR),
                template_path=str(MEMORY_TEMPLATE) if MEMORY_TEMPLATE.exists() else None,
                id="memory",
                fixed_user_id=PERSONAL_USER_ID,  # Fixed user ID for personal companion
            )
            toolsets.append(memory_toolset)
            logger.info("Memory system toolset added to agent (user_id='owner')")
        except Exception as e:  # pragma: no cover - defensive logging
            logger.warning(f"Failed to create memory toolset: {e}")

    # Create the main agent with all features
    # Include DeferredToolRequests as output type for human-in-the-loop
    # Note: backend=None because deps are provided per-session at runtime
    agent = create_deep_agent(
        model="openai:gpt-4.1",
        instructions=MAIN_INSTRUCTIONS,
        backend=None,  # Backend comes from deps at runtime
        # Toolsets
        include_todo=True,
        include_filesystem=True,
        include_subagents=True,
        include_skills=True,
        include_execute=True,  # Force include execute - backend is provided via deps at runtime
        toolsets=toolsets,
        # Subagents
        subagents=SUBAGENT_CONFIGS,
        include_general_purpose_subagent=False,  # We only want our custom subagent
        # Skills
        skill_directories=[{"path": str(SKILLS_DIR), "recursive": True}],
        # Human-in-the-loop: require approval for execute
        interrupt_on={
            "execute": True,
            "write_file": False,
        },
    )
    
    # Add dynamic memory context injection for personal companion AI
    if MEMORY_SYSTEM_AVAILABLE:
        @agent.instructions
        def inject_user_memory_context(ctx: Any) -> str:  # pragma: no cover
            """Inject user memory context (name, preferences) into system prompt."""
            try:
                memory_sys = MemorySystem(
                    user_id=PERSONAL_USER_ID,
                    memory_dir=str(MEMORY_DIR),
                    template_path=str(MEMORY_TEMPLATE) if MEMORY_TEMPLATE.exists() else None
                )
                
                # Extract user name directly
                data = memory_sys.storage.get_all_data()
                basic_info = data.get("profile", {}).get("basic_info", {})
                user_name = basic_info.get("姓名") or basic_info.get("昵称")
                
                # Build personalized prompt with user name prominently displayed
                parts = []
                
                if user_name:
                    parts.append("## 👤 当前用户")
                    parts.append(f"**用户姓名：{user_name}**")
                    parts.append("")
                    parts.append("**⚠️ 重要指令**：")
                    parts.append(f"- 你只在**打招呼**或**对话开始时**称呼用户为：**{user_name}**，让用户知道你记得他们")
                    parts.append(f"- 打招呼后，正常交流即可，不需要频繁提及用户名字")
                    parts.append(f"- 这是你的主人，你是专属于 **{user_name}** 的私人助理")
                    parts.append(f"- 所有回复都要以用户 **{user_name}** 为中心（但不需要每次都提到名字）")
                    parts.append("")
                
                # Get full memory context (will include name again, but that's okay for emphasis)
                memory_context = memory_sys.get_context(sections=["profile"])
                if memory_context:
                    parts.append(memory_context)
                
                return "\n".join(parts)
            except Exception as e:
                logger.warning(f"Failed to inject user memory context: {e}")
            
            return ""
    
    return agent


async def get_or_create_session(session_id: str) -> UserSession:
    """Get existing session or create a new one with isolated Docker container or fallback backend."""
    global session_manager, user_sessions, docker_available

    if session_id in user_sessions:
        return user_sessions[session_id]

    # Try to use Docker sandbox if available, otherwise fall back to FilesystemBackend
    backend = None
    if docker_available and session_manager is not None:
        try:
            sandbox = await session_manager.get_or_create(session_id)
            backend = sandbox
            logger.info(f"Created Docker sandbox for session: {session_id}")
        except (DockerException, FileNotFoundError, ConnectionError) as e:
            logger.warning(f"Docker not available, falling back to FilesystemBackend: {e}")
            docker_available = False
            # Create per-session workspace directory
            session_workspace = WORKSPACE_DIR / session_id
            session_workspace.mkdir(parents=True, exist_ok=True)
            backend = FilesystemBackend(str(session_workspace))
    else:
        # Docker not available, use FilesystemBackend
        session_workspace = WORKSPACE_DIR / session_id
        session_workspace.mkdir(parents=True, exist_ok=True)
        backend = FilesystemBackend(str(session_workspace))
        logger.info(f"Using FilesystemBackend for session: {session_id}")

    # Create deps with the backend
    deps = DeepAgentDeps(backend=backend)

    # Create and store session
    session = UserSession(session_id=session_id, deps=deps)
    user_sessions[session_id] = session

    logger.info(f"Created new session: {session_id}")
    return session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared agent and session manager on startup."""
    global agent, session_manager, docker_available

    # Create shared agent (stateless)
    agent = create_agent()

    # Try to initialize Docker session manager
    try:
        import docker
        # Test Docker connection
        docker_client = docker.from_env()
        docker_client.ping()
        docker_available = True
        
        # Create session manager for per-user Docker containers
        session_manager = SessionManager(
            default_runtime=None,  # Will use default python:3.12-slim
            default_idle_timeout=3600,  # 1 hour idle timeout
        )
        session_manager.start_cleanup_loop(interval=300)  # Cleanup every 5 min
        print("Agent initialized (shared across sessions)")
        print(f"Skills directory: {SKILLS_DIR}")
        print("Session manager started with auto-cleanup (Docker enabled)")
    except (DockerException, FileNotFoundError, ConnectionError, ImportError) as e:
        docker_available = False
        session_manager = None
        print("Agent initialized (shared across sessions)")
        print(f"Skills directory: {SKILLS_DIR}")
        print(f"⚠️  Docker not available: {e}")
        print("⚠️  Using FilesystemBackend fallback (code execution disabled)")
    
    # Start frontend dev server if in development mode
    frontend_process = None
    dist_dir = STATIC_DIR / "dist"
    node_modules_dir = STATIC_DIR / "node_modules"
    
    # Only start dev server if dist/ doesn't exist (not built) and node_modules exists
    if not dist_dir.exists() and node_modules_dir.exists():
        try:
            # Check if npm is available
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
            
            print("Starting frontend development server...")
            # Start npm run dev in the background
            # Use shell=True on Windows for better compatibility
            kwargs = {
                "cwd": str(STATIC_DIR),
                "env": {**os.environ, "FORCE_COLOR": "1"},
            }
            if sys.platform == "win32":
                kwargs["shell"] = True
                # CREATE_NEW_PROCESS_GROUP is available on Windows
                if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                    kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["stdout"] = subprocess.DEVNULL
                kwargs["stderr"] = subprocess.DEVNULL
            
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                **kwargs
            )
            print(f"✓ Frontend dev server started (PID: {frontend_process.pid})")
            print("  Frontend: http://localhost:3000")
            print("  Backend:  http://localhost:8080")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  Could not start frontend dev server: {e}")
            print("⚠️  Make sure npm is installed and run 'npm install' in static/ directory")
            frontend_process = None
    elif dist_dir.exists():
        print("Using production build (dist/ directory found)")
        print("Backend available at http://localhost:8080")
    else:
        print("⚠️  Frontend not built. Run 'npm install && npm run build' in static/ directory")
        print("Backend available at http://localhost:8080")
    
    yield

    # Shutdown frontend dev server if it was started
    if frontend_process is not None:
        print("Stopping frontend dev server...")
        try:
            if sys.platform == "win32":
                # On Windows, use taskkill to terminate the process tree
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)],
                    capture_output=True,
                )
            else:
                frontend_process.terminate()
                try:
                    frontend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    frontend_process.kill()
            print("✓ Frontend dev server stopped")
        except Exception as e:
            print(f"⚠️  Error stopping frontend dev server: {e}")

    # Shutdown all sessions if Docker was available
    if session_manager is not None:
        count = await session_manager.shutdown()
        print(f"Shutdown complete. Stopped {count} sessions.")
    else:
        print("Shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="pydantic-deep Full Example",
    description="Full-featured example demonstrating all pydantic-deep capabilities",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
# In production, serve from dist/ directory (built React app)
# In development, serve from static/ directory (source files)
DIST_DIR = STATIC_DIR / "dist"
if DIST_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DIST_DIR)), name="static")
else:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    # Try dist/index.html first (production build), then static/index.html (development)
    html_path = DIST_DIR / "index.html" if DIST_DIR.exists() else STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Frontend not found. Run 'npm run build' in static/ directory</h1>")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat with the agent.

    Session ID is sent in the first message. Each session_id gets its own
    isolated Docker container and message history.

    Protocol:
    1. Client connects to /ws/chat
    2. Client sends first message with session_id: {"session_id": "xxx", "message": "..."}
    3. Server streams responses with various event types:
       - {"type": "start"} - Agent run started
       - {"type": "text_delta", "content": "..."} - Streaming text chunk
       - {"type": "thinking_delta", "content": "..."} - Thinking text chunk
       - {"type": "tool_start", "tool_name": "...", "args": {...}} - Tool called
       - {"type": "tool_output", "tool_name": "...", "output": "..."} - Tool result
       - {"type": "approval_required", "requests": [...]} - Human approval needed
       - {"type": "response", "content": "..."} - Final response
       - {"type": "done"} - Agent run complete
       - {"type": "error", "content": "..."} - Error occurred
    """
    global agent

    await websocket.accept()

    if agent is None:
        await websocket.send_json({"type": "error", "content": "Agent not initialized"})
        return

    session: UserSession | None = None

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Get session_id from message (required for first message, optional after)
            session_id = message_data.get("session_id")
            if session is None:
                if not session_id:
                    # Generate new session ID if not provided
                    session_id = str(uuid.uuid4())
                    await websocket.send_json({"type": "session_created", "session_id": session_id})
                session = await get_or_create_session(session_id)
                logger.info(f"WebSocket connected for session: {session_id}")

            user_message = message_data.get("message", "")
            approval_response = message_data.get("approval")  # For handling approvals

            # Handle approval response
            if approval_response is not None:
                await handle_approval(websocket, session, approval_response)
                continue

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            try:
                await run_agent_with_streaming(websocket, session, user_message)
            except Exception as e:
                logger.exception("Error in agent run")
                await websocket.send_json({"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        if session:
            logger.info(f"WebSocket disconnected for session: {session.session_id}")
        # Note: We don't delete the session here - it can be reused


async def run_agent_with_streaming(
    websocket: WebSocket,
    session: UserSession,
    user_message: str,
    deferred_results: DeferredToolResults | None = None,
) -> None:
    """Run agent with streaming and handle DeferredToolRequests."""
    global agent

    logger.info(f"=== Starting agent run for session {session.session_id} ===")
    logger.info(f"User message: {user_message[:100] if user_message else '(continuation)'}")
    logger.info(f"Deferred results: {deferred_results is not None}")
    logger.info(f"Message history length: {len(session.message_history)}")

    # Send start event
    await websocket.send_json({"type": "start"})

    # Use iter() for streaming execution with session's message history
    assert agent is not None
    async with agent.iter(
        user_message if deferred_results is None else None,
        deps=session.deps,
        message_history=session.message_history,
        deferred_tool_results=deferred_results,
    ) as run:
        node_count = 0
        async for node in run:
            node_count += 1
            logger.debug(f"Node {node_count}: {type(node).__name__}")
            await process_node(websocket, node, run, session)

        # Get the final result
        result = run.result
        logger.info(f"Agent finished after {node_count} nodes")
        logger.info(f"Result output type: {type(result.output).__name__}")

    # Check if we got DeferredToolRequests (needs approval)
    if isinstance(result.output, DeferredToolRequests):
        logger.info(f"Got DeferredToolRequests with {len(result.output.approvals)} approvals")
        # Store state for continuation in session
        session.pending_approval_state = {
            "message_history": result.all_messages(),
            "approvals": result.output.approvals,
        }

        # Send approval request to frontend
        approval_requests = []
        for call in result.output.approvals:
            logger.info(f"  Approval needed: {call.tool_name}({call.args})")
            approval_requests.append(
                {
                    "tool_call_id": call.tool_call_id,
                    "tool_name": call.tool_name,
                    "args": call.args if isinstance(call.args, dict) else str(call.args),
                }
            )

        await websocket.send_json(
            {
                "type": "approval_required",
                "requests": approval_requests,
            }
        )
        return

    # Update session's message history for next request
    session.message_history = result.all_messages()
    logger.info(f"Updated message history to {len(session.message_history)} messages")

    # Update memory system statistics (optional)
    # Use fixed PERSONAL_USER_ID for personal companion AI (not session-based)
    if MEMORY_SYSTEM_AVAILABLE:
        try:
            memory_sys = MemorySystem(
                user_id=PERSONAL_USER_ID,  # Fixed user ID for personal companion
                memory_dir=str(MEMORY_DIR),
                template_path=str(MEMORY_TEMPLATE) if MEMORY_TEMPLATE.exists() else None
            )
            memory_sys.increment_conversation_count()
            logger.debug("Updated memory statistics for owner")
        except Exception as e:
            logger.warning(f"Failed to update memory statistics: {e}")

    # Send final response
    logger.info(f"Sending response: {str(result.output)[:200]}...")
    await websocket.send_json(
        {
            "type": "response",
            "content": str(result.output),
        }
    )

    # Send completion event
    await websocket.send_json({"type": "done"})
    logger.info("=== Agent run complete ===")


async def handle_approval(
    websocket: WebSocket, session: UserSession, approval_response: dict
) -> None:
    """Handle approval response from frontend and continue agent."""
    if not session.pending_approval_state:
        await websocket.send_json({"type": "error", "content": "No pending approval"})
        return

    # Build approval results
    approvals: dict[str, ToolApproved] = {}
    for tool_call_id, approved in approval_response.items():
        if approved:
            approvals[tool_call_id] = ToolApproved()
        # If not approved, we just don't include it (will be denied)

    # Restore message history from pending state
    session.message_history = session.pending_approval_state["message_history"]

    # Clear pending state
    session.pending_approval_state = {}

    # Continue agent with approvals
    try:
        await run_agent_with_streaming(
            websocket,
            session,
            "",  # No new message
            deferred_results=DeferredToolResults(approvals=approvals),
        )
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})


async def _stream_model_request(websocket: WebSocket, node: Any, run: Any) -> None:
    """Stream text chunks from a ModelRequestNode."""
    await websocket.send_json({"type": "status", "content": "Generating response..."})

    # Track current tool call being streamed (for args streaming)
    current_tool_name: str | None = None
    current_tool_call_id: str | None = None

    async with node.stream(run.ctx) as request_stream:
        final_result_found = False

        # First, iterate through events to find deltas and final result marker
        async for event in request_stream:
            if isinstance(event, PartStartEvent):
                logger.debug(f"     PartStartEvent: {event.part!r}")
                # Check if this is a tool call part starting
                if hasattr(event.part, "tool_name"):
                    current_tool_name = event.part.tool_name
                    current_tool_call_id = getattr(event.part, "tool_call_id", None)
                    # Send tool_call_start event
                    await websocket.send_json(
                        {
                            "type": "tool_call_start",
                            "tool_name": current_tool_name,
                            "tool_call_id": current_tool_call_id,
                        }
                    )
            elif isinstance(event, PartDeltaEvent):
                await _handle_part_delta(websocket, event, current_tool_name)
            elif isinstance(event, FinalResultEvent):
                logger.debug(f"     FinalResultEvent: tool_name={event.tool_name}")
                final_result_found = True
                break  # Stop iterating events, switch to streaming text

        # If final result was found, stream the text output
        # Note: stream_text() yields cumulative text, so we compute deltas
        if final_result_found:
            previous_text = ""
            async for cumulative_text in request_stream.stream_text():
                # Extract only the new part (delta)
                delta = cumulative_text[len(previous_text) :]
                if delta:
                    await websocket.send_json({"type": "text_delta", "content": delta})
                previous_text = cumulative_text


async def _handle_part_delta(
    websocket: WebSocket, event: PartDeltaEvent, current_tool_name: str | None
) -> None:
    """Handle streaming delta events."""
    if isinstance(event.delta, TextPartDelta):
        await websocket.send_json({"type": "text_delta", "content": event.delta.content_delta})
    elif isinstance(event.delta, ThinkingPartDelta):
        await websocket.send_json({"type": "thinking_delta", "content": event.delta.content_delta})
    elif isinstance(event.delta, ToolCallPartDelta):
        # Stream tool call arguments as they come in
        await websocket.send_json(
            {
                "type": "tool_args_delta",
                "tool_name": current_tool_name,
                "args_delta": event.delta.args_delta,
            }
        )


async def _stream_tool_calls(
    websocket: WebSocket, node: Any, run: Any, session: UserSession
) -> None:
    """Stream tool call events from a CallToolsNode."""
    tool_names_by_id: dict[str, str] = {}

    async with node.stream(run.ctx) as handle_stream:
        async for event in handle_stream:
            logger.debug(f"     Event type: {type(event).__name__}")

            if isinstance(event, FunctionToolCallEvent):
                tool_name = event.part.tool_name
                tool_args = event.part.args
                tool_call_id = event.part.tool_call_id
                logger.info(f"  TOOL CALL: {tool_name}({tool_args})")

                if tool_call_id:
                    tool_names_by_id[tool_call_id] = tool_name

                await websocket.send_json(
                    {
                        "type": "tool_start",
                        "tool_name": tool_name,
                        "args": tool_args if isinstance(tool_args, dict) else str(tool_args),
                    }
                )

            elif isinstance(event, FunctionToolResultEvent):
                tool_call_id = event.tool_call_id
                tool_name = tool_names_by_id.get(tool_call_id, "unknown")
                result_content = event.result.content
                logger.info(f"  TOOL RESULT: {tool_name} -> {str(result_content)[:100]}...")

                await websocket.send_json(
                    {
                        "type": "tool_output",
                        "tool_name": tool_name,
                        "output": str(result_content),
                    }
                )

                # Send TODO update after write_todos or read_todos
                if tool_name in ("write_todos", "read_todos"):
                    await _send_todos_update(websocket, session)


async def _send_todos_update(websocket: WebSocket, session: UserSession) -> None:
    """Send current TODO list to frontend."""
    todos = [todo.model_dump() for todo in session.deps.todos]
    await websocket.send_json(
        {
            "type": "todos_update",
            "todos": todos,
        }
    )


async def process_node(websocket: WebSocket, node: Any, run: Any, session: UserSession) -> None:
    """Process a node and send appropriate WebSocket events with streaming."""
    if isinstance(node, UserPromptNode):
        logger.debug("  -> UserPromptNode")
        await websocket.send_json({"type": "status", "content": "Processing user prompt..."})

    elif Agent.is_model_request_node(node):
        logger.debug("  -> ModelRequestNode: streaming tokens")
        await _stream_model_request(websocket, node, run)

    elif Agent.is_call_tools_node(node):
        logger.debug(f"  -> CallToolsNode with {len(node.model_response.parts)} parts")
        await _stream_tool_calls(websocket, node, run, session)

    elif isinstance(node, End):
        await websocket.send_json({"type": "status", "content": "Completed!"})


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),  # noqa: B008
    session_id: str = Query(
        "", description="Session ID (optional, will create new if not provided)"
    ),
):
    """Upload a file (CSV, PDF, etc.) to a specific session."""
    try:
        # Generate session_id if not provided or empty
        if not session_id:
            session_id = str(uuid.uuid4())

        # Get or create session
        session = await get_or_create_session(session_id)

        content = await file.read()
        filename = file.filename or "uploaded_file"

        logger.info(f"Uploading file: {filename} ({len(content)} bytes) to session {session_id}")

        # Upload to the session's backend (Docker container)
        path = session.deps.upload_file(filename, content)
        logger.info(f"File uploaded to: {path}")

        # Verify the file exists in the container (if backend supports execute)
        if hasattr(session.deps.backend, "execute"):
            verify_result = session.deps.backend.execute(f"ls -la {path}")  # type: ignore[union-attr]
            logger.info(f"Verify upload: {verify_result.output.strip()}")

        return JSONResponse(
            content={
                "status": "success",
                "filename": filename,
                "path": path,
                "size": len(content),
                "session_id": session_id,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/files")
async def list_files(session_id: str = Query(..., description="Session ID")):
    """List files in workspace and uploads for a specific session."""
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    files: dict[str, list[str]] = {
        "workspace": [],
        "uploads": [],
    }

    # List workspace files from container (if backend supports execute)
    if hasattr(session.deps.backend, "execute"):
        result = session.deps.backend.execute("find /workspace -type f 2>/dev/null")  # type: ignore[union-attr]
        if result.exit_code == 0:
            files["workspace"] = [f for f in result.output.strip().split("\n") if f]

    # List uploads from deps
    files["uploads"] = list(session.deps.uploads.keys())

    return JSONResponse(content=files)


@app.get("/files/download/{filepath:path}")
async def download_file(filepath: str, session_id: str = Query(..., description="Session ID")):
    """Download a file from a session's workspace."""
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    # Read file from container
    result = session.deps.backend.read(f"/workspace/{filepath}")
    if "Error:" in result:
        raise HTTPException(status_code=404, detail="File not found")

    # Return as downloadable response
    return JSONResponse(
        content={
            "filename": filepath.split("/")[-1],
            "content": result,
        }
    )


@app.get("/files/content/{filepath:path}")
async def get_file_content(filepath: str, session_id: str = Query(..., description="Session ID")):
    """Get file content for preview (supports any path in the container).

    Args:
        filepath: Full path to file (e.g., /workspace/script.py or /uploads/data.csv)
        session_id: Session ID
    """
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    # Decode the path if it was URL-encoded
    import urllib.parse

    decoded_path = urllib.parse.unquote(filepath)

    # Ensure path starts with /
    if not decoded_path.startswith("/"):
        decoded_path = "/" + decoded_path

    logger.debug(f"Reading file: {decoded_path} for session {session_id}")

    # Read file from container
    try:
        result = session.deps.backend.read(decoded_path)

        # Check for error patterns in result
        if result.startswith("Error:") or "No such file" in result:
            raise HTTPException(status_code=404, detail=f"File not found: {decoded_path}")

        return JSONResponse(
            content={
                "path": decoded_path,
                "filename": decoded_path.split("/")[-1],
                "content": result,
                "size": len(result),
            }
        )
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"File not found: {decoded_path}") from e
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/files/binary/{filepath:path}")
async def get_file_binary(filepath: str, session_id: str = Query(..., description="Session ID")):
    """Get binary file content (for images, etc.).

    Args:
        filepath: Full path to file (e.g., /workspace/chart.png)
        session_id: Session ID
    """
    from fastapi.responses import Response

    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    # Decode the path if it was URL-encoded
    import urllib.parse

    decoded_path = urllib.parse.unquote(filepath)

    # Ensure path starts with /
    if not decoded_path.startswith("/"):
        decoded_path = "/" + decoded_path

    logger.debug(f"Reading binary file: {decoded_path} for session {session_id}")

    # Get file extension for content type
    ext = decoded_path.split(".")[-1].lower()
    content_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "ico": "image/x-icon",
        "pdf": "application/pdf",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    try:
        # Read binary file from container using base64
        if hasattr(session.deps.backend, "execute"):
            # Use quotes around path to handle spaces
            result = session.deps.backend.execute(f'base64 "{decoded_path}"')
            logger.debug(f"base64 command exit code: {result.exit_code}")

            if result.exit_code != 0:
                logger.error(f"base64 failed: {result.output}")
                raise HTTPException(status_code=404, detail=f"File not found: {decoded_path}")

            import base64

            # Clean the output - remove any whitespace/newlines that base64 adds
            b64_output = result.output.strip().replace("\n", "").replace("\r", "").replace(" ", "")

            # Fix padding if needed
            padding_needed = len(b64_output) % 4
            if padding_needed:
                b64_output += "=" * (4 - padding_needed)

            binary_content = base64.b64decode(b64_output)
            return Response(content=binary_content, media_type=content_type)
        else:
            raise HTTPException(
                status_code=500, detail="Backend does not support binary file reading"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error reading binary file: {decoded_path}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/todos")
async def get_todos(session_id: str = Query(..., description="Session ID")):
    """Get current todo list for a specific session."""
    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    return JSONResponse(
        content={
            "todos": [todo.model_dump() for todo in session.deps.todos],
        }
    )


@app.post("/reset")
async def reset(session_id: str = Query(..., description="Session ID")):
    """Reset a specific session."""
    global session_manager, user_sessions

    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Release the session's Docker container
    if session_manager:
        await session_manager.release(session_id)

    # Remove from user sessions
    del user_sessions[session_id]

    logger.info(f"Reset session: {session_id}")

    return JSONResponse(content={"status": "reset complete", "session_id": session_id})


@app.post("/session/new")
async def create_new_session():
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())
    session = await get_or_create_session(session_id)

    return JSONResponse(
        content={
            "session_id": session.session_id,
            "status": "created",
        }
    )


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return JSONResponse(
        content={
            "sessions": list(user_sessions.keys()),
            "count": len(user_sessions),
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
        "session_count": len(user_sessions),
    }


@app.get("/preview/{session_id}/{filepath:path}")
async def preview_file(session_id: str, filepath: str):
    """Serve raw files from container for live preview.

    This endpoint serves files WITHOUT line numbers, with proper Content-Type,
    allowing HTML files to load relative CSS/JS/images naturally.

    Example: /preview/abc123/workspace/index.html
             -> loads HTML, which requests style.css
             -> browser resolves to /preview/abc123/workspace/style.css
    """
    from fastapi.responses import Response

    if session_id not in user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = user_sessions[session_id]

    # Ensure path starts with /
    if not filepath.startswith("/"):
        filepath = "/" + filepath

    logger.debug(f"Preview file: {filepath} for session {session_id}")

    # Get file extension for content type
    ext = filepath.split(".")[-1].lower() if "." in filepath else ""
    content_types = {
        # Web
        "html": "text/html; charset=utf-8",
        "htm": "text/html; charset=utf-8",
        "css": "text/css; charset=utf-8",
        "js": "application/javascript; charset=utf-8",
        "mjs": "application/javascript; charset=utf-8",
        "json": "application/json; charset=utf-8",
        # Images
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "ico": "image/x-icon",
        # Fonts
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "eot": "application/vnd.ms-fontobject",
        # Other
        "pdf": "application/pdf",
        "xml": "application/xml",
        "txt": "text/plain; charset=utf-8",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    # Check if binary file
    binary_extensions = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp",
        "ico",
        "pdf",
        "woff",
        "woff2",
        "ttf",
        "eot",
    }
    is_binary = ext in binary_extensions

    try:
        if hasattr(session.deps.backend, "execute"):
            if is_binary:
                # Read binary file via base64
                result = session.deps.backend.execute(f'base64 "{filepath}"')
                if result.exit_code != 0:
                    raise HTTPException(status_code=404, detail=f"File not found: {filepath}")

                import base64

                b64_output = (
                    result.output.strip().replace("\n", "").replace("\r", "").replace(" ", "")
                )
                padding_needed = len(b64_output) % 4
                if padding_needed:
                    b64_output += "=" * (4 - padding_needed)

                binary_content = base64.b64decode(b64_output)
                return Response(content=binary_content, media_type=content_type)
            else:
                # Read text file - use cat WITHOUT -n (no line numbers)
                result = session.deps.backend.execute(f'cat "{filepath}"')
                if result.exit_code != 0:
                    raise HTTPException(status_code=404, detail=f"File not found: {filepath}")

                return Response(content=result.output, media_type=content_type)
        else:
            raise HTTPException(status_code=500, detail="Backend does not support file serving")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error serving preview file: {filepath}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
