import os
import asyncio
import tempfile
import shutil
import time
from typing import List, Dict, Any, Optional
import uuid

import docx2txt
from pypdf import PdfReader
import numpy as np
from nano_graphrag import GraphRAG, QueryParam

from app.core.config import settings


class KnowledgeService:
    """知识库服务，处理文件上传、知识图谱构建和查询"""

    def __init__(self):
        """初始化知识库服务"""
        # 创建知识库工作目录
        os.makedirs(settings.KNOWLEDGE_BASE_DIR, exist_ok=True)
        self.kb_instances = {}  # 存储不同知识库实例 {kb_id: GraphRAG实例}
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """从文件中提取文本
        
        支持PDF、DOCX等格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                pdf = PdfReader(f)
                for page in pdf.pages:
                    text += page.extract_text() + "\n\n"
            return text
            
        elif file_ext == '.docx':
            return docx2txt.process(file_path)
            
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
    
    async def create_knowledge_base(self, name: str) -> Dict[str, Any]:
        """创建新的知识库
        
        Args:
            name: 知识库名称
            
        Returns:
            知识库信息
        """
        kb_id = str(uuid.uuid4())
        kb_dir = os.path.join(settings.KNOWLEDGE_BASE_DIR, kb_id)
        os.makedirs(kb_dir, exist_ok=True)
        
        # 初始化GraphRAG实例
        graph_rag = GraphRAG(
            working_dir=kb_dir,  # 工作目录
        )
        
        # 存储GraphRAG实例
        self.kb_instances[kb_id] = graph_rag
        
        return {
            "id": kb_id,
            "name": name,
            "created_at": os.path.getctime(kb_dir),
            "document_count": 0,
        }
    
    async def upload_document(self, kb_id: str, file, filename: str) -> Dict[str, Any]:
        """上传文档到知识库
        
        Args:
            kb_id: 知识库ID
            file: 上传的文件
            filename: 文件名
            
        Returns:
            文档信息
        """
        if kb_id not in self.kb_instances:
            raise ValueError(f"知识库不存在: {kb_id}")
            
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # 保存上传的文件内容
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            # 提取文本内容
            content = self._extract_text_from_file(tmp_path)
            
            # 获取GraphRAG实例
            graph_rag = self.kb_instances[kb_id]
            
            # 将文档添加到知识图谱
            doc_id = filename.replace(".", "_") + "_" + str(uuid.uuid4())[:8]
            await graph_rag.add_document(content, doc_id)
            
            return {
                "id": doc_id,
                "filename": filename,
                "size": len(content),
                "uploaded_at": os.path.getctime(tmp_path),
            }
        finally:
            # 删除临时文件
            os.unlink(tmp_path)
    
    async def query_knowledge_base(self, kb_id: str, query: str) -> Dict[str, Any]:
        """查询知识库
        
        Args:
            kb_id: 知识库ID
            query: 查询文本
            
        Returns:
            查询结果
        """
        if kb_id not in self.kb_instances:
            raise ValueError(f"知识库不存在: {kb_id}")
            
        # 获取GraphRAG实例
        graph_rag = self.kb_instances[kb_id]
        
        # 设置查询参数
        param = QueryParam(
            max_explore_iteration=2,  # 最大探索迭代次数
            local_radius=1,           # 本地半径
            local_max_nodes=15,       # 本地最大节点数
            global_max_consider_community=10,  # 全局最大考虑社区数
        )
        
        # 执行查询
        response = await graph_rag.query(query, param=param)
        
        return {
            "query": query,
            "response": response,
            "timestamp": time.time(),
        }
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """列出所有知识库
        
        Returns:
            知识库列表
        """
        kb_list = []
        
        for kb_id in os.listdir(settings.KNOWLEDGE_BASE_DIR):
            kb_path = os.path.join(settings.KNOWLEDGE_BASE_DIR, kb_id)
            if os.path.isdir(kb_path):
                # 获取或创建GraphRAG实例
                if kb_id not in self.kb_instances:
                    try:
                        self.kb_instances[kb_id] = GraphRAG(
                            working_dir=kb_path,
                            debug_mode=False,
                        )
                    except Exception as e:
                        print(f"加载知识库 {kb_id} 失败: {str(e)}")
                        continue
                
                # 添加到列表
                kb_list.append({
                    "id": kb_id,
                    "name": f"知识库-{kb_id[:6]}",
                    "created_at": os.path.getctime(kb_path),
                    "document_count": len(os.listdir(os.path.join(kb_path, "documents"))) if os.path.exists(os.path.join(kb_path, "documents")) else 0,
                })
        
        return kb_list
    
    def get_knowledge_base(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """获取知识库信息
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            知识库信息，如果不存在则返回None
        """
        kb_path = os.path.join(settings.KNOWLEDGE_BASE_DIR, kb_id)
        if not os.path.isdir(kb_path):
            return None
            
        # 获取或创建GraphRAG实例
        if kb_id not in self.kb_instances:
            try:
                self.kb_instances[kb_id] = GraphRAG(
                    working_dir=kb_path,
                    debug_mode=False,
                )
            except Exception as e:
                print(f"加载知识库 {kb_id} 失败: {str(e)}")
                return None
        
        return {
            "id": kb_id,
            "name": f"知识库-{kb_id[:6]}",
            "created_at": os.path.getctime(kb_path),
            "document_count": len(os.listdir(os.path.join(kb_path, "documents"))) if os.path.exists(os.path.join(kb_path, "documents")) else 0,
        } 