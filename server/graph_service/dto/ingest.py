from pydantic import BaseModel, Field
from graph_service.dto.common import Message
from typing import Dict, Type, Optional  



class AddMessagesRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the messages to add')
    messages: list[Message] = Field(..., description='The messages to add')
    # new add with schema   change - 1     首先更改：支持客户端传入 schema； 接下来去看路由的修改
    entity_schema: Optional[Dict[str, Dict]] = None  # 序列化的 schema 定义



class AddEntityNodeRequest(BaseModel):
    uuid: str = Field(..., description='The uuid of the node to add')
    group_id: str = Field(..., description='The group id of the node to add')
    name: str = Field(..., description='The name of the node to add')
    summary: str = Field(default='', description='The summary of the node to add')
