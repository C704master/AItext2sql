from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient


def _setup_model_client():
    """设置模型客户端"""
    model_config = {
        "model": "deepseek-chat",
        "base_url": "http://",
        "api_key": "",
        "model_info": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
        },
    },

    return OpenAIChatCompletionClient(**model_config)

# 单例设计模式（该对象只创建一次）
model_client = _setup_model_client()