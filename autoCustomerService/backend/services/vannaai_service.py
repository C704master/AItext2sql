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
        chromadb_config = {'persistent': chromadb_data_path}
        ChromaDB_VectorStore.__init__(self, config=chromadb_config)

        # 大模型组件 的 配置参数
        llm_config = {'api_key': api_key, 'model': model}
        OpenAI_Chat.__init__(self, client=client, config=llm_config)

    def optimize_sql_query(
            self,
            question: str
    ) -> str:
        prompt = f"""你是一个资深的SQL问题优化专家，请你一步一步遵循以下提示，优化SQL问题，最后返回一个尽量按照下面要求的SQL问题：
                    1. **明确性和具体性**：确保提问明确具体，使用具体的表名和字段名，提供完整的上下文信息。\n
                    2. ** 可执行性和可行性 **：确保提问可以通过标准的SQL语句实现，包含所有必要的条件和过滤条件。
                    3. ** 逻辑性和一致性 **：检查提问中的逻辑关系是否清晰，条件是否一致，避免逻辑矛盾。
                    4. ** 简洁性和直接性 **：使用简洁明了的语言描述问题，直接指出核心问题，避免冗长和复杂表述。
                    5. ** 相关性和针对性 **：确保提问与数据库结构和数据紧密相关，明确指出涉及的具体数据表和字段。
                    6. ** 标准化和规范化 **：使用标准的SQL术语和语法，遵循SQL的最佳实践和规范。
                    7. ** 完整性和详尽性 **：确保提问包含所有必要的细节，检查是否有遗漏的关键信息。
                    8. ** 可验证性和测试性 **：确保提问可以通过实际执行SQL语句来验证结果，提供必要的测试数据或场景。"""
        prompt += f"\n\nSQL问题：{question}"
        return self.submit_prompt(self, prompt=prompt)


# 实例化 MyVanna
vn = MyVanna(api_key=openai_api_key, model=openai_model, client=deepseek_client)
# 连接 MySQL 数据库
vn.connect_to_mysql(host=host_name, user=user_name, password=user_password, dbname=db_name, port=port_number)


# 将vanna基类的各个函数 拆解出来 ，变成 各个服务

# 判断 SQL 是否有效
def is_sql_valid(query: str) -> bool:
    return vn.is_sql_valid(query)


# 1.优化 SQL 问题
def optimize_sql_question(user_question: str) -> str:
    """优化用户SQL提问"""

    return vn.optimize_sql_query(user_question)


# 2.根据 SQL问题， 生成 “SQL查询分析报告”

def generate_sql_question_analysis_report() -> str:
    """生成SQL问题分析报告"""

    return vn.generate_sql_question_analysis_report()

# 3.生成 SQL

# 4.根据生成的 SQL， 生成 “SQL解释报告”

# 5.执行生成的 SQL

# 6.将 SQL 执行结果， 生成 “SQL执行结果报告”

# 7.将 SQL 执行结果， 生成 “结果图表”
