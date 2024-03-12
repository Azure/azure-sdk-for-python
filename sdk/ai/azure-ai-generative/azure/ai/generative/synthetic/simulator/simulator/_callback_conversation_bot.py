# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from typing import List, Tuple

from azure.ai.generative.synthetic.simulator._conversation import (
    ConversationBot,
    ConversationTurn,
)


class CallbackConversationBot(ConversationBot):
    def __init__(self, callback, user_template, user_template_parameters, *args, **kwargs):
        self.callback = callback
        self.user_template = user_template
        self.user_template_parameters = user_template_parameters

        super().__init__(*args, **kwargs)

    async def generate_response(
        self,
        session: "RetryClient",  # type: ignore[name-defined]
        conversation_history: List[ConversationTurn],
        max_history: int,
        turn_number: int = 0,
    ) -> Tuple[dict, dict, int, dict]:
        chat_protocol_message = self._to_chat_protocol(
            self.user_template, conversation_history, self.user_template_parameters
        )
        msg_copy = copy.deepcopy(chat_protocol_message)
        result = await self.callback(msg_copy)

        self.logger.info("Using user provided callback returning response.")

        time_taken = 0
        try:
            response = {
                "samples": [result["messages"][-1]["content"]],
                "finish_reason": ["stop"],
                "id": None,
            }
        except Exception as exc:
            raise TypeError("User provided callback do not conform to chat protocol standard.") from exc

        self.logger.info("Parsed callback response")

        return response, {}, time_taken, result

    # pylint: disable=unused-argument
    def _to_chat_protocol(self, template, conversation_history, template_parameters):
        messages = []

        for _, m in enumerate(conversation_history):
            messages.append({"content": m.message, "role": m.role.value})

        return {
            "template_parameters": template_parameters,
            "messages": messages,
            "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
        }
