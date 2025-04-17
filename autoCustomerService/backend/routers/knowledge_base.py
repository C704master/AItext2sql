from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
from minio import Minio
from pymilvus import connections, Collection
import uuid

from database import get_db
from models import KnowledgeBase, User
from routers.auth import oauth2_scheme
from config import settings

router = APIRouter()

# 初始化Minio客户端
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

# 初始化Milvus连接
connections.connect(
    alias="default",
    host=settings.MILVUS_HOST,
    port=settings.MILVUS_PORT
)

class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str

class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    content: str
    file_path: str
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # 验证文件类型
    if not file.filename.endswith(('.txt', '.pdf', '.docx', '.md')):
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 上传到Minio
    try:
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            file.file,
            file.size,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    # 保存到数据库
    file_path = f"{settings.MINIO_BUCKET_NAME}/{unique_filename}"
    db_knowledge = KnowledgeBase(
        title=file.filename,
        content="",  # 这里可以添加文件内容提取的逻辑
        file_path=file_path,
        created_by=1  # 这里需要从token中获取用户ID
    )
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    
    return {"message": "文件上传成功", "id": db_knowledge.id}

@router.get("/", response_model=List[KnowledgeBaseResponse])
async def list_knowledge(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    knowledge_list = db.query(KnowledgeBase).offset(skip).limit(limit).all()
    return knowledge_list

@router.get("/{knowledge_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    if knowledge is None:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    return knowledge

@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    if knowledge is None:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    # 从Minio删除文件
    try:
        minio_client.remove_object(settings.MINIO_BUCKET_NAME, knowledge.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")
    
    db.delete(knowledge)
    db.commit()
    return {"message": "知识库条目已删除"} 