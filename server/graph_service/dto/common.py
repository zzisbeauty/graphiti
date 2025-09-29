from datetime import datetime
from typing import Literal

from graphiti_core.utils.datetime_utils import utc_now
from pydantic import BaseModel, Field


class Result(BaseModel):
    message: str
    success: bool


class Message(BaseModel):
    content: str = Field(..., description='The content of the message')
    uuid: str | None = Field(default=None, description='The uuid of the message (optional)')
    name: str = Field(
        default='', description='The name of the episodic node for the message (optional)'
    )
    role_type: Literal['user', 'assistant', 'system'] = Field(
        ..., description='The role type of the message (user, assistant or system)'
    )
    role: str | None = Field(
        description='The custom role of the message to be used alongside role_type (user name, bot name, etc.)',
    )
    timestamp: datetime = Field(default_factory=utc_now, description='The timestamp of the message')
    source_description: str = Field(
        default='', description='The description of the source of the message'
    )




# 熙增 专门处理 JSON 数据的封装响应
from typing import Optional, Dict, Any, List

class DataProcessingResult(BaseModel):
    """数据处理结果响应"""
    message: str
    success: bool
    episodes_processed: int
    total_nodes_created: int
    total_edges_created: int
  
class BulkDataProcessingResult(BaseModel):
    """批量数据处理结果响应"""  
    message: str 
    success: bool
    episodes_processed: int  
    total_nodes_created: int  
    total_edges_created: int  
    processed_items: List[Dict[str, Any]] = Field(default_factory=list)


# 新增 专门处理  schema 的响应
class SchemaRegistrationResult(BaseModel):  
    """Schema 注册结果响应"""  
    message: str  
    success: bool  
    registered_schemas: List[str]