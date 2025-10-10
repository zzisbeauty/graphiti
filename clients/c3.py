#!/usr/bin/env python3  
"""  
客户端使用示例 - 演示如何使用自定义 schema  
"""  
import requests  
import json  
from datetime import datetime  
  
# API 基础 URL  
BASE_URL = "http://192.168.1.6:5903/api"  
  
def test_custom_schema():  
    """测试自定义 schema 功能"""  
      
    # 定义自定义 schema  
    custom_schemas = [  
        {  
            "name": "Product",  
            "description": "产品实体",  
            "properties": {  
                "name": {"type": "string", "description": "产品名称", "required": True},  
                "price": {"type": "number", "description": "产品价格", "required": False},  
                "category": {"type": "string", "description": "产品类别", "required": False}  
            }  
        },  
        {  
            "name": "Customer",   
            "description": "客户实体",  
            "properties": {  
                "name": {"type": "string", "description": "客户姓名", "required": True},  
                "email": {"type": "string", "description": "客户邮箱", "required": False},  
                "age": {"type": "integer", "description": "客户年龄", "required": False}  
            }  
        }  
    ]  
  
    # 添加 episode 请求  
    episode_data = {  
        "name": "产品销售记录",  
        "episode_body": "客户张三购买了价格为299元的智能手表，客户邮箱是zhangsan@example.com，年龄28岁",  
        "source_description": "销售系统记录",  
        "source": "text",  
        "group_id": "sales_data",  
        "custom_schemas": custom_schemas  
    }  
  
    print("正在添加 Episode...")  
    try:  
        response = requests.post(f"{BASE_URL}/episodes", json=episode_data)  
        print("添加 Episode 响应:", response.json())  
    except Exception as e:  
        print(f"添加 Episode 失败: {e}")  
  
    # 搜索示例  
    search_data = {  
        "query": "智能手表",  
        "group_id": "sales_data",  
        "limit": 10  
    }  
  
    print("\n正在搜索...")  
    try:  
        response = requests.post(f"{BASE_URL}/search/nodes", json=search_data)  
        print("搜索响应:", response.json())  
    except Exception as e:  
        print(f"搜索失败: {e}")  
  
if __name__ == "__main__":  
    # 首先检查健康状态  
    try:  
        response = requests.get("http://192.168.1.6:5903/health")  
        print("健康检查:", response.json())  
          
        # 运行测试  
        test_custom_schema()  
          
    except Exception as e:  
        print(f"服务器连接失败: {e}")  
        print("请确保服务器已启动: python start_server.py")