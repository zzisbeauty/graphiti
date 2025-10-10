import os  
import logging  
from datetime import datetime, timezone  
from typing import Any, Dict, List, Optional  
from fastapi import APIRouter, HTTPException  
from pydantic import BaseModel, Field, create_model  
  
from graphiti_core import Graphiti  
from graphiti_core.llm_client.config import LLMConfig  
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient  
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig  
from graphiti_core.nodes import EpisodeType  
  
logger = logging.getLogger(__name__)  
router = APIRouter(prefix="/api", tags=["episodes"])  
  
# 全局 Graphiti 客户端  
graphiti_client: Optional[Graphiti] = None  
  
  
class CustomEntitySchema(BaseModel):  
    """自定义实体 schema 定义"""  
    name: str = Field(..., description="实体类型名称")  
    description: str = Field(..., description="实体类型描述")  
    properties: Dict[str, Any] = Field(..., description="实体属性定义")  
  
  
class AddEpisodeRequest(BaseModel):  
    """添加 episode 的请求模型"""  
    name: str = Field(..., description="Episode 名称")  
    episode_body: str = Field(..., description="Episode 内容")  
    source_description: str = Field(..., description="来源描述")  
    source: str = Field(default="message", description="来源类型")  
    group_id: Optional[str] = Field(None, description="分组 ID")  
    custom_schemas: Optional[List[CustomEntitySchema]] = Field(None, description="自定义实体 schemas")  
    reference_time: Optional[datetime] = Field(None, description="参考时间")  
  
  
class SearchRequest(BaseModel):  
    """搜索请求模型"""  
    query: str = Field(..., description="搜索查询")  
    group_id: Optional[str] = Field(None, description="分组 ID")  
    limit: int = Field(default=10, description="返回结果数量限制")  
  



class ApiResponse(BaseModel):  
    """API 响应模型"""  
    success: bool  
    message: str  
    data: Optional[Any] = None  
  
  
async def initialize_graphiti():  
    """初始化 Graphiti 客户端"""  
    global graphiti_client  
      
    try:  
        llm_config = LLMConfig(  
            api_key=os.getenv("OPENAI_API_KEY", "empty"),  
            model=os.getenv("MODEL_NAME", "/app/models/custom/Qwen3-4B-Instruct-2507"),  
            base_url=os.getenv("OPENAI_BASE_URL", "http://192.168.1.6:5915/v1"),  
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),  
        )  

        llm_client = OpenAIGenericClient(config=llm_config)  
          
        embedder = OpenAIEmbedder(  
            config=OpenAIEmbedderConfig(  
                api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),  
                embedding_model=os.getenv("EMBEDDER_MODEL_NAME", "BAAI/bge-large-zh-v1.5"),  
                base_url=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),  
            )  
        )  
          
        graphiti_client = Graphiti(  
            uri=os.getenv("NEO4J_URI"),  
            user=os.getenv("NEO4J_USER"),  
            password=os.getenv("NEO4J_PASSWORD"),  
            llm_client=llm_client,  
            embedder=embedder,  
            max_coroutines=int(os.getenv("SEMAPHORE_LIMIT", "10")),  
        )  
          
        await graphiti_client.build_indices_and_constraints()  
        logger.info("Graphiti 客户端初始化成功")  
          
    except Exception as e:  
        logger.error(f"初始化 Graphiti 客户端失败: {e}")  
        raise  
  
  
def create_dynamic_entity_model(schema: CustomEntitySchema) -> type[BaseModel]:  
    """根据自定义 schema 创建动态 Pydantic 模型"""  
    fields = {}  
    for prop_name, prop_def in schema.properties.items():  
        if isinstance(prop_def, dict):  
            field_type = prop_def.get('type', 'str')  
            field_description = prop_def.get('description', '')  
            required = prop_def.get('required', False)  
              
            type_mapping = {  
                'string': str,  
                'integer': int,  
                'number': float,  
                'boolean': bool,  
                'array': List[str],  
            }  
              
            python_type = type_mapping.get(field_type, str)  
              
            if required:  
                fields[prop_name] = (python_type, Field(..., description=field_description))  
            else:  
                fields[prop_name] = (Optional[python_type], Field(None, description=field_description))  
      
    return create_model(schema.name, **fields, __base__=BaseModel)  
  
  
@router.on_event("startup")  
async def startup_event():  
    """路由启动时初始化 Graphiti"""  
    await initialize_graphiti()  
  
  
@router.post("/episodes", response_model=ApiResponse)  
async def add_episode(request: AddEpisodeRequest):  
    """添加 episode 到知识图谱"""  
    if not graphiti_client:  
        raise HTTPException(status_code=500, detail="Graphiti 客户端未初始化")  
      
    try:  
        # 转换自定义 schemas 为 entity_types  
        entity_types = {}  
        if request.custom_schemas:  
            for schema in request.custom_schemas:  
                try:  
                    entity_model = create_dynamic_entity_model(schema)  
                    entity_types[schema.name] = entity_model  
                    logger.info(f"创建自定义实体类型: {schema.name}")  
                except Exception as e:  
                    logger.error(f"创建实体类型 {schema.name} 失败: {e}")  
                    raise HTTPException(status_code=400, detail=f"无效的 schema: {schema.name}")  
          
        # 设置参考时间  
        reference_time = request.reference_time or datetime.now(timezone.utc)  
          
        # 转换 source 类型  
        episode_type = EpisodeType.message  
        if request.source == "json":  
            episode_type = EpisodeType.json  
        elif request.source == "text":  
            episode_type = EpisodeType.text  
          
        # 调用 Graphiti 的 add_episode 方法  
        result = await graphiti_client.add_episode(  
            name=request.name,  
            episode_body=request.episode_body,  
            source_description=request.source_description,  
            reference_time=reference_time,  
            source=episode_type,  
            group_id=request.group_id,  
            entity_types=entity_types if entity_types else None,  
        )  
          
        return ApiResponse(  
            success=True,  
            message="Episode 添加成功",  
            data={  
                "episode_uuid": result.episode.uuid,  
                "created_nodes": len(result.nodes),  
                "created_edges": len(result.edges),  
            }  
        )  
          
    except HTTPException:  
        raise  
    except Exception as e:  
        logger.error(f"添加 episode 失败: {e}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
  
@router.post("/search/nodes", response_model=ApiResponse)  
async def search_nodes(request: SearchRequest):  
    """搜索节点"""  
    if not graphiti_client:  
        raise HTTPException(status_code=500, detail="Graphiti 客户端未初始化")  
      
    try:  
        results = await graphiti_client.search(  
            query=request.query,  
            group_ids=[request.group_id] if request.group_id else None,  
            num_results=request.limit  
        )  
          
        return ApiResponse(  
            success=True,  
            message="搜索成功",  
            data={"edges": [edge.model_dump() for edge in results]}  
        )  
    except Exception as e:  
        logger.error(f"搜索失败: {e}")  
        raise HTTPException(status_code=500, detail=str(e))