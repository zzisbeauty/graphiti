from fastapi import FastAPI, HTTPException, BackgroundTasks  
from pydantic import BaseModel, Field  
from typing import Optional, Dict, Any, List  
from datetime import datetime, timezone  
import asyncio  
import json  
import logging  
from contextlib import asynccontextmanager  
  
from graphiti_core import Graphiti  
from graphiti_core.nodes import EpisodeType  
from graphiti_core.llm_client.openai_client import OpenAIClient  
from graphiti_core.embedder.openai import OpenAIEmbedder  


import os, sys

def find_project_root(marker_files=('pyproject.toml', '.git', 'requirements.txt')):
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if any(os.path.exists(os.path.join(path, marker)) for marker in marker_files):
            return path
        path = os.path.dirname(path)
    raise RuntimeError("Project root not found.")

project_root = find_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from configs import get_settings  


# 配置日志  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  
  
# 全局变量  
graphiti_client: Optional[Graphiti] = None  
episode_queues: Dict[str, asyncio.Queue] = {}  
queue_workers: Dict[str, bool] = {}  
  
# 请求模型  
class AddEpisodeRequest(BaseModel):  
    name: str = Field(..., description="Episode 名称")  
    episode_body: str = Field(..., description="Episode 内容")  
    source: str = Field(default="text", description="数据类型: json, message, text")  
    source_description: str = Field(default="", description="数据来源描述")  
    group_id: str = Field(..., description="分组ID")  
    entity_types: Optional[List[str]] = Field(None, description="自定义实体类型")  
    edge_types: Optional[List[str]] = Field(None, description="自定义边类型")  
    uuid: Optional[str] = Field(None, description="可选的UUID")  
  
class EpisodeResponse(BaseModel):  
    status: str  
    message: str  
    episode_id: Optional[str] = None  
  
# 应用生命周期管理  
@asynccontextmanager  
async def lifespan(app: FastAPI):  
    # 启动时初始化  
    global graphiti_client  
    settings = get_settings()  
      
    try:  
        # 初始化 LLM 客户端  
        llm_client = OpenAIClient(  
            api_key=settings.openai_api_key,  
            model=settings.model_name or "gpt-4",  
            base_url=settings.openai_base_url  
        )  
          
        # 初始化 Embedder 客户端  
        embedder = OpenAIEmbedder(  
            api_key=settings.openai_api_key,  
            model=settings.embedding_model_name or "text-embedding-ada-002"  
        )  
          
        # 初始化 Graphiti 客户端  
        graphiti_client = Graphiti(  
            uri=settings.neo4j_uri,  
            user=settings.neo4j_user,  
            password=settings.neo4j_password,  
            llm_client=llm_client,  
            embedder=embedder,  
            max_coroutines=settings.semaphore_limit  
        )  
          
        # 构建索引和约束  
        await graphiti_client.build_indices_and_constraints()  
        logger.info("Graphiti 客户端初始化成功")  
          
    except Exception as e:  
        logger.error(f"初始化 Graphiti 客户端失败: {e}")  
        raise  
      
    yield  
      
    # 关闭时清理  
    if graphiti_client:  
        await graphiti_client.close()  
        logger.info("Graphiti 客户端已关闭")  
  
app = FastAPI(  
    title="Graphiti Data Import Service",  
    description="基于 Graphiti 核心库的数据导入服务",  
    version="1.0.0",  
    lifespan=lifespan  
)  
  
# 队列处理函数  
async def process_episode_queue(group_id: str):  
    """处理特定 group_id 的队列"""  
    global episode_queues, queue_workers  
      
    queue = episode_queues[group_id]  
    queue_workers[group_id] = True  
      
    try:  
        while True:  
            try:  
                episode_task = await asyncio.wait_for(queue.get(), timeout=1.0)  
                await episode_task()  
                queue.task_done()  
            except asyncio.TimeoutError:  
                # 检查队列是否为空，如果为空则退出  
                if queue.empty():  
                    break  
            except Exception as e:  
                logger.error(f"处理队列 {group_id} 时出错: {e}")  
    finally:  
        queue_workers[group_id] = False  
        logger.info(f"队列处理器 {group_id} 已停止")  
  
