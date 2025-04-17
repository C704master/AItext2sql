from typing import AsyncGenerator
import asyncio
import openai
import httpx
from config import settings


class LLMService:
    def __init__(self):
        # 创建自定义的 httpx 客户端
        http_client = httpx.Client(
            base_url=settings.DEEPSEEK_API_BASE,
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
        )

        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
            http_client=http_client
        )
        self.model = settings.DEEPSEEK_MODEL
        self.conversation_history = []

    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """流式对话处理"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的客服助手，请用专业、友好的语气回答用户的问题。"},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"发生错误: {str(e)}"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []