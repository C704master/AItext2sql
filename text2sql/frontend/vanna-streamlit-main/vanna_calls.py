import streamlit as st

from vanna.remote import VannaDefault




from openai import OpenAI
from dotenv import load_dotenv
import os

from vannaai_service import MyVanna

# 加入后端路径
# import sys
# sys.path.append('C:\\workspace\\text2sql')



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
# 定义数据库类型（可配置）
DB_TYPE = "MySQL"  # 可选值: "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server"



# 初始化 OpenAI 客户端
deepseek_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url,
)

# 初始化Vanna，设置缓存时间为1小时
@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = MyVanna(api_key=openai_api_key, model=openai_model, client=deepseek_client)
    # # 连接 MySQL 数据库
    vn.connect_to_mysql(host=host_name, user=user_name, password=user_password, dbname=db_name, port=port_number)

    # vn = VannaDefault(api_key=st.secrets.get("VANNA_API_KEY"), model='chinook')
    # vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    return vn

@st.cache_data(show_spinner="生成样例问题中，请稍等")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()


@st.cache_data(show_spinner="生成SQL中，请稍等")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="检查SQL是否合法中，请稍等")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="执行SQL中，请稍等")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="检测是否生成图表中，请稍等")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="正在生成画图代码中，请稍等")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


@st.cache_data(show_spinner="正在执行画图代码中，请稍等")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


@st.cache_data(show_spinner="生成历史相似性问题中，请稍等")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="生成总结中，请稍等")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)