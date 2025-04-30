import asyncio
import os
import json
import logging
import uuid
from datetime import datetime
from typing import List, AsyncGenerator, Optional, Dict, Any, Tuple

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent
from autogen_agentchat.ui import Console  # 新增导入
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.experimental.task_centric_memory import MemoryController
from autogen_ext.experimental.task_centric_memory.utils import Teachability

from app.core.config import settings
from app.schemas.chat import ChatMessage
from app.core.llms import model_client

class ChatSession:
    """聊天会话类，用于管理单个用户的对话历史和记忆"""

    def __init__(self, session_id: str, user_id: str, memory_controller: MemoryController):
        """初始化聊天会话

        Args:
            session_id: 会话唯一标识符
            user_id: 用户唯一标识符
            memory_controller: 记忆控制器
        """
        self.session_id = session_id
        self.user_id = user_id
        self.memory_controller = memory_controller
        self.teachability = Teachability(memory_controller=memory_controller)
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.last_active = datetime.now()

    def add_message(self, message: ChatMessage) -> None:
        """添加消息到会话历史

        Args:
            message: 要添加的消息
        """
        self.messages.append(message)
        self.last_active = datetime.now()

    def get_messages(self) -> List[ChatMessage]:
        """获取会话历史消息

        Returns:
            会话历史消息列表
        """
        return self.messages

    def clear_messages(self) -> None:
        """清除会话历史消息"""
        self.messages = []

    async def add_memory(self, task: str, insight: str) -> None:
        """添加记忆

        Args:
            task: 任务描述
            insight: 相关的见解或知识
        """
        await self.memory_controller.add_memo(task=task, insight=insight)

    async def retrieve_memories(self, task: str, limit: int = 5) -> List[str]:
        """检索相关记忆

        Args:
            task: 当前任务描述
            limit: 返回的最大记忆数量

        Returns:
            相关记忆的见解列表
        """
        memos = await self.memory_controller.retrieve_relevant_memos(task=task, limit=limit)
        return [memo.insight for memo in memos if hasattr(memo, 'insight')]


