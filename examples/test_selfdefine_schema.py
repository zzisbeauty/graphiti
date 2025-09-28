from pydantic import BaseModel, Field  
from typing import List, Optional  


# 20250923 版本 schema 设计


# 实体定义  
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
  
# 边关系定义  
class MentionsEdge(BaseModel):  
    """提及关系的属性"""  
    context: Optional[str] = Field(None, description="提及的上下文")  
    importance: Optional[float] = Field(None, description="重要性评分 0-1")  
  
class DerivedFromEdge(BaseModel):  
    """来源关系的属性"""  
    page_number: Optional[str] = Field(None, description="页码或章节")  
    confidence: Optional[float] = Field(None, description="来源可信度 0-1")  
  
class PrerequisiteOfEdge(BaseModel):  
    """前置条件关系的属性"""  
    necessity_level: Optional[str] = Field(None, description="必要程度：必须/建议/可选")  
    learning_order: Optional[int] = Field(None, description="学习顺序")  
  
class RelatesToEdge(BaseModel):  
    """相关关系的属性"""  
    relation_strength: Optional[float] = Field(None, description="关联强度 0-1")  
    relation_type: Optional[str] = Field(None, description="关联类型：相似/对比/补充")  
  
class EvolvesFromEdge(BaseModel):  
    """演化关系的属性"""  
    evolution_type: Optional[str] = Field(None, description="演化类型：修正/深化/扩展")  
    time_gap: Optional[str] = Field(None, description="时间间隔")  
  
class AppliesToEdge(BaseModel):  
    """应用关系的属性"""  
    application_context: Optional[str] = Field(None, description="应用场景")  
    effectiveness: Optional[float] = Field(None, description="应用效果 0-1")  
  
class ConflictsWithEdge(BaseModel):  
    """冲突关系的属性"""  
    conflict_type: Optional[str] = Field(None, description="冲突类型：矛盾/对立/不兼容")  
    resolution_needed: Optional[bool] = Field(None, description="是否需要解决")  
  
class SupportsGoalEdge(BaseModel):  
    """支持目标关系的属性"""  
    support_level: Optional[str] = Field(None, description="支持程度：强/中/弱")  
    contribution: Optional[str] = Field(None, description="具体贡献")  
  
class SuggestsEdge(BaseModel):  
    """建议关系的属性"""  
    priority: Optional[str] = Field(None, description="优先级：高/中/低")  
    reasoning: Optional[str] = Field(None, description="建议理由")  
  
class CreatesEdge(BaseModel):  
    """创建关系的属性"""  
    creation_date: Optional[str] = Field(None, description="创建日期")  
    creation_context: Optional[str] = Field(None, description="创建背景")  
  
class ConnectsWithEdge(BaseModel):  
    """连接关系的属性"""  
    connection_type: Optional[str] = Field(None, description="连接类型：协作/讨论/指导")  
    interaction_frequency: Optional[str] = Field(None, description="交互频率")  
  

# 实体类型字典定义  
entity_types = {  
    'Person': Person,                    # 学习者或知识创作者  
    'Note': Note,                        # 用户的学习笔记或记录  
    'Concept': Concept,                  # 具体的概念、术语或知识点  
    'Knowledge': Knowledge,              # 具体的知识片段或事实  
    'LearningTarget': LearningTarget,    # 具体的学习目标  
    'Resource': Resource,                # 学习资源  
    'LearningPath': LearningPath,        # 学习建议或下一步方向  
    'ErrorCorrection': ErrorCorrection,  # 错误纠正记录  
}

# 边类型映射 - 将中文关系名称映射到对应的边类型类  
edge_types = {  
    # 基础关系  
    '提及': MentionsEdge,           # 笔记中提到某个概念  
    '来源于': DerivedFromEdge,      # 知识片段来源于某个资源  
      
    # 概念间关系  
    '前置条件': PrerequisiteOfEdge,  # 概念A是理解概念B的前提条件  
    '相关于': RelatesToEdge,        # 概念之间存在关联但不是前置关系  
      
    # 知识演化关系  
    '演化自': EvolvesFromEdge,      # 新理解从旧理解演化而来  
    '冲突于': ConflictsWithEdge,    # 知识片段之间存在矛盾或冲突  
      
    # 应用和目标关系  
    '应用于': AppliesToEdge,        # 概念应用到具体场景或目标  
    '支持目标': SupportsGoalEdge,   # 知识片段支持某个学习目标  
      
    # 建议和指导关系  
    '建议': SuggestsEdge,          # 基于当前概念建议下一步学习方向  
      
    # 归属和社交关系  
    '创建': CreatesEdge,           # 用户创建了某个内容  
    '连接': ConnectsWithEdge,      # 用户之间的社交或协作关系  
}

# 边类型映射 - 定义哪些实体类型之间可以建立哪些关系  
edge_type_map = {  
    # 笔记相关关系
    ('Note', 'Concept'): ['提及'],                    # 笔记提及概念  
    ('Note', 'Resource'): ['来源于'],                 # 笔记来源于资源  
      
    # 概念间关系
    ('Concept', 'Concept'): ['前置条件', '相关于'],    # 概念间的依赖和关联  
      
    # 知识片段关系
    ('Knowledge', 'Knowledge'): ['演化自', '冲突于'],  # 知识的演化和冲突  
    ('Knowledge', 'Concept'): ['相关于'],             # 知识片段与概念的关联  
      
    # 应用关系  
    ('Concept', 'LearningTarget'): ['应用于'],        # 概念应用于学习目标  
    ('Concept', 'Resource'): ['应用于'],              # 概念在资源中的应用  
      
    # 支持关系  
    ('Knowledge', 'LearningTarget'): ['支持目标'],     # 知识支持学习目标  
      
    # 建议关系  
    ('Concept', 'LearningPath'): ['建议'],            # 概念建议学习路径  
    ('Resource', 'LearningPath'): ['建议'],           # 资源建议学习路径  
      
    # 归属关系  
    ('Person', 'Note'): ['创建'],                     # 用户创建笔记  
    ('Person', 'Knowledge'): ['创建'],                # 用户创建知识片段  
    ('Person', 'LearningTarget'): ['创建'],           # 用户设定学习目标  
      
    # 社交关系  
    ('Person', 'Person'): ['连接'],                   # 用户间的连接关系  
      
    # 纠错关系  
    ('ErrorCorrection', 'Concept'): ['相关于'],       # 错误纠正与概念的关联  
    ('ErrorCorrection', 'Knowledge'): ['相关于'],     # 错误纠正与知识的关联  
}