import json

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
# 定义数据库类型（可配置）
DB_TYPE = "MySQL"  # 可选值: "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server"



# 初始化 OpenAI 客户端
deepseek_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url,
)


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):

    def __init__(self, api_key, model, client, db_type=DB_TYPE, db_schema=None):
        # 向量数据库 的 配置参数
        # 向量数据库存储数据的路径path 向量数据库的模式调为持久化 persistent
        chromadb_config = {'path':chromadb_data_path,'client':'persistent'}
        ChromaDB_VectorStore.__init__(self, config=chromadb_config)

        # 大模型组件 的 配置参数
        llm_config = {'api_key': api_key, 'model': model}
        OpenAI_Chat.__init__(self, client=client, config=llm_config)

        # 关系型数据库 的 配置参数
        self.db_type = db_type
        self.db_schema = db_schema

    # def optimize_sql_query(
    #         self,
    #         question: str
    # ) -> str:
    #     """优化用户SQL提问，这个函数效果不是很好，但是实验跑通了"""
    #     prompt = f"""你是一个资深的SQL问题优化专家，请你一步一步遵循以下提示，优化SQL问题，最后返回一个尽量按照下面要求的SQL问题：
    #                 1. **明确性和具体性**：确保提问明确具体，使用具体的表名和字段名，提供完整的上下文信息。\n
    #                 2. ** 可执行性和可行性 **：确保提问可以通过标准的SQL语句实现，包含所有必要的条件和过滤条件。
    #                 3. ** 逻辑性和一致性 **：检查提问中的逻辑关系是否清晰，条件是否一致，避免逻辑矛盾。
    #                 4. ** 简洁性和直接性 **：使用简洁明了的语言描述问题，直接指出核心问题，避免冗长和复杂表述。
    #                 5. ** 相关性和针对性 **：确保提问与数据库结构和数据紧密相关，明确指出涉及的具体数据表和字段。
    #                 6. ** 标准化和规范化 **：使用标准的SQL术语和语法，遵循SQL的最佳实践和规范。
    #                 7. ** 完整性和详尽性 **：确保提问包含所有必要的细节，检查是否有遗漏的关键信息。
    #                 8. ** 可验证性和测试性 **：确保提问可以通过实际执行SQL语句来验证结果，提供必要的测试数据或场景。"""
    #     prompt += f"\n\nSQL问题：{question}"
    #     role = "user"
    #     # 最后要传入的 prompt 是一个列表，包含多个消息字典，每个字典包含键 "content"
    #     prompts = [
    #         {"content": prompt, "role": role},
    #     ]
    #     return self.submit_prompt(prompt=prompts, model=openai_model)

    # 创建一个查找表信息的函数

    def find_schema(self,
                                              question: str) -> str:
        """定义一个函数，用于查找表信息"""
        # 向量数据库中查找表信息
        ddl_documents = ChromaDB_VectorStore._extract_documents(
            self.ddl_collection.query(
                query_texts=[question],
                n_results=5, # 返回前5个结果
            )
        )
        if ddl_documents:
            # 将前5个文档的定义信息拼接成一个字符串
            table_definitions = []
            for doc in ddl_documents[:5]:  # 只取前5个文档
                if isinstance(doc, dict):
                    table_definitions.append(json.dumps(doc))
                else:
                    table_definitions.append(str(doc))

            # 将所有文档的定义信息拼接成一个字符串
            concatenated_definitions = " \n\n ".join(table_definitions)
            return concatenated_definitions
        else:
            return "No table definition found."





    def analyse_sql_question(self,
                                              question: str) -> str:
        """生成SQL问题分析报告"""
        # 找向量数据库中有没有表的信息
        self.db_schema = self.find_schema(question)

        prompt = f"""
            你是一名专业的数据库分析与生成SQL命令的分析专家。你的任务是深入分析用户的自然语言查询，并结合给定的数据库表结构信息，生成一份完整详细的关于生成SQL命令的分析报告。这份报告将作为后续指导另一个大模型生成精确SQL命令的关键依据。
            **核心目标：**
            
            基于用户查询和数据库结构，输出一份结构化的报告，详细描述如何将用户意图转化为SQL查询的关键步骤和考虑因素。
            
            **你需要处理以下信息：**
            
            * **数据库类型：** {self.db_type}
            * **数据库结构：**
                ```sql
                {self.db_schema}
                ```
            * **用户原始问题：** [query]
            
            **请按照以下步骤进行分析并生成报告：**
            
            1.  **查询意图深度分析：**
                * 详细描述用户提出的自然语言查询的核心意图。用户希望从数据库中检索或操作哪些数据？他们的最终目标是什么？
                * 识别查询中涉及的关键概念和实体。
            
            2.  **主要实体与关系识别：**
                * 根据用户查询和数据库结构，识别出查询所涉及的主要实体（对应数据库中的表）。
                * 分析这些实体之间的关系（例如，一对一、一对多、多对多），并确定可能需要进行的表连接。
            
            3.  **所需表与字段精确确定：**
                * 列出用户查询明确或暗示需要使用的所有表名。
                * 列出需要从这些表中检索的所有字段名。如果需要进行计算或聚合操作，也请在此处说明。
            
            4.  **潜在歧义与缺失信息识别：**
                * 分析用户查询中可能存在的歧义或不明确之处。例如，用户是否使用了模糊的术语、未指定具体的条件、或者查询范围不清晰？
                * 指出生成完整且准确SQL语句所需的任何缺失信息。
            
            5.  **SQL操作类型与结构初步构思：**
                * 基于对用户意图的理解，确定需要执行的SQL操作类型（例如：SELECT, INSERT, UPDATE, DELETE）。对于查询操作，需要进一步考虑是否需要聚合函数（SUM, AVG, COUNT, MAX, MIN）、分组（GROUP BY）、排序（ORDER BY）、限制结果数量（LIMIT）等。
                * 初步构思SQL查询语句的基本结构框架，包括涉及的表、大致的连接方式和主要的条件逻辑。
            
            6.  **报告输出 - 请严格按照以下格式：**

            ### SQL 命令生成报告
        
            #### 1. 用户原始问题：
            [在此处填写用户的自然语言查询]
        
            #### 2. 数据库类型：
            {self.db_type}
        
            #### 3. 数据库结构：
            ```sql
            {self.db_schema}
            ```
        
            #### 4. 查询意图描述：
            [对用户查询意图进行详细描述]
        
            #### 5. 需要使用的表名列表：
            - [表名1]
            - [表名2]
            - ...
        
            #### 6. 需要使用的字段列表：
            - 表名1: [字段1], [字段2], ...
            - 表名2: [字段1], [字段2], ...
            - ...
            （请注明是否需要使用聚合函数，例如：`SUM(sales_amount)`）
        
            #### 7. 需要的表连接描述：
            - [如果需要连接，描述连接的表以及连接条件（例如：`orders` 表通过 `user_id` 连接到 `users` 表）]
            - [如果不需要连接，说明原因]
        
            #### 8. 筛选条件描述：
            - [描述用户查询中隐含或明确要求的筛选条件 (例如：`WHERE status = '已发货'`)]
            - [如果存在多个筛选条件，请说明它们之间的逻辑关系 (例如：AND, OR)]
        
            #### 9. 分组描述：
            - [描述是否需要对结果进行分组 (GROUP BY)，以及分组的字段是什么]
            - [说明分组后是否需要进行聚合操作]
        
            #### 10. 排序描述：
            - [描述是否需要对结果进行排序 (ORDER BY)，以及排序的字段和排序方式 (ASC/DESC)]
        
            #### 11. 潜在歧义与缺失信息：
            - [列出用户查询中存在的任何潜在歧义，并说明可能导致不同SQL解释的情况]
            - [指出生成完整SQL语句所需的缺失信息，并说明需要用户提供哪些额外细节]
        
            #### 12. 初步的SQL查询结构草案：
            ```sql
            -- 基于以上分析的初步 SQL 查询结构
            SELECT [在此处填写需要选择的字段]
            FROM [在此处填写需要使用的表名]
            [在此处填写需要的连接 (例如：INNER JOIN table2 ON ...)]
            WHERE [在此处填写筛选条件]
            [在此处填写分组 (例如：GROUP BY ...)]
            [在此处填写排序 (例如：ORDER BY ...)]
            [在此处填写限制结果数量 (例如：LIMIT ...)]
            ;
            ```
        请确保你的报告内容详尽、准确，能够清晰地反映用户查询的意图以及如何将其转化为可执行的SQL命令。这份报告的质量将直接影响后续SQL语句生成的准确性。
        注意：如果用户在第2次、第3次等提出了修改建议，每次不需要将整篇报告输出。
        """
        prompt += f"\n\nSQL问题：{question}"
        role = "user"
        # 最后要传入的 prompt 是一个列表，包含多个消息字典，每个字典包含键 "content"
        prompts = [
            {"content": prompt, "role": role},
        ]
        return self.submit_prompt(prompt=prompts, model=openai_model)

    def generate_sql_v2(self,
                        question: str, context: str, analysis_report: str) -> str:
        """生成SQL"""
        prompt = f"""
        你是一名专业的SQL转换专家。你的任务是基于上下文信息及SQL命令生成报告，将用户的自然语言查询转换为精确的SQL语句。
        
        ## 生成SQL的指导原则：
        
        1.  **严格遵循报告中的分析：** 仔细阅读并理解上述的SQL命令生成报告，包括查询意图、需要使用的表和字段、连接方式、筛选条件、分组和排序要求。
        2.  **生成有效的SQL语句：** 仅输出符合 {self.db_type} 数据库语法的有效SQL语句，不要添加任何额外的解释或说明。
        3.  **准确表达筛选条件：** 报告中如有筛选条件描述，务必在生成的SQL语句中准确实现。
        4.  **正确使用表连接：** 按照报告中"需要的表连接描述"进行表连接，并确保连接条件正确。
        5.  **实现分组和聚合：** 如果报告中指示需要进行分组（GROUP BY）或聚合操作（例如 SUM, COUNT, AVG），请在SQL语句中正确实现。
        6.  **实现排序：** 按照报告中"排序描述"的要求，使用 ORDER BY 子句对结果进行排序。
        7.  **考虑数据库特性：** 生成的SQL语句应符合 {self.db_type} 数据库的特定语法和函数。
        8.  **SQL格式规范：** 使用清晰可读的SQL格式，适当添加换行和缩进，以提高可读性。
        9.  **避免使用不支持的语法：** 不要使用 {self.db_type} 数据库不支持的特殊语法或函数。
        10. **仅生成SQL：** 最终输出结果必须是纯粹的SQL查询语句，没有任何额外的文本。
        
        特别注意：最终只生成一条您认为最符合用户查询需求的SQL语句。
        """
        prompt += f"\n\nSQL问题：{question}"
        prompt += f"\n\nSQL上下文：{context}"
        prompt += f"\n\nSQL分析报告：{analysis_report}"

        role = "user"
        # 最后要传入的 prompt 是一个列表，包含多个消息字典，每个字典包含键 "content"
        prompts = [
            {"content": prompt, "role": role},
        ]
        return self.submit_prompt(prompt=prompts, model=openai_model)

    def explain_sql(self,
                    sql: str) -> str:
        """解释SQL语句的含义"""
        prompt = f"""
        你是一名专业的SQL解释专家，你的任务是以准确、易懂的方式向非技术人员解释给定的SQL语句的含义和作用。
        
        ## 数据库类型
        {self.db_type}
        
        ## 数据库结构
        ```sql
        {self.db_schema}
        ```
        
        ## 用户问题
        [query]
        
        ## 需要解释的SQL语句
        [sql]
        
        ## 规则
        
        1.  **使用通俗易懂的语言：** 解释应该避免使用过于专业或技术性的术语。目标是让没有任何编程或数据库知识的人也能理解。
        2.  **准确且全面地解释：** 确保解释的准确性，并覆盖SQL语句的主要功能和逻辑。
        3.  **解释关键子句：** 针对SQL语句中的每个主要子句（例如 `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `ORDER BY`, `JOIN` 等）解释其作用和目的。
        4.  **说明查询结果：** 清晰地描述执行这条SQL语句后，预计会从数据库中返回什么类型的数据和结果。
        5.  **解释复杂特性：**
            * **聚合函数：** 如果SQL语句中使用了聚合函数（如 `SUM`, `AVG`, `COUNT`, `MAX`, `MIN`），解释这些函数的作用以及它们是如何计算结果的。
            * **表连接：** 如果使用了表连接（如 `JOIN`），解释为什么要进行连接，以及连接是如何根据相关字段将不同表中的数据关联起来的。可以结合数据库结构进行解释。
            * **子查询：** 如果使用了子查询（嵌套查询），解释子查询的目的以及它是如何帮助主查询获取所需数据的。
        6.  **结合数据库结构：** 在解释过程中，可以适当引用提供的数据库表结构，帮助理解表名、字段名的含义以及表之间的关系。例如，解释 `users.name` 时，可以说明 `name` 是 `users` 表中的一个字段，用于存储用户的姓名。
        7.  **保持简洁明了：** 尽量用简短的句子表达清楚意思，避免冗长的描述。解释的长度一般不超过200字。
        8.  **直接解释提供的SQL：** 你的解释应该直接针对用户问题 `[query]` 和 `[sql]` 部分提供的具体SQL代码。
        
        **示例解释框架：**
        
        "这条SQL语句的作用是[整体功能描述]。它首先从 `[表名]` 表中[FROM子句的解释]。然后，它会筛选出满足[WHERE子句的解释]的记录。如果使用了 `GROUP BY`，则会按照[GROUP BY子句的解释]进行分组，并且可能会使用[聚合函数]计算每个组的结果。最后，结果可能会按照[ORDER BY子句的解释]进行排序。总的来说，这条语句会返回[对查询结果的总结性描述]。"
        """
        prompt += f"\n\nSQL语句：{sql}"

        role = "user"
        # 最后要传入的 prompt 是一个列表，包含多个消息字典，每个字典包含键 "content"
        prompts = [
            {"content": prompt, "role": role},
        ]
        return self.submit_prompt(prompt=prompts, model=openai_model)

    def visualization_recommend(self,
                                sql: str, query: str, results_json) -> str:
        prompt = """```
            你是一名专业的数据可视化专家，负责根据提供的用户指令、SQL查询及其结果数据，推荐最合适的数据可视化方式，并给出详细的配置建议。
            
            ## 规则
            
            1.  **分析SQL查询：** 理解SQL查询的目标，例如是进行趋势分析、比较不同类别的数据、展示数据分布还是显示详细数据。
            2.  **分析查询结果数据结构：** 检查返回的数据包含哪些字段，它们的数据类型（数值型、分类型等），以及数据的组织方式（例如，是否包含时间序列、类别标签、数值指标等）。
            3.  **基于数据结构和查询目标推荐可视化类型：**
                * 如果数据涉及**时间序列**且需要展示**趋势**，推荐 `"line"` (折线图)。
                * 如果需要**比较不同类别**的**数值大小**，推荐 `"bar"` (柱状图)。
                * 如果需要展示**各部分占总体的比例**，且类别数量不多，推荐 `"pie"` (饼图)。需要确保数值型字段是总量的一部分。
                * 如果需要展示**两个数值变量之间的关系**或**数据点的分布**，推荐 `"scatter"` (散点图)。
                * 如果数据结构复杂、细节重要，或者无法找到合适的图表类型清晰表达，推荐 `"table"` (表格)。
            4.  **提供详细的可视化配置建议：** 根据选择的可视化类型，提供具体的配置参数。
                * **通用配置：** `"title"` (图表标题，应简洁明了地概括图表内容)。
                * **柱状图 (`"bar"`):**
                    * `"xAxis"` (X轴字段名，通常是分类型字段)。
                    * `"yAxis"` (Y轴字段名，通常是数值型字段)。
                    * `"seriesName"` (系列名称，如果只有一个系列可以省略)。
                * **折线图 (`"line"`):**
                    * `"xAxis"` (X轴字段名，通常是时间或有序的分类型字段)。
                    * `"yAxis"` (Y轴字段名，通常是数值型字段)。
                    * `"seriesName"` (系列名称，如果只有一个系列可以省略)。
                * **饼图 (`"pie"`):**
                    * `"nameField"` (名称字段名，通常是分类型字段，用于显示饼图的标签)。
                    * `"valueField"` (数值字段名，用于计算每个扇区的大小)。
                    * `"seriesName"` (系列名称，如果只有一个系列可以省略)。
                * **散点图 (`"scatter"`):**
                    * `"xAxis"` (X轴字段名，通常是数值型字段)。
                    * `"yAxis"` (Y轴字段名，通常是数值型字段)。
                    * `"seriesName"` (系列名称，如果只有一个系列可以省略)。
                * **表格 (`"table"`):** 不需要特定的坐标轴或系列配置，可以考虑添加 `"columns"` 字段，列出需要在表格中显示的字段名。
            5.  **输出格式必须符合如下JSON格式:**
            
                ```json
                {
                    "type": "可视化类型",
                    "config": {
                        "title": "图表标题",
                        "xAxis": "X轴字段名",
                        "yAxis": "Y轴字段名",
                        "seriesName": "系列名称"
                        // 其他配置参数根据可视化类型添加
                    }
                }
                ```
            
                对于饼图：
            
                ```json
                {
                    "type": "pie",
                    "config": {
                        "title": "图表标题",
                        "nameField": "名称字段名",
                        "valueField": "数值字段名",
                        "seriesName": "系列名称"
                    }
                }
                ```
            
                对于表格：
            
                ```json
                {
                    "type": "table",
                    "config": {
                        "title": "数据表格",
                        "columns": ["字段名1", "字段名2", ...]
                    }
                }
                ```
            
            ## 支持的可视化类型
            
            - `"bar"`: 柱状图
            - `"line"`: 折线图
            - `"pie"`: 饼图
            - `"scatter"`: 散点图
            - `"table"`: 表格(对于不适合图表的数据)
            特别注意：如果用户有对生成的图表有明确的特定要求，一定要严格遵守用户的指令。例如用户明确要求生成饼状图，就不能生成柱状图。
            """
        task = f"""
                ## 用户指令
                 {query}

                ## 待分析的SQL查询
                {sql}

                ## SQL查询结果数据
                ```json
                {results_json}
                ```

                请根据提供的上述信息，分析并输出最合适的可视化类型和配置，输出必须是有效的JSON
                """
        prompt += task
        role = "user"
        # 最后要传入的 prompt 是一个列表，包含多个消息字典，每个字典包含键 "content"
        prompts = [
            {"content": prompt, "role": role},
        ]
        return self.submit_prompt(prompt=prompts, model=openai_model)



