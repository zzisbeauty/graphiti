"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Protocol, TypedDict

from pydantic import BaseModel, Field

from .models import Message, PromptFunction, PromptVersion
from .prompt_helpers import to_prompt_json
from typing import List, Optional

# class EdgeDuplicate(BaseModel):
#     duplicate_facts: list[int] = Field(..., description='List of ids of any duplicate facts. If no duplicate facts are found, default to empty list.',)
#     contradicted_facts: list[int] = Field(...,description='List of ids of facts that should be invalidated. If no facts should be invalidated, the list should be empty.',)
#     fact_type: str = Field(..., description='One of the provided fact types or DEFAULT')

class EdgeDuplicate(BaseModel):  
    duplicate_facts: Optional[list[int]] = Field(None, description='List of ids of any duplicate facts. If no duplicate facts are found, default to empty list.')  
    contradicted_facts: Optional[list[int]] = Field(None, description='List of ids of facts that should be invalidated. If no facts should be invalidated, the list should be empty.')  
    fact_type: Optional[str] = Field(None, description='One of the provided fact types or DEFAULT')


class UniqueFact(BaseModel):
    uuid: str = Field(..., description='unique identifier of the fact')
    fact: str = Field(..., description='fact of a unique edge')


class UniqueFacts(BaseModel):
    unique_facts: list[UniqueFact]


class Prompt(Protocol):
    edge: PromptVersion
    edge_list: PromptVersion
    resolve_edge: PromptVersion


class Versions(TypedDict):
    edge: PromptFunction
    edge_list: PromptFunction
    resolve_edge: PromptFunction


def edge(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that de-duplicates edges from edge lists.',
        ),
        Message(
            role='user',
            content=f"""
        Given the following context, determine whether the New Edge represents any of the edges in the list of Existing Edges.

        <EXISTING EDGES>
        {to_prompt_json(context['related_edges'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
        </EXISTING EDGES>

        <NEW EDGE>
        {to_prompt_json(context['extracted_edges'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
        </NEW EDGE>
        
        Task:
        If the New Edges represents the same factual information as any edge in Existing Edges, return the id of the duplicate fact
            as part of the list of duplicate_facts.
        If the NEW EDGE is not a duplicate of any of the EXISTING EDGES, return an empty list.

        Guidelines:
        1. The facts do not need to be completely identical to be duplicates, they just need to express the same information.
        """,
        ),
    ]


def edge_list(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that de-duplicates edges from edge lists.',
        ),
        Message(
            role='user',
            content=f"""
        Given the following context, find all of the duplicates in a list of facts:

        Facts:
        {to_prompt_json(context['edges'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}

        Task:
        If any facts in Facts is a duplicate of another fact, return a new fact with one of their uuid's.

        Guidelines:
        1. identical or near identical facts are duplicates
        2. Facts are also duplicates if they are represented by similar sentences
        3. Facts will often discuss the same or similar relation between identical entities
        4. The final list should have only unique facts. If 3 facts are all duplicates of each other, only one of their
            facts should be in the response
        """,
        ),
    ]


# 边关系解析 - 原始的
def _resolve_edge(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that de-duplicates facts from fact lists and determines which existing '
            'facts are contradicted by the new fact.',
        ),
        Message(
            role='user',
            content=f"""
        <NEW FACT>
        {context['new_edge']}
        </NEW FACT>
        
        <EXISTING FACTS>
        {context['existing_edges']}
        </EXISTING FACTS>
        <FACT INVALIDATION CANDIDATES>
        {context['edge_invalidation_candidates']}
        </FACT INVALIDATION CANDIDATES>
        
        <FACT TYPES>
        {context['edge_types']}
        </FACT TYPES>
        

        Task:
        If the NEW FACT represents identical factual information of one or more in EXISTING FACTS, return the idx of the duplicate facts.
        Facts with similar information that contain key differences should not be marked as duplicates.
        If the NEW FACT is not a duplicate of any of the EXISTING FACTS, return an empty list.
        
        Given the predefined FACT TYPES, determine if the NEW FACT should be classified as one of these types.
        Return the fact type as fact_type or DEFAULT if NEW FACT is not one of the FACT TYPES.
        
        Based on the provided FACT INVALIDATION CANDIDATES and NEW FACT, determine which existing facts the new fact contradicts.
        Return a list containing all idx's of the facts that are contradicted by the NEW FACT.
        If there are no contradicted facts, return an empty list.

        Guidelines:
        1. Some facts may be very similar but will have key differences, particularly around numeric values in the facts.
            Do not mark these facts as duplicates.
        """,
        ),
    ]


