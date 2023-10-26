# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, Dict, List
from azure.ai.generative.synthetic.simulator._conversation import (
    ConversationBot,
    ConversationRole,
    simulate_conversation,
)
from azure.ai.generative.synthetic.simulator._model_tools.models import (
    OpenAIChatCompletionsModel,
    AsyncHTTPClientWithRetry,
)
from azure.ai.generative.synthetic.simulator import _template_dir as template_dir
from azure.ai.generative.synthetic.simulator._model_tools import APITokenManager, OpenAIChatCompletionsModel


import logging
import os
import asyncio
import threading
import json

BASIC_MD = os.path.join(template_dir, "basic.md")
USER_MD = os.path.join(template_dir, "user.md")


class Simulator:
    def __init__(
        self,
        systemConnection: "AzureOpenAIModelConfiguration" = None,
        userConnection: "AzureOpenAIModelConfiguration" = None,
        simulate_callback: Callable[[str, List[Dict], dict], str] = None,
    ):
        self.userConnection = self._to_openai_chat_completion_model(userConnection)
        self.systemConnection = self._to_openai_chat_completion_model(systemConnection)
        self.simulate_callback = simulate_callback

    def _to_openai_chat_completion_model(self, config: "AzureOpenAIModelConfiguration"):
        token_manager = PlainTokenManager(
            openapi_key=config.api_key,
            auth_header="api-key",
            logger=logging.getLogger(f"{config.deployment_name}_bot_token_manager")
        )        
        return OpenAIChatCompletionsModel(
            endpoint_url=f"{config.api_base}openai/deployments/{config.deployment_name}/chat/completions",
            token_manager=token_manager,
            api_version=config.api_version,
            name=config.model_name,
            **config.model_kwargs
        )

    def create_bot(
        self,
        role: str,
        conversation_template: str,
        instantiation_parameters: dict,
        model: OpenAIChatCompletionsModel = None,
    ):
        bot = ConversationBot(
            role=role,
            model=model,
            conversation_template=conversation_template,
            instantiation_parameters=instantiation_parameters,
        )
        return bot

    def setup_bot(
        self,
        role: str,
        template: str,
        parameters: dict
    ):
        if role == ConversationRole.ASSISTANT:
            with open(BASIC_MD, "r") as f:
                chatbot_name_key = "chatbot_name"
                assistant_template = f.read()
                assistant_parameters = {chatbot_name_key: "ChatBot"}
                if parameters.get(chatbot_name_key) is not None:
                    assistant_parameters[chatbot_name_key] = parameters[chatbot_name_key]

            return self.create_bot(
                role, assistant_template, assistant_parameters, self.userConnection
            )

        elif role == ConversationRole.USER:
            return self.create_bot(role, template, parameters, self.systemConnection)

    async def simulate_async(
        self,
        template: "Template",
        parameters: dict,
        max_conversation_turns: int,
        api_call_retry_max_count: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: float = 0,
    ):
        # create user bot
        gpt_bot = self.setup_bot(ConversationRole.USER, str(template), parameters)

        if self.userConnection == None:
            bots = [gpt_bot]
        else:
            customer_bot = self.setup_bot(
                ConversationRole.ASSISTANT, str(template), parameters
            )
            bots = [gpt_bot, customer_bot]
        # simulate the conversation

        asyncHttpClient = AsyncHTTPClientWithRetry(
            n_retry=api_call_retry_max_count,
            retry_timeout=api_call_retry_sleep_sec,
            logger=logging.getLogger()
        )

        async with asyncHttpClient.client as session:
            conversation_id, conversation_history = await simulate_conversation(
                bots=bots,
                simulate_callback=self.simulate_callback,
                session=session,
                turn_limit=max_conversation_turns,
                api_call_delay_sec=api_call_delay_sec,
                template_paramaters=parameters,
            )

        return self._to_chat_protocol(template, conversation_history, parameters)

    def _get_citations(self, parameters, context_keys):
        citations = []
        for c_key in context_keys:
            if isinstance(parameters[c_key], dict):
                for k, v in parameters[c_key].items():
                    citations.append(
                        {
                            "id": k,
                            "content": self._to_citation_content(v)
                        }
                    )
            else:
                citations.append(
                    {
                        "id": c_key,
                        "content": self._to_citation_content(parameters[c_key])
                    }
                )

        return {
            "citations": citations
        }
                    
    def _to_citation_content(self, obj):
        if isinstance(obj, str):
            return obj
        else:
            return json.dumps(obj)

    def _to_chat_protocol(self, template, conversation_history, template_parameters):
        messages = []

        for i, m in enumerate(conversation_history):
            citations = self._get_citations(template_parameters, template.context_key)
            messages.append(
                {
                    "content": m.message,
                    "role": m.role.value,
                    "turn_number": i,
                    "template_parameters": template_parameters,
                    "context": citations
                }
            )

        return {
            "messages": messages,
            "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
        }

    def wrap_async(
        self,
        results,
        template: str,
        parameters: dict,
        max_conversation_turns: int,
        api_call_retry_max_count: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: float = 0,
    ):
        result = asyncio.run(
            self.simulate_async(
                template=template,
                parameters=parameters,
                max_conversation_turns=max_conversation_turns,
                api_call_retry_max_count=api_call_retry_max_count,
                api_call_retry_sleep_sec=api_call_retry_sleep_sec,
                api_call_delay_sec=api_call_delay_sec,
            )
        )
        results[0] = result

    def simulate(
        self,
        template: str,
        parameters: dict,
        max_conversation_turns: int,
        api_call_retry_max_count: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: float = 0,
    ):
        results = [None]

        thread = threading.Thread(
            target=self.wrap_async,
            args=(
                results,
                template,
                parameters,
                max_conversation_turns,
                api_call_retry_max_count,
                api_call_retry_sleep_sec,
                api_call_delay_sec,
            ),
        )

        thread.start()
        thread.join()

        return results[0]



class PlainTokenManager(APITokenManager):
    def __init__(self, openapi_key, logger, **kwargs):
        super().__init__(logger, **kwargs)
        self.token = openapi_key

    async def get_token(self):
        return self.token
