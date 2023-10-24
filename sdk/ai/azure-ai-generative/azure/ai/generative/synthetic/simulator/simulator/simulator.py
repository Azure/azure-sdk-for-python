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
from azure.ai.generative.entities import AzureOpenAIModelConfiguration
from azure.ai.generative.synthetic.simulator._model_tools import APITokenManager, OpenAIChatCompletionsModel


import logging
import os
import asyncio
import threading

BASIC_MD = os.path.join(template_dir, "basic.md")
USER_MD = os.path.join(template_dir, "user.md")


class Simulator:
    def __init__(
        self,
        systemConnection: AzureOpenAIModelConfiguration = None,
        userConnection: AzureOpenAIModelConfiguration = None,
        simulate_callback: Callable[[str, List[Dict], dict], str] = None,
    ):
        self.userConnection = self._to_openai_chat_completion_model(userConnection)
        self.systemConnection = self._to_openai_chat_completion_model(systemConnection)
        self.simulate_callback = simulate_callback

    def _to_openai_chat_completion_model(self, config: AzureOpenAIModelConfiguration):
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
                assistant_template = f.read()
                assistant_parameters = {"chatbot_name": "ChatBot"}
            return self.create_bot(
                role, assistant_template, assistant_parameters, self.userConnection
            )

        elif role == ConversationRole.USER:
            return self.create_bot(role, template, parameters, self.systemConnection)

    async def simulate_async(
        self,
        template: str,
        parameters: dict,
        max_conversation_turns: int,
        api_call_retry_max_count: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: float = 0,
    ):
        # create user bot
        gpt_bot = self.setup_bot(ConversationRole.USER, template, parameters)

        if self.userConnection == None:
            bots = [gpt_bot]
        else:
            customer_bot = self.setup_bot(
                ConversationRole.ASSISTANT, template, parameters
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
                simualte_callback=self.simulate_callback,
                session=session,
                turn_limit=max_conversation_turns,
                api_call_delay_sec=api_call_delay_sec,
                meta_data=parameters["metadata"],
            )
        formatted_conversation = {
            "conversation_id": conversation_id,
            "conversation": [
                turn.to_annotation_format(turn_number=turn_number)
                for (turn_number, turn) in enumerate(conversation_history)
            ],
            "meta_data": parameters,
        }
        return self.to_chat_protocol(formatted_conversation)

    def to_chat_protocol(self, formatted_conversation):
        c = formatted_conversation
        conver_list = c["conversation"]

        metadata = c["meta_data"]
        conv_id = c["conversation_id"]

        messages = []

        for m in conver_list:
            messages.append(
                {
                    "content": m["response"],
                    "role": m["actor"],
                    "turn_number": m["turn_number"],
                    "meta_data": metadata,
                    "conversation_id": conv_id,
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
