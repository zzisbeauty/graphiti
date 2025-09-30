#!/usr/bin/env python3  
"""  
快速测试 Graphiti 的脚本 - 包含模型配置  
"""  
import asyncio  
from datetime import datetime, timezone  
from graphiti_core import Graphiti  
from graphiti_core.nodes import EpisodeType  
from graphiti_core.llm_client.config import LLMConfig  
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient  
  
async def test_add_episode():  
    """测试添加文本片段到知识图谱"""  
      
    # 配置本地模型  
    llm_config = LLMConfig(  
        api_key="vllm",  # 本地模型占位符  
        model="/app/models/custom/Qwen3-4B-Thinking-2507",  # 您的模型名称  
        base_url="http://192.168.1.6:5915/v1",  # 本地模型地址  
        temperature=0.7  
    )  
      
    # 创建 LLM 客户端  
    llm_client = OpenAIGenericClient(config=llm_config)  

    from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig 
    embedder = OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key="sk-wrgrwxbiylqqetuhbyumnahrqsdnyiqdqkkdslfmrjtotcfb",  # 使用真实的 OpenAI API key  
            embedding_model="BAAI/bge-large-zh-v1.5",
            base_url="https://api.siliconflow.cn/v1"
        )
    )




    # 正确的 Graphiti 初始化方式  
    graphiti = Graphiti(  
        uri="bolt://192.168.1.6:7689",  
        user="neo4j",   
        password="aa1230.aa2",  
        llm_client=llm_client,  # 传入配置好的 LLM 客户端 
        embedder=embedder 
    )  
      
    # 测试文本  
    test_text = """  
    今天我和张三讨论了新项目的进展。张三是我们公司的技术总监，  
    他提到这个项目将使用Python和Neo4j技术栈。我们计划在下个月  
    完成第一个版本的开发。项目的目标是构建一个知识图谱系统，  
    帮助公司更好地管理和查询数据。  
    """  
      
    try:  
        # 建立索引和约束  
        await graphiti.build_indices_and_constraints()  
          
        # 添加测试文本到知识图谱  
        result = await graphiti.add_episode(  
            name="项目讨论记录",  
            episode_body=test_text,  
            source_description="会议记录",  
            reference_time=datetime.now(timezone.utc),  
            source=EpisodeType.text,  
            group_id="test_project"  
        )  
          
        print("✅ 成功添加文本到知识图谱!")  
        print(f"📝 Episode UUID: {result.episode.uuid}")  
        print(f"🔗 创建了 {len(result.nodes)} 个节点")  
        print(f"🔗 创建了 {len(result.edges)} 个关系")  
          
        # 打印提取的实体  
        print("\n📋 提取的实体:")  
        for node in result.nodes:  
            print(f"  - {node.name}")  
              
        # 打印提取的关系  
        print("\n🔗 提取的关系:")  
        for edge in result.edges:  
            print(f"  - {edge.source_node_name} -> {edge.target_node_name}: {edge.fact}")  
              
    except Exception as e:  
        print(f"❌ 错误: {e}")  
      
    finally:  
        # 关闭连接  
        await graphiti.close()  
  
if __name__ == "__main__":  
    asyncio.run(test_add_episode())