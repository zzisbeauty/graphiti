from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str | None = Field(None)
    model_name: str | None = Field(None)
    embedding_model_name: str | None = Field(None)
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    use_custom_entities: bool = Field(False, description="Enable custom entity extraction")

    model_config = SettingsConfigDict(env_file='/home/graphiti/server/.env', extra='ignore')


@lru_cache
def get_settings():
    # settings = Settings()
    # print(f"Loaded config - NEO4J_URI: {settings.neo4j_uri}")
    # print(f"Loaded config - OPENAI_BASE_URL: {settings.openai_base_url}")
    # print(f"Loaded config - MODEL_NAME: {settings.model_name}")  
    return Settings()  # type: ignore[call-arg]
    # return settings


ZepEnvDep = Annotated[Settings, Depends(get_settings)]
