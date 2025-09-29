import asyncio
from contextlib import asynccontextmanager
from functools import partial
from fastapi import APIRouter, FastAPI, status
from graphiti_core.nodes import EpisodeType  # type: ignore
from graphiti_core.utils.maintenance.graph_data_operations import clear_data  # type: ignore
from graph_service.dto import AddEntityNodeRequest, AddMessagesRequest, Message, Result
from graph_service.zep_graphiti import ZepGraphitiDep


class AsyncWorker:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.task = None

    async def worker(self):
        while True:
            try:
                print(f'Got a job: (size of remaining queue: {self.queue.qsize()})')
                job = await self.queue.get()
                await job()
            except asyncio.CancelledError:
                break

    async def start(self):
        self.task = asyncio.create_task(self.worker())

    async def stop(self):
        if self.task:
            self.task.cancel()
            await self.task
        while not self.queue.empty():
            self.queue.get_nowait()


async_worker = AsyncWorker()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await async_worker.start()
    yield
    await async_worker.stop()


router = APIRouter(lifespan=lifespan)


# old
# @router.post('/messages', status_code=status.HTTP_202_ACCEPTED)
# async def add_messages(
#     request: AddMessagesRequest,
#     graphiti: ZepGraphitiDep,
# ):
#     async def add_messages_task(m: Message):
#         await graphiti.add_episode(
#             uuid=m.uuid,
#             group_id=request.group_id,
#             name=m.name,
#             episode_body=f'{m.role or ""}({m.role_type}): {m.content}',
#             reference_time=m.timestamp,
#             source=EpisodeType.message,
#             source_description=m.source_description,
#         )

#     for m in request.messages:
#         await async_worker.queue.put(partial(add_messages_task, m))

#     return Result(message='Messages added to processing queue', success=True)


# with schema
from pydantic import BaseModel  
from typing import Dict, Type, Optional  

@router.post('/messages', status_code=status.HTTP_201_CREATED)  
async def add_messages(  
    request: AddMessagesRequest,  
    entity_schema: Optional[Dict[str, Type[BaseModel]]] = None,  # 新增参数  
    graphiti: ZepGraphitiDep,  
):  
    # 使用客户端传入的 schema  
    entity_types = graphiti.get_entity_types_from_schema(entity_schema)  
      
    async def add_messages_task(m: Message):  
        await graphiti.add_episode(  
            uuid=m.uuid,  
            group_id=request.group_id,  
            name=m.name,  
            episode_body=f'{m.role or ""}({m.role_type}): {m.content}',  
            reference_time=m.timestamp,  
            source=EpisodeType.message,  
            source_description=m.source_description,  
            entity_types=entity_types  # 传递动态 schema  
        )


""" 此端点客户端传入示例
{  
  "group_id": "learning_session_1",  
  "messages": [...],  
  "entity_schema": {  
    "Note": {  
      "description": "用户的学习笔记或记录",  
      "fields": {  
        "title": {"type": "str", "description": "标题"},  
        "content": {"type": "str", "description": "内容"}  
      }  
    },  
    "Concept": {  
      "description": "具体的概念、术语或知识点",  
      "fields": {  
        "concept_name": {"type": "str", "description": "概念名称"},  
        "understanding_level": {"type": "str", "description": "理解程度"}  
      }  
    }  
  }  
}
"""



@router.post('/entity-node', status_code=status.HTTP_201_CREATED)
async def add_entity_node(
    request: AddEntityNodeRequest,
    graphiti: ZepGraphitiDep,
):
    node = await graphiti.save_entity_node(
        uuid=request.uuid,
        group_id=request.group_id,
        name=request.name,
        summary=request.summary,
    )
    return node


@router.delete('/entity-edge/{uuid}', status_code=status.HTTP_200_OK)
async def delete_entity_edge(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_entity_edge(uuid)
    return Result(message='Entity Edge deleted', success=True)


@router.delete('/group/{group_id}', status_code=status.HTTP_200_OK)
async def delete_group(group_id: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_group(group_id)
    return Result(message='Group deleted', success=True)


@router.delete('/episode/{uuid}', status_code=status.HTTP_200_OK)
async def delete_episode(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_episodic_node(uuid)
    return Result(message='Episode deleted', success=True)


@router.post('/clear', status_code=status.HTTP_200_OK)
async def clear(
    graphiti: ZepGraphitiDep,
):
    await clear_data(graphiti.driver)
    await graphiti.build_indices_and_constraints()
    return Result(message='Graph cleared', success=True)
