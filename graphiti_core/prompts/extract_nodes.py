from typing import Any, Protocol, TypedDict
from pydantic import BaseModel, Field
from .models import Message, PromptFunction, PromptVersion
from .prompt_helpers import to_prompt_json

class ExtractedEntity(BaseModel):
    name: str = Field(..., description='Name of the extracted entity')
    entity_type_id: int = Field(description='ID of the classified entity type. Must be one of the provided entity_type_id integers.',)

class ExtractedEntities(BaseModel):
    extracted_entities: list[ExtractedEntity] = Field(..., description='List of extracted entities')

class MissedEntities(BaseModel):
    missed_entities: list[str] = Field(..., description="Names of entities that weren't extracted")

class EntityClassificationTriple(BaseModel):
    uuid: str = Field(description='UUID of the entity')
    name: str = Field(description='Name of the entity')
    entity_type: str | None = Field(default=None, description='Type of the entity. Must be one of the provided types or None')

class EntityClassification(BaseModel):
    entity_classifications: list[EntityClassificationTriple] = Field(..., description='List of entities classification triples.')

class EntitySummary(BaseModel):
    summary: str = Field(..., description='Summary containing the important information about the entity. Under 250 words',)

class Prompt(Protocol):
    extract_message: PromptVersion
    extract_json: PromptVersion
    extract_text: PromptVersion
    reflexion: PromptVersion
    classify_nodes: PromptVersion
    extract_attributes: PromptVersion
    extract_summary: PromptVersion

class Versions(TypedDict):
    extract_message: PromptFunction
    extract_json: PromptFunction
    extract_text: PromptFunction
    reflexion: PromptFunction
    classify_nodes: PromptFunction
    extract_attributes: PromptFunction
    extract_summary: PromptFunction


# ========================================================= 系统提示，定义角色和任务
# def extract_json(context: dict[str, Any]) -> list[Message]:
#     sys_prompt = """You are an AI assistant that extracts entity nodes from JSON. 
#     Your primary task is to extract and classify relevant entities from JSON files"""

#     user_prompt = f"""
# <ENTITY TYPES>
# {context['entity_types']}
# </ENTITY TYPES>

# <SOURCE DESCRIPTION>:
# {context['source_description']}
# </SOURCE DESCRIPTION>
# <JSON>
# {context['episode_content']}
# </JSON>

# {context['custom_prompt']}

# Given the above source description and JSON, extract relevant entities from the provided JSON.
# For each entity extracted, also determine its entity type based on the provided ENTITY TYPES and their descriptions.
# Indicate the classified entity type by providing its entity_type_id.

# Guidelines:
# 1. Always try to extract an entities that the JSON represents. This will often be something like a "name" or "user field
# 2. Do NOT extract any properties that contain dates
# """
#     return [
#         Message(role='system', content=sys_prompt),
#         Message(role='user', content=user_prompt),
#     ]

