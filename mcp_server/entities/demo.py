from pydantic import BaseModel, Field  
from typing import List, Optional  
  
# 您的实体定义  
class Person(BaseModel):  
    """学习者或知识创作者，如作者、老师、同学等具体的人"""  
    user_id: Optional[str] = Field(None, description="用户ID")  
    display_name: Optional[str] = Field(None, description="姓名/昵称")  
    interests: Optional[List[str]] = Field(None, description="兴趣领域")  
    preferences: Optional[str] = Field(None, description="偏好")  
  
class Note(BaseModel):  
    """用户的学习笔记或记录，包含具体的学习内容"""  
    note_id: Optional[str] = Field(None, description="笔记ID")  
    title: Optional[str] = Field(None, description="标题")  
    content: Optional[str] = Field(None, description="内容")  
    created_time: Optional[str] = Field(None, description="创建时间")  
    updated_time: Optional[str] = Field(None, description="更新时间")  
    source: Optional[str] = Field(None, description="来源")  
    importance_mark: Optional[str] = Field(None, description="重点标记")  
    version: Optional[str] = Field(None, description="版本")  
  
class Concept(BaseModel):  
    """具体的概念、术语或知识点，如'并发'、'操作系统'、'机器学习'等"""  
    concept_id: Optional[str] = Field(None, description="概念ID")  
    concept_name: Optional[str] = Field(None, description="概念名称")  
    user_definition: Optional[str] = Field(None, description="用户定义")  
    prerequisite_concepts: Optional[List[str]] = Field(None, description="前置概念")  
    related_concepts: Optional[List[str]] = Field(None, description="相关概念")  
    examples: Optional[List[str]] = Field(None, description="示例")  
    application_domains: Optional[List[str]] = Field(None, description="应用领域")  
    understanding_level: Optional[str] = Field(None, description="理解程度")  
    version: Optional[str] = Field(None, description="版本")  
  
class Knowledge(BaseModel):  
    """具体的知识片段或事实，如'Python是编程语言'、'TCP是传输协议'等"""  
    knowledge_id: Optional[str] = Field(None, description="知识ID")  
    content_summary: Optional[str] = Field(None, description="知识内容摘要")  
    confidence_level: Optional[str] = Field(None, description="用户表达的确定程度")  
    source_context: Optional[str] = Field(None, description="知识来源上下文")  
    actual_examples: Optional[List[str]] = Field(None, description="实际应用例子")  
    contradictions: Optional[List[str]] = Field(None, description="矛盾点")  
    version: Optional[str] = Field(None, description="版本")  
  
class LearningTarget(BaseModel):  
    """具体的学习目标，如'掌握Python编程'、'理解操作系统原理'等"""  
    target_id: Optional[str] = Field(None, description="目标ID")  
    target_description: Optional[str] = Field(None, description="目标描述")  
    target_domain: Optional[str] = Field(None, description="目标领域")  
    priority: Optional[str] = Field(None, description="优先级")  
    deadline: Optional[str] = Field(None, description="期限")  
    progress_status: Optional[str] = Field(None, description="进度状态")  
  
class Resource(BaseModel):  
    """学习资源，如书籍、视频、文档、网站等具体材料"""  
    resource_id: Optional[str] = Field(None, description="资源ID")  
    resource_type: Optional[str] = Field(None, description="类型")  
    title: Optional[str] = Field(None, description="标题")  
    author: Optional[str] = Field(None, description="作者")  
    url_path: Optional[str] = Field(None, description="URL/路径")  
    publish_time: Optional[str] = Field(None, description="出版/创建时间")  
    usefulness_rating: Optional[float] = Field(None, description="有用性评价")  
    importance_mark: Optional[str] = Field(None, description="重点标记")  
  
class LearningPath(BaseModel):  
    """学习建议或下一步方向，如'建议先学习数据结构'、'可以深入研究算法'等"""  
    direction_id: Optional[str] = Field(None, description="方向ID")  
    suggested_topic: Optional[str] = Field(None, description="建议主题")  
    reasoning: Optional[str] = Field(None, description="推荐理由")  
    priority: Optional[str] = Field(None, description="优先级")  
    estimated_time: Optional[str] = Field(None, description="预估时间")  
  
class ErrorCorrection(BaseModel):  
    """错误纠正记录，指出并修正理解中的错误"""  
    correction_id: Optional[str] = Field(None, description="纠错ID")  
    error_description: Optional[str] = Field(None, description="错误描述")  
    suggested_correction: Optional[str] = Field(None, description="建议纠正")  
    confidence: Optional[float] = Field(None, description="置信度")  
    reference_source: Optional[str] = Field(None, description="参考来源")  
  


# ENTITY_TYPES 定义  
ENTITY_TYPES: dict[str, type[BaseModel]] = {  
    'Person': Person,  
    'Note': Note,  
    'Concept': Concept,  
    'Knowledge': Knowledge,  
    'LearningTarget': LearningTarget,  
    'Resource': Resource,  
    'LearningPath': LearningPath,  
    'ErrorCorrection': ErrorCorrection,  
}
