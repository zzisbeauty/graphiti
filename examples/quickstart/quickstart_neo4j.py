"""
Copyright 2025, Zep Software, Inc.

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

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

#################################################
# CONFIGURATION
#################################################
# Set up logging and environment variables for
# connecting to Neo4j database
#################################################

# Configure logging
logging.basicConfig(level=INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)
logger = logging.getLogger(__name__)


load_dotenv()


# Neo4j connection parameters
# Make sure Neo4j Desktop is running with a local DBMS started
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'aa1230.aa2')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')


async def main():
    #################################################
    # INITIALIZATION

    # 连接到 Neo4j 数据库并设置 Graphiti 所需的索引和约束。
    #################################################
    # Connect to Neo4j and set up Graphiti indices
    # This is required before using other Graphiti
    # functionality
    #################################################

    # Initialize Graphiti with Neo4j connection
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        # 核心方法：它创建优化查询性能和确保数据完整性所需的数据库结构； 这是索引的意义; 1. 范围索引：用于基本的查询优化; 2. 全文索引：用于文本搜索功能
        await graphiti.build_indices_and_constraints()

        breaking = 'break'



        #################################################
        # ADDING EPISODES

        # Episodes 是 Graphiti 中信息的基本单位；Episodes 可以是文本或结构化 JSON 数据，系统会自动处理这些数据以提取实体和关系。
        """
        text: 纯文本内容（默认）
        json: 结构化数据
        message: 对话式内容
        # 当您添加一个 Episode 时，Graphiti 会自动执行以下处理步骤
        - 实体提取：从 Episode 内容中识别和提取实体节点
        - 关系提取：分析实体之间的关系并创建边
        - 节点解析：处理提取的节点并进行去重

        # 在 MCP 服务器中，add_memory 函数展示了如何添加 Episodes; 该函数会调用 client.add_episode 来处理实际的数据添加，包括实体类型配置和时间戳设置。
        """
        #################################################
        # Episodes are the primary units of information
        # in Graphiti. They can be text or structured JSON
        # and are automatically processed to extract entities
        # and relationships.
        #################################################

        # Example: Add Episodes
        # Episodes list containing both text and JSON episodes
        episodes = [
            {
                'content': '卡玛拉·哈里斯是加利福尼亚州的司法部长。她此前曾担任旧金山的地区检察官。',
                'type': EpisodeType.text,
                'description': '播客转录',
            },
            {
                'content': '作为司法部长，哈里斯的任期是从 2011 年 1 月 3 日到 2017 年 1 月 3 日',
                'type': EpisodeType.text,
                'description': '播客转录',
            },
            {
                'content': {
                    'name': '加文·纽瑟姆',
                    'position': '州长',
                    'state': '加利福尼亚州',
                    'previous_role': '副州长',
                    'previous_location': '旧金山',
                },
                'type': EpisodeType.json,
                'description': '播客元数据',
            },
            {
                'content': {
                    'name': '加文·纽瑟姆',
                    'position': '州长',
                    'term_start': '2019 年 1 月 7 日',
                    'term_end': '至今',
                },
                'type': EpisodeType.json,
                'description': '播客元数据',
            },
        ]

        # Add episodes to the graph
        for i, episode in enumerate(episodes):
            await graphiti.add_episode( # 客户端添加 episodes（基本单元，即数据）
                name=f'Freakonomics Radio {i}',
                episode_body=episode['content']
                if isinstance(episode['content'], str)
                else json.dumps(episode['content']),
                source=episode['type'],
                source_description=episode['description'],
                reference_time=datetime.now(timezone.utc),
            )
            print(f'Added episode: Freakonomics Radio {i} ({episode["type"].value})')

        #################################################
        # BASIC SEARCH

        # Graphiti 中最简单的检索关系（边）的方法是使用 search 方法，它执行混合搜索，结合语义相似性和 BM25 文本检索
        # 还有 混合搜索机制
        #################################################
        # The simplest way to retrieve relationships (edges)
        # from Graphiti is using the search method, which
        # performs a hybrid search combining semantic
        # similarity and BM25 text retrieval.
        #################################################

        # Perform a hybrid search combining semantic similarity and BM25 retrieval
        print("\n正在搜索: '谁是加利福尼亚州的司法部长？'")
        results = await graphiti.search('谁是加利福尼亚州的司法部长？')

        # Print search results
        print('\nSearch Results:')
        for result in results:
            print(f'UUID: {result.uuid}')
            print(f'Fact: {result.fact}')
            if hasattr(result, 'valid_at') and result.valid_at:
                print(f'Valid from: {result.valid_at}')
            if hasattr(result, 'invalid_at') and result.invalid_at:
                print(f'Valid until: {result.invalid_at}')
            print('---')


        #################################################
        # CENTER NODE SEARCH
        #################################################
        # For more contextually relevant results, you can
        # use a center node to rerank search results based
        # on their graph distance to a specific node
        #################################################

        # Use the top search result's UUID as the center node for reranking
        if results and len(results) > 0:
            # Get the source node UUID from the top result
            center_node_uuid = results[0].source_node_uuid

            print('\nReranking search results based on graph distance:')
            print(f'Using center node UUID: {center_node_uuid}')

            reranked_results = await graphiti.search(
                'Who was the California Attorney General?', center_node_uuid=center_node_uuid
            )

            # Print reranked search results
            print('\nReranked Search Results:')
            for result in reranked_results:
                print(f'UUID: {result.uuid}')
                print(f'Fact: {result.fact}')
                if hasattr(result, 'valid_at') and result.valid_at:
                    print(f'Valid from: {result.valid_at}')
                if hasattr(result, 'invalid_at') and result.invalid_at:
                    print(f'Valid until: {result.invalid_at}')
                print('---')
        else:
            print('No results found in the initial search to use as center node.')



        #################################################
        # NODE SEARCH USING SEARCH RECIPES
        #################################################
        # Graphiti provides predefined search recipes
        # optimized for different search scenarios.
        # Here we use NODE_HYBRID_SEARCH_RRF for retrieving
        # nodes directly instead of edges.
        #################################################

        # Example: Perform a node search using _search method with standard recipes
        print(
            '\nPerforming node search using _search method with standard recipe NODE_HYBRID_SEARCH_RRF:'
        )

        # Use a predefined search configuration recipe and modify its limit
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5  # Limit to 5 results

        # Execute the node search
        node_search_results = await graphiti._search(
            query='California Governor',
            config=node_search_config,
        )

        # Print node search results
        print('\nNode Search Results:')
        for node in node_search_results.nodes:
            print(f'Node UUID: {node.uuid}')
            print(f'Node Name: {node.name}')
            node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
            print(f'Content Summary: {node_summary}')
            print(f'Node Labels: {", ".join(node.labels)}')
            print(f'Created At: {node.created_at}')
            if hasattr(node, 'attributes') and node.attributes:
                print('Attributes:')
                for key, value in node.attributes.items():
                    print(f'  {key}: {value}')
            print('---')


    finally:
        #################################################
        # CLEANUP
        #################################################
        # Always close the connection to Neo4j when
        # finished to properly release resources
        #################################################

        # Close the connection
        await graphiti.close()
        print('\nConnection closed')


if __name__ == '__main__':
    asyncio.run(main())
