# 华侨大学智能体综合应用平台

## 项目简介
这是一个基于大语言模型的智能体综合应用平台，提供多种智能体服务，包括智能客服、数据分析、知识库问答和文案创作等功能。

## 技术栈
- 前端：React + TypeScript + TailwindCSS + Vite
- 后端：Python + FastAPI
- 数据库：MySQL + Milvus
- 文件存储：Minio
- 部署：Docker

## 项目结构
```
.
├── frontend/          # 前端项目
├── backend/           # 后端项目
├── docker/            # Docker相关配置
└── docs/              # 项目文档
```

## 快速开始
1. 安装依赖
```bash
# 前端
cd frontend
npm install

# 后端
cd backend
pip install -r requirements.txt
```

2. 启动服务
```bash
# 前端开发服务器
cd frontend
npm run dev

# 后端服务
cd backend
uvicorn main:app --reload
```

## 环境要求
- Node.js >= 16
- Python >= 3.8
- Docker & Docker Compose
- MySQL >= 8.0
- Milvus >= 2.0
- Minio 