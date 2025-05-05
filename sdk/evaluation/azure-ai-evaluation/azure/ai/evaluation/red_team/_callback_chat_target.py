# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Callable, Dict, List, Optional

from pyrit.models import (
    PromptRequestResponse,
    construct_response_from_request,
)
from pyrit.prompt_target import PromptChatTarget

logger = logging.getLogger(__name__)


class _CallbackChatTarget(PromptChatTarget):
    def __init__(
        self,
        *,
        callback: Callable[[List[Dict], bool, Optional[str], Optional[Dict[str, Any]]], Dict],
        stream: bool = False,
    ) -> None:
        """
        Initializes an instance of the _CallbackChatTarget class.

        It is intended to be used with PyRIT where users define a callback function
        that handles sending a prompt to a target and receiving a response.
        The _CallbackChatTarget class is a wrapper around the callback function that allows it to be used
        as a target in the PyRIT framework.
        For that reason, it merely handles additional functionality such as memory.

        Args:
            callback (Callable): The callback function that sends a prompt to a target and receives a response.
            stream (bool, optional): Indicates whether the target supports streaming. Defaults to False.
        """
        PromptChatTarget.__init__(self)
        self._callback = callback
        self._stream = stream

    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse) -> PromptRequestResponse:

        self._validate_request(prompt_request=prompt_request)
        request = prompt_request.request_pieces[0]

        messages = self._memory.get_chat_messages_with_conversation_id(conversation_id=request.conversation_id)

        messages.append(request.to_chat_message())

        logger.info(f"Sending the following prompt to the prompt target: {request}")

        # response_context contains "messages", "stream", "session_state, "context"
        response_context = await self._callback(messages=messages, stream=self._stream, session_state=None, context=None) # type: ignore

        response_text = response_context["messages"][-1]["content"]
        response_entry = construct_response_from_request(
            request=request, response_text_pieces=[response_text]
        )

        logger.info(
            "Received the following response from the prompt target"
            + f"{response_text}"
        )
        return response_entry

    def _validate_request(self, *, prompt_request: PromptRequestResponse) -> None:
        if len(prompt_request.request_pieces) != 1:
            raise ValueError("This target only supports a single prompt request piece.")

        if prompt_request.request_pieces[0].converted_value_data_type != "text":
            raise ValueError("This target only supports text prompt input.")

    def is_json_response_supported(self) -> bool:
        """Indicates that this target supports JSON response format."""
        return False
