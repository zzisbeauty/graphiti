from enum import Enum

DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_TOKENS = 8192

class ModelSize(Enum):
    small = 'small'
    medium = 'medium'


class LLMConfig:
    """ such as OpenAI's GPT models. It stores the API key, model name, and base URL """
    def __init__(
        self,
        api_key: str | None = None,

        model: str | None = None,
        small_model: str | None = None,
        # model: str="qwen-plus",
        # small_model:str = "qwen-turbo",
        
        # base_url: str | None = None, # None 时 openai 库默认调用 openai base url
        base_url: str ="https://vip.apiyi.com/v1/",
        # base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",

        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.small_model = small_model
        self.temperature = temperature
        self.max_tokens = max_tokens
