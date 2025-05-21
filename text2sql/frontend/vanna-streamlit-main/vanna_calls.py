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
DB_TYPE = os.getenv("DB_TYPE")

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
    return vn


@st.cache_data(show_spinner="生成样例问题中，请稍等")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()


# 已重写
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


# 已重写
@st.cache_data(show_spinner="正在生成画图代码中，请稍等")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


# 已重写
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


# 以下函数是自定义的新函数，用于增强之前的函数功能

# 生成SQL问题解析报告
@st.cache_data(show_spinner="生成SQL问题解析报告中，请稍等")
def generate_sql_question_report_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql_question_report(question=question)


# 生成SQL
@st.cache_data(show_spinner="采用特质化prompt模板，生成SQL中，请稍等")
def generate_sql_v2_cached(question: str, context: str, analysis_report: str):
    vn = setup_vanna()
    return vn.generate_sql_v2(question=question, context=context, analysis_report=analysis_report)


# 生成可视化推荐报告
@st.cache_data(show_spinner="生成可视化推荐报告中，请稍等")
def generate_result_visual_command_v2_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_result_visual_command_v2(question=question, sql=sql, df=df)


# 生成特质化plotly画图代码
@st.cache_data(show_spinner="正在生成特质化plotly画图代码中，请稍等")
def generate_plotly_code_v2_cached(question: str = None, sql: str = None, df_metadata: str = None,
                                   visual_command: str = None, **kwargs):
    vn = setup_vanna()
    code = vn.generate_plotly_code_v2(question=question, sql=sql, df_metadata=df_metadata,
                                      visual_command=visual_command, **kwargs)
    return code


# 执行画图代码，返回图像对象
@st.cache_data(show_spinner="正在特质化plotly画图代码中，请稍等")
def generate_plot_v2_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure_v2(plotly_code=code, df=df)


# 解释SQL语句
@st.cache_data(show_spinner="正在特质化plotly画图代码中，请稍等")
def generate_sql_explain_v2_cached(sql):
    vn = setup_vanna()
    return vn.explain_sql(sql=sql)


# 生成SQL查询总结报告
@st.cache_data(show_spinner="生成总结中，请稍等")
def generate_summary_v2_cached(question, df, sql):
    vn = setup_vanna()
    return vn.generate_summary_v2(question=question, df=df, sql=sql)


# 执行SQL，返回SQL查询结果
@st.cache_data(show_spinner="执行SQL中，请稍等")
def run_sql_v2_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

# 查找上下文信息
@st.cache_data(show_spinner="查找上下文信息中，请稍等")
def find_schema_cached(question):
    vn = setup_vanna()
    return vn.find_schema(question=question)