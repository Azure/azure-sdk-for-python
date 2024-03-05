# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import logging
from typing import Any, Dict, Optional

from openai import AzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from azure.ai.generative.evaluate._user_agent import USER_AGENT
from azure.ai.generative.constants._common import USER_AGENT_HEADER_KEY
from azure.core.credentials import TokenCredential

semaphore = asyncio.Semaphore(10)

LOGGER = logging.getLogger(__name__)


class AzureOpenAIClient:  # pylint: disable=client-accepts-api-version-keyword
    # pylint: disable=unused-argument
    def __init__(self, openai_params: Dict, credential: Optional[TokenCredential] = None, **kwargs: Any) -> None:
        self._azure_endpoint = (
            openai_params.get("azure_endpoint", None)
            if openai_params.get("azure_endpoint", None)
            else openai_params.get("api_base", None)
        )
        self._api_key = openai_params.get("api_key", None)
        self._api_version = openai_params.get("api_version", None)
        self._azure_deployment = (
            openai_params.get("azure_deployment", None)
            if openai_params.get("azure_deployment", None)
            else openai_params.get("deployment_id", None)
        )

        self._client = AzureOpenAI(
            azure_endpoint=self._azure_endpoint.strip("/"),
            api_version=self._api_version,
            api_key=self._api_key,
            default_headers={USER_AGENT_HEADER_KEY: USER_AGENT, "client_operation_source": "evaluate"},
        )

    def bounded_chat_completion(self, messages: Any) -> Any:
        try:
            result = self._client.with_options(max_retries=5).chat.completions.create(
                model=self._azure_deployment,
                messages=messages,
                temperature=0,
                seed=0,
            )
            return result
        except Exception as ex:  # pylint: disable=broad-except
            LOGGER.debug("Failed to call llm with exception : %s", str(ex))
            return ex

    def get_chat_completion_content_from_response(self, response: Any) -> Any:  # pylint: disable=name-too-long
        if isinstance(response, ChatCompletion):
            return response.choices[0].message.content
        return None
