from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

def _setup_model_client():
    """设置模型客户端"""
    model_config = {
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "sk-377e8edb52a04cc08f97124f4b7107d4",
        "model_info": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
        },
    }

    return OpenAIChatCompletionClient(**model_config)

# 单例设计模式（该对象只创建一次）
model_client = _setup_model_client()