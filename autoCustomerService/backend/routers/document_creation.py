from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import openai
import json
import os
from datetime import datetime

from database import get_db
from models import DocumentTemplate, ChatHistory, User
from routers.auth import oauth2_scheme
from config import settings

router = APIRouter()

class DocumentRequest(BaseModel):
    template_id: int
    parameters: dict
    additional_requirements: str = ""

class DocumentResponse(BaseModel):
    content: str
    download_url: str

@router.get("/templates", response_model=List[DocumentTemplate])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    templates = db.query(DocumentTemplate).offset(skip).limit(limit).all()
    return templates

@router.post("/create")
async def create_document(
    request: DocumentRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    async def generate():
        try:
            # 获取模板
            template = db.query(DocumentTemplate).filter(DocumentTemplate.id == request.template_id).first()
            if not template:
                raise HTTPException(status_code=404, detail="模板不存在")
            
            # 使用OpenAI API生成文档内容
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""你是一个专业的文档创作助手。请根据以下模板和参数生成文档：
模板内容：
{template.template_content}

参数：
{json.dumps(request.parameters, ensure_ascii=False)}

额外要求：
{request.additional_requirements}

请生成专业、规范的文档内容。"""},
                    {"role": "user", "content": "请生成文档内容"}
                ],
                stream=True
            )
            
            full_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{timestamp}.txt"
            
            # 保存文件
            file_path = os.path.join("static", "documents", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            
            # 生成下载URL
            download_url = f"/static/documents/{filename}"
            
            # 保存到数据库
            db_chat = ChatHistory(
                user_id=1,  # 这里需要从token中获取用户ID
            )
            db.add(db_chat)
            db.commit()
            
            yield f"data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/templates")
async def create_template(
    name: str,
    description: str,
    template_content: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # 创建新模板
    template = DocumentTemplate(
        name=name,
        description=description,
        template_content=template_content,
        created_by=1  # 这里需要从token中获取用户ID
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template 