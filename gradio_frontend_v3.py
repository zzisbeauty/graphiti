import gradio as gr    
import requests    
import json    
from datetime import datetime    
    
API_BASE_URL = "http://192.168.1.6:5926"  
  
def add_memory_via_rest_api(name, episode_body, source, source_description, group_id):    
    """通过 REST API 添加记忆片段"""    
    try:    
        # 构建符合 REST API 格式的请求数据    
        messages_data = {    
            "messages": [{    
                "name": name,    
                "content": episode_body,    
                "role": "user",  # 固定使用 user 角色  
                "role_type": "user",  # 这里必须是 'user', 'assistant', 'system' 之一  
                "source_description": source_description    
            }],    
            "group_id": group_id or "default"    
        }    
            
        # 发送到 REST API 的 /messages 端点    
        response = requests.post(    
            f"{API_BASE_URL}/messages",    
            json=messages_data,    
            headers={"Content-Type": "application/json"},    
            timeout=30    
        )    
            
        if response.status_code == 202:  # REST API 返回 202 Accepted    
            return f"✅ 成功添加记忆片段: {name}"    
        else:    
            return f"❌ HTTP错误: {response.status_code} - {response.text}"    

    except Exception as e:    
        return f"❌ 错误: {str(e)}"  
  
# 创建 Gradio 界面
def create_add_memory_interface():    
    with gr.Blocks(title="Graphiti 记忆片段管理") as demo:    
        gr.Markdown("# 📝 添加记忆片段到知识图谱")    
        gr.Markdown(f"**REST API Server**: `{API_BASE_URL}`")  # 修改这里  

        # 其余代码保持不变...  
        with gr.Row():
            with gr.Column(scale=2):    
                name_input = gr.Textbox(    
                    label="记忆片段名称",    
                    placeholder="例如: 客户对话记录",    
                    info="为这个记忆片段起一个描述性的名称"    
                )    
                    
                source_type = gr.Radio(    
                    choices=["text", "message", "json"],    
                    value="text",    
                    label="内容类型",    
                    info="选择记忆片段的数据格式"    
                )    
                    
                episode_body = gr.Textbox(    
                    label="记忆片段内容",    
                    placeholder="输入要存储的内容...",    
                    lines=8,    
                    info="根据选择的类型输入相应格式的内容"    
                )    
                    
                with gr.Row():    
                    source_description = gr.Textbox(    
                        label="来源描述",    
                        placeholder="例如: 客服聊天记录",    
                        info="描述这个记忆片段的来源"    
                    )    
                        
                    group_id = gr.Textbox(    
                        label="分组ID (可选)",    
                        placeholder="例如: customer_service",    
                        info="用于组织相关的记忆片段"    
                    )    
                    
                submit_btn = gr.Button("🚀 添加记忆片段", variant="primary")    
                    
            with gr.Column(scale=1):    
                gr.Markdown("""    
                ### 📋 格式说明    
                    
                **Text 格式**:    
                ```    
                今天天气很好，适合外出。    
                ```    
                    
                **Message 格式**:    
                ```    
                user: 你好，请问营业时间？    
                assistant: 我们营业时间是9:00-18:00    
                ```    
                    
                **JSON 格式**:    
                ```json    
                {    
                  "customer": {    
                    "name": "张三",    
                    "phone": "13800138000"    
                  },    
                  "order": {    
                    "id": "ORD001",    
                    "amount": 299.99    
                  }    
                }    
                ```    
                """)    
            
        result_output = gr.Textbox(    
            label="处理结果",    
            lines=3,    
            interactive=False    
        )    
            
        submit_btn.click(    
            fn=add_memory_via_rest_api,    
            inputs=[name_input, episode_body, source_type, source_description, group_id],    
            outputs=result_output    
        )    
  
        gr.Examples(    
            examples=[    
                ["客户咨询记录", "user: 请问有什么优惠活动吗？\nassistant: 目前有新用户8折优惠", "message", "客服对话", "customer_service"],    
                ["产品信息", "我们的新产品XYZ具有高性能、低功耗的特点，适合企业级应用。", "text", "产品介绍", "products"],    
                ["订单数据", '{"order_id": "12345", "customer": "李四", "amount": 199.99, "status": "completed"}', "json", "订单系统", "orders"]    
            ],  
            inputs=[name_input, episode_body, source_type, source_description, group_id]    
        )  
  
    return demo    
  
if __name__ == "__main__":    
    demo = create_add_memory_interface()    
    demo.launch(server_name="0.0.0.0", server_port=7860)