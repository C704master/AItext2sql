from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from minio import Minio
from minio.error import S3Error
import io
from config import settings

# 先定义router
router = APIRouter()

# 初始化 Minio 客户端
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_extension}"
        
        # 读取文件内容
        file_content = await file.read()
        
        # 上传到 Minio
        minio_client.put_object(
            settings.MINIO_BUCKET,
            filename,
            io.BytesIO(file_content),
            len(file_content),
            content_type=file.content_type
        )
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            content_type=file.content_type,
            size=len(file_content)
        )
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """下载文件"""
    try:
        # 获取文件对象
        file_obj = minio_client.get_object(
            settings.MINIO_BUCKET,
            f"{file_id}"
        )
        
        # 获取文件元数据
        file_stat = minio_client.stat_object(
            settings.MINIO_BUCKET,
            f"{file_id}"
        )
        
        return StreamingResponse(
            file_obj,
            media_type=file_stat.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_stat.metadata.get("x-amz-meta-original-filename", file_id)}"'
            }
        )
    except S3Error as e:
        raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    """删除文件"""
    try:
        minio_client.remove_object(
            settings.MINIO_BUCKET,
            f"{file_id}"
        )
        return {"message": "文件删除成功"}
    except S3Error as e:
        raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 