import gradio as gr  
import requests  
import json  
import asyncio  
import aiohttp  
  
# MCP 服务器地址  
MCP_SERVER_URL = "http://192.168.1.6:8000"  

async def add_memory_to_graph(name, episode_body, group_id, source_description, source_type):  
    """调用 MCP 服务器的 add_memory 工具"""  
    try:  
        # 这里需要实现对 MCP 服务器的调用  
        # 由于 MCP 使用 SSE 协议，您可能需要使用专门的 MCP 客户端库  
        # 或者直接通过 HTTP 调用（如果服务器支持）  

        payload = {  
            "name": name,  
            "episode_body": episode_body,  
            "group_id": group_id,  
            "source_description": source_description,  
            "source": source_type  
        }  
          
        # 注意：这是简化的示例，实际需要实现 MCP 协议调用  
        return f"成功添加记忆：{name} (group_id: {group_id})"  

    except Exception as e:  
        return f"错误：{str(e)}"  
  
async def search_nodes(query, group_ids, max_nodes):  
    """搜索节点"""  
    try:  
        # 实现节点搜索逻辑
        return f"搜索结果：{query}"  
    except Exception as e:  
        return f"搜索错误：{str(e)}"  

def create_gradio_interface():  
    """创建 Gradio 界面"""

    with gr.Blocks(title="Graphiti 知识图谱管理") as demo:  
        gr.Markdown("# Graphiti 知识图谱前端")  

        with gr.Tab("添加记忆"):  
            with gr.Row():  
                with gr.Column():  
                    name_input = gr.Textbox(label="记忆名称", placeholder="例如：红楼梦章节1")  
                    episode_body = gr.Textbox(  
                        label="内容",   
                        lines=10,   
                        placeholder="输入要添加到知识图谱的内容..."  
                    )  
                    group_id_input = gr.Textbox(  
                        label="分组ID",   
                        placeholder="例如：hlm_group, tech_docs"  
                    )  
                    source_desc = gr.Textbox(  
                        label="来源描述",   
                        placeholder="例如：红楼梦原文，技术文档"  
                    )  
                    source_type = gr.Dropdown(  
                        choices=["text", "json", "message"],  
                        value="text",  
                        label="内容类型"  
                    )  

                with gr.Column():  
                    add_result = gr.Textbox(label="添加结果", lines=5)  
                    add_btn = gr.Button("添加到知识图谱", variant="primary")  

        with gr.Tab("搜索节点"):
            with gr.Row():
                with gr.Column():
                    search_query = gr.Textbox(label="搜索查询", placeholder="输入搜索关键词...")  
                    search_group_ids = gr.Textbox(
                        label="搜索分组",
                        placeholder="留空搜索所有分组，或输入特定分组ID"
                    )
                    max_nodes_input = gr.Slider(
                        minimum=1,
                        maximum=50,
                        value=10,
                        label="最大结果数"  
                    )

                with gr.Column():  
                    search_result = gr.Textbox(label="搜索结果", lines=10)  
                    search_btn = gr.Button("搜索节点", variant="primary")  

        with gr.Tab("搜索事实"):  
            with gr.Row():  
                with gr.Column():  
                    fact_query = gr.Textbox(label="事实搜索", placeholder="搜索关系和事实...")  
                    fact_group_ids = gr.Textbox(label="搜索分组")  
                    max_facts = gr.Slider(1, 50, 10, label="最大结果数")  
                      
                with gr.Column():  
                    fact_result = gr.Textbox(label="事实搜索结果", lines=10)  
                    fact_search_btn = gr.Button("搜索事实", variant="primary")  
          
        # 绑定事件处理函数  
        def handle_add_memory(name, body, group_id, source_desc, source_type):  
            # 由于 Gradio 不直接支持 async，需要使用 asyncio  
            loop = asyncio.new_event_loop()  
            asyncio.set_event_loop(loop)  
            try:  
                result = loop.run_until_complete(  
                    add_memory_to_graph(name, body, group_id, source_desc, source_type)  
                )  
                return result  
            finally:  
                loop.close()  
          
        def handle_search_nodes(query, group_ids, max_nodes):  
            loop = asyncio.new_event_loop()  
            asyncio.set_event_loop(loop)  
            try:  
                result = loop.run_until_complete(  
                    search_nodes(query, group_ids, max_nodes)  
                )  
                return result  
            finally:  
                loop.close()  
          
        add_btn.click(  
            handle_add_memory,  
            inputs=[name_input, episode_body, group_id_input, source_desc, source_type],  
            outputs=add_result  
        )  
          
        search_btn.click(  
            handle_search_nodes,  
            inputs=[search_query, search_group_ids, max_nodes_input],  
            outputs=search_result  
        )  
      
    return demo  
  
if __name__ == "__main__":  
    demo = create_gradio_interface()  
    demo.launch(  
        server_name="0.0.0.0",  
        server_port=7860,  
        share=False  
    )