def extract_json(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """你是一个从 JSON 中提取实体节点的 AI 助手。你的主要任务是从 JSON 文件中提取并分类相关实体"""
    user_prompt = f"""
<实体类型>
{context['entity_types']}
</实体类型>


<来源描述>:
{context['source_description']}
</来源描述>
<JSON>
{context['episode_content']}
</JSON>

{context['custom_prompt']}

根据上述来源描述和 JSON，从提供的 JSON 中提取相关实体。对于每个提取的实体，还需根据提供的实体类型及其描述确定实体类型。通过提供对应的 entity_type_id 来指明分类后的实体类型。

指南：
1. 始终尝试提取 JSON 所表示的实体，这通常是“名称”或“用户字段”等。
2. 不要提取任何包含日期的属性。
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


# ======================================================== extract_message  此提示词够用

def extract_message(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that extracts entity nodes from conversational messages. 
    Your primary task is to extract and classify the speaker and other significant entities mentioned in the conversation."""

    user_prompt = f"""
<ENTITY TYPES>
{context['entity_types']}
</ENTITY TYPES>

<PREVIOUS MESSAGES>
{to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
{context['episode_content']}
</CURRENT MESSAGE>

Instructions:

You are given a conversation context and a CURRENT MESSAGE. Your task is to extract **entity nodes** mentioned **explicitly or implicitly** in the CURRENT MESSAGE.
Pronoun references such as he/she/they or this/that/those should be disambiguated to the names of the 
reference entities. Only extract distinct entities from the CURRENT MESSAGE. Don't extract pronouns like you, me, he/she/they, we/us as entities.

1. **Speaker Extraction**: Always extract the speaker (the part before the colon `:` in each dialogue line) as the first entity node.
   - If the speaker is mentioned again in the message, treat both mentions as a **single entity**.

2. **Entity Identification**:
   - Extract all significant entities, concepts, or actors that are **explicitly or implicitly** mentioned in the CURRENT MESSAGE.
   - **Exclude** entities mentioned only in the PREVIOUS MESSAGES (they are for context only).

3. **Entity Classification**:
   - Use the descriptions in ENTITY TYPES to classify each extracted entity.
   - Assign the appropriate `entity_type_id` for each one.

4. **Exclusions**:
   - Do NOT extract entities representing relationships or actions.
   - Do NOT extract dates, times, or other temporal information—these will be handled separately.

5. **Formatting**:
   - Be **explicit and unambiguous** in naming entities (e.g., use full names when available).

{context['custom_prompt']}
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]

def _extract_message(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """你是一个从对话消息中提取实体节点的 AI 助手。你的主要任务是提取并分类对话中提到的说话者及其他重要实体。"""

    user_prompt = f"""
<实体类型>
{context['entity_types']}
</实体类型>

<之前的消息>
{to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
</之前的消息>

<当前消息>
{context['episode_content']}
</当前消息>

说明：

你将获得一个对话上下文和当前消息。你的任务是从当前消息中提取**明确或隐含提及**的**实体节点**。
代词如他/她/他们或这/那/那些应明确指代为对应的实体名称。
仅从当前消息中提取独立实体，不要将“你”、“我”、“他/她/他们”、“我们/咱们”等代词作为实体提取。

1. **说话者提取**：始终将说话者（每句对话中冒号“:”前的部分）作为第一个实体节点提取。
   - 如果说话者在消息中多次出现，应视为**同一实体**。

2. **实体识别**：
   - 提取当前消息中**明确或隐含**提及的所有重要实体、概念或角色。
   - **排除**仅在之前的消息中提及的实体（这些只作上下文参考）。

3. **实体分类**：
   - 使用实体类型描述来分类每个提取的实体。
   - 为每个实体分配对应的 `entity_type_id`。

4. **排除内容**：
   - 不提取表示关系或动作的实体。
   - 不提取日期、时间或其他时间信息——这些将另行处理。

5. **格式要求**：
   - 实体命名需**明确且无歧义**（例如尽量使用全名）。

{context['custom_prompt']}
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]

def __extract_message(context: dict[str, Any]) -> list[Message]:  
    """优化后的中文实体提取 prompt"""  
    sys_prompt = """你是一个专业的中文实体提取助手。你的任务是从对话中提取实体节点。  
  
重要规则：  
1. 必须严格按照JSON格式输出，不要添加任何解释文字  
2. 只提取当前消息中明确提到的实体  
3. 使用完整的实体名称，避免缩写  
4. 确保entity_type_id是有效的数字"""  
  
    user_prompt = f"""  
<实体类型>  
{context['entity_types']}  
</实体类型>  
  
<当前消息>  
{context['episode_content']}  
</当前消息>  
  
任务：从当前消息中提取实体，输出格式如下：  
  
{{  
  "extracted_entities": [  
    {{  
      "name": "实体名称",  
      "entity_type_id": 数字ID  
    }}  
  ]  
}}  
  
示例：  
{{  
  "extracted_entities": [  
    {{"name": "曹雪芹", "entity_type_id": 1}},  
    {{"name": "红楼梦", "entity_type_id": 2}}  
  ]  
}}  
  
严格按照上述JSON格式输出，不要包含任何其他文字：  
"""  
      
    return [  
        Message(role='system', content=sys_prompt),  
        Message(role='user', content=user_prompt),  
    ]


# ========================================================================== extract_text
def extract_text(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that extracts entity nodes from text. Your primary task is to extract and classify the speaker and other significant entities mentioned in the provided text."""
    user_prompt = f"""
                <ENTITY TYPES>
                {context['entity_types']}
                </ENTITY TYPES>

                <TEXT>
                {context['episode_content']}
                </TEXT>

                Given the above text, extract entities from the TEXT that are explicitly or implicitly mentioned.
                For each entity extracted, also determine its entity type based on the provided ENTITY TYPES and their descriptions.
                Indicate the classified entity type by providing its entity_type_id.

                {context['custom_prompt']}

                Guidelines:
                1. Extract significant entities, concepts, or actors mentioned in the conversation.
                2. Avoid creating nodes for relationships or actions.
                3. Avoid creating nodes for temporal information like dates, times or years (these will be added to edges later).
                4. Be as explicit as possible in your node names, using full names and avoiding abbreviations.
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]

# CHINESE - 1
def _extract_text(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """你是一个从文本中提取实体节点的 AI 助手。你的主要任务是提取并分类提供文本中提到的说话者及其他重要实体。"""
    user_prompt = f"""
                    <实体类型>
                    {context['entity_types']}
                    </实体类型>

                    <文本>
                    {context['episode_content']}
                    </文本>

                    请根据上述文本，从文本中明确或隐含提及的实体中提取实体。对于每个提取的实体，还需根据提供的实体类型及其描述确定其实体类型。
                    通过提供对应的 entity_type_id 来指明分类后的实体类型。

                    {context['custom_prompt']}

                    指南：
                    1. 提取对话中提到的重要实体、概念或角色。
                    2. 避免为关系或动作创建节点。
                    3. 避免为时间信息（如日期、时间或年份）创建节点（这些信息稍后会加到边上）。
                    4. 节点名称尽可能明确，使用全名，避免缩写。
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]

def __extract_text(context: dict[str, Any]) -> list[Message]:  
    sys_prompt = """你是专业的中文实体提取助手。严格按照JSON格式输出，不要添加解释。  
      
    重要约束：  
    1. 只输出实体名称和类型ID  
    2. 不要提取任何属性信息  
    3. 不要使用嵌套对象或复杂结构"""  
  
    user_prompt = f"""  
<实体类型>  
{context['entity_types']}  
</实体类型>  
  
<文本>  
{context['episode_content']}  
</文本>  
  
从文本中提取实体，严格按照以下JSON格式输出：  
  
{{  
  "extracted_entities": [  
    {{  
      "name": "实体名称",  
      "entity_type_id": 数字ID  
    }}  
  ]  
}}  
  
注意：只提取实体名称，不要添加任何额外的属性或描述信息。  
  
只输出JSON，不要其他内容：  
"""  
      
    return [  
        Message(role='system', content=sys_prompt),  
        Message(role='user', content=user_prompt),  
    ]


# ===================================================================== reflexion
def reflexion(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that determines which entities have not been extracted from the given context"""
    user_prompt = f"""
                <PREVIOUS MESSAGES>
                {to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
                </PREVIOUS MESSAGES>
                <CURRENT MESSAGE>
                {context['episode_content']}
                </CURRENT MESSAGE>

                <EXTRACTED ENTITIES>
                {context['extracted_entities']}
                </EXTRACTED ENTITIES>

                Given the above previous messages, current message, and list of extracted entities; determine if any entities haven't been extracted.
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def _reflexion(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """你是一个 AI 助手，用于判断给定上下文中是否有未被提取的实体"""

    user_prompt = f"""
<之前的消息>
{to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
</之前的消息>
<当前消息>
{context['episode_content']}
</当前消息>

<已提取的实体>
{context['extracted_entities']}
</已提取的实体>


请根据上述之前的消息、当前消息和已提取实体列表，判断是否还有未被提取的实体。
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]



# ============================================================================= classify_nodes
def classify_nodes(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that classifies entity nodes given the context from which they were extracted"""
    user_prompt = f"""
    <PREVIOUS MESSAGES>
    {to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
    </PREVIOUS MESSAGES>
    <CURRENT MESSAGE>
    {context['episode_content']}
    </CURRENT MESSAGE>
    
    <EXTRACTED ENTITIES>
    {context['extracted_entities']}
    </EXTRACTED ENTITIES>
    
    <ENTITY TYPES>
    {context['entity_types']}
    </ENTITY TYPES>
    
    Given the above conversation, extracted entities, and provided entity types and their descriptions, classify the extracted entities.
    
    Guidelines:
    1. Each entity must have exactly one type
    2. Only use the provided ENTITY TYPES as types, do not use additional types to classify entities.
    3. If none of the provided entity types accurately classify an extracted node, the type should be set to None
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]

def _classify_nodes(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """你是一个 AI 助手，用于根据提取实体的上下文对实体节点进行分类"""

    user_prompt = f"""
    <之前的消息>
    {to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
    </之前的消息>
    <当前消息>
    {context['episode_content']}
    </当前消息>
    
    <已提取的实体>
    {context['extracted_entities']}
    </已提取的实体>
    
    <实体类型>
    {context['entity_types']}
    </实体类型>
    
    根据上述对话、提取的实体以及提供的实体类型及其描述，对提取的实体进行分类。
    
    指南：
    1. 每个实体必须且只能有一个类型。
    2. 只能使用提供的实体类型来分类实体，不能使用额外的类型。
    3. 如果没有提供的实体类型能准确分类某个实体，则该实体类型应设为 None。
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]



# ======================================================================================= extract_attributes   抽取 node 属性
def _extract_attributes(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that extracts entity properties from the provided text.',
        ),
        Message(
            role='user',
            content=f"""

        <MESSAGES>
        {to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </MESSAGES>

        Given the above MESSAGES and the following ENTITY, update any of its attributes based on the information provided
        in MESSAGES. Use the provided attribute descriptions to better understand how each attribute should be determined.

        Guidelines:
        1. Do not hallucinate entity property values if they cannot be found in the current context.
        2. Only use the provided MESSAGES and ENTITY to set attribute values.
        
        <ENTITY>
        {context['node']}
        </ENTITY>
        """,
        ),
    ]

def __extract_attributes(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='你是一个有帮助的助手，用于从提供的文本中提取实体属性。',
        ),
        Message(
            role='user',
            content=f"""
        <消息>
        {to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </消息>

        根据上述消息和以下实体，基于消息中提供的信息更新其属性。
        请利用提供的属性描述更好地理解每个属性应如何确定。

        指南：
        1. 如果当前上下文中找不到属性值，请勿臆造实体属性值。
        2. 只能使用提供的消息和实体来设置属性值。
        
        <实体>
        {context['node']}
        </实体>
        """,
        ),
    ]

# 此 prompt   Qwen3-4B-Thinking-2507 可以正常理解
# 适配 qwen3 的 def extract_attributes 指令缺失

# # 此方法 gpt-4-mini 可以正常使用
def _____extract_attributes(context: dict[str, Any]) -> list[Message]:  
    return [  
        Message(  
            role='system',  
            content='你是一个有帮助的助手，用于从提供的文本中提取实体属性。',  
        ),  
        Message(  
            role='user',  
            content=f"""  
        <消息>  
        {to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}  
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}  
        </消息>  
  
        根据上述消息和以下实体，基于消息中提供的信息更新其属性。  
        请利用提供的属性描述更好地理解每个属性应如何确定。  
  
        指南：  
        1. 如果当前上下文中找不到属性值，请勿臆造实体属性值。  
        2. 只能使用提供的消息和实体来设置属性值。  
        3. 请返回实际的属性值，不要返回 JSON schema 定义。  
        4. 返回格式必须是扁平的 JSON 对象，直接包含属性字段。  
        5. 例如：{{"person_name": "具体姓名", "role": "具体角色"}}  
          
        <实体>  
        {context['node']}  
        </实体>  
        """,  
        ),  
    ]

def extract_attributes(context: dict[str, Any]) -> list[Message]:  
    return [  
        Message(  
            role='system',  
            content='你是专业的实体属性提取助手。严格按照JSON对象格式输出，不要返回数组。',  
        ),  
        Message(  
            role='user',  
            content=f"""  
<消息>  
{to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}  
{to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}  
</消息>  
  
<实体>  
{context['node']}  
</实体>  
  
基于上述消息和实体信息，更新实体属性。  
  
重要要求：  
1. 必须返回JSON对象格式，不要返回数组  
2. 只使用消息中明确提到的信息  
3. 不要编造不存在的属性值  
  
输出格式示例：  
{{  
  "属性名1": "属性值1",  
  "属性名2": "属性值2"  
}}  
  
只输出JSON对象：  
""",  
        ),  
    ]



# ========================================================================================= extract_summary 这个 prompt 专门用于为实体生成不超过250字的摘要。
def _extract_summary(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that extracts entity summaries from the provided text.',
        ),
        Message(
            role='user',
            content=f"""

        <MESSAGES>
        {to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </MESSAGES>

        Given the above MESSAGES and the following ENTITY, update the summary that combines relevant information about the entity
        from the messages and relevant information from the existing summary.
        
        Guidelines:
        1. Do not hallucinate entity summary information if they cannot be found in the current context.
        2. Only use the provided MESSAGES and ENTITY to set attribute values.
        3. The summary attribute represents a summary of the ENTITY, and should be updated with new information about the Entity from the MESSAGES. 
            Summaries must be no longer than 250 words.

        <ENTITY>
        {context['node']}
        </ENTITY>
        """,
        ),
    ]

def extract_summary(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='你是一个有帮助的助手，用于从提供的文本中提取实体摘要。',
        ),
        Message(
            role='user',
            content=f"""

        <消息>
        {to_prompt_json(context['previous_episodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </消息>


        根据上述消息和以下实体，更新该实体的摘要，摘要应结合消息中及现有摘要中有关该实体的相关信息。
        
        指南：
        1. 如果当前上下文中找不到实体摘要信息，请勿臆造。
        2. 只能使用提供的消息和实体来设置属性值。
        3. 摘要属性代表该实体的概要，应包含来自消息的新信息，且摘要不得超过250字。


        <实体>
        {context['node']}
        </实体>
        """,
        ),
    ]



versions: Versions = {
    'extract_message': extract_message,
    'extract_json': extract_json,
    'extract_text': extract_text,
    'reflexion': reflexion,
    'extract_summary': extract_summary,
    'classify_nodes': classify_nodes,
    'extract_attributes': extract_attributes,
}
