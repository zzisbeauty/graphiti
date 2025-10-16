from pydantic import BaseModel, Field  
from typing import Optional, List, Literal  
  
# ================================  
# 核心实体层  
# ================================  
  
class Concept(BaseModel):  
    """概念节点 - 知识网络中的术语锚点  
      
    代表独立的**名词或名词短语**,是知识图谱中可被多次引用的节点。  
      
    提取指南:  
    - 识别文本中明确提到的**术语名称**(不是完整的句子或陈述)  
    - 通常是名词或名词短语,例如:"CPU"、"寄存器"、"流水线技术"  
    - **不要提取完整的句子或陈述**,即使它们表达了一个主题  
    - 适用于任何领域:学术、技术、商业、社会、艺术、生活等  
      
    **与 Insight 的区别**:  
    - Concept: "CPU"(术语)  
    - Insight: "CPU是计算机的核心部件"(陈述)  
    """
    description: Optional[str] = Field(None, description="概念简要定义或解释")  
    category: Optional[str] = Field(None, description="概念所属领域或分类")  
      
    # 同义词归一  
    canonical_name: Optional[str] = Field(  
        None,   
        description="规范化名称,用于同义词归一。例如'缓存'和'Cache'都映射到'Cache'"  
    )  
  



class Insight(BaseModel):  
    """洞见节点 - 语义主题级认知单元  
      
    Insight 表示用户在理解、思考或表达过程中形成的**完整陈述**。  
    它是对某个主题、现象、经验或知识片段的综合性表达。  
      
    **特点**:  
    - 必须是**完整的句子或段落**,而不是单一的术语  
    - 可以是知识总结、观察结论、经验反思、理论说明或观点陈述  
    - 是语义上完整、聚焦的认知单元  
      
    **提取指南**:  
    1. 每个 Insight 必须是**完整的句子**,表达一个独立的知识点  
    2. 每个 Insight 聚焦一个核心议题,包含 1-2 个核心 Concept  
    3. 长文本中出现多个不同主题或视角时,应拆分为多个 Insight  
    4. 不要求含有主观标记(如"我认为"),客观陈述亦可  
      
    **示例**:  
    - Insight: "CPU是计算机的核心部件之一"(完整句子,涉及"CPU"这个 Concept)  
    - Insight: "控制单元负责从内存中获取指令并解码"(完整句子,涉及"控制单元"、"内存"等 Concept)  
      
    **与 Concept 的区别**:  
    - Concept: "CPU"(术语)  
    - Insight: "CPU是计算机的核心部件"(陈述)  
    """
      
    # 认知功能类型  
    interpretation_role: Optional[Literal[  
        "descriptive",   # 描述事实、原理或过程  
        "explanatory",   # 解释原因、机制或原理  
        "evaluative",    # 表达观点、评价或取舍  
        "comparative",   # 对比两个或多个对象  
        "inferential",   # 推论、假设或外推  
        "procedural",    # 步骤或方法说明  
        "reflective",    # 反思、顿悟或元认知  
        "questioning",   # 提出问题或未解之处  
        "summarizing"    # 总结、提炼或归纳要点  
    ]] = Field(None, description="该认知单元在知识构建中的功能")  
      
    # 来源标记  
    source_type: Optional[Literal["user", "system"]] = Field(  
        None,   
        description="标记是用户明确记录(user)还是系统自动提取(system)"  
    )  
      
    # 关键词  
    keywords: Optional[List[str]] = Field(  
        None,   
        description="从内容中提取的关键术语,用于知识连接和聚类"  
    )  
      
    # 上下文信息  
    context: Optional[str] = Field(  
        None,   
        description="该知识表达的背景或来源(如笔记来源、书名、会议内容、场景等)"  
    )  
      
    # 是否为修正  
    is_correction: Optional[bool] = Field(  
        False,   
        description="是否为对前述知识的更正或修订"  
    )  
  
  
