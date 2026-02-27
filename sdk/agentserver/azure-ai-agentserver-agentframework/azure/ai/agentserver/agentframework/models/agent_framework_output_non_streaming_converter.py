# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import datetime
import json
from typing import Any, Optional

from agent_framework import AgentResponse, Content

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponsesAssistantMessageItemResource,
)

from . import constants
from .agent_id_generator import generate_agent_id
from .human_in_the_loop_helper import HumanInTheLoopHelper

logger = get_logger()


class AgentFrameworkOutputNonStreamingConverter:  # pylint: disable=name-too-long
    """Non-streaming converter: AgentResponse -> OpenAIResponse."""

    def __init__(self, context: AgentRunContext, *, hitl_helper: Optional[HumanInTheLoopHelper] = None):
        self._context = context
        self._response_id = None
        self._response_created_at = None
        self._hitl_helper = hitl_helper

    def _ensure_response_started(self) -> None:
        if not self._response_id:
            self._response_id = self._context.response_id  # type: ignore
        if not self._response_created_at:
            self._response_created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())  # type: ignore

    def _build_item_content_output_text(self, text: str) -> ItemContentOutputText:
        return ItemContentOutputText(text=text, annotations=[])

    def _new_assistant_message_item(self, message_text: str) -> ResponsesAssistantMessageItemResource:
        item_content = self._build_item_content_output_text(message_text)
        return ResponsesAssistantMessageItemResource(
            id=self._context.id_generator.generate_message_id(), status="completed", content=[item_content]
        )

    def transform_output_for_response(self, response: AgentResponse) -> OpenAIResponse:
        """Build an OpenAIResponse capturing all supported content types.

        Previously this method only emitted text message items. We now also capture:
          - function_call content -> function_call output item
          - function_result content -> function_call_output item

        to stay aligned with the streaming converter so no output is lost.

        :param response: The AgentResponse from the agent framework.
        :type response: AgentResponse

        :return: The constructed OpenAIResponse.
        :rtype: OpenAIResponse
        """
        logger.debug("Transforming non-streaming response (messages=%d)", len(response.messages))
        self._ensure_response_started()

        completed_items: list[dict] = []

        for i, message in enumerate(response.messages):
            logger.debug("Non-streaming: processing message index=%d type=%s", i, type(message).__name__)
            if not message.contents:
                continue
            for j, content in enumerate(message.contents):
                logger.debug("  content index=%d in message=%d type=%s", j, i, type(content).__name__)
                self._append_content_item(content, completed_items)

        response_data = self._construct_response_data(completed_items)
        openai_response = OpenAIResponse(response_data)
        logger.info(
            "OpenAIResponse built (id=%s, items=%d)",
            self._response_id,
            len(completed_items),
        )
        return openai_response

    # ------------------------- helper append methods -------------------------

    def _append_content_item(self, content: Any, sink: list[dict]) -> None:
        """Dispatch a content object to the appropriate append helper.

        :param content: The content object to dispatch.
        :type content: Any
        :param sink: The list to append items to.
        :type sink: list[dict]
        """
        match content.type:
            case "text" | "text_reasoning":
                self._append_text_content(content, sink)
            case "function_call":
                self._append_function_call_content(content, sink)
            case "function_result":
                self._append_function_result_content(content, sink)
            case "function_approval_request":
                self._append_user_input_request_content(content, sink)
            case "usage":
                logger.debug("Skipping usage content (input/output token counts)")
            case _:
                logger.warning("Unhandled content type in non-streaming: %s", content.type)

    def _append_text_content(self, content: Content, sink: list[dict]) -> None:
        text_value = content.text
        if not text_value:
            return
        item_id = self._context.id_generator.generate_message_id()
        sink.append(
            {
                "id": item_id,
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": text_value,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            }
        )
        logger.debug("    added message item id=%s text_len=%d", item_id, len(text_value))

    def _append_function_call_content(self, content: Content, sink: list[dict]) -> None:
        name = content.name or ""
        arguments = content.arguments or ""
        if not isinstance(arguments, str):
            try:
                arguments = json.dumps(arguments)
            except Exception:  # pragma: no cover - fallback # pylint: disable=broad-exception-caught
                arguments = str(arguments)
        call_id = content.call_id or self._context.id_generator.generate_function_call_id()
        func_item_id = self._context.id_generator.generate_function_call_id()
        sink.append(
            {
                "id": func_item_id,
                "type": "function_call",
                "status": "completed",
                "call_id": call_id,
                "name": name,
                "arguments": arguments or "",
            }
        )
        logger.debug(
            "    added function_call item id=%s call_id=%s name=%s args_len=%d",
            func_item_id,
            call_id,
            name,
            len(arguments or ""),
        )

    def _append_function_result_content(self, content: Content, sink: list[dict]) -> None:
        # Coerce the function result into a simple display string.
        raw = content.result
        result: list[str | dict[str, Any]] = []
        match raw:
            case str():
                result = [raw]
            case list():
                result = [self._coerce_result_text(item) for item in raw]
        call_id = content.call_id
        func_out_id = self._context.id_generator.generate_function_output_id()
        sink.append(
            {
                "id": func_out_id,
                "type": "function_call_output",
                "status": "completed",
                "call_id": call_id,
                "output": json.dumps(result) if len(result) > 0 else "",
            }
        )
        logger.debug(
            "added function_call_output item id=%s call_id=%s output_len=%d",
            func_out_id,
            call_id,
            len(result),
        )

    def _append_user_input_request_content(self, content: Content, sink: list[dict]) -> None:
        converted_content = None
        if self._hitl_helper:
            converted_content = self._hitl_helper.convert_user_input_request_content(content)

        if converted_content:
            call_id = converted_content.get("call_id", "")
            name = converted_content.get("name", "")
            arguments = converted_content.get("arguments", "")
        else:
            function_call = content.function_call
            call_id = function_call.call_id or ""
            name = function_call.name or ""
            arguments = function_call.arguments or ""
        if not isinstance(arguments, str):
            arguments = json.dumps(arguments)

        sink.append(
            {
                "id": self._context.id_generator.generate_function_call_id(),
                "type": "function_call",
                "status": "in_progress",
                "call_id": call_id,
                "name": name,
                "arguments": arguments,
            }
        )
        logger.debug("added user_input_request content call_id=%s", call_id)

    # ------------- simple normalization helper -------------------------
    def _coerce_result_text(self, value: Any) -> str | dict:
        """Return a string or dict representation of a result value.

        :param value: The result value to coerce.
        :type value: Any
        :return: A string or dict representation.
        :rtype: str or dict
        """
        match value:
            case None:
                return ""
            case str():
                return value
            case _ if hasattr(value, "type") and value.type == "text":
                return {"type": "text", "text": value.text or ""}
            case _:
                return ""

    def _construct_response_data(self, output_items: list[dict]) -> dict:
        agent_id = generate_agent_id(self._context)

        response_data: dict[str, Any] = {
            "object": "response",
            "metadata": {},
            "agent": agent_id,
            "conversation": self._context.get_conversation_object(),
            "type": "message",
            "role": "assistant",
            "temperature": constants.DEFAULT_TEMPERATURE,
            "top_p": constants.DEFAULT_TOP_P,
            "user": "",
            "id": self._context.response_id,
            "created_at": self._response_created_at,
            "output": output_items,
            "parallel_tool_calls": True,
            "status": "completed",
        }
        return response_data
