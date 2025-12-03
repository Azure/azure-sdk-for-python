# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=attribute-defined-outside-init,protected-access
# mypy: disable-error-code="call-overload,assignment,arg-type,override"
from __future__ import annotations

import datetime
import json
from typing import Any, AsyncIterable, List, Optional

from agent_framework import AgentRunResponseUpdate, BaseContent, FunctionApprovalRequestContent, FunctionResultContent
from agent_framework._types import (
    ErrorContent,
    FunctionCallContent,
    TextContent,
)

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import (
    AgentId,
    CreatedBy,
    FunctionToolCallItemResource,
    FunctionToolCallOutputItemResource,
    ItemContentOutputText,
    ItemResource,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)

from .agent_id_generator import AgentIdGenerator
from .utils.async_iter import chunk_on_change, peek


class _BaseStreamingState:
    """Base interface for streaming state handlers."""

    async def convert_contents(self, contents: AsyncIterable[BaseContent]) -> AsyncIterable[ResponseStreamEvent]:  # pylint: disable=unused-argument
        raise NotImplementedError


class _TextContentStreamingState(_BaseStreamingState):
    """State handler for text and reasoning-text content during streaming."""

    def __init__(self, parent: AgentFrameworkOutputStreamingConverter):
        self._parent = parent

    async def convert_contents(self, contents: AsyncIterable[TextContent]) -> AsyncIterable[ResponseStreamEvent]:
        item_id = self._parent.context.id_generator.generate_message_id()
        output_index = self._parent.next_output_index()

        yield ResponseOutputItemAddedEvent(
            sequence_number=self._parent.next_sequence(),
            output_index=output_index,
            item=ResponsesAssistantMessageItemResource(
                id=item_id,
                status="in_progress",
                content=[],
                created_by=self._parent._created_by,
            ),
        )

        yield ResponseContentPartAddedEvent(
            sequence_number=self._parent.next_sequence(),
            item_id=item_id,
            output_index=output_index,
            content_index=0,
            part=ItemContentOutputText(text="", annotations=[], logprobs=[]),
        )

        text = ""
        async for content in contents:
            delta = content.text
            text += delta

            yield ResponseTextDeltaEvent(
                sequence_number=self._parent.next_sequence(),
                item_id=item_id,
                output_index=output_index,
                content_index=0,
                delta=delta,
            )

        yield ResponseTextDoneEvent(
            sequence_number=self._parent.next_sequence(),
            item_id=item_id,
            output_index=output_index,
            content_index=0,
            text=text,
        )

        content_part = ItemContentOutputText(text=text, annotations=[], logprobs=[])
        yield ResponseContentPartDoneEvent(
            sequence_number=self._parent.next_sequence(),
            item_id=item_id,
            output_index=output_index,
            content_index=0,
            part=content_part,
        )

        item = ResponsesAssistantMessageItemResource(
            id=item_id, 
            status="completed", 
            content=[content_part],
            created_by=self._parent._created_by,
        )
        yield ResponseOutputItemDoneEvent(
            sequence_number=self._parent.next_sequence(),
            output_index=output_index,
            item=item,
        )

        self._parent.add_completed_output_item(item)  # pylint: disable=protected-access


class _FunctionCallStreamingState(_BaseStreamingState):
    """State handler for function_call content during streaming."""

    def __init__(self, parent: AgentFrameworkOutputStreamingConverter):
        self._parent = parent

    async def convert_contents(
            self, contents: AsyncIterable[FunctionCallContent]
        ) -> AsyncIterable[ResponseStreamEvent]:
        content_by_call_id = {}
        ids_by_call_id = {}

        async for content in contents:
            if content.call_id not in content_by_call_id:
                item_id = self._parent.context.id_generator.generate_function_call_id()
                output_index = self._parent.next_output_index()

                content_by_call_id[content.call_id] = content
                ids_by_call_id[content.call_id] = (item_id, output_index)

                yield ResponseOutputItemAddedEvent(
                    sequence_number=self._parent.next_sequence(),
                    output_index=output_index,
                    item=FunctionToolCallItemResource(
                        id=item_id,
                        status="in_progress",
                        call_id=content.call_id,
                        name=content.name,
                        arguments="",
                        created_by=self._parent._created_by,
                    ),
                )
            else:
                content_by_call_id[content.call_id] = content_by_call_id[content.call_id] + content
                item_id, output_index = ids_by_call_id[content.call_id]

                args_delta = content.arguments if isinstance(content.arguments, str) else ""
                yield ResponseFunctionCallArgumentsDeltaEvent(
                    sequence_number=self._parent.next_sequence(),
                    item_id=item_id,
                    output_index=output_index,
                    delta=args_delta,
                )

        for call_id, content in content_by_call_id.items():
            item_id, output_index = ids_by_call_id[call_id]
            args = content.arguments if isinstance(content.arguments, str) else json.dumps(content.arguments)
            yield ResponseFunctionCallArgumentsDoneEvent(
                sequence_number=self._parent.next_sequence(),
                item_id=item_id,
                output_index=output_index,
                arguments=args,
            )

            item = FunctionToolCallItemResource(
                id=item_id,
                status="completed",
                call_id=call_id,
                name=content.name,
                arguments=args,
                created_by=self._parent._created_by,
            )
            yield ResponseOutputItemDoneEvent(
                sequence_number=self._parent.next_sequence(),
                output_index=output_index,
                item=item,
            )

            self._parent.add_completed_output_item(item)  # pylint: disable=protected-access


