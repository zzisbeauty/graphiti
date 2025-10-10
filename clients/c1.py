#!/usr/bin/env python3  
"""  
MCP 客户端测试脚本 - 读取本地文件并调用 Graphiti MCP 服务  
"""  
  
import asyncio  
import json  
import aiohttp  
from pathlib import Path  


class GraphitiMCPClient:  
    def __init__(self, base_url="http://192.168.1.6:8000"):  
        self.base_url = base_url  
        self.sse_url = f"{base_url}/sse"  
      
    async def add_memory(self, name: str, episode_body: str, group_id: str = "default_project", 
                        source: str = "text", source_description: str = ""):  
        """调用 add_memory 工具添加记忆片段"""  
        payload = {  
            "method": "tools/call",  
            "params": {  
                "name": "add_memory",  
                "arguments": {  
                    "name": name,  
                    "episode_body": episode_body,  
                    "group_id": group_id,  
                    "source": source,  
                    "source_description": source_description  
                }  
            }  
        }  
          
        async with aiohttp.ClientSession() as session:  
            async with session.post(self.sse_url, json=payload) as response:  
                if response.status == 200:  
                    result = await response.json()  
                    return result  
                else:  
                    print(f"错误: HTTP {response.status}")  
                    return None  
      
    async def search_nodes(self, query: str, group_ids: list[str] = [], max_nodes: int = 10):  
        """搜索节点"""  
        if group_ids is None:  
            group_ids = ["鲁迅文集"]  # 默认值  
        
        payload = {  
            "method": "tools/call",  
            "params": {  
                "name": "search_memory_nodes",  
                "arguments": {  
                    "query": query,  
                    "group_ids": group_ids,  # 注意这里是复数形式的列表  
                    "max_nodes": max_nodes   # 参数名是 max_nodes  
                }  
            }  
        }
          
        async with aiohttp.ClientSession() as session:  
            async with session.post(self.sse_url, json=payload) as response:  
                if response.status == 200:  
                    result = await response.json()  
                    return result  
                else:  
                    print(f"错误: HTTP {response.status}")  
                    return None  


    async def get_status(self):  
        """获取服务状态"""  
        payload = {  
            "method": "resources/read",  
            "params": {  
                "uri": "http://graphiti/status"  
            }  
        }  
          
        async with aiohttp.ClientSession() as session:  
            async with session.post(self.sse_url, json=payload) as response:  
                if response.status == 200:  
                    result = await response.json()  
                    return result  
                else:  
                    print(f"错误: HTTP {response.status}")  
                    return None  
  
async def main():
    # 初始化客户端
    client = GraphitiMCPClient("http://192.168.1.6:5903")  

    # 1. 检查服务状态
    print("=== 检查 MCP 服务状态 ===")  
    status = await client.get_status()
    if status:
        print(f"服务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")  
    else:
        print("无法连接到 MCP 服务，请检查服务是否启动")
        return

    # 2. 读取本地文件  
    file_path = Path("/home/graphiti/examples/data/百草园.txt")  
    if not file_path.exists():  
        print(f"文件不存在: {file_path}")  
        return  
    try:  
        with open(file_path, 'r', encoding='utf-8') as f:  
            content = f.read()  
        print(f"=== 成功读取文件 ===")  
        print(f"文件路径: {file_path}")  
        print(f"文件大小: {len(content)} 字符")  
        print(f"内容预览: {content[:200]}...")  
    except Exception as e:  
        print(f"读取文件失败: {e}")  
        return  

    # 3. 添加记忆片段  
    print("\n=== 添加记忆片段到知识图谱 ===")  
    result = await client.add_memory(  
        name="BCY",  
        episode_body=content,  
        group_id="鲁迅文集",  
        source="text",  
        source_description="本地文本文件"  
    )  

    if result:  
        print(f"添加结果: {json.dumps(result, indent=2, ensure_ascii=False)}")  
    else:  
        print("添加记忆片段失败")  
        return  

    # 4. 等待处理完成（因为是异步处理）  
    print("\n=== 等待处理完成 ===")  
    await asyncio.sleep(5)  

    # 5. 搜索测试
    print("\n=== 搜索测试 ===")
    search_queries = ["百草园", "鲁迅", "童年", "记忆"]

    for query in search_queries:  
        print(f"\n搜索关键词: {query}")  
        search_result = await client.search_nodes(query=query, group_ids=["鲁迅文集"], max_nodes=5)  
        if search_result:  
            print(f"搜索结果: {json.dumps(search_result, indent=2, ensure_ascii=False)}")  
        else:  
            print("搜索失败")  



if __name__ == "__main__":  
    asyncio.run(main())
