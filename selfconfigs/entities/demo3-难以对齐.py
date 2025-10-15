from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


# 知识片段（KnowledgeFragment）
class Insight(BaseModel):
    """  
    # Insight（认知片段）  
  
    Insight 表示用户在学习、阅读或思考过程中形成的 **知识表述单元**。  
    它是一个完整的句子或段落,包含对某个主题的描述、解释或评价。  
      
    **关键区别**:  
    - Insight 是完整的知识表达(句子或段落),如"计算机存储技术是信息系统的核心之一"  
    - Concept 是被引用的知识点(名词或短语),如"计算机存储技术"、"寄存器"  
      
    **提取规则**:  
    1. 如果文本是一个完整的陈述句,提取为 Insight  
    2. 如果文本只是一个术语或概念名称,提取为 Concept  
    3. 一个 Insight 可以包含多个 Concept  
    4. 优先提取 Insight,然后从 Insight 中识别 Concept  
  
    ## 抽取目标  
    1. 从文本中识别具有独立语义的完整知识表达(句子或段落);  
    2. 提取关键词和相关概念(Concept);  
    3. 判断该表达的认知功能(interpretation_role);  
    4. 建立 Insight → Concept 的语义关系。  
  
    ## 认知功能(interpretation_role)  
    Insight 根据其在知识构建中的功能可分类为:  
    - **descriptive**: 描述事实、原理或过程;  
    - **explanatory**: 解释原因、机制或原理;  
    - **evaluative**: 表达观点、评价或取舍;  
    - **comparative**: 对比两个或多个对象;  
    - **inferential**: 推论、假设或外推;  
    - **procedural**: 步骤或方法说明;  
    - **reflective**: 反思、顿悟或元认知;  
    - **questioning**: 提出问题或未解之处;  
    - **summarizing**: 总结、提炼或归纳要点。  
  
    ## 抽取原则  
    - 不要求 Insight 含有主观标记(如"我认为"),客观陈述亦可;  
    - 每个 Insight 应该是一个完整的句子或段落;  
    - 同一文本中出现多种认知功能时,可拆分为多个 Insight;  
    - interpretation_role 可为空,由系统后续推断;  
    - 用户可在审阅阶段修改系统推断结果。  
    """

    # —— 基本信息
    interpretation_role: Optional[
        Literal[
            "descriptive", "explanatory", "evaluative",
            "comparative", "inferential", "procedural",
            "reflective", "questioning", "summarizing"
        ]
    ] = Field(None, description="该知识表达在学习网络中的认知功能")

    source_type: Optional[Literal["user", "system"]] = Field(
        None, description="标记该片段是用户明确记录(user)还是系统自动提取(system)"
    )

    # —— 内容与连接
    keywords: Optional[List[str]] = Field(
        None, description="从内容中提取的关键术语，用于知识连接和聚类"
    )

    related_concepts: Optional[List[str]] = Field(
        None, description="与该片段相关的概念节点，用于建立语义关系"
    )

    context: Optional[str] = Field(
        None, description="该知识表达的背景或来源（如文件名、章节、笔记标题等）"
    )



class Concept(BaseModel):  
    """概念 - 知识网络中的术语节点  
      
    Concept 代表一个独立的术语、名词或短语,是知识网络中可被引用的基本单元。  
    它通常是一个名词或名词短语,而不是完整的句子。  
      
    **关键区别**:  
    - Concept 是术语或名词短语,如"计算机存储技术"、"寄存器"、"Cache"  
    - Insight 是完整的知识表达,如"寄存器容量极小但速度最快"  
      
    提取指南:  
    - 识别文本中明确提到的术语、概念名称  
    - 通常是名词或名词短语,不是完整的句子  
    - 可以从 Insight 中提取,也可以独立存在  
    - 每个 Concept 应该是独立的、可被多次引用的  
    """

    # 概念定义  
    definition: Optional[str] = Field(  
        None,  
        description="概念的定义或描述。如果用户提供了定义,优先使用用户的表述,否则可以从上下文中总结"  
    )
      
    # 领域分类  
    domain: Optional[str] = Field(  
        None,  
        description="概念所属的领域或学科,如'物理学'、'经济学'、'心理学'等"  
    )  
      
    # 实例说明  
    examples: Optional[List[str]] = Field(  
        None,  
        description="与该概念直接相关的实例或情境,用于帮助理解概念的应用场景"  
    )  
      
    # 前置知识  
    prerequisite_concepts: Optional[List[str]] = Field(  
        None,  
        description="理解此概念前需要掌握的前置概念。例如理解'梯度下降'需要先理解'导数'"  
    )  



ENTITY_TYPES = {  
    'Insight': Insight,  
    'Concept': Concept,  
}