class _FunctionCallOutputStreamingState(_BaseStreamingState):
    """Handles function_call_output items streaming (non-chunked simple output)."""

    def __init__(self, parent: AgentFrameworkOutputStreamingConverter):
        self._parent = parent

    async def convert_contents(
            self, contents: AsyncIterable[FunctionResultContent]
        ) -> AsyncIterable[ResponseStreamEvent]:
        async for content in contents:
            item_id = self._parent.context.id_generator.generate_function_output_id()
            output_index = self._parent.next_output_index()

            output = (f"{type(content.exception)}({str(content.exception)})"
                      if content.exception
                      else self._to_output(content.result))

            item = FunctionToolCallOutputItemResource(
                id=item_id,
                status="completed",
                call_id=content.call_id,
                output=output,
                created_by=self._parent._created_by,
            )

            yield ResponseOutputItemAddedEvent(
                sequence_number=self._parent.next_sequence(),
                output_index=output_index,
                item=item,
            )

            yield ResponseOutputItemDoneEvent(
                sequence_number=self._parent.next_sequence(),
                output_index=output_index,
                item=item,
            )

            self._parent.add_completed_output_item(item)  # pylint: disable=protected-access

    @classmethod
    def _to_output(cls, result: Any) -> str:
        if isinstance(result, str):
            return result
        if isinstance(result, list):
            text = []
            for item in result:
                if isinstance(item, BaseContent):
                    text.append(item.to_dict())
                else:
                    text.append(str(item))
            return json.dumps(text)
        return ""


class AgentFrameworkOutputStreamingConverter:
    """Streaming converter using content-type-specific state handlers."""

    def __init__(self, context: AgentRunContext, agent: Any = None) -> None:
        self._context = context
        self._agent = agent
        # sequence numbers must start at 0 for first emitted event
        self._sequence = -1
        self._next_output_index = -1
        self._response_id = self._context.response_id
        self._response_created_at = None
        self._completed_output_items: List[ItemResource] = []
        self._created_by: dict = {}

    def next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def next_output_index(self) -> int:
        self._next_output_index += 1
        return self._next_output_index

    def add_completed_output_item(self, item: ItemResource) -> None:
        self._completed_output_items.append(item)

    @property
    def context(self) -> AgentRunContext:
        return self._context

    async def convert(self, updates: AsyncIterable[AgentRunResponseUpdate]) -> AsyncIterable[ResponseStreamEvent]:
        self._ensure_response_started()

        created_response = self._build_response(status="in_progress")
        yield ResponseCreatedEvent(
            sequence_number=self.next_sequence(),
            response=created_response,
        )

        yield ResponseInProgressEvent(
            sequence_number=self.next_sequence(),
            response=created_response,
        )

        is_changed = (
            lambda a, b: a is not None and b is not None and a.message_id != b.message_id  # pylint: disable=unnecessary-lambda-assignment
        )
        async for group in chunk_on_change(updates, is_changed):
            has_value, first_tuple, contents_with_author = await peek(self._read_updates(group))
            if not has_value:
                continue

            first, _ = first_tuple  # Extract content from (content, author_name) tuple

            state = None
            if isinstance(first, TextContent):
                state = _TextContentStreamingState(self)
            elif isinstance(first, (FunctionCallContent, FunctionApprovalRequestContent)):
                state = _FunctionCallStreamingState(self)
            elif isinstance(first, FunctionResultContent):
                state = _FunctionCallOutputStreamingState(self)
            elif isinstance(first, ErrorContent):
                code=getattr(first, "error_code", None) or "server_error"
                message=getattr(first, "message", None) or "An error occurred"
                raise ValueError(f"ErrorContent received: code={code}, message={message}")
                # yield ResponseErrorEvent(
                #     sequence_number=self.next_sequence(),
                #     code=getattr(first, "error_code", None) or "server_error",
                #     message=getattr(first, "message", None) or "An error occurred",
                #     param="",
                # )
                # continue
            if not state:
                continue

            # Extract just the content from (content, author_name) tuples using async generator
            async def extract_contents():
                async for content, _ in contents_with_author:
                    yield content
            
            async for content in state.convert_contents(extract_contents()):
                yield content

        yield ResponseCompletedEvent(
            sequence_number=self.next_sequence(),
            response=self._build_response(status="completed"),
        )

    def _build_created_by(self, author_name: Optional[str]) -> dict:
        agent_dict = {
            "type": "agent_id",
            "name": author_name if author_name else "",
            "version": "",  # Default to empty string
        }
        
        return {
            "agent": agent_dict,
            "response_id": self._response_id,
        }

    async def _read_updates(self, updates: AsyncIterable[AgentRunResponseUpdate]) -> AsyncIterable[tuple[BaseContent, Optional[str]]]:
        current_author_name: Optional[str] = None
        
        async for update in updates:
            if not update.contents:
                continue

            # Extract author_name from update (only once on first update)
            if not self._created_by:
                author_name = getattr(update, "author_name", "") or ""
                current_author_name = author_name
                self._created_by = self._build_created_by(author_name)

            accepted_types = (TextContent,
                              FunctionCallContent,
                              FunctionApprovalRequestContent,
                              FunctionResultContent,
                              ErrorContent)
            for content in update.contents:
                if isinstance(content, accepted_types):
                    yield (content, current_author_name)

    def _ensure_response_started(self) -> None:
        if not self._response_created_at:
            self._response_created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def _build_response(self, status: str) -> OpenAIResponse:
        self._ensure_response_started()
        agent_id = AgentIdGenerator.generate(self._context)
        response_data = {
            "object": "response",
            "agent_id": agent_id,
            "id": self._response_id,
            "status": status,
            "created_at": self._response_created_at,
            "conversation": self._context.get_conversation_object(),
        }
        if status == "completed" and self._completed_output_items:
            response_data["output"] = self._completed_output_items
        return OpenAIResponse(response_data)
