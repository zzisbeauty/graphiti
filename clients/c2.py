#!/usr/bin/env python3  
"""  
MCP 客户端测试脚本 - WebSocket 版本  
"""  
  
import asyncio  
import json  
import websockets  
from pathlib import Path  
import uuid  
  
class GraphitiMCPClient:  
    def __init__(self, ws_url="ws://192.168.1.6:5903/ws"):  
        self.ws_url = ws_url  
        self.websocket = None  
      
    async def connect(self):  
        """建立 WebSocket 连接"""  
        try:  
            self.websocket = await websockets.connect(self.ws_url)  
            print("WebSocket 连接已建立")  
            return True  
        except Exception as e:  
            print(f"WebSocket 连接失败: {e}")  
            return False  
      
    async def send_request(self, method, params):  
        """发送 MCP 请求"""  
        if not self.websocket:  
            if not await self.connect():  
                return None  
          
        request = {  
            "jsonrpc": "2.0",  
            "id": str(uuid.uuid4()),  
            "method": method,  
            "params": params  
        }  
          
        try:  
            await self.websocket.send(json.dumps(request))  
            response = await self.websocket.recv()  
            return json.loads(response)  
        except Exception as e:  
            print(f"请求失败: {e}")  
            return None  
      
    async def add_memory(self, name: str, episode_body: str, group_id: str = "my_project",   
                        source: str = "text", source_description: str = ""):  
        """调用 add_memory 工具"""  
        return await self.send_request("tools/call", {  
            "name": "add_memory",  
            "arguments": {  
                "name": name,  
                "episode_body": episode_body,  
                "group_id": group_id,  
                "source": source,  
                "source_description": source_description  
            }  
        })  
      
    async def search_nodes(self, query: str, group_ids: list[str] = None, max_nodes: int = 10):  
        """搜索节点"""  
        if group_ids is None:  
            group_ids = ["my_project"]  
          
        return await self.send_request("tools/call", {  
            "name": "search_memory_nodes",  
            "arguments": {  
                "query": query,  
                "group_ids": group_ids,  
                "max_nodes": max_nodes  
            }  
        })  
      
    async def get_status(self):  
        """获取服务状态"""  
        return await self.send_request("resources/read", {  
            "uri": "http://graphiti/status"  
        })  
      
    async def close(self):  
        """关闭连接"""  
        if self.websocket:  
            await self.websocket.close()  
  
async def main():  
    # 初始化客户端  
    client = GraphitiMCPClient("ws://192.168.1.6:5903/ws")  
      
    try:  
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
  
        # 4. 等待处理完成  
        print("\n=== 等待处理完成 ===")  
        await asyncio.sleep(5)  
  
        # 5. 搜索测试  
        print("\n=== 搜索测试 ===")  
        search_queries = ["百草园", "鲁迅", "童年", "记忆"]  
  
        for query in search_queries:  
            print(f"\n搜索关键词: {query}")  
            search_result = await client.search_nodes(  
                query=query,   
                group_ids=["鲁迅文集"],   
                max_nodes=5  
            )  
            if search_result:  
                print(f"搜索结果: {json.dumps(search_result, indent=2, ensure_ascii=False)}")  
            else:  
                print("搜索失败")  
  
    finally:  
        await client.close()  
  
if __name__ == "__main__":  
    asyncio.run(main())