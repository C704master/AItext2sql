from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., description="知识库名称")


class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""
    id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    created_at: float = Field(..., description="创建时间戳")
    document_count: int = Field(0, description="文档数量")


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    uploaded_at: float = Field(..., description="上传时间戳")


class KnowledgeBaseQuery(BaseModel):
    """知识库查询请求"""
    query: str = Field(..., description="查询内容")


class KnowledgeBaseQueryResponse(BaseModel):
    """知识库查询响应"""
    query: str = Field(..., description="查询内容")
    response: str = Field(..., description="回答内容")
    timestamp: float = Field(..., description="查询时间戳") 