ENTITY_TYPES = {  
    'Concept': Concept,  
    'Insight': Insight,  
}




# ================================  
# 🔹 关系基类  
# ================================  
  
class RelationBase(BaseModel):  
    """所有关系类型的基类"""  
    directional: bool = Field(..., description="该关系是否有方向性")  
    symmetric: bool = Field(..., description="该关系是否对称(可逆)")  
    layer: str = Field(..., description="关系所属层级")  


# """ 
# # 定义的关系解释
# | 关系类型                      | 通俗理解                                               | 用途                                     | 典型句式示例                                                     |
# | ------------------------- | -------------------------------------------------- | -------------------------------------- | ---------------------------------------------------------- |
# | **REFERENCES**            | **“提到了这个概念”**。Insight 中出现了 Concept，但没有深入定义或描述。     | 这是最常见、最基础的关系类型，用来标记 “这个主题表达中涉及了哪些知识点”。 | “计算机存储技术影响系统性能。” → Insight 引用了 Concept：“计算机存储技术”、“系统性能”。   |
# | **DEFINES**               | **“定义了这个概念”**。Insight 明确说明了 Concept 是什么。           | 用于建立“知识的定义来源”，即某个概念由谁定义、怎么定义的。         | “CPU 是计算机的中央处理单元。” → Insight 定义了 Concept：“CPU”。            |
# | **DESCRIBES**             | **“描述了这个概念的特征或机制”**。Insight 解释了 Concept 怎么运作、有何特征。 | 用来捕捉 “概念的内在属性或原理”。                     | “CPU 包含控制单元和算术逻辑单元。” → Insight 描述了 Concept：“CPU”的结构。       |
# | **REFERENCES_IN_PASSING** | **“顺带提到了这个概念”**。Insight 只是背景提及或举例。                 | 用于降低噪声，区分核心主题与边缘提及。                    | “类似于 CPU 的设计，GPU 也有并行处理结构。” → Insight 核心讲的是 GPU，但顺带提到 CPU。 |

# | 强度          | 关系类型                    | 比喻                                      |
# | ----------- | ----------------------- | --------------------------------------- |
# | 🔴 **强连接**  | `DEFINES`               | Insight 在“命名并说明”一个概念。像老师讲“什么是XX”。       |
# | 🟠 **中连接**  | `DESCRIBES`             | Insight 在“解释”一个概念的内部特性。像老师说“XX由哪些部分组成”。 |
# | 🟢 **弱连接**  | `REFERENCES`            | Insight “提到了”一个概念。像提到一个关键词。             |
# | ⚪️ **极弱连接** | `REFERENCES_IN_PASSING` | Insight “顺便说到”一个概念。像举例或比较时提一下。          |
# """

# 此关系被 DEFINE 等取代
# class REFERENCES(BaseModel):  
#     """ 引用关系 - Insight → Concept  

#     表示 Insight 引用或提及了 Concept。  
#     这是 Insight 和 Concept 之间的通用连接类型。  
      
#     提取指南:  
#     - 识别 Insight 中提到的所有 Concept
#     - 通过 importance 字段区分核心概念和次要概念  
#     - 通过 relation_pattern 字段标记概念在句子中的角色  
#     """  
#     importance: Optional[Literal["primary", "secondary"]] = Field(  
#         "primary",   
#         description="Concept 在该 Insight 中的重要性:primary(核心主题)/secondary(次要提及)"  
#     )

#     relation_pattern: Optional[Literal["subject", "object", "attribute", "context"]] = Field(  
#         None,  
#         description="Concept 在 Insight 中的语法角色:subject(主语)/object(宾语)/attribute(属性)/context(背景)"  
#     )  



# ================================  
# 🔹 Insight → Concept 关系 [语义层]  
# ================================  
  
