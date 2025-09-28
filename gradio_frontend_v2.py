""" 调用后端MCP SERVER  可以自定义 schema
"""

import gradio as gr  
import json  
import asyncio  
import aiohttp  
from typing import Dict, Any, List, Optional  
import logging  
  
# 配置日志  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  
  
# MCP 服务器地址  
MCP_SERVER_URL = "http://192.168.1.6:5925"



# 预定义的实体类型示例（基于 MCP 服务器的 ENTITY_TYPES）  
DEFAULT_ENTITY_TYPES = {  
    "Person": {  
        "description": "人物实体",  
        "fields": {  
            "name": "姓名",  
            "age": "年龄",   
            "occupation": "职业"  
        }  
    },  
    "Organization": {  
        "description": "组织机构",  
        "fields": {  
            "name": "名称",  
            "type": "类型",  
            "industry": "行业"  
        }  
    },   
    "Location": {  
        "description": "地理位置",  
        "fields": {  
            "name": "地名",  
            "type": "位置类型",  
            "coordinates": "坐标"  
        }  
    }  
}  
  
DEFAULT_EDGE_TYPES = {  
    "WORKS_AT": "工作于",  
    "LOCATED_IN": "位于",  
    "FOUNDED": "创立",  
    "MANAGES": "管理"  
}


class MCPClient:  
    """MCP 客户端，用于与 Graphiti MCP 服务器通信"""  
      
    def __init__(self, server_url: str):  
        self.server_url = server_url  
        self.session = None  
      
    async def _get_session(self):  
        if self.session is None:  
            self.session = aiohttp.ClientSession()  
        return self.session  
      
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:  
        """调用 MCP 工具"""  
        session = await self._get_session()  
          
        # MCP 协议格式  
        payload = {  
            "jsonrpc": "2.0",  
            "id": 1,  
            "method": "tools/call",  
            "params": {  
                "name": tool_name,  
                "arguments": arguments  
            }  
        }  
          
        try:  
            async with session.post(  
                f"{self.server_url}/sse",  
                json=payload,  
                headers={"Content-Type": "application/json"}  
            ) as response:  
                if response.status == 200:  
                    result = await response.json()  
                    return result  
                else:  
                    error_text = await response.text()  
                    return {"error": f"HTTP {response.status}: {error_text}"}  
        except Exception as e:  
            return {"error": f"连接错误: {str(e)}"}  
      
    async def close(self):  
        if self.session:  
            await self.session.close()  
  
# 全局 MCP 客户端实例  
mcp_client = MCPClient(MCP_SERVER_URL)


async def add_memory_to_graph(name: str, episode_body: str, group_id: str,   
                             source_description: str, source_type: str,  
                             entity_types_json: str = "", edge_types_json: str = "",  
                             use_custom_schema: bool = False) -> str:  
    """调用 MCP 服务器的 add_memory 工具"""  
    try:  
        # 构建参数  
        arguments = {  
            "name": name,  
            "episode_body": episode_body,  
            "source_description": source_description,  
            "source": source_type  
        }  
          
        if group_id.strip():  
            arguments["group_id"] = group_id.strip()  
          
        # 如果启用自定义 schema，解析并添加到参数中  
        if use_custom_schema:  
            try:  
                if entity_types_json.strip():  
                    entity_types = json.loads(entity_types_json)  
                    arguments["entity_types"] = entity_types  
                  
                if edge_types_json.strip():  
                    edge_types = json.loads(edge_types_json)  
                    arguments["edge_types"] = edge_types  
            except json.JSONDecodeError as e:  
                return f"Schema JSON 格式错误: {str(e)}"  
          
        # 调用 MCP 工具  
        result = await mcp_client.call_tool("add_memory", arguments)  
          
        if "error" in result:  
            return f"错误: {result['error']}"  
        elif "result" in result:  
            return f"成功: {result['result'].get('message', '记忆已添加')}"  
        else:  
            return f"成功添加记忆: {name}"  
              
    except Exception as e:  
        logger.error(f"添加记忆时出错: {str(e)}")  
        return f"错误: {str(e)}"
    

