from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    # openai_api_key: str
    openai_api_key="sk-wuTITomWJ5hVYsVb304d3f94Ec144e3bAa5eCc11Ff6aA0E9"

    # openai_base_url: str | None = Field(None)
    openai_base_url="https://vip.apiyi.com"
    model_name: str | None = Field(None)
    embedding_model_name: str | None = Field(None)
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_settings():
    return Settings()


ZepEnvDep = Annotated[Settings, Depends(get_settings)]
