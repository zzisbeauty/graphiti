from typing import Dict, Type, Optional  
from pydantic import BaseModel, Field, create_model  


def deserialize_entity_schema(schema_dict: Dict[str, Dict] | None) -> Dict[str, Type[BaseModel]] | None:  
    """将序列化的 schema 字典转换为 Pydantic 模型类型"""  
    if schema_dict is None:  
        return None  
      
    entity_types = {}  
    for type_name, type_definition in schema_dict.items():  
        # 正确的字段定义格式  
        field_definitions = {}  
        for field_name, field_info in type_definition.get('fields', {}).items():  
            # 使用正确的类型注解格式  
            field_type = field_info.get('type', 'str')  
            if field_type == 'str':  
                python_type = str  
            elif field_type == 'int':  
                python_type = int  
            elif field_type == 'float':  
                python_type = float  
            elif field_type == 'list':  
                python_type = list  
            else:  
                python_type = str  # 默认为字符串  
              
            # 创建字段定义 - 格式为 (type, Field(...))  
            field_definitions[field_name] = (  
                Optional[python_type],   
                Field(None, description=field_info.get('description', ''))  
            )  
          
        # 动态创建 Pydantic 模型  
        model_class = create_model(  
            type_name,  
            **field_definitions  
        )  
          
        # 设置文档字符串  
        model_class.__doc__ = type_definition.get('description', '')  
        entity_types[type_name] = model_class  
      
    return entity_types