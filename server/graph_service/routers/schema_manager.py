import importlib  
from typing import Dict, Any, List  
from pydantic import BaseModel  
  

class SchemaManager:  
    """ 简化的 Schema 管理器，直接接受客户端传入的 schema """  

    def __init__(self):
        self.loaded_schemas: Dict[str, type[BaseModel]] = {}  

    def register_schemas_direct(self, schemas: Dict[str, type[BaseModel]]) -> Dict[str, type[BaseModel]]:  
        """直接注册客户端传入的 schema 字典"""  
        self.loaded_schemas.update(schemas)  
        return schemas  

    def get_schemas_by_names(self, names: List[str]) -> Dict[str, type[BaseModel]]:  
        """根据名称获取 Schema"""  
        return {name: self.loaded_schemas[name] for name in names if name in self.loaded_schemas}  

    def get_all_schemas(self) -> Dict[str, type[BaseModel]]:  
        """获取所有已注册的 Schema"""
        return self.loaded_schemas.copy()  

    def clear_schemas(self):
        """清空所有 Schema"""  
        self.loaded_schemas.clear()