# 简化后的英文版本
def __resolve_edge(context: dict[str, Any]) -> list[Message]:
    # 预定义JSON示例，避免在f-string中处理复杂的花括号转义
    json_example1 = '{"duplicate_facts": [2, 5], "fact_type": "BIRTH_DATE", "contradicted_facts": [7]}'
    json_example2 = '{"duplicate_facts": [], "fact_type": "DEFAULT", "contradicted_facts": []}'
    
    return [
        Message(
            role="system",
            content="You are an assistant that removes duplicate facts and checks if a new fact contradicts existing ones. Your response must be a single JSON object (no explanations, no extra text).",
        ),
        Message(
            role="user",
            content=f"""<NEW FACT>
{context['new_edge']}
</NEW FACT>

<EXISTING FACTS>
{context['existing_edges']}
</EXISTING FACTS>

<FACT INVALIDATION CANDIDATES>
{context['edge_invalidation_candidates']}
</FACT INVALIDATION CANDIDATES>

<FACT TYPES>
{context['edge_types']}
</FACT TYPES>

Strict Task:
1. If NEW FACT is identical to any EXISTING FACTS, return duplicate_facts as a list of their idx values.
   - If no duplicates, return an empty list [] (never return None or omit the field).
2. Determine the fact_type of NEW FACT.
   - If it matches one of the FACT TYPES, return that type as a string.
   - Otherwise return "DEFAULT".
3. Based on FACT INVALIDATION CANDIDATES and NEW FACT, return contradicted_facts as a list of idx values.
   - If none, return [].

Output Format (must follow strictly):
- Return exactly one JSON object, no extra text.
- JSON must include ALL THREE fields:
  - "duplicate_facts": list of integers (idx values). Must be [] if none.
  - "fact_type": string (one of FACT TYPES or "DEFAULT").
  - "contradicted_facts": list of integers (idx values). Must be [] if none.
- Never return null, None, or omit fields.
- Must be valid RFC8259 JSON (no comments, no trailing commas).

Valid JSON examples:
{json_example1}
{json_example2}

Final reminder:
LLM must output exactly one JSON object with all required fields, using [] for empty lists, never None/null, and no extra text.
"""),
    ]


