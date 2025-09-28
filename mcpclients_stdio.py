#!/usr/bin/env python3  
"""  
STDIO 传输标准方式 - 导入古诗词数据  
"""  
  
import asyncio  
import json  
from mcp import ClientSession, StdioServerParameters  
from mcp.client.stdio import stdio_client  

from webdatas import json_data as poetry_data


async def wait_for_server_ready(session, max_retries=60, retry_interval=1):  
    """等待服务器准备就绪"""  
    for i in range(max_retries):  
        try:
            # 使用 read_resource 而不是 call_tool  
            result = await session.read_resource("http://graphiti/status")  
            print(f"状态检查结果: {result}")
            if result and result.get("status") == "ok":  
                print("服务器已准备就绪")
                return True
        except Exception as e:
            print(f"等待服务器准备中... ({i+1}/{max_retries}): {str(e)}")  
            await asyncio.sleep(retry_interval)  
    return False


async def import_poetry_data():  
    """使用 STDIO 传输标准方式导入数据"""  
      
    # 配置服务器参数 - 客户端会自动启动和管理服务器进程  
    server_params = StdioServerParameters(  
        command="python",
        args=[
            "graphiti_mcp_server.py",
            "--transport", "stdio",
            "--use-custom-entities",
            "--group-id", "poetry"
        ]
    )

    try:  
        # 使用 stdio_client 建立连接  
        async with stdio_client(server_params) as (read, write):  
            async with ClientSession(read, write) as session:  
                # 等待服务器准备就绪
                # 添加延迟确保服务器完全初始化  
                # await asyncio.sleep(20)  
                if not await wait_for_server_ready(session):  
                    raise Exception("服务器初始化超时")  

                print(f"开始导入 {len(poetry_data)} 首古诗词...")  
                  
                for i, poem in enumerate(poetry_data, 1):  
                    # 将诗词转换为 JSON 字符串  
                    poem_json = json.dumps(poem, ensure_ascii=False)  

                    # 使用作者和标题作为名称  
                    name = f"{poem['author']} - {poem['title']}"  
                    print(f"正在导入第 {i} 首: {name}")  
                      
                    # 调用 add_memory 工具  
                    result = await session.call_tool("add_memory", {  
                        "name": name,  
                        "episode_body": poem_json,  
                        "source": "json",  
                        "source_description": "古诗词数据",  
                        "group_id": "poetry",  
                        "uuid": poem['id']  
                    })  
                    print(f"导入结果: {result}")  
                    # 添加延迟避免过快请求  
                    await asyncio.sleep(0.5)  
                print("所有古诗词数据导入完成！")  
    except Exception as e:  
        print(f"导入过程中出现错误: {e}")



if __name__ == "__main__":  
    asyncio.run(import_poetry_data())