class DEFINES(RelationBase):  
    """定义关系 - Insight → Concept [语义层]  
      
    表示 Insight 定义或解释了 Concept 的含义。  
      
    提取指南:  
    - 识别"是"、"指的是"、"定义为"等定义性表述  
    - 区分正式定义与非正式解释  
    - 跨领域示例:  
      * 技术: "寄存器是CPU中高速的存储单元"  
      * 生物: "光合作用是植物利用光能合成有机物的过程"  
      * 经济: "通货膨胀是指货币购买力下降的现象"  
    """  
    directional: bool = Field(True, description="定义关系有明确方向")  
    symmetric: bool = Field(False, description="定义关系不对称")  
    layer: str = Field("semantic", description="语义层") 

    definition_type: Optional[Literal["formal", "informal", "example-based"]] = Field(
        None, description="定义的类型"
    ) 

    
class DESCRIBES(RelationBase):  
    """描述关系 - Insight → Concept [语义层]  
      
    表示 Insight 描述了 Concept 的特征、机制或工作原理。  
      
    提取指南:  
    - 识别对 Concept 的特征、属性、机制的描述  
    - 不是定义,而是对特性的说明  
    - 跨领域示例:  
      * 技术: "CPU通过不断循环执行指令来实现数据处理"  
      * 生物: "心脏通过收缩和舒张来泵血"  
      * 社会: "市场通过供需关系来调节价格"  
    """  
    directional: bool = Field(True, description="描述关系有明确方向")  
    symmetric: bool = Field(False, description="描述关系不对称")  
    layer: str = Field("semantic", description="语义层")  
      
    aspect: Optional[Literal["feature", "mechanism", "behavior"]] = Field(  
        None, description="描述的方面"  
    )  
  
  
class REFERENCES_IN_PASSING(RelationBase):  
    """次要提及关系 - Insight → Concept [语义层]  
      
    表示 Insight 顺带提及了 Concept,但不是核心主题。  
      
    提取指南:  
    - 识别非核心的概念引用  
    - 通常出现在对比、举例、背景说明中  
    - 跨领域示例:  
      * 技术: "除了CPU,还有GPU等处理器"  
      * 历史: "除了工业革命,还有信息革命"  
    """  
    directional: bool = Field(True, description="提及关系有明确方向")  
    symmetric: bool = Field(False, description="提及关系不对称")  
    layer: str = Field("semantic", description="语义层")  


# ================================  
# 🔹 Concept → Concept 关系  
# ================================  
  
# --- 等价层 [equivalence] ---  
  
class ALIASED_AS(RelationBase):  
    """同义关系 - Concept ↔ Concept [等价层]  
      
    表示两个概念是同一事物的不同表达形式。  
      
    提取指南:  
    - 识别"也称为"、"即"、"又名"等同义标记  
    - 跨领域示例:  
      * 技术: "缓存" ↔ "Cache"  
      * 医学: "高血压" ↔ "Hypertension"  
      * 日常: "电脑" ↔ "计算机"  
    """  
    directional: bool = Field(False, description="同义关系无方向")  
    symmetric: bool = Field(True, description="同义关系对称")  
    layer: str = Field("equivalence", description="等价层")

# --- 结构层 [structural] ---  
  
class PART_OF(RelationBase):  
    """组成关系 - Concept → Concept [结构层]  
      
    表示当前概念是另一个概念的组成部分。  
    体现层级结构(整体-部分)。  
      
    提取指南:  
    - 识别"是...的一部分"、"包含于"、"属于"等表述  
    - 跨领域示例:  
      * 技术: "寄存器" 是 "CPU" 的一部分  
      * 生物: "心脏" 是 "循环系统" 的一部分  
      * 组织: "研发部" 是 "公司" 的一部分  
    """  
    directional: bool = Field(True, description="组成关系有明确方向")  
    symmetric: bool = Field(False, description="组成关系不对称")  
    layer: str = Field("structural", description="结构层")  


