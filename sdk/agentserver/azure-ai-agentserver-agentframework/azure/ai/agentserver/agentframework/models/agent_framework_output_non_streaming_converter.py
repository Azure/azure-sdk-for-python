# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import datetime
import json
from typing import Any, List, cast

from agent_framework import AgentRunResponse, FunctionResultContent
from agent_framework._types import FunctionCallContent, TextContent

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponsesAssistantMessageItemResource,
)

from .agent_id_generator import AgentIdGenerator
from .constants import Constants

logger = get_logger()


class AgentFrameworkOutputNonStreamingConverter:  # pylint: disable=name-too-long
    """Non-streaming converter: AgentRunResponse -> OpenAIResponse."""

    def __init__(self, context: AgentRunContext):
        self._context = context
        self._response_id = None
        self._response_created_at = None

    def _ensure_response_started(self) -> None:
        if not self._response_id:
            self._response_id = self._context.response_id  # type: ignore
        if not self._response_created_at:
            self._response_created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())  # type: ignore

    def _build_item_content_output_text(self, text: str) -> ItemContentOutputText:
        return ItemContentOutputText(type="output_text", text=text, annotations=[])

    def _new_assistant_message_item(self, message_text: str) -> ResponsesAssistantMessageItemResource:
        item_content = self._build_item_content_output_text(message_text)
        return ResponsesAssistantMessageItemResource(
            role="assistant", type="message", id=self._context.id_generator.generate_message_id(), status="completed", content=[item_content]
        )

    def transform_output_for_response(self, response: AgentRunResponse) -> OpenAIResponse:
        """Build an OpenAIResponse capturing all supported content types.

        Previously this method only emitted text message items. We now also capture:
          - FunctionCallContent  -> function_call output item
          - FunctionResultContent -> function_call_output item

        to stay aligned with the streaming converter so no output is lost.

        :param response: The AgentRunResponse from the agent framework.
        :type response: AgentRunResponse

        :return: The constructed OpenAIResponse.
        :rtype: OpenAIResponse
        """
        logger.debug("Transforming non-streaming response (messages=%d)", len(response.messages))
        self._ensure_response_started()

        completed_items: List[dict] = []

        for i, message in enumerate(response.messages):
            logger.debug("Non-streaming: processing message index=%d type=%s", i, type(message).__name__)
            contents = getattr(message, "contents", None)
            if not contents:
                continue
            for j, content in enumerate(contents):
                logger.debug("  content index=%d in message=%d type=%s", j, i, type(content).__name__)
                self._append_content_item(content, completed_items)

        openai_response = self._construct_response_data(completed_items)
        logger.info(
            "OpenAIResponse built (id=%s, items=%d)",
            self._response_id,
            len(completed_items),
        )
        return openai_response

    # ------------------------- helper append methods -------------------------

    def _append_content_item(self, content: Any, sink: List[dict]) -> None:
        """Dispatch a content object to the appropriate append helper.

        Adding this indirection keeps the main transform method compact and makes it
        simpler to extend with new content types later.

        :param content: The content object to append.
        :type content: Any
        :param sink: The list to append the converted content dict to.
        :type sink: List[dict]

        :return: None
        :rtype: None
        """
        if isinstance(content, TextContent):
            self._append_text_content(content, sink)
        elif isinstance(content, FunctionCallContent):
            self._append_function_call_content(content, sink)
        elif isinstance(content, FunctionResultContent):
            self._append_function_result_content(content, sink)
        else:
            logger.debug("unsupported content type skipped: %s", type(content).__name__)

    def _append_text_content(self, content: TextContent, sink: List[dict]) -> None:
        text_value = getattr(content, "text", None)
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

    def _append_function_call_content(self, content: FunctionCallContent, sink: List[dict]) -> None:
        name = getattr(content, "name", "") or ""
        arguments = getattr(content, "arguments", "")
        if not isinstance(arguments, str):
            try:
                arguments = json.dumps(arguments)
            except Exception:  # pragma: no cover - fallback # pylint: disable=broad-exception-caught
                arguments = str(arguments)
        call_id = getattr(content, "call_id", None) or self._context.id_generator.generate_function_call_id()
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

    def _append_function_result_content(self, content: FunctionResultContent, sink: List[dict]) -> None:
        # Coerce the function result into a simple display string.
        result = []
        raw = getattr(content, "result", None)
        if isinstance(raw, str):
            result = [raw]
        elif isinstance(raw, list):
            for item in raw:
                result.append(self._coerce_result_text(item))   # type: ignore
        call_id = getattr(content, "call_id", None) or ""
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

    # ------------- simple normalization helper -------------------------
    def _coerce_result_text(self, value: Any) -> str | dict:
        """
        Return a string if value is already str or a TextContent-like object; else str(value).

        :param value: The value to coerce.
        :type value: Any

        :return: The coerced string or dict.
        :rtype: str | dict
        """
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        # Direct TextContent instance
        if isinstance(value, TextContent):
            content_payload = {"type": "text", "text": getattr(value, "text", "")}
            return content_payload

        return ""

    def _construct_response_data(self, output_items: List[dict]) -> OpenAIResponse:
        agent_id = AgentIdGenerator.generate(self._context)

        response_data = {
            "metadata": {},
            "agent": agent_id,
            "conversation": self._context.get_conversation_object(),
            "type": "message",
            "role": "assistant",
            "temperature": Constants.DEFAULT_TEMPERATURE,
            "top_p": Constants.DEFAULT_TOP_P,
            "user": "",
            "id": self._context.response_id,
            "created_at": self._response_created_at,
            "output": output_items,
            "parallel_tool_calls": True,
            "status": "completed",
        }
        return cast(OpenAIResponse, response_data)
