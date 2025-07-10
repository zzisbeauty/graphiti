from collections.abc import Iterable
from openai import AsyncAzureOpenAI, AsyncOpenAI
from openai.types import EmbeddingModel
from .client import EmbedderClient, EmbedderConfig

DEFAULT_EMBEDDING_MODEL = 'text-embedding-3-small'


class OpenAIEmbedderConfig(EmbedderConfig):
    # embedding_model: EmbeddingModel | str = DEFAULT_EMBEDDING_MODEL
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    api_key: str | None = None
    # base_url: str | None = None
    base_url : str = "https://vip.apiyi.com/v1/"
    # base_url : str = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class OpenAIEmbedder(EmbedderClient):
    def __init__(
        self,
        config: OpenAIEmbedderConfig | None = None,
        client: AsyncOpenAI | AsyncAzureOpenAI | None = None,
    ):
        if config is None:
            config = OpenAIEmbedderConfig()
        self.config = config

        if client is not None:
            self.client = client
        else:
            self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)

    async def create(
        self, input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]]
    ) -> list[float]:
        result = await self.client.embeddings.create(
            input=input_data, model=self.config.embedding_model
        )
        return result.data[0].embedding[: self.config.embedding_dim]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        result = await self.client.embeddings.create(
            input=input_data_list, model=self.config.embedding_model
        )
        return [embedding.embedding[: self.config.embedding_dim] for embedding in result.data]