def main():



    # 实例化 MyVanna
    vn = MyVanna(api_key=openai_api_key, model=openai_model, client=deepseek_client)
#     # 把表的ddl信息放入向量数据库中
#     vn.add_documentation(f"""CREATE TABLE `Album`
# (
#     `AlbumId` INT NOT NULL,    `Title` NVARCHAR(160) NOT NULL,    `ArtistId` INT NOT NULL,    CONSTRAINT `PK_Album` PRIMARY KEY  (`AlbumId`));  """)



    # # 连接 MySQL 数据库
    # vn.connect_to_mysql(host=host_name, user=user_name, password=user_password, dbname=db_name, port=port_number)
    # # 测试服务

    test_result = vn.analyse_sql_question("Please give me the information of all the albums")
    print(test_result)


    # app = VannaFlaskApp(vn, allow_llm_to_see_data=True)
    # app.run()

if __name__ == "__main__":
    main()

# 将vanna基类的各个函数 拆解出来 ，变成 各个服务

# 判断 SQL 是否有效

# 1.优化 SQL 问题


# 2.根据 SQL问题， 生成 “SQL查询分析报告”


# 3.生成 SQL

# 4.根据生成的 SQL， 生成 “SQL解释报告”

# 5.执行生成的 SQL

# 6.将 SQL 执行结果， 生成 “SQL执行结果报告”

# 7.将 SQL 执行结果， 生成 “结果图表”
