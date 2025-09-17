from pydantic import BaseModel, Field  
from typing import List, Optional  


class Concept(BaseModel):  
    """核心概念/知识点。知识关联放在实体属性上，便于快速检索相关概念。"""  
    title: str = Field(description="标题")  
    description: str = Field(description="描述")   
    tags: List[str] = Field(description="标签列表")  
    aliases: Optional[List[str]] = Field(None, description="别名")  
    priority_level: Optional[str] = Field(None, description="重点标签（普通/重点/其他）")  
    knowledge_relations: Optional[List[str]] = Field(None, description="知识关联(list of Concept id)")  


class Note(BaseModel):  
    """段落/片段笔记，用于关联 Concept"""  
    text: str = Field(description="文本内容")  
    source_id: str = Field(description="来源id")  
    confidence: float = Field(description="置信度")  
    language: Optional[str] = Field(None, description="语言")  
    page_number: Optional[str] = Field(None, description="页码/时间戳")  
    priority_level: Optional[str] = Field(None, description="重点标签")  


class Resource(BaseModel):  
    """原始资料或信息源"""  
    resource_type: str = Field(description="类型(Notion/PDF/视频/会议/网页等)")  
    title: str = Field(description="标题")  
    url: str = Field(description="URL")  
    author: str = Field(description="作者")  
    ingest_time: str = Field(description="ingest时间")  
    transcript_id: Optional[str] = Field(None, description="transcript_id")  
    format: Optional[str] = Field(None, description="格式")  


class Review(BaseModel):  
    """复习记录，学习建议放在 Review 实体上，便于复习时给用户提示。"""  
    timestamp: str = Field(description="时间戳")  
    result: str = Field(description="结果")  
    next_review_time: str = Field(description="下次复习时间")  
    score: Optional[float] = Field(None, description="分数")  
    interval: Optional[int] = Field(None, description="学习间隔")  
    learning_advice: Optional[str] = Field(None, description="学习建议")  


class Person(BaseModel):  
    """作者/讲者或自己，用于资源归属与复习"""  
    person_name: str = Field(description="姓名")  
    role: str = Field(description="角色（作者/讲者/自己）")  
    department: Optional[str] = Field(None, description="部门/小组")



class MentionsEdge(BaseModel):  
    """Note → Concept，笔记中提到的知识点"""  
    evidence: str = Field(description="证据")  
    confidence: float = Field(description="置信度")  
  
class DerivedFromEdge(BaseModel):  
    """Note → Resource，笔记来源"""  
    confidence: float = Field(description="置信度")  
  
class RelatedToEdge(BaseModel):  
    """Concept ↔ Concept，语义关联"""  
    relation_type: str = Field(description="关系类型（类似/支持/矛盾/因果等）")  
    confidence: float = Field(description="置信度")  
  
class ReviewedAtEdge(BaseModel):  
    """Person → Review，记录复习行为"""  
    score: Optional[float] = Field(None, description="分数")  
    interval: Optional[int] = Field(None, description="间隔")  
  
# CREATED_BY 和 ABOUT 关系无需额外属性，使用默认的 EntityEdge 即可



entity_types = {  
    'Concept': Concept,  
    'Note': Note,  
    'Resource': Resource,  
    'Review': Review,  
    'Person': Person  
}  
  
edge_types = {  
    'MENTIONS': MentionsEdge,  
    'DERIVED_FROM': DerivedFromEdge,  
    'RELATED_TO': RelatedToEdge,  
    'REVIEWED_AT': ReviewedAtEdge,  
    # CREATED_BY 和 ABOUT 使用默认边类型  
}  
  
# result = await graphiti.add_episode(  
#     name='Knowledge Episode',  
#     episode_body=episode_content,  
#     source_description='Learning content',  
#     reference_time=datetime.now(timezone.utc),  
#     entity_types=entity_types,  
#     edge_types=edge_types,  
#     group_id='your_group_id'  
# )
