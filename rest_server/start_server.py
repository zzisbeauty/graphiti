#!/usr/bin/env python3  
"""  
启动自定义 REST API 服务器  
"""  
import uvicorn  
import os  
from dotenv import load_dotenv  
  
# 加载环境变量  
load_dotenv("/home/graphiti/mcp_server/.env")  
  
if __name__ == "__main__":  
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")  
    port = int(os.getenv("PORT", "5903"))  
      
    uvicorn.run(  
        "rest_server.main:app",  
        host=host, 
        port=port,  
        reload=True,  
        log_level="info"  
    )
