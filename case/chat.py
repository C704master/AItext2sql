from typing import List, Optional, Dict
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """单条聊天消息模型"""
    role: str  # 'user' 或 'assistant'
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage]  # 当前请求的消息，只用于当前请求，不会存储
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    user_id: Optional[str] = "default"  # 用户ID，用于维护用户的记忆体
    session_id: Optional[str] = None  # 会话ID，如果提供则使用指定会话，否则创建新会话


class ChatResponse(BaseModel):
    """聊天响应模型"""
    content: str
    role: str = "assistant"


class MemoryAddRequest(BaseModel):
    """添加记忆请求模型"""
    user_id: str
    task: str
    insight: str


class MemoryRetrieveRequest(BaseModel):
    """检索记忆请求模型"""
    user_id: str
    task: str


class SessionRequest(BaseModel):
    """会话请求模型"""
    user_id: str
    session_id: Optional[str] = None


class SessionResponse(BaseModel):
    """会话响应模型"""
    session_id: str
    user_id: str
    created_at: str
    last_active: str
    messages: List[Dict[str, str]]