from typing import List, Dict, Any, Optional  
from fastapi import APIRouter, HTTPException, status, Depends  

from graph_service.zep_graphiti import ZepGraphitiDep    
from graph_service.dto.common import DataProcessingResult, BulkDataProcessingResult  
from graph_service.routers.data_universal_json_processor import UniversalJsonProcessor  





router = APIRouter(prefix="/data-processing", tags=["Data Processing"])  


@router.post('/process-json', status_code=status.HTTP_201_CREATED)  
async def process_json_data(  
    json_data: List[Dict[str, Any]],  
    group_id: str,  
    graphiti: ZepGraphitiDep,  
    processing_config: Optional[Dict[str, Any]] = None,  
    schema_names: Optional[List[str]] = None,  
) -> DataProcessingResult:  
    """处理 JSON 数据"""  
    try:  
        # 数据预处理 - 转换为标准 RawEpisode 格式  
        raw_episodes = UniversalJsonProcessor.process_json_to_episodes(  
            json_data, processing_config  
        )  
          
        # 为每个 episode 设置 group_id  
        for episode in raw_episodes:  
            episode.group_id = group_id  
          
        # 批量添加到图数据库  
        result = await graphiti.add_episode_bulk_with_custom_schema(  
            bulk_episodes=raw_episodes,  
            group_id=group_id,  
            entity_types=schema_names,  
        )  
          
        return DataProcessingResult(  
            message=f"成功处理 {len(raw_episodes)} 条数据",  
            success=True,  
            episodes_processed=len(result.episodes),  
            total_nodes_created=len(result.nodes),  
            total_edges_created=len(result.edges),  
        )  

    except ValueError as e:  
        raise HTTPException(  
            status_code=status.HTTP_400_BAD_REQUEST,  
            detail=f"数据验证失败: {str(e)}"  
        )  
    except Exception as e:  
        raise HTTPException(  
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail=f"数据处理失败: {str(e)}"  
        )  


@router.post('/process-bulk-json', status_code=status.HTTP_201_CREATED)  
async def process_bulk_json_data(
    graphiti: ZepGraphitiDep,
    datasets: List[Dict[str, Any]],
    global_group_id: Optional[str] = None,
    global_schema_names: Optional[List[str]] = None,  
) -> BulkDataProcessingResult:  
    """批量处理多个 JSON 数据集"""  
    try:  
        all_raw_episodes = []  
        processed_items = []  
          
        for dataset in datasets:  
            json_data = dataset.get("data", [])  
            group_id = dataset.get("group_id", global_group_id)  
            processing_config = dataset.get("processing_config")  
              
            # 处理单个数据集  
            raw_episodes = UniversalJsonProcessor.process_json_to_episodes(  
                json_data, processing_config
            )  
              
            # 设置 group_id
            for episode in raw_episodes:
                episode.group_id = group_id

            all_raw_episodes.extend(raw_episodes)
            processed_items.append({
                "group_id": group_id,
                "episodes_count": len(raw_episodes)  
            })

        # 批量添加到图数据库
        result = await graphiti.add_episode_bulk_with_custom_schema(
            bulk_episodes=all_raw_episodes,  
            entity_types=global_schema_names,
        )

        return BulkDataProcessingResult(
            message=f"成功批量处理 {len(all_raw_episodes)} 条数据",
            success=True,
            episodes_processed=len(result.episodes),
            total_nodes_created=len(result.nodes),
            total_edges_created=len(result.edges),
            processed_items=processed_items  
        )

    except Exception as e:  
        raise HTTPException(  
            status_code=status.HTTP_400_BAD_REQUEST,  
            detail=f"批量数据处理失败: {str(e)}"  
        )
