import requests  
import json  
from datetime import datetime  
from typing import List, Dict, Any, Union  
import uuid as uuid_lib  

import sys

def find_project_root(marker_files=('pyproject.toml', '.git', 'requirements.txt')):
    import os
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if any(os.path.exists(os.path.join(path, marker)) for marker in marker_files):
            return path
        path = os.path.dirname(path)
    raise RuntimeError("Project root not found.")

project_root = find_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


""" 调用的是 REST API，但是 REST server 无法自定义 schema  因此此代码搁置， 但是此代码有需要可以去尝试做一些简单的调用测试
"""


class GraphitiRestClient:  
    def __init__(self, base_url: str = "http://localhost:5926"):  
        self.base_url = base_url.rstrip('/')  
        self.session = requests.Session()  
      
    def convert_list_to_messages(self,   
                                data_list: List[Dict[str, Any]],   
                                content_fields: List[str] = None,  
                                name_field: str = "title",  
                                id_field: str = "id",  
                                role: str = "system",  
                                role_type: str = "json_import") -> List[Dict[str, Any]]:  
        """  
        通用数据转换工具：将数组数据转换为消息格式  
          
        Args:  
            data_list: 原始数据数组  
            content_fields: 用作内容的字段列表，如果为None则使用整个对象  
            name_field: 用作消息名称的字段  
            id_field: 用作UUID的字段  
            role: 消息角色  
            role_type: 角色类型  
          
        Returns:  
            转换后的消息列表  
        """  
        messages = []  
          
        for item in data_list:  
            # 生成内容  
            if content_fields:  
                # 只包含指定字段  
                content_data = {field: item.get(field) for field in content_fields if field in item}  
            else:  
                # 使用整个对象  
                content_data = item  
              
            # 生成消息名称  
            name = item.get(name_field, f"数据项-{len(messages) + 1}")  
              
            # 生成或使用现有UUID  
            message_uuid = item.get(id_field, str(uuid_lib.uuid4()))  
              
            message = {  
                "uuid": message_uuid,  
                "name": str(name),  
                "content": json.dumps(content_data, ensure_ascii=False),  
                "role": role,  
                "role_type": role_type,  
                "timestamp": datetime.now().isoformat(),  
                "source_description": f"数据导入 - {name}"  
            }  
            messages.append(message)  
          
        return messages  
      
    def add_messages(self, group_id: str, messages: List[Dict[str, Any]]) -> dict:  
        """调用REST API的POST /messages端点"""  
        url = f"{self.base_url}/messages"  
        payload = {  
            "group_id": group_id,  
            "messages": messages  
        }  
          
        try:  
            response = self.session.post(url, json=payload)  
            response.raise_for_status()  
            return response.json()  
        except requests.exceptions.RequestException as e:  
            print(f"请求失败: {e}")  
            if hasattr(e, 'response') and e.response is not None:  
                print(f"响应状态码: {e.response.status_code}")  
                print(f"响应内容: {e.response.text}")  
            raise  
      
    def import_json_data(self,   
                        group_id: str,  
                        data: Union[List[Dict[str, Any]], Dict[str, Any]],  
                        **convert_kwargs) -> dict:  
        """ 通用JSON数据导入方法  
        Args:  
            group_id: 组ID  
            data: 要导入的数据（可以是数组或单个对象）  
            **convert_kwargs: 传递给convert_list_to_messages的参数  
        Returns:  
            API响应结果  
        """  
        # 如果是单个对象，转换为数组  
        if isinstance(data, dict):  
            data_list = [data]  
        else:  
            data_list = data  
          
        # 转换数据格式  
        messages = self.convert_list_to_messages(data_list, **convert_kwargs)  
          
        # 调用API  
        return self.add_messages(group_id, messages)  
  
from webdatas import *

# 使用示例  
if __name__ == "__main__":    
    client = GraphitiRestClient("http://192.168.1.6:5926")  
      
    # # 方式1：使用所有字段  
    # result = client.import_json_data(  
    #     group_id="classical_poetry",  
    #     data=json_data,  
    #     name_field="title",  
    #     id_field="id",  
    #     role_type="poetry_import"  
    # )  
      
    # 方式2：只使用特定字段作为内容  
    result = client.import_json_data(  
        group_id="classical_poetry",  
        data=json_data,  
        content_fields=["author", "title", "paragraphs"],  
        name_field="title",  
        id_field="id"  
    )  
      
    print("导入完成:", result)