class INCLUDES(RelationBase):  
    """包含关系 - Concept → Concept [结构层]  
      
    表示当前概念包含另一个概念作为部分或成员。  
    是 PART_OF 的逆关系。  
      
    提取指南:  
    - 识别"包含"、"由...组成"等表述  
    - 跨领域示例:  
      * 技术: "CPU" 包含 "寄存器"  
      * 生物: "循环系统" 包含 "心脏"  
    """  
    directional: bool = Field(True, description="包含关系有明确方向")  
    symmetric: bool = Field(False, description="包含关系不对称")  
    layer: str = Field("structural", description="结构层")  


# --- 功能层 [functional] ---  
  
class PERFORMS(RelationBase):  
    """执行关系 - Concept → Concept [功能层]  
      
    表示一个概念执行或承担另一个概念所代表的动作、任务或功能。  
      
    提取指南:  
    - 识别"执行"、"负责"、"完成"等功能性表述  
    - 跨领域示例:  
      * 技术: "CPU" 执行 "指令解析"  
      * 生物: "肝脏" 执行 "代谢功能"  
      * 组织: "销售部" 执行 "市场推广"  
    """  
    directional: bool = Field(True, description="执行关系有明确方向")  
    symmetric: bool = Field(False, description="执行关系不对称")  
    layer: str = Field("functional", description="功能层") 

  
class USES(RelationBase):  
    """使用关系 - Concept → Concept [功能层]  
      
    表示一个概念使用另一个概念、资源或方法以达成功能或目的。  
      
    提取指南:  
    - 识别"使用"、"采用"、"利用"等使用性表述  
    - 跨领域示例:  
      * 技术: "现代CPU" 使用 "流水线技术"  
      * 商业: "公司" 使用 "激励机制"  
      * 医疗: "医生" 使用 "抗生素"  
    """  
    directional: bool = Field(True, description="使用关系有明确方向")  
    symmetric: bool = Field(False, description="使用关系不对称")  
    layer: str = Field("functional", description="功能层") 



# --- 逻辑层 [logical] ---  
  
class CAUSES(RelationBase):  
    """因果关系 - Concept → Concept [逻辑层]  
      
    表示一个概念导致另一个概念的发生、存在或变化。  
      
    提取指南:  
    - 识别"导致"、"引起"、"造成"等因果标记词  
    - 区分直接因果与间接影响  
    - 跨领域示例:  
      * 技术: "高温" 导致 "芯片过热"  
      * 生物: "病毒感染" 导致 "免疫反应"  
      * 经济: "利率上升" 导致 "投资下降"  
    """  
    directional: bool = Field(True, description="因果关系有明确方向")  
    symmetric: bool = Field(False, description="因果关系不对称")  
    layer: str = Field("logical", description="逻辑层")  
      
    strength: Optional[Literal["direct", "indirect"]] = Field(  
        None, description="因果关系的强度"  
    )  


# --- 演化层 [evolutionary] ---  
  
class DERIVED_FROM(RelationBase):  
    """派生关系 - Concept → Concept [演化层]  
      
    表示一个概念从另一个概念演化、继承或抽象而来。  
      
    提取指南:  
    - 识别继承、演化、变体关系  
    - 跨领域示例:  
      * 技术: "RISC-V" 派生自 "RISC 架构"  
      * 学术: "量子计算" 派生自 "量子力学"  
      * 艺术: "现代主义" 派生自 "古典主义"  
    """  
    directional: bool = Field(True, description="派生关系有明确方向")  
    symmetric: bool = Field(False, description="派生关系不对称")  
    layer: str = Field("evolutionary", description="演化层")  



