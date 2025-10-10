from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field


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



from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str | None = Field(None)
    model_name: str | None = Field(None)
    embedding_model_name: str | None = Field(None)

    # Embedding 配置（SiliconFlow）  
    embedding_api_key: str | None = Field(None)  
    embedding_base_url: str | None = Field(None)  

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    model_config = SettingsConfigDict(env_file='/home/graphiti/server/.env', extra='ignore')


@lru_cache
def get_settings():
    return Settings()  # type: ignore[call-arg]


ZepEnvDep = Annotated[Settings, Depends(get_settings)]
