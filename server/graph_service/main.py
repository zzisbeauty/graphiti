from contextlib import asynccontextmanager  
  
from fastapi import FastAPI  
from fastapi.responses import JSONResponse  
  
from graph_service.config import get_settings  
from graph_service.routers import ingest, retrieve  
from graph_service.routers.ingest import async_worker  # 添加导入  
from graph_service.zep_graphiti import initialize_graphiti  
  
  
@asynccontextmanager  
async def lifespan(_: FastAPI):  
    settings = get_settings()  
    await initialize_graphiti(settings)  
      
    # 启动 AsyncWorker  
    await async_worker.start()  
      
    yield  
      
    # 关闭时停止 worker  
    await async_worker.stop()  
  
  
app = FastAPI(lifespan=lifespan)  
  
app.include_router(retrieve.router)  
app.include_router(ingest.router)  
  
  
@app.get('/healthcheck')  
async def healthcheck():  
    return JSONResponse(content={'status': 'healthy'}, status_code=200)