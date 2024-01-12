# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import logging

from openai import AsyncAzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion

semaphore = asyncio.Semaphore(10)

LOGGER = logging.getLogger(__name__)


class AzureOpenAIClient:

    def __init__(self, openai_params):
        self._azure_endpoint = openai_params.get("azure_endpoint", None) if openai_params.get("azure_endpoint", None) \
            else openai_params.get("api_base", None)
        self._api_key = openai_params.get("api_key", None)
        self._api_version = openai_params.get("api_version", None)
        self._azure_deployment = openai_params.get("azure_deployment", None)\
            if openai_params.get("azure_deployment", None) else openai_params.get("deployment_id", None)

        self._client = AsyncAzureOpenAI(
            azure_endpoint=self._azure_endpoint,
            api_version=self._api_version,
            api_key=self._api_key,
        )

    async def bounded_chat_completion(self, messages):
        async with semaphore:
            try:
                result = await self._client.with_options(max_retries=5).chat.completions.create(
                    model=self._azure_deployment,
                    messages=messages
                )
                return result
            except Exception as ex:
                LOGGER.debug(f"Failed to call llm with exception :  {str(ex)}")
                return ex

    @staticmethod
    def get_chat_compeletion_content_from_response(response):
        if isinstance(response, ChatCompletion):
            return response.choices[0].message.content
        return None
