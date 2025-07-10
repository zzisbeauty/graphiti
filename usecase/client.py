import asyncio  
import json  
import os  
from datetime import datetime, timezone  
from graphiti_core import Graphiti  
from graphiti_core.nodes import EpisodeType  
from graphiti_core.search.search_helpers import search_results_to_context_string  
  
def split_text_by_chars(file_path, chunk_size=1000):  
    with open('./usecase/data/红楼梦.txt', 'r', encoding='utf-8') as f:  
        text = f.read()  
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]  
    return chunks  
  
# def save_results_to_json(results, filename):  
#     """将解析结果保存为JSON文件"""  
#     # 创建输出目录  
#     os.makedirs('output', exist_ok=True)  
      
#     # 序列化结果  
#     serializable_results = {  
#         'episode': results.episode.model_dump(mode='json') if results.episode else None,  
#         'nodes': [node.model_dump(mode='json') for node in results.nodes],  
#         'edges': [edge.model_dump(mode='json') for edge in results.edges],  
#         'timestamp': datetime.now(timezone.utc).isoformat(),  
#         'total_nodes': len(results.nodes),  
#         'total_edges': len(results.edges)  
#     }  
      
#     # 保存到文件  
#     filepath = f'output/{filename}'  
#     with open(filepath, 'w', encoding='utf-8') as f:  
#         json.dump(serializable_results, f, ensure_ascii=False, indent=2)  
      
#     print(f"结果已保存到: {filepath}")  
#     return filepath  
  

def save_results_to_json(results, filename):  
    """将解析结果保存为JSON文件"""  
    # 创建输出目录  
    os.makedirs('output', exist_ok=True)  
      
    # 检查输入类型并相应处理  
    if isinstance(results, dict):  
        # 如果是字典，直接序列化  
        serializable_results = results  
    else:  
        # 如果是 AddEpisodeResults 对象，按原来的方式处理  
        serializable_results = {  
            'episode': results.episode.model_dump(mode='json') if results.episode else None,  
            'nodes': [node.model_dump(mode='json') for node in results.nodes],  
            'edges': [edge.model_dump(mode='json') for edge in results.edges],  
            'timestamp': datetime.now(timezone.utc).isoformat(),  
            'total_nodes': len(results.nodes),  
            'total_edges': len(results.edges)  
        }  
      
    # 保存到文件  
    filepath = f'output/{filename}'  
    with open(filepath, 'w', encoding='utf-8') as f:  
        json.dump(serializable_results, f, ensure_ascii=False, indent=2)  
      
    print(f"结果已保存到: {filepath}")  
    return filepath


async def process_all_chunks(graphiti, chunks, group_id="hongloumeng"):  
    """处理所有文本块并收集结果"""  
    all_results = []  
      
    for i, chunk in enumerate(chunks):  
        print(f"处理第 {i+1}/{len(chunks)} 个文本块...")  
          
        try:  
            # 添加文本块到知识图谱  
            result = await graphiti.add_episode(  
                name=f"红楼梦_第{i+1}段",  
                episode_body=chunk,  
                source=EpisodeType.text,  
                source_description="红楼梦小说文本",  
                reference_time=datetime.now(timezone.utc),  
                group_id=group_id  
            )  
              
            all_results.append(result)  
              
            # 保存单个块的结果  
            save_results_to_json(result, f"hongloumeng_chunk_{i+1}.json")  
              
            print(f"第 {i+1} 块处理完成: {len(result.nodes)} 个节点, {len(result.edges)} 个关系")  
              
        except Exception as e:  
            print(f"处理第 {i+1} 块时出错: {e}")  
            continue  
      
    return all_results  
  
