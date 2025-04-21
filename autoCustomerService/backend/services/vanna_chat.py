from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# 从 .env 文件中读取配置
openai_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_model = os.getenv("DEEPSEEK_MODEL")
database_url = os.getenv("DATABASE_URL")

# 初始化 MyVanna 类
vn = MyVanna(config={
    'api_key': openai_api_key,
    'model': openai_model,
    'database_url': database_url
})

# 连接数据库（假设 ChromaDB_VectorStore 支持数据库连接）
vn.connect_to_mssql(database_url)

from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()