class ChatService:
    """聊天服务类，处理与LLM的对话逻辑，支持多用户和用户记忆"""

    # 存储用户实例的字典
    _user_memory_controllers: Dict[str, MemoryController] = {}
    _user_teachability: Dict[str, Teachability] = {}
    # 存储用户会话的字典
    _sessions: Dict[str, ChatSession] = {}

    def __init__(self, model: Optional[str] = None):
        """初始化聊天服务

        Args:
            model: 使用的模型名称，如果为None则使用配置中的默认模型
        """
        self.model_client = model_client

        # 初始化日志记录器
        self.logger = logging.getLogger("chat_service")

        # 获取项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        # 确保记忆存储目录存在
        self.memories_dir = os.path.join(self.base_dir, "data", "memories")
        os.makedirs(self.memories_dir, exist_ok=True)

        # 确保会话存储目录存在
        self.sessions_dir = os.path.join(self.base_dir, "data", "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)

        # 创建日志目录
        logs_dir = os.path.join(self.base_dir, "logs", "chat")
        os.makedirs(logs_dir, exist_ok=True)

        # 初始化日志处理
        file_handler = logging.FileHandler(os.path.join(logs_dir, "memory.log"))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

        # 默认系统提示
        self.default_system_message = """你是但问智能助手，一个具有记忆能力的AI助手。

你的能力和职责：
1. 你可以记住用户之前的教导、偏好和重要信息
2. 当用户要求你记住某些信息时，你应明确确认并将其保存到记忆中
3. 当用户提出新问题时，你应主动考虑之前存储的相关记忆
4. 如果用户询问你记得的内容，你应该准确地回答并引用相关记忆

交流风格：
1. 保持专业、友好和有帮助性
2. 回答简洁明确，避免不必要的冗长
3. 当使用记忆时，可以自然地提及，但不需要明确说明这是你的记忆
4. 如果你不确定或没有相关记忆，请说实而不是羞造信息"""

    def _get_user_memory_controller(self, user_id: str) -> MemoryController:
        """获取或创建用户的记忆控制器

        Args:
            user_id: 用户ID

        Returns:
            用户的MemoryController实例
        """
        if user_id not in self._user_memory_controllers:
            self.logger.info(f"创建用户记忆控制器: {user_id}")

            # 为用户准备记忆相关路径
            memory_path = os.path.join(self.memories_dir, f"{user_id}.json")
            logs_path = os.path.join(self.base_dir, "logs", "memories", f"{user_id}.log")

            try:
                # 创建记忆控制器
                memory_controller = MemoryController(
                    reset=False,  # 不重置现有记忆
                    client=self.model_client,  # 使用模型客户端
                    config={
                        "memory_path": memory_path,  # 记忆存储路径
                        "log_path": logs_path,       # 日志路径
                        "verbose": True,             # 输出详细日志
                        "embedding_dimensions": 1536  # 嵌入向量维度
                    }
                )

                # 存储记忆控制器
                self._user_memory_controllers[user_id] = memory_controller

                self.logger.info(f"成功创建用户记忆控制器: {user_id}")
            except Exception as e:
                error_msg = f"创建用户记忆控制器失败 {user_id}: {e}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        return self._user_memory_controllers[user_id]

    def _get_user_teachability(self, user_id: str) -> Teachability:
        """获取或创建用户的Teachability实例

        Args:
            user_id: 用户ID

        Returns:
            用户的Teachability实例
        """
        if user_id not in self._user_teachability:
            # 获取记忆控制器
            memory_controller = self._get_user_memory_controller(user_id)

            # 创建Teachability包装器
            teachability = Teachability(memory_controller=memory_controller)

            # 存储用户Teachability对象
            self._user_teachability[user_id] = teachability

            self.logger.info(f"已创建用户Teachability实例: {user_id}")

        return self._user_teachability[user_id]

    def get_or_create_session(self, user_id: str, session_id: Optional[str] = None) -> ChatSession:
        """获取或创建用户会话

        Args:
            user_id: 用户ID
            session_id: 会话ID，如果为None则自动生成

        Returns:
            用户会话
        """
        # 如果没有提供会话ID，生成一个新的
        if session_id is None:
            session_id = str(uuid.uuid4())

        # 如果会话已存在，直接返回
        if session_id in self._sessions:
            return self._sessions[session_id]

        # 获取用户的记忆控制器
        try:
            memory_controller = self._get_user_memory_controller(user_id)
        except Exception as e:
            self.logger.error(f"Error getting memory controller for session {session_id}: {e}")
            # 如果获取失败，创建一个空的
            memory_controller = MemoryController(client=self.model_client)

        # 创建新的会话
        session = ChatSession(session_id=session_id, user_id=user_id, memory_controller=memory_controller)

        # 存储会话
        self._sessions[session_id] = session

        self.logger.info(f"Created new session {session_id} for user {user_id}")
        return session

    def save_session(self, session_id: str) -> None:
        """保存会话到文件

        Args:
            session_id: 会话ID
        """
        if session_id not in self._sessions:
            self.logger.warning(f"Session {session_id} not found, cannot save")
            return

        session = self._sessions[session_id]
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")

        try:
            # 将会话序列化为JSON
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_active": session.last_active.isoformat(),
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in session.messages
                ]
            }

            # 保存到文件
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Saved session {session_id} with {len(session.messages)} messages")
        except Exception as e:
            self.logger.error(f"Error saving session {session_id}: {e}")

    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """从文件加载会话

        Args:
            session_id: 会话ID

        Returns:
            加载的会话，如果不存在则返回None
        """
        # 如果会话已经在内存中，直接返回
        if session_id in self._sessions:
            return self._sessions[session_id]

        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")

        # 如果文件不存在，返回None
        if not os.path.exists(session_path):
            self.logger.warning(f"Session file {session_path} not found")
            return None

        try:
            # 从文件加载会话数据
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 获取用户ID
            user_id = session_data.get("user_id")
            if not user_id:
                self.logger.error(f"Session file {session_path} does not contain user_id")
                return None

            # 创建新的会话
            session = self.get_or_create_session(user_id=user_id, session_id=session_id)

            # 加载消息
            messages = session_data.get("messages", [])
            for msg_data in messages:
                session.add_message(ChatMessage(
                    role=msg_data.get("role", "user"),
                    content=msg_data.get("content", "")
                ))

            # 更新时间戳
            if "created_at" in session_data:
                session.created_at = datetime.fromisoformat(session_data["created_at"])
            if "last_active" in session_data:
                session.last_active = datetime.fromisoformat(session_data["last_active"])

            self.logger.info(f"Loaded session {session_id} with {len(session.messages)} messages")
            return session
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return None

    async def add_user_memory(self, user_id: str, task: str, insight: str) -> None:
        """直接为用户添加记忆

        Args:
            user_id: 用户ID
            task: 任务描述
            insight: 相关的见解或知识

        Raises:
            RuntimeError: 如果添加记忆失败
        """
        self.logger.info(f"为用户添加记忆 {user_id}: task='{task}', insight='{insight[:50]}...'")

        try:
            # 获取记忆控制器
            memory_controller = self._get_user_memory_controller(user_id)

            # 添加记忆
            await memory_controller.add_memo(task=task, insight=insight)

            self.logger.info(f"成功添加用户记忆: {user_id}")
        except Exception as e:
            error_msg = f"添加用户记忆失败 {user_id}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def retrieve_user_memories(self, user_id: str, task: str, limit: int = 5) -> List[Dict[str, str]]:
        """检索用户相关的记忆

        Args:
            user_id: 用户ID
            task: 当前任务描述
            limit: 返回的最大记忆数量，默认为5

        Returns:
            相关记忆的列表，每个记忆包含task和insight
        """
        self.logger.info(f"检索用户记忆 {user_id} 相关任务: '{task}'")

        # 如果任务为空，返回空列表
        if not task or task.strip() == "":
            self.logger.warning(f"任务描述为空: {user_id}")
            return []

        try:
            # 获取记忆控制器
            memory_controller = self._get_user_memory_controller(user_id)

            # 检索相关记忆
            memos = await memory_controller.retrieve_relevant_memos(task=task, limit=limit)

            # 如果没有找到记忆，返回空列表
            if not memos:
                self.logger.info(f"未找到相关记忆: {user_id}")
                return []

            # 转换为字典列表
            result = []
            for memo in memos:
                memo_dict = {
                    "task": memo.task if hasattr(memo, 'task') else "",
                    "insight": memo.insight if hasattr(memo, 'insight') else ""
                }
                result.append(memo_dict)

            self.logger.info(f"检索到 {len(result)} 条记忆: {user_id}")
            return result
        except Exception as e:
            error_msg = f"检索用户记忆失败 {user_id}: {e}"
            self.logger.error(error_msg)
            return []  # 出错时返回空列表

    async def _create_chat_memory(self, messages: List[ChatMessage]) -> ListMemory:
        """创建聊天记忆，包含历史消息

        Args:
            messages: 聊天消息列表，除最后一条用户消息外

        Returns:
            包含历史消息的ListMemory对象
        """
        # 创建内存对象
        memory = ListMemory()

        # 添加历史对话消息
        for msg in messages:
            role_prefix = "用户" if msg.role == "user" else "助手"
            await memory.add(
                MemoryContent(
                    content=f"{role_prefix}: {msg.content}",
                    mime_type=MemoryMimeType.TEXT
                )
            )

        return memory

    async def chat_stream(self, messages: List[ChatMessage],
                         system_prompt: Optional[str] = None,
                         user_id: str = "default",
                         session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """流式对话生成，支持用户记忆和会话管理

        Args:
            messages: 聊天消息列表，只用于当前请求，不会存储
            system_prompt: 系统提示，如果提供则用于创建代理
            user_id: 用户ID，用于维护用户的记忆体，默认为"default"
            session_id: 会话ID，如果提供则使用指定会话，否则创建新会话

        Yields:
            流式生成的响应片段
        """
        # 确保有消息
        if not messages or messages[-1].role != "user":
            yield "请提供有效的用户消息"
            return

        # 获取用户最后一条消息
        last_user_message = messages[-1].content
        self.logger.info(f"处理用户 {user_id} 的聊天请求: '{last_user_message[:50]}...'")

        # 获取或创建会话
        session = self.get_or_create_session(user_id=user_id, session_id=session_id)
        # 将当前用户消息添加到会话中
        session.add_message(messages[-1])
        try:

            # 创建当前对话的上下文记忆
            # 优先使用会话中的消息，如果会话中没有足够的消息，则使用传入的消息
            session_messages = session.get_messages()
            context_messages = session_messages[:-1] if len(session_messages) > 1 else messages[:-1]

            # 创建包含上下文的记忆列表
            memories = []

            # 添加用户的Teachability记忆
            # teachability = self._get_user_teachability(user_id)
            # memories.append(teachability)
            #
            # # 如果有上下文消息，创建并添加聊天上下文记忆
            if context_messages:
                chat_context = await self._create_chat_memory(context_messages)
                memories.append(chat_context)

            # 使用包含上下文的记忆列表创建新的代理
            agent = AssistantAgent(
                name=f"agent_{user_id}",
                model_client=self.model_client,
                system_message=system_prompt or self.default_system_message,
                model_client_stream=True,  # 启用流式输出
                memory=memories  # 使用包含上下文的记忆列表
            )

            # 初始化变量来收集完整的响应
            full_response = ""
            assistant_message = ChatMessage(role="assistant", content="")

            # 流式生成响应
            async for event in agent.run_stream(task=last_user_message):
                if isinstance(event, ModelClientStreamingChunkEvent):
                    yield event.content
                elif isinstance(event, TaskResult):
                    full_response = event.messages[-1].content

            # 将助手响应添加到会话中
            session.add_message(assistant_message)

            # 保存会话
            self.save_session(session.session_id)

            # 对话结束后，分析是否需要添加新的记忆
            await self._process_potential_memory(user_id, last_user_message, full_response)

        except Exception as e:
            error_msg = f"聊天处理失败 {user_id}: {e}"
            self.logger.error(error_msg)
            yield f"很抱歉，处理您的请求时出现了错误。请稍后再试。"

    async def _process_potential_memory(self, user_id: str, user_message: str, assistant_response: str) -> None:
        """处理潜在的记忆，检测是否需要记住当前对话

        Args:
            user_id: 用户ID
            user_message: 用户消息
            assistant_response: 助手响应
        """
        try:
            # 检测用户是否要求记住某些信息
            memory_keywords = [
                "记住", "记住我", "记住这个", "记住我的", "记录", "保存", "笔记", "学习",
                "remember", "memorize", "keep in mind", "note", "save", "learn"
            ]

            # 检测助手是否确认记住
            confirmation_keywords = [
                "我已经记住", "我已记录", "我记住了", "已保存", "我会记住",
                "I've remembered", "I've noted", "I'll remember"
            ]

            # 如果用户要求记忆且助手确认了记忆
            if (any(keyword in user_message.lower() for keyword in memory_keywords) and
                any(keyword in assistant_response.lower() for keyword in confirmation_keywords)):
                self.logger.info(f"检测到记忆请求: {user_id}")

                # 添加记忆
                await self.add_user_memory(
                    user_id=user_id,
                    task=user_message,
                    insight=assistant_response
                )
        except Exception as e:
            # 记录错误但不中断流程
            self.logger.error(f"处理潜在记忆失败 {user_id}: {e}")

    async def get_all_user_memories(self, user_id: str) -> List[Dict[str, str]]:
        """获取用户的所有记忆

        Args:
            user_id: 用户ID

        Returns:
            用户所有记忆的列表
        """
        self.logger.info(f"获取用户所有记忆: {user_id}")

        try:
            # 使用空任务检索所有记忆
            return await self.retrieve_user_memories(user_id, task="", limit=100)
        except Exception as e:
            error_msg = f"获取用户所有记忆失败 {user_id}: {e}"
            self.logger.error(error_msg)
            return []

    async def delete_user_memory(self, user_id: str) -> bool:
        """删除用户的所有记忆

        Args:
            user_id: 用户ID

        Returns:
            操作是否成功
        """
        self.logger.info(f"删除用户所有记忆: {user_id}")

        try:
            # 删除记忆控制器实例
            if user_id in self._user_memory_controllers:
                del self._user_memory_controllers[user_id]

            # 删除Teachability实例
            if user_id in self._user_teachability:
                del self._user_teachability[user_id]

            # 删除代理实例
            if user_id in self._user_agents:
                del self._user_agents[user_id]

            # 删除记忆文件
            memory_path = os.path.join(self.memories_dir, f"{user_id}.json")
            if os.path.exists(memory_path):
                os.remove(memory_path)

            self.logger.info(f"成功删除用户记忆: {user_id}")
            return True
        except Exception as e:
            error_msg = f"删除用户记忆失败 {user_id}: {e}"
            self.logger.error(error_msg)
            return False

    async def direct_chat(self, user_id: str, message: str, system_prompt: Optional[str] = None) -> str:
        """直接聊天功能，不使用流式响应，适用于API调用

        Args:
            user_id: 用户ID
            message: 用户消息
            system_prompt: 可选的系统提示

        Returns:
            助手的完整响应
        """
        self.logger.info(f"直接聊天: {user_id} - '{message[:50]}...'")

        try:
            # 创建包含上下文的记忆列表
            memories = []

            # 添加用户的Teachability记忆
            teachability = self._get_user_teachability(user_id)
            memories.append(teachability)

            # 创建新的代理
            agent = AssistantAgent(
                name=f"agent_{user_id}",
                model_client=self.model_client,
                system_message=system_prompt or self.default_system_message,
                memory=memories
            )

            # 执行非流式对话
            response, _ = await agent.run(task=message)

            # 处理潜在的记忆
            await self._process_potential_memory(user_id, message, response)

            return response
        except Exception as e:
            error_msg = f"直接聊天失败 {user_id}: {e}"
            self.logger.error(error_msg)
            return "很抱歉，处理您的请求时出现了错误。请稍后再试。"

    async def interactive_console(self, user_id: str = "console_user", system_prompt: Optional[str] = None) -> None:
        """启动交互式控制台模式

        Args:
            user_id: 用户ID，默认为"console_user"
            system_prompt: 可选的系统提示
        """
        print(f"启动与用户 {user_id} 的交互式对话。输入'exit'或'quit'退出。")

        # 创建包含上下文的记忆列表
        memories = []

        # 添加用户的Teachability记忆
        teachability = self._get_user_teachability(user_id)
        memories.append(teachability)

        # 创建新的代理
        agent = AssistantAgent(
            name=f"agent_{user_id}",
            model_client=self.model_client,
            system_message=system_prompt or self.default_system_message,
            memory=memories
        )

        while True:
            user_input = input("\n用户: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # 使用Console UI显示流式输出
            await Console(agent.run_stream(task=user_input))

            # 处理潜在的记忆
            full_response = ""  # 此处需要实现方法获取完整响应
            await self._process_potential_memory(user_id, user_input, full_response)