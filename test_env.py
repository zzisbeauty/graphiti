import os  
from pathlib import Path  
from dotenv import load_dotenv


env_path = '/home/graphiti/mcp_server/.env'  
if Path(env_path).exists():  
    load_dotenv(env_path)  
    print(f"成功加载 {env_path}")  
else:  
    print(f"警告: {env_path} 不存在")  
    load_dotenv()  # 回退到默认行为