import vanna

from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()
# 从 .env 文件中读取配置
openai_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_model = os.getenv("DEEPSEEK_MODEL")
database_url = os.getenv("DATABASE_URL")

from vanna.remote import VannaDefault
vn = VannaDefault(model='chinook', api_key=vanna.get_api_key('568421706@qq.com'))
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask("What are the top 10 albums by sales?")




from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run()

