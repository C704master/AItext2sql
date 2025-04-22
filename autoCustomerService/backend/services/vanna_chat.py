from vanna.openai import OpenAI_Chat
from vanna.milvus.milvus_vector import Milvus_VectorStore
from dotenv import load_dotenv
import os
import requests

# 加载 .env 文件中的环境变量
load_dotenv()

class MyVanna(Milvus_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        super().__init__(config)
        self.config = config or {}

    def ask(self, question):
        # 调用 DeepSeek API
        url = self.config.get("base_url", "https://api.deepseek.com/v1/chat")
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": question}]
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["output"]["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

# 从 .env 文件中读取配置
openai_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_model = os.getenv("DEEPSEEK_MODEL")
database_url = os.getenv("DATABASE_URL")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL")

# 初始化 MyVanna 类
vn = MyVanna(config={
    'api_key': openai_api_key,
    'model': openai_model,
    'database_url': database_url,
    'base_url': deepseek_base_url
})

# 连接数据库（假设 Milvus_VectorStore 支持数据库连接）
vn.connect_to_mysql(database_url)

from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()