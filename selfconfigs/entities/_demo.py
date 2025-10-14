from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


# 知识片段（KnowledgeFragment）
class Insight(BaseModel):
    """
    # 知识片段（Insight）

    “知识片段”是用户在学习、阅读、思考或生活中形成的 **独立认知表达**。
    它可以是一种理解、一条观察、一种推论、一段总结，甚至是零散的文字记录。
    这些片段不要求准确或完整，也不要求用户在记录时区分类别。

    系统的任务是帮助用户在图谱中 **自动发现、连接和演化这些知识点**，
    让知识在时间中积累、互相启发与修正。“知识片段”是整个学习网络中最基础、最原子的单元。

    ## 抽取目标
    1. 从原始文本中识别用户表达的核心认知或理解。
    2. 对每个独立认知单元，建立一个 Insight 节点。
    3. 提取关键词和关联概念，用于知识连接。
    4. 识别用户的表达风格（interpretation_style），以捕捉认知的思考方式。

    ## 表达风格识别指南（interpretation_style）
    每个知识片段可能反映不同的表达意图或思考方式。系统应尝试从语言中判断其风格。
    常见风格包括：
    - **analogical（类比式）**：用“像…一样”、“类似于…”等比喻性语言；
    - **summarizing（概括式）**：出现“总之”、“可以归纳为…”、“三点…”等总结性表述；
    - **critical（批判式）**：含“问题”、“不足”、“不是这样”等评价或反驳语；
    - **explaining（解释式）**：有因果连接词“因为”、“所以”、“导致”、“原理是…”；
    - **reflective（反思式）**：出现“我认为”、“我发现”、“我理解到…”等第一人称表达；
    - **comparative（对比式）**：涉及“A 与 B 的区别”、“相比之下”、“不同之处”；
    - **procedural（步骤式）**：出现“第一步”、“然后”、“最后”等顺序逻辑；
    - **hypothetical（假设式）**：出现“如果…则…”、“假如…”、“设想…”；
    - **questioning（提问式）**：以问号结尾，或包含“为什么”、“如何”、“是否”等疑问；
    - **descriptive（描述式）**：仅叙述事实或观察，没有主观评价。

    ## 抽取原则
    - 抽取时不应修改原始内容，仅识别结构化信号；
    - 每个 Insight 应尽量保持语义完整和独立；
    - 如果同一文本中出现多种表达风格，应拆分为多个 Insight；
    - 风格字段（interpretation_style）可留空，系统可后续自动补全；
    - 用户可在审阅阶段修正系统推断的风格。

    ## 目标效果
    Insight 不仅记录“用户理解了什么”，也记录“用户是以怎样的思维方式理解的”。
    这为后续的关系推断（如 AnalogousTo, Refines, Summarizes）提供语义支撑，
    并帮助系统在用户笔记间发现隐含的启发与对比关系。
    """
    
    # —— 知识网络连接
    keywords: Optional[List[str]] = Field(
        None,
        description="从认知内容中提取的关键术语或主题。用户提供优先；否则系统自动提取。"
    )
    related_concepts: Optional[List[str]] = Field(
        None,
        description="关联的概念或知识节点。用户提供优先；否则基于上下文推断。"
    )

    # —— 上下文信息
    context_info: Optional[str] = Field(
        None,
        description="该片段产生的背景环境；可由用户提供或从来源（文件名、页面标题等）提取。"
    )

    # —— 个人化信息
    personal_note: Optional[str] = Field(
        None,
        description="用户的个人理解、联想或感悟（用于区分客观引用与主观观点）。"
    )

    # —— 反思标记
    is_correction: Optional[bool] = Field(
        None,
        description="是否为纠正性认知（例如用户写了'原来我误解了'、'其实不是这样'等）。"
    )

    # —— interpretation_style（新字段）  即 thinking_pattern
    interpretation_style: Optional[
        Literal[
            "analogical",   # 类比式（“像…一样”）
            "summarizing",  # 概括式（总结/归纳）
            "critical",     # 批判/质疑式
            "explaining",   # 解释/说明式（教学风格）
            "reflective",   # 反思式（元认知、感悟）
            "comparative",  # 对比式（A 与 B 比较）
            "procedural",   # 步骤/操作式（分步骤描述）
            "hypothetical", # 假设式（“如果…则…”）
            "questioning",  # 提问式（疑问、未解）
            "descriptive"   # 描述式（事实/观察）
        ]
    ] = Field(
        None,
        description=(
            "用户的思考方式。如果用户明确标注,优先使用用户提供的;否则由系统根据语言特征自动推断"
        )
    )

    # —— 推断来源与置信度（便于用户查看哪些是 AI 推断）
    interpretation_source: Optional[Literal["user", "system"]] = Field(
        None,
        description="标记 interpretation_style 的来源：用户(user) 或 系统自动推断(auto) 等。"
    )

    # # 置信度不是业务属性,不需要显式存储，不要
    # interpretation_confidence: Optional[float] = Field(
    #     None,
    #     ge=0.0, le=1.0,
    #     description="当 interpretation_style 为系统推断时，给出置信度（0-1）。"
    # )

    # # —— 抽取/处理元数据（供调试、可视化与改进模型使用） 调试信息不应该作为 Entity 属性 ，不要
    # extraction_metadata: Optional[Dict[str, Any]] = Field(
    #     default_factory=dict,
    #     description=(
    #         "自动抽取时的辅助信息（例如：触发的规则、关键词、句式特征、情感分数、句子长度等），"
    #         "用于解释系统为何给出该 interpretation_style。"
    #     )
    # )

    # # —— 可选：记录原始来源类型与时间（有助于上下文判断）；和 Episode source 字段重复 ，不要
    # source_type: Optional[Literal["note", "book", "article", "lecture", "web", "quote"]] = Field(
    #     None,
    #     description="该片段的来源类型（如笔记、文章、讲座等），有助于推断表达风格，同时有助于用户明确哪份资料对自己学习帮助最大"
    # )




class Concept(BaseModel):  
    """概念  
      
    "概念"是知识网络中的语义节点,用于连接多个知识片段(Insight)。它代表一个相对稳定、可被引用或讨论的知识点。  
    概念由系统自动从 Episode 内容中抽取。当用户在文本中明确提到某个  
    主题、术语或知识点时,系统会识别并创建对应的 Concept 实体。  
      
    提取指南:  
    - 识别用户明确提到的概念、主题或知识点  
    - 即使概念只在单个 Insight 中出现,只要它是一个独立的、可被引用的知识点,就应该提取  
    - 每个 Concept 应具备清晰语义边界,避免过宽(如"系统")或过窄(如"一次系统调用")  
    - 概念名通常为名词或短语,如"熵增定律"、"贝叶斯推断"  
    - 不要过度推断用户未明确提及的概念  
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