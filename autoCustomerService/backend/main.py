from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.chat import router as chat_router
from routers.auth import router as auth_router
from routers.file_upload import router as file_upload_router
from config import Settings  # 确保从 config 导入 Settings
import os

# 验证 Settings 是否正确加载
settings = Settings()  # 确保实例化 Settings 对象
if not hasattr(settings, "MINIO_ENDPOINT"):
    raise AttributeError("Settings 缺少 MINIO_ENDPOINT 属性，请检查 config.py 文件。")
if not hasattr(settings, "MINIO_ACCESS_KEY"):
    raise AttributeError("Settings 缺少 MINIO_ACCESS_KEY 属性，请检查 config.py 文件。")
if not hasattr(settings, "MINIO_SECRET_KEY"):
    raise AttributeError("Settings 缺少 MINIO_SECRET_KEY 属性，请检查 config.py 文件。")
if not hasattr(settings, "MINIO_BUCKET"):
    raise AttributeError("Settings 缺少 MINIO_BUCKET 属性，请检查 config.py 文件。")

app = FastAPI(
    title="Auto Customer Service",
    description="智能客服系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册路由
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(file_upload_router, prefix="/api/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Welcome to Auto Customer Service API"} 

# 确保运行 uvicorn 时指定根目录
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir="C:\\workspace\\autoCustomerService\\backend")
