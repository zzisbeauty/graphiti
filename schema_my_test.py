# test_my_schema.py  
import asyncio  
from datetime import datetime, timezone  
from graphiti_core.graphiti import Graphiti  
from schema_my import entity_types
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig


# 配置本地 vLLM 客户端  
# llm_config = LLMConfig(  
#     api_key="empty",  # vLLM 不需要真实 API key  
#     model="/app/models/custom/Qwen3-4B-Thinking-2507",  # 您的模型路径/名称  
#     small_model="Qwen3-4B-Thinking-2507",  # 可以使用同一个模型  
#     base_url="http://192.168.1.6:5915/v1",  # 您的 vLLM 服务地址  
#     max_tokens=1024
# )

# 配置本地 swift 客户端  
llm_config = LLMConfig(  
    api_key="empty",  # vLLM 不需要真实 API key  
    model="Qwen3-4B-Think-2507",  # 您的模型路径/名称  
    small_model="Qwen3-4B-Thinking-2507",  # 可以使用同一个模型  
    base_url="http://192.168.1.6:5917/v1",  # 您的 vLLM 服务地址  
    max_tokens=1024
)

# # 配置本地 llama-factory 客户端  
# llm_config = LLMConfig(  
#     api_key="empty",  # vLLM 不需要真实 API key  
#     model="Qwen3-4B-Thinking-2507",  # 您的模型路径/名称  
#     small_model="Qwen3-4B-Thinking-2507",  # 可以使用同一个模型  
#     base_url="http://192.168.1.6:8001/v1",  # 您的 vLLM 服务地址  
#     max_tokens=1024
# )  
  
llm_client = OpenAIGenericClient(config=llm_config)  

# 配置 embedding 使用 OpenAI（或其他支持 embedding 的服务）  
embedder = OpenAIEmbedder(
    config=OpenAIEmbedderConfig(
        api_key="sk-wrgrwxbiylqqetuhbyumnahrqsdnyiqdqkkdslfmrjtotcfb",  # 使用真实的 OpenAI API key  
        embedding_model="BAAI/bge-large-zh-v1.5",
        base_url="https://api.siliconflow.cn/v1"
    )
)


async def main():  
    # 初始化 Graphiti  
    graphiti = Graphiti(  
        uri="bolt://192.168.1.6:7689",  
        user="neo4j",   
        password="aa1230.aa2",
        llm_client = llm_client,
        embedder=embedder
    )  
      
    # 构建索引  
    await graphiti.build_indices_and_constraints()  
      
    # 测试添加数据  
    result = await graphiti.add_episode(  
        name='Test Episode',  
        episode_body='这是一个测试笔记，包含一些概念和知识点。',  
        source_description='测试数据',  
        reference_time=datetime.now(timezone.utc),  
        entity_types=entity_types,
        group_id='test_group'  
    )  

    print(f"添加结果: {result}")  
      
    # 关闭连接  
    await graphiti.close()  




if __name__ == "__main__":  
    asyncio.run(main())