# 数据导入端点  
@app.post("/add_episode", response_model=EpisodeResponse)  
async def add_episode(request: AddEpisodeRequest, background_tasks: BackgroundTasks):  
    """  
    添加 Episode 到知识图谱  
      
    支持三种数据类型：  
    - text: 纯文本  
    - json: JSON 结构化数据  
    - message: 对话格式数据  
    """  
    global graphiti_client, episode_queues, queue_workers  
      
    if not graphiti_client:  
        raise HTTPException(status_code=500, detail="Graphiti 客户端未初始化")  
      
    try:  
        # 验证输入  
        if not request.episode_body.strip():  
            raise HTTPException(status_code=400, detail="Episode body 不能为空")  
          
        # 映射数据类型  
        source_type = EpisodeType.text  
        if request.source.lower() == "message":  
            source_type = EpisodeType.message  
        elif request.source.lower() == "json":  
            source_type = EpisodeType.json  
        elif request.source.lower() == "text":  
            source_type = EpisodeType.text  
        else:  
            raise HTTPException(status_code=400, detail=f"不支持的数据类型: {request.source}")  
          
        # 定义处理函数  
        async def process_episode():  
            try:  
                logger.info(f"开始处理 Episode: {request.name}, Group: {request.group_id}")  
                  
                # 准备自定义 schema  
                entity_types = None  
                edge_types = None  
                edge_type_map = None  
                  
                if request.entity_types:  
                    # 这里可以根据需要扩展自定义实体类型的处理逻辑  
                    logger.info(f"使用自定义实体类型: {request.entity_types}")  
                  
                # 调用 Graphiti 核心方法  
                result = await graphiti_client.add_episode(  
                    name=request.name,  
                    episode_body=request.episode_body,  
                    source=source_type,  
                    source_description=request.source_description,  
                    group_id=request.group_id,  
                    uuid=request.uuid,  
                    reference_time=datetime.now(timezone.utc),  
                    entity_types=entity_types,  
                    edge_types=edge_types,  
                    edge_type_map=edge_type_map  
                )  
                  
                logger.info(f"Episode {request.name} 处理成功")  
                return result  
                  
            except Exception as e:  
                logger.error(f"处理 Episode {request.name} 时出错: {e}")  
                raise  
          
        # 初始化队列（如果不存在）  
        if request.group_id not in episode_queues:  
            episode_queues[request.group_id] = asyncio.Queue()  
          
        # 将任务添加到队列  
        await episode_queues[request.group_id].put(process_episode)  
          
        # 启动队列处理器（如果未运行）  
        if not queue_workers.get(request.group_id, False):  
            background_tasks.add_task(process_episode_queue, request.group_id)  
          
        queue_size = episode_queues[request.group_id].qsize()  
          
        return EpisodeResponse(  
            status="queued",  
            message=f"Episode '{request.name}' 已加入处理队列 (队列位置: {queue_size})"  
        )  
          
    except HTTPException:  
        raise  
    except Exception as e:  
        logger.error(f"添加 Episode 时出错: {e}")  
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")  
  
# 健康检查端点  
@app.get("/health")  
async def health_check():  
    """健康检查"""  
    if not graphiti_client:  
        raise HTTPException(status_code=503, detail="Graphiti 客户端未初始化")  
      
    try:  
        # 检查数据库连接  
        await graphiti_client.driver.verify_connectivity()  
        return {  
            "status": "healthy",  
            "timestamp": datetime.now(timezone.utc).isoformat(),  
            "graphiti_initialized": graphiti_client is not None  
        }  
    except Exception as e:  
        raise HTTPException(status_code=503, detail=f"服务不健康: {str(e)}")  
  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)