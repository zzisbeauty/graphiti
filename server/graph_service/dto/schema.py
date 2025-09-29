from typing import Dict, List, Optional, Any  
from pydantic import BaseModel, Field  

""" 专门处理自定义的 schema
"""


class SchemaDefinition(BaseModel):  
    """Schema 定义"""  
    name: str = Field(description="Schema 名称")  
    schema_class: str = Field(description="Schema 类名")   
    module_path: str = Field(description="模块路径")  


class RegisterSchemaRequest(BaseModel):  
    """注册 Schema 请求"""  
    schemas: List[SchemaDefinition] = Field(description="要注册的 Schema 列表")  
  

class SchemaInfoResponse(BaseModel):  
    """Schema 信息响应"""  
    registered_schemas: Dict[str, Dict[str, Any]] = Field(description="已注册的 Schema 信息")  
    total_count: int = Field(description="Schema 总数")
