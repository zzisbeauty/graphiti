from pydantic import BaseModel, Field

from graph_service.dto.common import Message


class AddMessagesRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the messages to add')
    messages: list[Message] = Field(..., description='The messages to add')
    # todo 新增以添加自定义 schema
    use_custom_entities: bool = False  # 添加此字段


class AddEntityNodeRequest(BaseModel):
    uuid: str = Field(..., description='The uuid of the node to add')
    group_id: str = Field(..., description='The group id of the node to add')
    name: str = Field(..., description='The name of the node to add')
    summary: str = Field(default='', description='The summary of the node to add')


# todo 新增以解析 API 传入的字段
class AddEpisodeWithSchemaRequest(BaseModel):  
    name: str = Field(..., description='Episode name')  
    episode_body: str = Field(..., description='Episode content')  
    group_id: str = Field(..., description='Group ID')  
    source_description: str = Field(default='', description='Source description')  
    use_custom_entities: bool = Field(default=True, description='Whether to use custom entity types')