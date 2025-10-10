import os  
import logging  
from contextlib import asynccontextmanager  
from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware  
from dotenv import load_dotenv  


import sys

def find_project_root(marker_files=('pyproject.toml', '.git', 'requirements.txt')):
    import os
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if any(os.path.exists(os.path.join(path, marker)) for marker in marker_files):
            return path
        path = os.path.dirname(path)
    raise RuntimeError("Project root not found.")

project_root = find_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from routes import router  



# 加载环境变量  
load_dotenv("/home/graphiti/mcp_server/.env")  
  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  
  
  
@asynccontextmanager  
async def lifespan(app: FastAPI):  
    """应用生命周期管理"""  
    logger.info("应用启动完成")  
    yield  
    logger.info("应用关闭")  

  
app = FastAPI(  
    title="Custom Graphiti REST API",  
    description="支持自定义 schema 的 Graphiti REST API 服务",  
    version="1.0.0",  
    lifespan=lifespan  
)  
  
# 添加 CORS 支持  
app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  

# 注册路由  
app.include_router(router)  
  
  
@app.get("/health")  
async def health_check():  
    """健康检查端点"""  
    return {"status": "healthy", "message": "服务正常运行"}  
  
  
if __name__ == "__main__":  
    import uvicorn  
      
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")  
    port = int(os.getenv("PORT", "5903"))  
      