def resolve_edge(context: dict[str, Any]) -> list[Message]:
    # 预定义JSON示例，避免花括号转义问题
    json_example1 = '{"duplicate_facts": [2, 5], "fact_type": "BIRTH_DATE", "contradicted_facts": [7]}'
    json_example2 = '{"duplicate_facts": [], "fact_type": "DEFAULT", "contradicted_facts": []}'
    
    return [
        Message(
            role="system",
            content="你是一个助手，负责去重事实并检查新事实是否与已有事实矛盾。你的最终回答必须严格是一个 JSON 对象（仅有该对象，不允许额外文本或解释）。",
        ),
        Message(
            role="user",
            content=f"""<NEW FACT>
{context['new_edge']}
</NEW FACT>

<EXISTING FACTS>
{context['existing_edges']}
</EXISTING FACTS>

<FACT INVALIDATION CANDIDATES>
{context['edge_invalidation_candidates']}
</FACT INVALIDATION CANDIDATES>

<FACT TYPES>
{context['edge_types']}
</FACT TYPES>

任务（严格）：
1. 如果 NEW FACT 与 EXISTING FACTS 完全相同，返回 duplicate_facts（数组），内容为重复事实的 idx 列表；如果没有重复，返回空数组 []（绝对不能返回 None 或省略字段）。
2. 判断 NEW FACT 的 fact_type。若与提供的 FACT TYPES 完全匹配，返回该字符串；否则返回 "DEFAULT"。
3. 根据 FACT INVALIDATION CANDIDATES 和 NEW FACT，返回 contradicted_facts（数组），包含所有被新事实反驳的已有事实 idx；如果没有，返回 []。

输出格式（必须严格遵守）：
- 仅返回一个 JSON 对象，且没有任何附加文本。
- JSON 对象必须包含以下三个字段（不能省略）：
  - "duplicate_facts": 整数数组（EXISTING FACTS 的 idx 值），若无则 []。
  - "fact_type": 字符串（FACT TYPES 的值或 "DEFAULT"）。
  - "contradicted_facts": 整数数组（EXISTING FACTS 的 idx 值），若无则 []。
- 不允许返回 null / None / "null" 或省略字段。空值必须用空数组 [] 表示。
- 必须返回合法的 RFC8259 JSON（无注释、无尾逗号）。

合法 JSON 示例：
{json_example1}
{json_example2}

再次提醒：
LLM 的最终输出必须严格为单个 JSON 对象，包含所有字段，空数组必须使用 []，不可返回 None/null 或额外文本。
"""),
    ]


# 另一种更安全的实现方式，使用模板字符串
def resolve_edge_template_version(context: dict[str, Any]) -> list[Message]:
    """使用字符串模板的版本，完全避免f-string花括号问题"""
    
    template = """<NEW FACT>
{new_edge}
</NEW FACT>

<EXISTING FACTS>
{existing_edges}
</EXISTING FACTS>

<FACT INVALIDATION CANDIDATES>
{edge_invalidation_candidates}
</FACT INVALIDATION CANDIDATES>

<FACT TYPES>
{edge_types}
</FACT TYPES>

任务（严格）：
1. 如果 NEW FACT 与 EXISTING FACTS 完全相同，返回 duplicate_facts（数组），内容为重复事实的 idx 列表；如果没有重复，返回空数组 []（绝对不能返回 None 或省略字段）。
2. 判断 NEW FACT 的 fact_type。若与提供的 FACT TYPES 完全匹配，返回该字符串；否则返回 "DEFAULT"。
3. 根据 FACT INVALIDATION CANDIDATES 和 NEW FACT，返回 contradicted_facts（数组），包含所有被新事实反驳的已有事实 idx；如果没有，返回 []。

输出格式（必须严格遵守）：
- 仅返回一个 JSON 对象，且没有任何附加文本。
- JSON 对象必须包含以下三个字段（不能省略）：
  - "duplicate_facts": 整数数组（EXISTING FACTS 的 idx 值），若无则 []。
  - "fact_type": 字符串（FACT TYPES 的值或 "DEFAULT"）。
  - "contradicted_facts": 整数数组（EXISTING FACTS 的 idx 值），若无则 []。
- 不允许返回 null / None / "null" 或省略字段。空值必须用空数组 [] 表示。
- 必须返回合法的 RFC8259 JSON（无注释、无尾逗号）。

合法 JSON 示例：
{"duplicate_facts": [2, 5], "fact_type": "BIRTH_DATE", "contradicted_facts": [7]}
{"duplicate_facts": [], "fact_type": "DEFAULT", "contradicted_facts": []}

再次提醒：
LLM 的最终输出必须严格为单个 JSON 对象，包含所有字段，空数组必须使用 []，不可返回 None/null 或额外文本。
"""

    return [
        Message(
            role="system",
            content="你是一个助手，负责去重事实并检查新事实是否与已有事实矛盾。你的最终回答必须严格是一个 JSON 对象（仅有该对象，不允许额外文本或解释）。",
        ),
        Message(
            role="user",
            content=template.format(**context)
        ),
    ]



versions: Versions = {'edge': edge, 'edge_list': edge_list, 'resolve_edge': resolve_edge}
