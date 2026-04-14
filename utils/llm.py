from typing import Optional

from loguru import logger
from openai import AsyncOpenAI
from utils.schema import LLMConfig
from config import get_llm_config


class LLM:

    def __init__(
        self, llm_name: str = "default", llm_config: Optional[LLMConfig] = None
    ):
        llm_config = get_llm_config(llm_name, llm_config)
        self.model = llm_config.model
        self.api_key = llm_config.api_key
        self.base_url = llm_config.base_url
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def format_messages(self, messages):
        formated_messages = []
        for message in messages:
            if isinstance(message, dict):
                formated_messages.append(message)
            else:
                formated_messages.append(message.dict())
        return format_messages

    async def ask(self, messages):
        return await self.ask_tool(messages, [], "none")

    async def ask_tool(self, messages, tools, tool_choice):
        params = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "stream": False,
        }
        logger.info(f"ask_tool with params: {params}")
        response = await self.client.chat.completions.create(**params)
        logger.info(f"ask_tool with response: {response.__dict__}")
        return response.choices[0].message
