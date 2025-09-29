from fastapi import APIRouter, HTTPException, status  
from graph_service.dto import RegisterSchemaRequest, SchemaInfoResponse, Result

# 依赖注入 ZepGraphitiDep 实例
from graph_service.zep_graphiti import ZepGraphitiDep  


router = APIRouter(prefix="/custom-schema", tags=["Custom Schema"])  




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
    sys.path.insert(0, '/home/graphiti')







# from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List 
from fastapi import APIRouter, HTTPException, status, Depends 


# 全局 Schema 管理器  
from graph_service.routers.schema_manager import SchemaManager
from graph_service.dto.common import SchemaRegistrationResult

schema_manager = SchemaManager()


@router.post('/register-schemas-direct', status_code=status.HTTP_201_CREATED)  
async def register_schemas_direct(  
    schemas: Dict[str, Any],  # 直接接收 schema 字典  
    graphiti: ZepGraphitiDep,  
) -> SchemaRegistrationResult:  
    """直接注册客户端传入的 Schema"""  
    try:  
        # 直接注册 schema（假设客户端已经传入了正确的 Pydantic 模型）  
        registered_schemas = schema_manager.register_schemas_direct(schemas)  
          
        # 在 ZepGraphiti 中注册  
        graphiti.register_entity_types(registered_schemas)  
          
        return SchemaRegistrationResult(  
            message=f"成功注册 {len(registered_schemas)} 个 Schema",  
            success=True,  
            registered_schemas=list(registered_schemas.keys())  
        )  
      
    except Exception as e:  
        raise HTTPException(  
            status_code=status.HTTP_400_BAD_REQUEST,  
            detail=f"Schema 注册失败: {str(e)}"  
        )  
  
@router.get('/schemas', status_code=status.HTTP_200_OK)  
async def get_schemas(graphiti: ZepGraphitiDep) -> SchemaInfoResponse:  
    """获取所有已注册的 Schema 信息"""  
    schemas_info = graphiti.get_all_entity_schemas()  
    return SchemaInfoResponse(  
        registered_schemas=schemas_info,  
        total_count=len(schemas_info)  
    )  
  
@router.delete('/schemas', status_code=status.HTTP_200_OK)  
async def clear_schemas(graphiti: ZepGraphitiDep) -> Result:  
    """清空所有已注册的 Schema"""  
    schema_manager.clear_schemas()  
    graphiti.clear_entity_types()  
      
    return Result(message="所有 Schema 已清空", success=True)