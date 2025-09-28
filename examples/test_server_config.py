import asyncio  
from datetime import datetime, timezone  
from graphiti_core.graphiti import Graphiti  
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

""" 修改模型后可能涉及到如下指令的修改
/home/graphiti/graphiti_core/prompts/extract_nodes.py
"""


# 配置 yi api model
# llm_config = LLMConfig(  
#     api_key="sk-wuTITomWJ5hVYsVb304d3f94Ec144e3bAa5eCc11Ff6aA0E9",
#     # model="gpt-4.1-mini-2025-04-14",
#     model="gpt-4.1-mini",
#     # model="deepseek-v3-0324",
#     # model = "qwen-max-longcontext",
#     # model="gpt-5-mini",  # 可以使用同一个模型     gpt-5-mini 也比较便宜
#     # small_model="gpt-5-mini",  # 可以使用同一个模型     gpt-5-mini 也比较便宜
#     base_url="https://api.apiyi.com/v1",  # 您的 vLLM 服务地址  
#     # max_tokens=2048
# )


# 配置本地 vLLM 客户端
llm_config = LLMConfig(
    api_key="empty",  # vLLM 不需要真实 API key  
    # model="/app/models/custom/Qwen3-4B-Thinking-2507",
    model="/app/models/custom/Qwen3-4B-Instruct-2507",
    # model="/app/models/custom/DeepSeek-R1-0528-Qwen3-8B",
    base_url="http://192.168.1.6:5915/v1",  # 您的 vLLM 服务地址  
    # max_tokens=5000
)


# # 配置本地 swift 客户端
# llm_config = LLMConfig(
#     api_key="empty",  # vLLM 不需要真实 API key 
#     # model="Qwen3-4B-Think-2507",  # 您的模型路径/名称
#     model="qwen3",
#     base_url="http://192.168.1.6:5917/v1",  # 您的 vLLM 服务地址
#     max_tokens=4096
# )


# 配置本地 llama-factory 客户端  
# todo 会出现兼容 openai api 的接口未完全兼容，对客户端传入的对话中的 role 字段不兼容的情况，导致报错，对话无法进行，而 role openai api 对话标准字段
# llm_config = LLMConfig(  
#     api_key="empty",  # vLLM 不需要真实 API key  
#     # model="Qwen3-4B-Thinking-2507",  # 您的模型路径/名称   
#     model="Qwen3-4B-Instruct", 
#     base_url="http://192.168.1.6:8001/v1",  # 您的 vLLM 服务地址  
#     max_tokens=8000
# )


llm_client = OpenAIGenericClient(config=llm_config)  


# 配置 embedding 使用 OpenAI（或其他支持 embedding 的服务）  
embedder = OpenAIEmbedder(
    config=OpenAIEmbedderConfig(
        api_key="sk-wrgrwxbiylqqetuhbyumnahrqsdnyiqdqkkdslfmrjtotcfb",  # 使用真实的 OpenAI API key  
        embedding_model="BAAI/bge-large-zh-v1.5",
        base_url="https://api.siliconflow.cn/v1",
    )
)


NEO4J_URL = "bolt://192.168.1.6:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWD = "aa1230.aa2"