async def search_nodes(query: str, group_ids: str, max_nodes: int, entity_filter: str = "") -> str:  
    """搜索节点"""  
    try:  
        arguments = {  
            "query": query,  
            "max_nodes": max_nodes  
        }  
          
        if group_ids.strip():  
            # 支持多个 group_id，用逗号分隔  
            group_list = [g.strip() for g in group_ids.split(",") if g.strip()]  
            arguments["group_ids"] = group_list  
          
        if entity_filter.strip():  
            arguments["entity"] = entity_filter.strip()  
          
        result = await mcp_client.call_tool("search_memory_nodes", arguments)  
          
        if "error" in result:  
            return f"搜索错误: {result['error']}"  
        elif "result" in result:  
            nodes = result["result"].get("nodes", [])  
            if not nodes:  
                return "未找到相关节点"  
              
            # 格式化搜索结果  
            formatted_results = []  
            for i, node in enumerate(nodes, 1):  
                formatted_results.append(  
                    f"{i}. {node.get('name', 'Unknown')}\n"  
                    f"   类型: {', '.join(node.get('labels', []))}\n"  
                    f"   摘要: {node.get('summary', 'N/A')}\n"  
                    f"   分组: {node.get('group_id', 'N/A')}\n"  
                    f"   UUID: {node.get('uuid', 'N/A')}\n"  
                )  
              
            return f"找到 {len(nodes)} 个节点:\n\n" + "\n".join(formatted_results)  
        else:  
            return "搜索完成，但未返回预期结果"  
              
    except Exception as e:  
        logger.error(f"搜索节点时出错: {str(e)}")  
        return f"搜索错误: {str(e)}"  
  
async def search_facts(query: str, group_ids: str, max_facts: int) -> str:  
    """搜索事实关系"""  
    try:  
        arguments = {  
            "query": query,  
            "max_facts": max_facts  
        }  
          
        if group_ids.strip():  
            group_list = [g.strip() for g in group_ids.split(",") if g.strip()]  
            arguments["group_ids"] = group_list  
          
        result = await mcp_client.call_tool("search_memory_facts", arguments)  
          
        if "error" in result:  
            return f"搜索错误: {result['error']}"  
        elif "result" in result:  
            facts = result["result"].get("facts", [])  
            if not facts:  
                return "未找到相关事实"  
              
            # 格式化事实结果  
            formatted_results = []  
            for i, fact in enumerate(facts, 1):  
                formatted_results.append(  
                    f"{i}. {fact.get('fact', 'Unknown fact')}\n"  
                    f"   关系类型: {fact.get('relation_type', 'N/A')}\n"  
                    f"   有效时间: {fact.get('valid_at', 'N/A')}\n"  
                    f"   分组: {fact.get('group_id', 'N/A')}\n"  
                )
            return f"找到 {len(facts)} 个事实:\n\n" + "\n".join(formatted_results)  
        else:
            return "搜索完成，但未返回预期结果"
              
    except Exception as e:  
        logger.error(f"搜索事实时出错: {str(e)}")  
        return f"搜索错误: {str(e)}"
    