# ================================  
# Insight → Insight 关系  
# ================================  
  
  
class EXTENDS(RelationBase):  
    """扩展关系 - Insight → Insight [推理层]  
      
    表示一个 Insight 扩展或补充了另一个 Insight 的内容。  
      
    提取指南:  
    - 识别"进一步"、"补充说明"、"另外"等扩展性表述  
    - 跨领域示例:  
      * 学术: "量子纠缠现象" 扩展 "量子力学基本原理"  
      * 技术: "微服务架构的优势" 扩展 "分布式系统设计"  
      * 商业: "远程办公的挑战" 扩展 "远程办公的优势"  
    """  
    directional: bool = Field(True, description="扩展关系有明确方向")  
    symmetric: bool = Field(False, description="扩展关系不对称")  
    layer: str = Field("reasoning", description="推理层")  
  
  
class SUPPORTS(RelationBase):  
    """支持关系 - Insight → Insight [推理层]  
      
    表示一个 Insight 支持、佐证或强化了另一个 Insight 的观点。  
      
    提取指南:  
    - 识别"证明"、"支持"、"验证"等支持性表述  
    - 跨领域示例:  
      * 学术: "实验数据" 支持 "理论假设"  
      * 技术: "性能测试结果" 支持 "优化方案有效"  
      * 商业: "市场调研数据" 支持 "产品定位策略"  
    """  
    directional: bool = Field(True, description="支持关系有明确方向")  
    symmetric: bool = Field(False, description="支持关系不对称")  
    layer: str = Field("reasoning", description="推理层")  
    strength: Optional[Literal["strong", "moderate", "weak"]] = Field(  
        None, description="支持强度"  
    )  


class CONTRADICTS(RelationBase):  
    """矛盾关系 - Insight ↔ Insight [推理层]  
      
    表示两个 Insight 之间存在矛盾或冲突,支持知识修正和演化。  
      
    提取指南:  
    - 识别"但是"、"相反"、"矛盾"等对立性表述  
    - 跨领域示例:  
      * 学术: "新研究发现" 矛盾 "传统理论"  
      * 技术: "实际测试结果" 矛盾 "预期性能"  
      * 商业: "用户反馈" 矛盾 "产品假设"  
    """  
    directional: bool = Field(False, description="矛盾关系通常是对称的")  
    symmetric: bool = Field(True, description="矛盾关系对称")  
    layer: str = Field("reasoning", description="推理层")  
    resolution_status: Optional[Literal["unresolved", "resolved", "accepted"]] = Field(  
        None, description="矛盾解决状态"  
    )  



  
# ================================  
# 🔹 完整的 EDGE_TYPE_MAP  
# ================================  
  
EDGE_TYPES = {  
    # Concept → Concept 关系 [结构层/功能层/等价层]  
    'ALIASED_AS': ALIASED_AS,  
    'PART_OF': PART_OF,  
    'INCLUDES': INCLUDES,  
    'PERFORMS': PERFORMS,  
    'USES': USES,  
    'CAUSES': CAUSES,  
    'DERIVED_FROM': DERIVED_FROM,  
      
    # Insight → Concept 关系 [语义层]  
    'DEFINES': DEFINES,  
    'DESCRIBES': DESCRIBES,  
    'REFERENCES_IN_PASSING': REFERENCES_IN_PASSING,  
            
    # Insight → Insight 关系 [推理层]  
    'EXTENDS': EXTENDS,  
    'SUPPORTS': SUPPORTS,  
    'CONTRADICTS': CONTRADICTS,  
}  


EDGE_TYPE_MAP = {  
    # Insight → Concept 关系  
    ('Insight', 'Concept'): [  
        'DEFINES', 'DESCRIBES', 'REFERENCES_IN_PASSING'  
    ],  
    
    # Concept 之间的关系  
    ('Concept', 'Concept'): [  
        'ALIASED_AS', 'PART_OF', 'INCLUDES',   
        'PERFORMS', 'USES', 'CAUSES', 'DERIVED_FROM'  
    ],  
      
    # Insight 之间的关系  
    ('Insight', 'Insight'): ['EXTENDS', 'SUPPORTS', 'CONTRADICTS'],  
}