# ================================== 第一阶段，只有 Insight → Concept 结构型边 ==================================


# About (主题锚定关系)
# confidence 字段支持后续的图谱质量控制,可以过滤掉置信度低的边
class About(BaseModel):  
    """涉及或讨论关系  
      
    表示 Insight 的核心内容涉及或讨论了某个 Concept。  
    这是 Insight 和 Concept 之间最主要的连接类型。  
      
    提取指南:  
    - 识别 Insight 的核心主题  
    - 如果 Concept 是 Insight 的主要讨论对象,使用 About  
    - 评估主题识别的确定性,设置 confidence 值  
    """  
    relevance: Optional[str] = Field(  
        None,  
        description="相关性强度:primary(主要主题)/secondary(次要主题)"  
    )  
      
    confidence: Optional[float] = Field(  
        None,  
        ge=0.0, le=1.0,  
        description="系统对主题识别的置信度(0~1)。用于过滤弱主题或模糊主题,在主题提取不唯一时特别有用"  
    )


# # ReferencesInPassing (次要提及关系) 
# """
# 为什么这个优化有价值:
#     reference_context 为后续的隐含关系推断提供了关键信号
#     例如,如果两个 Concept 都在 analogy 语境中被提及,系统可以推断它们之间可能存在 AnalogousTo 关系
#     这与您的产品目标"帮用户显性化隐含关系"完美契合
# """
class ReferencesInPassing(BaseModel):  
    """次要提及关系  
      
    表示 Insight 顺带提及了某个 Concept,但不是核心主题。  
    这条边在图谱中形成"语义桥梁",帮助发现远距离的潜在连接。  
      
    提取指南:  
    - 识别 Insight 中非核心的概念引用  
    - 通常出现在对比、举例、背景说明中  
    - 捕捉提及的具体语境,用于后续推理  
    """  
    reference_context: Optional[str] = Field(  
        None,  
        description="提及的语境:comparison(对比)/analogy(类比)/background(背景)/example(举例)"  
    )

# Defines (定义关系)
# """
# 为什么这个优化有价值:

# source_type 帮助追溯知识来源,支持"尊重用户认知状态"的理念
# precision_level 标记定义的完整性,为后续的概念演化提供基础
# 当用户后来给出更精确的定义时,系统可以通过 Graphiti 的时间追踪机制标记旧定义为 invalid_at
# """
class Defines(BaseModel):  
    """定义关系  
      
    表示 Insight 给出了 Concept 的定义或核心含义。  
    清晰指向"概念构建"。  
      
    提取指南:  
    - 识别"X 是..."、"X 指的是..."等定义性表达  
    - Insight 应该包含对 Concept 的明确定义  
    - 区分定义的来源和精确程度  
    """  
    definition_type: Optional[str] = Field(  
        None,  
        description="定义类型:formal(正式定义)/informal(非正式解释)/example-based(基于示例)"  
    )  
      
    source_type: Optional[str] = Field(  
        None,  
        description="定义来源:user(用户自创)/citation(引用资料)/derived(总结提炼)"  
    )  
      
    precision_level: Optional[str] = Field(  
        None,  
        description="定义精确程度:exact(精确定义)/approximate(大致说明)"  
    )

# Describes (描述关系)
# """
# 为什么这个优化有价值:

# scope 字段让模型能够区分静态结构和动态过程
# 这为后续的多维度知识检索提供了基础
# 例如,用户可以查询"某个概念的动态机制描述"
# """
class Describes(BaseModel):  
    """描述关系  
    表示 Insight 描述了 Concept 的特征、机制或工作原理。  
    可以扩展出丰富的语义图(属性网)。  

    提取指南:
    - 识别对 Concept 的特征、属性、机制的描述  
    - 不是定义,而是对特性的说明  
    - 区分结构性描述与动态机制描述  
    """  
    aspect: Optional[str] = Field(  
        None,  
        description="描述的方面:feature(特征)/mechanism(机制)/behavior(行为)"  
    )  
      
    scope: Optional[str] = Field(  
        None,  
        description="描述的范围:whole(整体特征)/part(局部特征)/dynamic(过程或变化)"  
    )


# 完整的 Edge Type Map 配置
EDGE_TYPE_MAP = {  
    # Insight → Concept (结构型边 - 只有 Insight 和 Concept 类型的节点之间才能建立这些边)  
    ('Insight', 'Concept'): ['About', 'ReferencesInPassing', 'Defines', 'Describes'],   
}  
  
EDGE_TYPES = {  
    'About': About,
    'ReferencesInPassing': ReferencesInPassing,  
    'Defines': Defines,  
    'Describes': Describes,  
}