# original main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from graph_service.config import get_settings
from graph_service.routers import ingest, retrieve
from graph_service.zep_graphiti import initialize_graphiti


# 注册路由
from graph_service.routers import ingest, retrieve, schema, data_process




@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await initialize_graphiti(settings)
    yield
    # Shutdown
    # No need to close Graphiti here, as it's handled per-request


app = FastAPI(lifespan=lifespan)


# 现有路由
app.include_router(retrieve.router)
app.include_router(ingest.router)


app.include_router(schema.router)   # 注册自定义 schema 路由  
app.include_router(data_process.router)  # 数据处理路由


@app.get('/healthcheck')
async def healthcheck():
    return JSONResponse(content={'status': 'healthy'}, status_code=200)
