import chromadb
from openai import OpenAI
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from vanna.openai import OpenAI_Chat
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 配置参数
openai_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_model = os.getenv("DEEPSEEK_MODEL")
database_url = os.getenv("DATABASE_URL")
openai_base_url = os.getenv("DEEPSEEK_BASE_URL")
host_name = os.getenv("MYSQL_HOST")
user_name = os.getenv("mysql_user")
user_password = os.getenv("mysql_password")
db_name = os.getenv("MYSQL_DATABASE")
port_number = 3306
chromadb_data_path = os.getenv("CHROMA_DATA_PATH")

# 初始化 OpenAI 客户端
deepseek_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url,
)


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, api_key, model, client):
        # 向量数据库 的 配置参数
        chromadb_config = {'persistent' : chromadb_data_path}
        ChromaDB_VectorStore.__init__(self,config=chromadb_config)

        # 大模型组件 的 配置参数
        llm_config = {'api_key': api_key, 'model': model}
        OpenAI_Chat.__init__(self, client=client, config=llm_config)


# 实例化 MyVanna
vn = MyVanna(api_key=openai_api_key, model=openai_model, client=deepseek_client)
# 连接 MySQL 数据库
vn.connect_to_mysql(host=host_name, user=user_name, password=user_password, dbname=db_name, port=port_number)


# See the documentation for other options

def main():
    # MySQL database credentials
    # vn.dialect = "MySQL"

    # vn.ask("Please give me the Title of all the album",allow_llm_to_see_data=True)

    app = VannaFlaskApp(vn, allow_llm_to_see_data=True)
    app.run()


if __name__ == "__main__":
    main()