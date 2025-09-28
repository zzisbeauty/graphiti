# config.py  
from functools import lru_cache  
from pydantic_settings import BaseSettings, SettingsConfigDict  
from pydantic import Field  
from dotenv import load_dotenv  
  
# 在类定义之前加载 .env 文件  
load_dotenv('/home/graphiti/mcp_server/.env')  
  
class GraphitiSettings(BaseSettings):  
    neo4j_uri: str  
    neo4j_user: str  
    neo4j_password: str  
    openai_api_key: str  
    openai_base_url: str | None = Field(None)  
    model_name: str | None = Field(None)  
    embedding_model_name: str | None = Field(None)  
    semaphore_limit: int = 10  
      
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

@lru_cache
def get_settings():
    return GraphitiSettings()  # type: ignore[call-arg]


# 测试配置是否正确加载
if __name__ == "__main__":
    settings = get_settings()
    print(f"Neo4j URI: {settings.neo4j_uri}")
    print(f"Neo4j User: {settings.neo4j_user}")
    print(f"OpenAI Key: {settings.openai_api_key[:10]}...")