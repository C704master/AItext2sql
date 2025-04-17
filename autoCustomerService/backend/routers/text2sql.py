from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import openai
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

from database import get_db
from models import ChatHistory, User
from routers.auth import oauth2_scheme
from config import settings

router = APIRouter()

class Text2SQLRequest(BaseModel):
    question: str
    database_schema: str

class Text2SQLResponse(BaseModel):
    sql_query: str
    explanation: str
    result: dict
    visualization: str

async def generate_sql_query(question: str, database_schema: str):
    # 使用OpenAI API生成SQL查询
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""你是一个专业的SQL专家。请根据用户的问题生成相应的SQL查询。
数据库结构如下：
{database_schema}

请生成SQL查询，并解释查询的目的和逻辑。"""},
            {"role": "user", "content": question}
        ],
        stream=True
    )
    return response

async def execute_sql_query(sql_query: str):
    # 这里需要实现实际的SQL查询执行逻辑
    # 示例：使用pandas从CSV文件读取数据
    try:
        # 这里应该替换为实际的数据库连接和查询
        df = pd.read_csv("example_data.csv")
        result = df.to_dict(orient="records")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL执行错误: {str(e)}")

def generate_visualization(data: list, sql_query: str):
    # 根据SQL查询类型生成相应的可视化
    try:
        df = pd.DataFrame(data)
        
        # 根据查询类型选择可视化方式
        if "COUNT" in sql_query.upper():
            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
        elif "SUM" in sql_query.upper() or "AVG" in sql_query.upper():
            fig = px.line(df, x=df.columns[0], y=df.columns[1])
        else:
            fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
        
        return fig.to_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"可视化生成错误: {str(e)}")

@router.post("/query")
async def text2sql_query(
    request: Text2SQLRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    async def generate():
        try:
            # 生成SQL查询
            response = await generate_sql_query(request.question, request.database_schema)
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # 解析生成的SQL查询
            sql_query = full_response.split("SQL查询:")[1].split("解释:")[0].strip()
            explanation = full_response.split("解释:")[1].strip()
            
            # 执行SQL查询
            result = await execute_sql_query(sql_query)
            
            # 生成可视化
            visualization = generate_visualization(result, sql_query)
            
            # 保存到数据库
            db_chat = ChatHistory(
                user_id=1,  # 这里需要从token中获取用户ID
                agent_type="text2sql",
                message=request.question,
                response=json.dumps({
                    "sql_query": sql_query,
                    "explanation": explanation,
                    "result": result,
                    "visualization": visualization
                })
            )
            db.add(db_chat)
            db.commit()
            
            yield f"data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream") 