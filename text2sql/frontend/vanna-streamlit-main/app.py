import time
import streamlit as st
from vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached,
    generate_sql_question_report_cached,
    generate_plot_v2_cached,
    generate_sql_v2_cached,
    generate_sql_explain_v2_cached,
    generate_plotly_code_v2_cached,
    generate_summary_v2_cached,
    find_schema_cached,
    run_sql_v2_cached,
    generate_result_visual_command_v2_cached,
)

# LOGO
# avatar_url = "https://vanna.ai/img/vanna.svg"
# 华侨大学logo
avatar_url = r"C:\workspace\text2sql\frontend\vanna-streamlit-main\assets\Huaqiao_University_logo.png"

st.set_page_config(layout="wide")

st.sidebar.title("输出设置")
st.sidebar.checkbox("展示SQL语句", value=True, key="show_sql")
st.sidebar.checkbox("展示查询到的数据", value=True, key="show_table")
st.sidebar.checkbox("展示plotly画图代码", value=True, key="show_plotly_code")
st.sidebar.checkbox("展示数据表格", value=True, key="show_chart")
st.sidebar.checkbox("展示总结", value=True, key="show_summary")
st.sidebar.checkbox("展示历史类似问题", value=True, key="show_followup")
st.sidebar.checkbox("展示SQL问题报告", value=True, key="show_analysis_sql_question_report")
st.sidebar.checkbox("展示SQL语句解释报告", value=True, key="show_SQL_interpretation_report")
st.sidebar.checkbox("展示可视化推荐报告", value=True, key="show_result_visual_command")
st.sidebar.button("重置对话", on_click=lambda: set_question(None), use_container_width=True)

st.title("华侨大学Text2SQL数据可视化智能系统")


# st.sidebar.write(st.session_state)


def set_question(question):
    st.session_state["my_question"] = question


# assistant_message_suggested = st.chat_message(
#     "assistant", avatar=avatar_url
# )
# if assistant_message_suggested.button("点击生成建议性的问题"):
#     st.session_state["my_question"] = None
#     questions = generate_questions_cached()
#     for i, question in enumerate(questions):
#         time.sleep(0.05)
#         button = st.button(
#             question,
#             on_click=set_question,
#             args=(question,),
#         )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "请告诉我关于您想知道的数据的问题",
    )

# 如果读入了 用户的问题，则 my_question 返回true
if my_question:
    st.session_state["my_question"] = my_question

    user_message = st.chat_message("user")

    # 显示用户输入的问题
    user_message.write(f"{my_question}")

    # 查找上下文信息
    context = find_schema_cached(f"{my_question}")

    # sql = generate_sql_cached(question=my_question)

    # 先生成SQL问题报告，然后再生成SQL
    sql_report = generate_sql_question_report_cached(question=my_question)

    # 先生成SQL问题报告
    if sql_report:
        assistant_message_sql_question_report = st.chat_message(
            "assistant", avatar=avatar_url
        )
        # 显示SQL问题分析报告
        assistant_message_sql_question_report.write(sql_report)
    else:
        assistant_message = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message.write("我无法生成SQL问题分析报告，请检查你的参数配置")
        st.stop()

    # 生成SQL语句
    sql = generate_sql_v2_cached(question=my_question, analysis_report=sql_report, context=context)
    explain_sql_report = generate_sql_explain_v2_cached(sql=sql)

    # 如果生成了SQL语句，则会触发这个逻辑结构
    if sql:
        #  如果SQL语句有效并且show_sql按钮为真，则显示SQL语句
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    # avatar_url是头像的地址，avatar是头像的意思
                    "assistant", avatar=avatar_url
                )
                # 显示SQL语句
                assistant_message_sql.code(sql, language="sql", line_numbers=True)

            # 如果SQL解释语句按钮为真，则显示SQL语句解释报告
            if st.session_state.get("show_SQL_interpretation_report", True):
                assistant_message_SQL_interpretation_report = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                assistant_message_SQL_interpretation_report.write(explain_sql_report)


        else:
            # 如果SQL语句无效，则显示SQL语句,然后停止程序
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.write(sql)
            st.stop()

        # 运行SQL语句，返回SQL查询到的数据集
        df = run_sql_v2_cached(sql=sql)

        # 如果SQL查询到了数据，则st的会话状态中加入df这个变量，代表 SQL查询到的数据集
        if df is not None:
            st.session_state["df"] = df

        # 如果SQL查询到了数据，则进入这个逻辑模块
        if st.session_state.get("df") is not None:
            # 如果show_table按钮为真，则显示SQL查询到的数据集
            if st.session_state.get("show_table", True):
                # 获取SQL查询到的数据集
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                # 如果SQL查询到的数据集大于10行，则只显示前10行的数据
                if len(df) > 10:
                    assistant_message_table.text("显示前10行的数据")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    #  如果SQL查询到的数据集小于等于10行，显示SQL查询到的所有数据集
                    assistant_message_table.dataframe(df)

            # 如果系统判断应该生成图表，则执行这个逻辑模块
            if should_generate_chart_cached(question=my_question, sql=sql, df=df):
                # 生成可视化推荐报告
                result_visual_command = None
                if st.session_state.get("show_result_visual_command", True):
                    result_visual_command = generate_result_visual_command_v2_cached(
                        sql=sql, question=my_question, df=df
                    )
                    # 显示可视化推荐报告
                    assistant_message_result_visual_command = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_result_visual_command.write(result_visual_command)

                # 生成plotly代码
                code = generate_plotly_code_v2_cached(visual_command=result_visual_command, question=my_question,
                                                      sql=sql, df=df)

                # 如果show_plotly_code按钮为真，则显示plotly代码
                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                # 如果plotly代码有效，则生成图表
                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_url,
                        )
                        # 生成图表
                        fig = generate_plot_v2_cached(code=code, df=df)
                        # 如果图表生成成功，则显示图表
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("plotly代码有错误，我不能生成图表")

            # 如果show_summary按钮按下去了，则执行这个逻辑模块
            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                # 生成摘要
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            # 如果show_followup按钮按下去了，则执行这个逻辑模块
            # 目前这个模块还没有写完
            # if st.session_state.get("show_followup", True):
            #     assistant_message_followup = st.chat_message(
            #         "assistant",
            #         avatar=avatar_url,
            #     )
            #     # 生成后续问题
            #     followup_questions = generate_followup_cached(
            #         question=my_question, sql=sql, df=df
            #     )
            #     st.session_state["df"] = None
            #
            #     if len(followup_questions) > 0:
            #         assistant_message_followup.text(
            #             "这里有些可能的后续问题，请选择一个"
            #         )
            #         # Print the first 5 follow-up questions
            #         for question in followup_questions[:5]:
            #             assistant_message_followup.button(question, on_click=set_question, args=(question,))

        # 生成一个问题是否满意的提示


    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message_error.error("由于缺少相应数据，我不能生成SQL语句")
