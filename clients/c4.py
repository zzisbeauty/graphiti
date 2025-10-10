import asyncio  
from mcp.client.sse import sse_client  
from mcp import ClientSession  
  
async def call_mcp_server():  
    try:  
        async with sse_client("http://localhost:8000/sse") as (read, write):  
            async with ClientSession(read, write) as session:  
                # 使用正确的工具名称 add_episode  
                result = await session.call_tool(  
                    "add_episode",  # 正确的工具名称  
                    {  
                        "name": "测试记忆",  
                        "episode_body": "这是一个测试内容",  
                        "group_id": "my_project",  
                        "source": "text",  
                        "source_description": "测试来源"  
                    }  
                )  
                return result  
    except Exception as e:  
        print(f"Error: {e}")  
        return None  
  
result = asyncio.run(call_mcp_server())  
print(result)