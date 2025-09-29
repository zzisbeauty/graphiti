import json  
from typing import List, Dict, Any, Optional  
from datetime import datetime, timezone  
from graphiti_core.utils.bulk_utils import RawEpisode  
from graphiti_core.nodes import EpisodeType  




class UniversalJsonProcessor:  
    """ 通用 JSON 数据预处理器，将任意 JSON 格式转换为 Graphiti 标准格式 """  

    @staticmethod  
    def process_json_to_episodes(  
        json_data: List[Dict[str, Any]],   
        config: Optional[Dict[str, Any]] = None  
    ) -> List[RawEpisode]:
        """  将任意 JSON 数据转换为 RawEpisode 列表  
        Args:  
            json_data: JSON 数据数组  
            config: 配置选项，包含字段映射和处理规则  
        Returns:  
            List[RawEpisode]: 转换后的标准格式列表  
        """  
        raw_episodes = []  
        default_config = {  
            "name_field": "title",  # 用作名称的字段  
            "id_field": "id",       # ID 字段  
            "content_fields": [],   # 内容字段列表  
            "metadata_fields": [],  # 元数据字段列表  
            "fallback_name": "数据条目",  
            "source_description": "JSON 数据"  
        }  

        # 合并配置  
        effective_config = {**default_config, **(config or {})}  

        for i, item_data in enumerate(json_data):  
            # 1. 生成名称  
            name = UniversalJsonProcessor._extract_name(item_data, effective_config, i)  

            # 2. 构建结构化内容  
            content = UniversalJsonProcessor._build_content(item_data, effective_config)  
              
            # 3. 生成来源描述  
            source_desc = UniversalJsonProcessor._build_source_description(  
                item_data, effective_config  
            )  

            # 4. 创建 RawEpisode  
            raw_episode = RawEpisode(  
                name=name,  
                content=content,  
                source_description=source_desc,  
                source=EpisodeType.json,  
                reference_time=datetime.now(timezone.utc)  
            )
 
            raw_episodes.append(raw_episode)  
          
        return raw_episodes  
      
    @staticmethod  
    def _extract_name(data: Dict[str, Any], config: Dict[str, Any], index: int) -> str:  
        """提取或生成数据条目名称"""  
        name_field = config.get("name_field")  
        id_field = config.get("id_field")  
        fallback_name = config.get("fallback_name", "数据条目")  
          
        # 优先使用指定的名称字段  
        if name_field and name_field in data:  
            name = str(data[name_field])  
            if name.strip():  
                return name  
          
        # 其次使用 ID 字段  
        if id_field and id_field in data:  
            return f"{fallback_name}_{data[id_field]}"  
          
        # 最后使用索引  
        return f"{fallback_name}_{index + 1}"  
      
    @staticmethod  
    def _build_content(data: Dict[str, Any], config: Dict[str, Any]) -> str:  
        """构建结构化内容"""  
        content_parts = []  
          
        # 添加基本信息部分  
        content_parts.append("=== 数据信息 ===")  
          
        # 处理指定的内容字段  
        content_fields = config.get("content_fields", [])  
        if content_fields:  
            content_parts.append("\n--- 主要内容 ---")  
            for field in content_fields:  
                if field in data:  
                    value = data[field]  
                    if isinstance(value, list):  
                        content_parts.append(f"{field}:")  
                        for item in value:  
                            content_parts.append(f"  - {item}")  
                    else:  
                        content_parts.append(f"{field}: {value}")  
          
        # 添加元数据部分  
        metadata_fields = config.get("metadata_fields", [])  
        if metadata_fields:  
            content_parts.append("\n--- 元数据 ---")  
            for field in metadata_fields:  
                if field in data:  
                    content_parts.append(f"{field}: {data[field]}")  
          
        # 添加所有其他字段  
        processed_fields = set(content_fields + metadata_fields)  
        other_fields = {k: v for k, v in data.items() if k not in processed_fields}  
          
        if other_fields:  
            content_parts.append("\n--- 其他信息 ---")  
            for key, value in other_fields.items():  
                if isinstance(value, (dict, list)):  
                    content_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")  
                else:  
                    content_parts.append(f"{key}: {value}")  
        
        # 添加完整原始数据
        content_parts.append("\n--- 原始数据 ---")  
        content_parts.append(json.dumps(data, ensure_ascii=False, indent=2))  
        return "\n".join(content_parts)  
      
    @staticmethod  
    def _build_source_description(data: Dict[str, Any], config: Dict[str, Any]) -> str:  
        """构建来源描述"""  
        base_desc = config.get("source_description", "JSON 数据")  
          
        # 尝试添加更具体的描述  
        name_field = config.get("name_field")  
        if name_field and name_field in data:  
            return f"{base_desc} - {data[name_field]}"  
          
        return base_desc  
  


# 针对你的诗词数据的配置示例  
POETRY_CONFIG = {  
    "name_field": "title",  
    "id_field": "id",   
    "content_fields": ["paragraphs"],  
    "metadata_fields": ["author"],  
    "fallback_name": "诗词作品",  
    "source_description": "中文诗词数据"  
}  


# 其他数据类型的配置示例  
ARTICLE_CONFIG = {  
    "name_field": "title",  
    "id_field": "id",  
    "content_fields": ["content", "body", "text"],  
    "metadata_fields": ["author", "date", "category"],  
    "fallback_name": "文章",  
    "source_description": "文章数据"  
}  
  

PRODUCT_CONFIG = {  
    "name_field": "name",  
    "id_field": "product_id",  
    "content_fields": ["description", "features"],  
    "metadata_fields": ["price", "category", "brand"],  
    "fallback_name": "产品",  
    "source_description": "产品数据"  
}