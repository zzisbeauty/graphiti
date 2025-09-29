import requests 

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
    sys.path.insert(0, '/home/graphiti')



from server.entities.base_entity import ENTITY_TYPES  # 导入您的自定义实体类型  


import requests  
import json  
from typing import Dict, Any, List  
from pydantic import BaseModel  
  
class GraphitiClient:  
    def __init__(self, base_url: str = "http://localhost:8000"):  
        self.base_url = base_url  
        self.session = requests.Session()  
      
    def register_schemas_direct(self, entity_types: Dict[str, type[BaseModel]]) -> Dict[str, Any]:  
        """直接注册 schema（需要传入实际的模型类实例化后的 schema）"""  
        url = f"{self.base_url}/custom-schema/register-schemas-direct"  
          
        # 将 Pydantic 模型类转换为可序列化的 schema 字典  
        serializable_schemas = {}  
        for name, model_class in entity_types.items():  
            # 使用 model_json_schema() 获取 schema 定义  
            serializable_schemas[name] = model_class.model_json_schema()  
          
        response = self.session.post(  
            url,  
            json=serializable_schemas,  
            headers={"Content-Type": "application/json"}  
        )  
          
        if response.status_code != 201:  
            raise Exception(f"Schema 注册失败: {response.text}")  
          
        return response.json()  
      
    def process_json_data(  
        self,   
        json_data: List[Dict[str, Any]],   
        group_id: str,  
        processing_config: Dict[str, Any] = None,  
        schema_names: List[str] = None  
    ) -> Dict[str, Any]:  
        """处理 JSON 数据"""  
        url = f"{self.base_url}/data-processing/process-json"  
          
        payload = {  
            "json_data": json_data,  
            "group_id": group_id,  
            "processing_config": processing_config,  
            "schema_names": schema_names  
        }  
          
        response = self.session.post(  
            url,  
            json=payload,  
            headers={"Content-Type": "application/json"}  
        )  
          
        if response.status_code != 201:  
            raise Exception(f"数据处理失败: {response.text}")  
          
        return response.json()  
      
    def get_schemas(self) -> Dict[str, Any]:  
        """获取已注册的 schema 信息"""  
        url = f"{self.base_url}/custom-schema/schemas"  
        response = self.session.get(url)  
          
        if response.status_code != 200:  
            raise Exception(f"获取 schema 失败: {response.text}")  
          
        return response.json()  
  
# 使用示例  
def main():  
    # 你的诗词数据  
    poetry_data = [  
        {  
            "author": "劉吉",  
            "paragraphs": [  
                "八珍一箸千金價，往往精庖賤惠文。",  
                "莫道形模大剛拙，剖珠也解獻殷勤。"  
            ],  
            "title": "魰",  
            "id": "6ad0677d-1bcf-4564-9334-870b483c06ca"  
        },  
        {  
            "author": "劉吉",  
            "paragraphs": [  
                "一箭不中鵠，五湖歸釣魚。"  
            ],  
            "title": "句",  
            "id": "3ee5e66e-b9fb-4087-ab3a-e82e662ae88b"  
        }  
    ]
      
    # 诗词数据处理配置  
    poetry_config = {  
        "name_field": "title",  
        "id_field": "id",  
        "content_fields": ["paragraphs"],  
        "metadata_fields": ["author"],  
        "fallback_name": "诗词作品",  
        "source_description": "中文诗词数据"  
    }  
      
    # 创建客户端  
    client = GraphitiClient()  
      
    try:  
        # 1. 注册 schema（如果需要的话）  
        # 注意：这里需要你的实际 ENTITY_TYPES 定义  
        schema_result = client.register_schemas_direct(ENTITY_TYPES)  
        print(f"Schema 注册成功: {schema_result}")  
          
        # 2. 处理诗词数据  
        print("正在处理诗词数据...")  
        processing_result = client.process_json_data(  
            json_data=poetry_data,  
            group_id="chinese_poetry",  
            processing_config=poetry_config,  
            schema_names=["Concept", "Knowledge"]  # 使用你需要的 schema  
        )  
        print(f"数据处理成功: {processing_result}")  

        # 3. 查看注册的 schema（可选）  
        # schemas_info = client.get_schemas()  
        # print(f"已注册的 schema: {schemas_info}")  
          
    except Exception as e:  
        print(f"错误: {e}")  
  
if __name__ == "__main__":  
    main()
