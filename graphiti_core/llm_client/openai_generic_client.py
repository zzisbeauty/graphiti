"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging
import typing
from typing import ClassVar



import re  
import json  
import logging  
import typing  
from pydantic import BaseModel  




import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from ..prompts.models import Message
from .client import LLMClient, get_extraction_language_instruction
from .config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from .errors import RateLimitError, RefusalError

logger = logging.getLogger(__name__)

DEFAULT_MODEL = 'gpt-4.1-mini'


class OpenAIGenericClient(LLMClient):
    """ OpenAIClient is a client class for interacting with OpenAI's language models.

    This class extends the LLMClient and provides methods to initialize the client, get an embedder, and generate responses from the language model.

    Attributes:
        client (AsyncOpenAI): The OpenAI client used to interact with the API.
        model (str): The model name to use for generating responses.
        temperature (float): The temperature to use for generating responses.
        max_tokens (int): The maximum number of tokens to generate in a response.

    Methods:
        __init__(config: LLMConfig | None = None, cache: bool = False, client: typing.Any = None):
            Initializes the OpenAIClient with the provided configuration, cache setting, and client.

        _generate_response(messages: list[Message]) -> dict[str, typing.Any]:
            Generates a response from the language model based on the provided messages.
    """

    # Class-level constants
    MAX_RETRIES: ClassVar[int] = 2

    def __init__(self, config: LLMConfig | None = None, cache: bool = False, client: typing.Any = None):
        """ Initialize the OpenAIClient with the provided configuration, cache setting, and client.

        Args:
            config (LLMConfig | None): The configuration for the LLM client, including API key, model, base URL, temperature, and max tokens.
            cache (bool): Whether to use caching for responses. Defaults to False.
            client (Any | None): An optional async client instance to use. If not provided, a new AsyncOpenAI client is created.
        """
        # removed caching to simplify the `generate_response` override
        if cache:
            raise NotImplementedError('Caching is not implemented for OpenAI')

        if config is None:
            config = LLMConfig()

        super().__init__(config, cache)

        if client is None:
            self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
        else:
            self.client = client



    # original
    # async def _generate_response(
    #     self,
    #     messages: list[Message],
    #     response_model: type[BaseModel] | None = None,
    #     max_tokens: int = DEFAULT_MAX_TOKENS,
    #     model_size: ModelSize = ModelSize.medium,
    # ) -> dict[str, typing.Any]:
    #     openai_messages: list[ChatCompletionMessageParam] = []
    #     for m in messages:
    #         m.content = self._clean_input(m.content)
    #         if m.role == 'user':
    #             openai_messages.append({'role': 'user', 'content': m.content})
    #         elif m.role == 'system':
    #             openai_messages.append({'role': 'system', 'content': m.content})
    #     try:
    #         response = await self.client.chat.completions.create(
    #             model=self.model or DEFAULT_MODEL,
    #             messages=openai_messages,
    #             temperature=self.temperature,
    #             max_tokens=self.max_tokens,
    #             response_format={'type': 'json_object'},
    #         )
    #         result = response.choices[0].message.content or ''
    #         return json.loads(result)
    #     except openai.RateLimitError as e:
    #         raise RateLimitError from e
    #     except Exception as e:
    #         logger.error(f'Error in generating LLM response: {e}')
    #         raise

    # 添加日志输出，检查模型响应
    # async def _generate_response(
    #     self,
    #     messages: list[Message],
    #     response_model: type[BaseModel] | None = None,
    #     max_tokens: int = DEFAULT_MAX_TOKENS,
    #     model_size: ModelSize = ModelSize.medium,
    # ) -> dict[str, typing.Any]:
    #     openai_messages: list[ChatCompletionMessageParam] = []
    #     for m in messages:
    #         m.content = self._clean_input(m.content)
    #         if m.role == 'user':
    #             openai_messages.append({'role': 'user', 'content': m.content})
    #         elif m.role == 'system':
    #             openai_messages.append({'role': 'system', 'content': m.content})
    #     try:  
    #         response = await self.client.chat.completions.create(  
    #             model=self.model or DEFAULT_MODEL,  
    #             messages=openai_messages,  
    #             temperature=self.temperature,  
    #             max_tokens=self.max_tokens,  
    #             # response_format={'type': 'json_object'},   # 本地三方模型不要这一行代码，这样模型会依赖 prompt 中的 JSON schema 说明来生成 JSON 输出
    #         )  

    #         # 添加详细的调试日志  
    #         logger.info(f"Response object: {response}")  
    #         logger.info(f"Choices length: {len(response.choices) if response.choices else 0}")  
            
    #         if not response.choices:  
    #             raise Exception("No choices in response")  
            
    #         result = response.choices[0].message.content or ''  
    #         logger.info(f"LLM raw response: '{result}'")  # 用引号包围以便看清空字符串  
    #         logger.info(f"Response length: {len(result)}")  

    #         if not result:  
    #             raise Exception("Empty response from LLM")  

    #         return json.loads(result)  
    #     except openai.RateLimitError as e:  
    #         raise RateLimitError from e  
    #     except Exception as e:  
    #         logger.error(f'Error in generating LLM response: {e}')  
    #         raise



    async def _generate_response(  
        self,  
        messages: list[Message],  
        response_model: type[BaseModel] | None = None,  
        max_tokens: int = DEFAULT_MAX_TOKENS,  
        model_size: ModelSize = ModelSize.medium,  
    ) -> dict[str, typing.Any]:  
        openai_messages: list[ChatCompletionMessageParam] = []  
        for m in messages:  
            m.content = self._clean_input(m.content)  
            if m.role == 'user':  
                openai_messages.append({'role': 'user', 'content': m.content})  
            elif m.role == 'system':  
                openai_messages.append({'role': 'system', 'content': m.content})  
        
        try:  
            response = await self.client.chat.completions.create(  
                model=self.model or DEFAULT_MODEL,  
                messages=openai_messages,  
                temperature=self.temperature,  
                max_tokens=self.max_tokens,  
                response_format={'type': 'json_object'},  
            )  
            
            # 适配您的自定义响应格式  
            # 检查是否是标准 OpenAI 格式  
            if hasattr(response, 'choices') and response.choices:  
                result = response.choices[0].message.content or ''  
            # 检查是否是您的自定义格式 {'response': '...'}  
            elif isinstance(response, dict) and 'response' in response:  
                result = response['response']  
            else:  
                # 尝试直接转换为字符串  
                result = str(response)
    
            if not result:  
                raise ValueError("Empty response from LLM")  
            
            # 尝试直接解析为 JSON  
            try:  
                return json.loads(result)  
            except json.JSONDecodeError:  
                # 如果直接解析失败,从文本中提取 JSON  
                logger.warning(f"Direct JSON parsing failed, extracting JSON from text")  
                extracted_json = self._extract_json_from_text(result)  
                if extracted_json:  
                    return extracted_json  
                else:  
                    raise ValueError(f"Could not extract valid JSON from response: {result[:200]}...")  
                    
        except openai.RateLimitError as e:  
            raise RateLimitError from e  
        except Exception as e:  
            logger.error(f'Error in generating LLM response: {e}')  
            raise  
    
    def _extract_json_from_text(self, text: str) -> dict[str, typing.Any] | None:  
        """从文本中提取 JSON,处理 <think> 标签等"""  
        if not text:  
            return None  
        
        # 移除 <think> 标签  
        cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)  
        cleaned_text = cleaned_text.strip()  
        
        # 查找 JSON 对象  
        json_start = cleaned_text.find('{')  
        json_end = cleaned_text.rfind('}') + 1  
        
        if json_start >= 0 and json_end > json_start:  
            try:  
                json_str = cleaned_text[json_start:json_end]  
                return json.loads(json_str)  
            except json.JSONDecodeError:  
                pass  
        
        return None























    async def generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int | None = None,
        model_size: ModelSize = ModelSize.medium,
        group_id: str | None = None,
        prompt_name: str | None = None,
    ) -> dict[str, typing.Any]:
        if max_tokens is None:
            max_tokens = self.max_tokens

        if response_model is not None:
            serialized_model = json.dumps(response_model.model_json_schema())
            messages[
                -1
            ].content += (
                f'\n\nRespond with a JSON object in the following format:\n\n{serialized_model}'
            )

        # Add multilingual extraction instructions
        messages[0].content += get_extraction_language_instruction(group_id)

        # Wrap entire operation in tracing span
        with self.tracer.start_span('llm.generate') as span:
            attributes = {
                'llm.provider': 'openai',
                'model.size': model_size.value,
                'max_tokens': max_tokens,
            }
            if prompt_name:
                attributes['prompt.name'] = prompt_name
            span.add_attributes(attributes)

            retry_count = 0
            last_error = None

            while retry_count <= self.MAX_RETRIES:
                try:
                    response = await self._generate_response(
                        messages, response_model, max_tokens=max_tokens, model_size=model_size
                    )
                    return response
                except (RateLimitError, RefusalError):
                    # These errors should not trigger retries
                    span.set_status('error', str(last_error))
                    raise
                except (
                    openai.APITimeoutError,
                    openai.APIConnectionError,
                    openai.InternalServerError,
                ):
                    # Let OpenAI's client handle these retries
                    span.set_status('error', str(last_error))
                    raise
                except Exception as e:
                    last_error = e

                    # Don't retry if we've hit the max retries
                    if retry_count >= self.MAX_RETRIES:
                        logger.error(f'Max retries ({self.MAX_RETRIES}) exceeded. Last error: {e}')
                        span.set_status('error', str(e))
                        span.record_exception(e)
                        raise

                    retry_count += 1

                    # Construct a detailed error message for the LLM
                    error_context = (
                        f'The previous response attempt was invalid. '
                        f'Error type: {e.__class__.__name__}. '
                        f'Error details: {str(e)}. '
                        f'Please try again with a valid response, ensuring the output matches '
                        f'the expected format and constraints.'
                    )

                    error_message = Message(role='user', content=error_context)
                    messages.append(error_message)
                    logger.warning(
                        f'Retrying after application error (attempt {retry_count}/{self.MAX_RETRIES}): {e}'
                    )

            # If we somehow get here, raise the last error
            span.set_status('error', str(last_error))
            raise last_error or Exception('Max retries exceeded with no specific error')
