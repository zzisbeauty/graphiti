from pydantic import BaseModel, Field
from graph_service.dto.common import Message
from typing import Dict, Type, Optional  



# 该方法是 REST API 中用于接收客户端消息数据的请求模型
class AddMessagesRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the messages to add')
    messages: list[Message] = Field(..., description='The messages to add')
    entity_schema: Optional[Dict[str, Dict]] = None  # 序列化的 schema 定义


class AddEntityNodeRequest(BaseModel):
    uuid: str = Field(..., description='The uuid of the node to add')
    group_id: str = Field(..., description='The group id of the node to add')
    name: str = Field(..., description='The name of the node to add')
    summary: str = Field(default='', description='The summary of the node to add')
