import httpx  
import asyncio  
  
async def test_connection():  
    async with httpx.AsyncClient() as client:  
        try:  
            response = await client.post(  
                "https://api.siliconflow.cn/v1/embeddings",  
                headers={  
                    "Authorization": "Bearer sk-fanwrgrwxbiylqqetuhbyumnahrqsdnyiqdqkkdslfmrjtotcfb",  
                    "Content-Type": "application/json"  
                },  
                json={"model": "BAAI/bge-large-zh-v1.5", "input": "test"}  
            )  
            print(f"成功: {response.status_code}")  
            print(response.json())  
        except Exception as e:  
            print(f"失败: {type(e).__name__}: {e}")  
  
asyncio.run(test_connection())
