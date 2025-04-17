from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from services.llm_service import LLMService
from models import ChatHistory, ChatHistoryResponse
from database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()
llm_service = LLMService()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式对话接口"""
    try:
        async def generate():
            try:
                async for chunk in llm_service.chat_stream(request.message):
                    data = json.dumps({"content": chunk}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            except Exception as e:
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/clear")
async def clear_chat():
    """清除对话历史"""
    llm_service.clear_history()
    return {"message": "对话历史已清除"}

@router.get("/chat/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取聊天历史"""
    chat_history = db.query(ChatHistory).offset(skip).limit(limit).all()
    return chat_history 