async def search_and_save_knowledge(graphiti, group_id="hongloumeng"):  
    """搜索知识图谱并保存搜索结果"""  
    search_queries = ["贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "贾府"]  
      
    all_search_results = {}  
      
    for query in search_queries:  
        print(f"搜索: {query}")  
          
        # 搜索节点  
        search_results = await graphiti.search_(  
            query=query,  
            group_ids=[group_id]  
        )  
          
        # 格式化搜索结果  
        formatted_results = {  
            'query': query,  
            'nodes': [  
                {  
                    'uuid': node.uuid,  
                    'name': node.name,  
                    'summary': node.summary,  
                    'labels': node.labels,  
                    'created_at': node.created_at.isoformat()  
                }  
                for node in search_results.nodes  
            ],  
            'edges': [  
                {  
                    'uuid': edge.uuid,  
                    'fact': edge.fact,  
                    'source_node_uuid': edge.source_node_uuid,  
                    'target_node_uuid': edge.target_node_uuid,  
                    'valid_at': edge.valid_at.isoformat() if edge.valid_at else None,  
                    'invalid_at': edge.invalid_at.isoformat() if edge.invalid_at else None  
                }  
                for edge in search_results.edges  
            ],  
            'episodes': [  
                {  
                    'uuid': episode.uuid,  
                    'name': episode.name,  
                    'content': episode.content[:200] + "..." if len(episode.content) > 200 else episode.content,  
                    'created_at': episode.created_at.isoformat()  
                }  
                for episode in search_results.episodes  
            ]  
        }  
          
        all_search_results[query] = formatted_results  
        print(f"找到 {len(search_results.nodes)} 个节点, {len(search_results.edges)} 个关系")  
      
    # 保存所有搜索结果  
    save_results_to_json({'search_results': all_search_results}, "hongloumeng_search_results.json")  
      
    return all_search_results  
  
async def export_full_graph(graphiti, group_id="hongloumeng"):  
    """导出完整的知识图谱"""  
    print("导出完整知识图谱...")  
      
    # 获取所有相关的episodes  
    episodes = await graphiti.retrieve_episodes(  
        reference_time=datetime.now(timezone.utc),  
        last_n=1000,  # 获取最近1000个episodes  
        group_ids=[group_id]  
    )  
      
    if episodes:  
        episode_uuids = [ep.uuid for ep in episodes]  
          
        # 获取所有相关的节点和边  
        graph_data = await graphiti.get_nodes_and_edges_by_episode(episode_uuids)  
          
        # 格式化完整图谱数据  
        full_graph = {  
            'metadata': {  
                'group_id': group_id,  
                'export_time': datetime.now(timezone.utc).isoformat(),  
                'total_episodes': len(episodes),  
                'total_nodes': len(graph_data.nodes),  
                'total_edges': len(graph_data.edges)  
            },  
            'episodes': [ep.model_dump(mode='json') for ep in episodes],  
            'nodes': [node.model_dump(mode='json') for node in graph_data.nodes],  
            'edges': [edge.model_dump(mode='json') for edge in graph_data.edges]  
        }  
          
        # 保存完整图谱  
        save_results_to_json(full_graph, "hongloumeng_full_graph.json")  
          
        print(f"完整图谱导出完成: {len(episodes)} 个episodes, {len(graph_data.nodes)} 个节点, {len(graph_data.edges)} 个关系")  
          
        return full_graph  
      
    return None  
  
async def main():  
    # 获取文本块  
    chunks = split_text_by_chars('')  
    print(f"文本已分割为 {len(chunks)} 个块")  
      
    # 初始化 Graphiti 客户端  
    graphiti = Graphiti(  
        uri="bolt://neo4j:7687",  
        user="neo4j",  
        password="aa1230.aa"  
    )  
      
    try:  
        # 构建索引和约束  
        await graphiti.build_indices_and_constraints()  
        print("数据库索引和约束构建完成")  
          
        # 处理所有文本块  
        all_results = await process_all_chunks(graphiti, chunks[:2])  
          
        # 合并所有结果  
        combined_results = {  
            'total_chunks_processed': len(all_results),  
            'total_nodes': sum(len(result.nodes) for result in all_results),  
            'total_edges': sum(len(result.edges) for result in all_results),  
            'processing_time': datetime.now(timezone.utc).isoformat(),  
            'chunks': [  
                {  
                    'chunk_index': i,  
                    'nodes_count': len(result.nodes),  
                    'edges_count': len(result.edges),  
                    'episode_uuid': result.episode.uuid if result.episode else None  
                }  
                for i, result in enumerate(all_results)  
            ]  
        }  
          
        # 保存处理摘要  
        save_results_to_json(combined_results, "hongloumeng_processing_summary.json")  
          
        # 搜索和保存知识  
        await search_and_save_knowledge(graphiti)  
          
        # 导出完整图谱  
        await export_full_graph(graphiti)  
          
        print("\n=== 处理完成 ===")  
        print(f"总共处理了 {len(all_results)} 个文本块")  
        print(f"总共提取了 {combined_results['total_nodes']} 个节点")  
        print(f"总共提取了 {combined_results['total_edges']} 个关系")  
        print("所有结果已保存到 output/ 目录")  
          
    except Exception as e:  
        print(f"处理过程中出现错误: {e}")  
        raise  
    finally:  
        # 关闭连接  
        await graphiti.close()  
        print("数据库连接已关闭")  
  
if __name__ == "__main__":  
    asyncio.run(main())