def create_gradio_interface():  
    """创建 Gradio 界面"""  
      
    with gr.Blocks(title="Graphiti 知识图谱管理", theme="soft") as demo:
        
        gr.Markdown("# 🧠 Graphiti 知识图谱前端")  
        gr.Markdown("连接到 MCP 服务器进行知识图谱管理")  
          
        with gr.Tab("📝 添加记忆"):  
            with gr.Row():  
                with gr.Column(scale=2):  
                    name_input = gr.Textbox(  
                        label="记忆名称",   
                        placeholder="例如：红楼梦章节1",  
                        info="为这条记忆起一个描述性的名称"  
                    )  
                    episode_body = gr.Textbox(  
                        label="内容",   
                        lines=8,   
                        placeholder="输入要添加到知识图谱的内容...",  
                        info="支持文本、JSON 或消息格式"  
                    )  
                      
                    with gr.Row():  
                        group_id_input = gr.Textbox(  
                            label="分组ID",   
                            placeholder="例如：hlm_group, tech_docs",  
                            info="用于组织相关的记忆，留空使用默认分组"  
                        )  
                        source_type = gr.Dropdown(  
                            choices=["text", "json", "message"],  
                            value="text",  
                            label="内容类型",  
                            info="选择内容的格式类型"  
                        )  
                      
                    source_desc = gr.Textbox(  
                        label="来源描述",   
                        placeholder="例如：红楼梦原文，技术文档",  
                        info="描述这条记忆的来源背景"  
                    )  
                  
                with gr.Column(scale=1):  
                    add_result = gr.Textbox(  
                        label="添加结果",   
                        lines=6,  
                        interactive=False  
                    )  
                    add_btn = gr.Button("🚀 添加到知识图谱", variant="primary", size="lg")  
              
            # 自定义 Schema 部分  
            with gr.Accordion("🔧 自定义 Schema（高级选项）", open=False):  
                use_custom_schema = gr.Checkbox(  
                    label="启用自定义 Schema",  
                    value=False,  
                    info="启用后可以自定义实体类型和关系类型"  
                )  
                  
                with gr.Row():  
                    with gr.Column():  
                        gr.Markdown("### 实体类型定义")  
                        entity_types_input = gr.Code(  
                            label="实体类型 (JSON)",  
                            language="json",  
                            value=json.dumps(DEFAULT_ENTITY_TYPES, indent=2, ensure_ascii=False),  
                            lines=10,  
                        )  
                      
                    with gr.Column():  
                        gr.Markdown("### 关系类型定义")  
                        edge_types_input = gr.Code(  
                            label="关系类型 (JSON)",  
                            language="json",   
                            value=json.dumps(DEFAULT_EDGE_TYPES, indent=2, ensure_ascii=False),  
                            lines=10,  
                        )

        with gr.Tab("🔍 搜索节点"):  
            with gr.Row():  
                with gr.Column():  
                    search_query = gr.Textbox(  
                        label="搜索查询",   
                        placeholder="输入搜索关键词...",  
                        info="搜索相关的实体节点"  
                    )  
                    search_group_ids = gr.Textbox(  
                        label="搜索分组",  
                        placeholder="留空搜索所有分组，或输入特定分组ID（多个用逗号分隔）",  
                        info="限制搜索范围到特定分组"  
                    )  
                      
                    with gr.Row():  
                        max_nodes_input = gr.Slider(  
                            minimum=1,  
                            maximum=50,  
                            value=10,  
                            label="最大结果数",  
                            info="限制返回的节点数量"  
                        )  
                        entity_filter = gr.Dropdown(  
                            choices=["", "Person", "Organization", "Location", "Preference", "Procedure"],  
                            value="",  
                            label="实体类型过滤",  
                            info="按实体类型过滤结果"  
                        )  
  
                with gr.Column():  
                    search_result = gr.Textbox(  
                        label="搜索结果",   
                        lines=15,  
                        interactive=False  
                    )  
                    search_btn = gr.Button("🔍 搜索节点", variant="primary")  
  
        with gr.Tab("🔗 搜索事实"):  
            with gr.Row():  
                with gr.Column():  
                    fact_query = gr.Textbox(  
                        label="事实搜索",   
                        placeholder="搜索关系和事实...",  
                        info="搜索实体间的关系事实"  
                    )  
                    fact_group_ids = gr.Textbox(  
                        label="搜索分组",  
                        placeholder="留空搜索所有分组，或输入特定分组ID（多个用逗号分隔）"  
                    )  
                    max_facts = gr.Slider(  
                        1, 50, 10,   
                        label="最大结果数",  
                        info="限制返回的事实数量"  
                    )  
                        
                with gr.Column():  
                    fact_result = gr.Textbox(  
                        label="事实搜索结果",   
                        lines=15,  
                        interactive=False  
                    )  
                    fact_search_btn = gr.Button("🔗 搜索事实", variant="primary")

                # 绑定事件处理函数  
        def handle_add_memory(name, body, group_id, source_desc, source_type,   
                             entity_types_json, edge_types_json, use_custom_schema):  
            # 由于 Gradio 不直接支持 async，需要使用 asyncio  
            loop = asyncio.new_event_loop()  
            asyncio.set_event_loop(loop)  
            try:  
                result = loop.run_until_complete(  
                    add_memory_to_graph(name, body, group_id, source_desc, source_type,  
                                      entity_types_json, edge_types_json, use_custom_schema)  
                )  
                return result  
            finally:  
                loop.close()  
  
        def handle_search_nodes(query, group_ids, max_nodes, entity_filter):  
            loop = asyncio.new_event_loop()  
            asyncio.set_event_loop(loop)  
            try:  
                result = loop.run_until_complete(  
                    search_nodes(query, group_ids, max_nodes, entity_filter)  
                )  
                return result  
            finally:  
                loop.close()  
  
        def handle_search_facts(query, group_ids, max_facts):  
            loop = asyncio.new_event_loop()  
            asyncio.set_event_loop(loop)  
            try:  
                result = loop.run_until_complete(  
                    search_facts(query, group_ids, max_facts)  
                )  
                return result  
            finally:  
                loop.close()  
  
        # 绑定按钮事件  
        add_btn.click(  
            handle_add_memory,  
            inputs=[name_input, episode_body, group_id_input, source_desc, source_type,  
                   entity_types_input, edge_types_input, use_custom_schema],  
            outputs=add_result  
        )  
  
        search_btn.click(  
            handle_search_nodes,  
            inputs=[search_query, search_group_ids, max_nodes_input, entity_filter],  
            outputs=search_result  
        )  
  
        fact_search_btn.click(  
            handle_search_facts,  
            inputs=[fact_query, fact_group_ids, max_facts],  
            outputs=fact_result  
        )  
  
    return demo


if __name__ == "__main__":  
    demo = create_gradio_interface()  
    demo.launch(  
        server_name="0.0.0.0",  
        server_port=7860,  
        share=False  
    )