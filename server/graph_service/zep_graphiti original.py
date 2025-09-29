import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from graphiti_core import Graphiti  # type: ignore
from graphiti_core.edges import EntityEdge  # type: ignore
from graphiti_core.errors import EdgeNotFoundError, GroupsEdgesNotFoundError, NodeNotFoundError
from graphiti_core.llm_client import LLMClient  # type: ignore
from graphiti_core.nodes import EntityNode, EpisodicNode  # type: ignore

from graph_service.config import ZepEnvDep
from graph_service.dto import FactResult


""" Graphiti REST API 服务的核心组件，它继承自 graphiti_core 的 Graphiti 类，为 REST API 提供了扩展的图数据库操作功能
ZepGraphiti 类本质上是对核心 Graphiti 类的 REST API 特定扩展，添加了 HTTP 错误处理、批量删除操作和 FastAPI 集成功能。它作为 REST API 服务层和 Graphiti 核心库之间的桥梁，提供了适合 Web API 使用的接口。

说明：
1. Graphiti 类是核心库的主要入口点，提供图数据库操作的基础功能，但它本身不包含任何 REST API 相关的代码。 graphiti.py 这个类专注于图数据库操作、LLM 集成和实体处理等核心功能。
2. REST API 服务使用了一个名为 ZepGraphiti 的包装类，它继承自核心的 Graphiti 类；
3. 实际的 REST API 端点定义在 FastAPI 路由文件中
    - server/graph_service/routers/retrieve.py
    - server/graph_service/routers/ingest.py
    - REST API 通过依赖注入使用 ZepGraphiti 实例： zep_graphiti.py:74-90 ； 这个依赖注入函数被路由中的端点使用，例如在搜索端点中： retrieve.py:17-27
4. 客户端发起 REST API 调用时，实际的调用流程是：
    - 客户端 → FastAPI 路由层 → ZepGraphiti → Graphiti 核心；
    - 也就是说，Graphiti 中定义的方法引入到 zep_graphiti 做封装；因此可以把 zep_graphiti 也视为一个服务层，即 Graphiti -> 封装 -> zep_graphiti ，由zep_graphiti作为一个完整的服务层存在
        - 且 zep_graphiti 也定义了其他一些服务：例如提供额外的数据库操作方法
        - 且同时还添加了 REST API 特定的功能，如 HTTP 错误处理，处理一些客户端与服务端请求之间的工作
    - 然后在 FAST API 层，依赖注入把 zep_graphiti 实例引用进来，就完成了客户端 --> 请求 FASTAPI --> 完成了对 zep_graphiti 服务层中封装服务的调用。
"""



logger = logging.getLogger(__name__)


class ZepGraphiti(Graphiti):
    def __init__(self, uri: str, user: str, password: str, llm_client: LLMClient | None = None):
        super().__init__(uri, user, password, llm_client)


    async def save_entity_node(self, name: str, uuid: str, group_id: str, summary: str = ''):
        new_node = EntityNode(
            name=name,
            uuid=uuid,
            group_id=group_id,
            summary=summary,
        )
        await new_node.generate_name_embedding(self.embedder)
        await new_node.save(self.driver)
        return new_node

    async def get_entity_edge(self, uuid: str):
        try:
            edge = await EntityEdge.get_by_uuid(self.driver, uuid)
            return edge
        except EdgeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e

    async def delete_group(self, group_id: str):
        try:
            edges = await EntityEdge.get_by_group_ids(self.driver, [group_id])
        except GroupsEdgesNotFoundError:
            logger.warning(f'No edges found for group {group_id}')
            edges = []
        nodes = await EntityNode.get_by_group_ids(self.driver, [group_id])
        episodes = await EpisodicNode.get_by_group_ids(self.driver, [group_id])
        for edge in edges:
            await edge.delete(self.driver)
        for node in nodes:
            await node.delete(self.driver)
        for episode in episodes:
            await episode.delete(self.driver)

    async def delete_entity_edge(self, uuid: str):
        try:
            edge = await EntityEdge.get_by_uuid(self.driver, uuid)
            await edge.delete(self.driver)
        except EdgeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e

    async def delete_episodic_node(self, uuid: str):
        try:
            episode = await EpisodicNode.get_by_uuid(self.driver, uuid)
            await episode.delete(self.driver)
        except NodeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e


async def get_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    if settings.openai_base_url is not None:
        client.llm_client.config.base_url = settings.openai_base_url
    if settings.openai_api_key is not None:
        client.llm_client.config.api_key = settings.openai_api_key
    if settings.model_name is not None:
        client.llm_client.model = settings.model_name
    try:
        yield client
    finally:
        await client.close()


async def initialize_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await client.build_indices_and_constraints()


def get_fact_result_from_edge(edge: EntityEdge):
    return FactResult(
        uuid=edge.uuid,
        name=edge.name,
        fact=edge.fact,
        valid_at=edge.valid_at,
        invalid_at=edge.invalid_at,
        created_at=edge.created_at,
        expired_at=edge.expired_at,
    )


ZepGraphitiDep = Annotated[ZepGraphiti, Depends(get_graphiti)]
