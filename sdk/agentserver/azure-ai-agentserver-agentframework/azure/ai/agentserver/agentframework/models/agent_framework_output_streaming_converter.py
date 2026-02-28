# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=attribute-defined-outside-init,protected-access
# mypy: disable-error-code="call-overload,assignment,arg-type"
from __future__ import annotations

import datetime
import json
import uuid
from collections.abc import AsyncIterable
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Union, cast

from agent_framework import AgentResponseUpdate, Content, ResponseStream

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import (
    FunctionToolCallItemResource,
    FunctionToolCallOutputItemResource,
    ItemContentOutputText,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseErrorEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)

from .agent_id_generator import generate_agent_id
from .human_in_the_loop_helper import HumanInTheLoopHelper

logger = get_logger()


class _BaseStreamingState:
    """Base interface for streaming state handlers."""

    def prework(self, ctx: Any) -> List[ResponseStreamEvent]:  # pylint: disable=unused-argument
        return []

    def convert_content(self, ctx: Any, content) -> List[ResponseStreamEvent]:  # pylint: disable=unused-argument
        raise NotImplementedError

    def afterwork(self, ctx: Any) -> List[ResponseStreamEvent]:  # pylint: disable=unused-argument
        return []


class _TextContentStreamingState(_BaseStreamingState):
    """State handler for text and reasoning-text content during streaming."""

    def __init__(self, context: AgentRunContext) -> None:
        self.context = context
        self.item_id = None
        self.output_index = None
        self.text_buffer = ""
        self.text_part_started = False

    def prework(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if self.item_id is not None:
            return events

        # Start a new assistant message item (in_progress)
        self.item_id = self.context.id_generator.generate_message_id()
        self.output_index = ctx._next_output_index  # pylint: disable=protected-access
        ctx._next_output_index += 1

        message_item = ResponsesAssistantMessageItemResource(
            id=self.item_id,
            status="in_progress",
            content=[],
        )

        events.append(
            ResponseOutputItemAddedEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=message_item,
            )
        )

        if not self.text_part_started:
            empty_part = ItemContentOutputText(text="", annotations=[], logprobs=[])
            events.append(
                ResponseContentPartAddedEvent(
                    sequence_number=ctx.next_sequence(),
                    item_id=self.item_id,
                    output_index=self.output_index,
                    content_index=0,
                    part=empty_part,
                )
            )
            self.text_part_started = True
        return events

    def convert_content(self, ctx: Any, content: Content) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        match content.type:
            case "text":
                delta = content.text or ""
            case "text_reasoning":
                delta = getattr(content, "reasoning", "") or ""
            case _:
                delta = getattr(content, "text", None) or getattr(content, "reasoning", "") or ""

        # buffer accumulated text
        self.text_buffer += delta

        # emit delta event for text
        assert self.item_id is not None, "Text state not initialized: missing item_id"
        assert self.output_index is not None, "Text state not initialized: missing output_index"
        events.append(
            ResponseTextDeltaEvent(
                sequence_number=ctx.next_sequence(),
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=0,
                delta=delta,
            )
        )
        return events

    def afterwork(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if not self.item_id:
            return events

        full_text = self.text_buffer
        assert self.item_id is not None and self.output_index is not None
        events.append(
            ResponseTextDoneEvent(
                sequence_number=ctx.next_sequence(),
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=0,
                text=full_text,
            )
        )
        final_part = ItemContentOutputText(text=full_text, annotations=[], logprobs=[])
        events.append(
            ResponseContentPartDoneEvent(
                sequence_number=ctx.next_sequence(),
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=0,
                part=final_part,
            )
        )
        completed_item = ResponsesAssistantMessageItemResource(
            id=self.item_id, status="completed", content=[final_part]
        )
        events.append(
            ResponseOutputItemDoneEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=completed_item,
            )
        )
        ctx._last_completed_text = full_text  # pylint: disable=protected-access
        # store for final response
        ctx._completed_output_items.append(
            {
                "id": self.item_id,
                "type": "message",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": full_text,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
                "role": "assistant",
            }
        )
        # reset state
        self.item_id = None
        self.output_index = None
        self.text_buffer = ""
        self.text_part_started = False
        return events


class _FunctionCallStreamingState(_BaseStreamingState):
    """State handler for function_call content during streaming."""

    def __init__(self, context: AgentRunContext, *, hitl_helper: Optional[HumanInTheLoopHelper] = None) -> None:
        self.context = context
        self.hitl_helper = hitl_helper
        self.item_id = None
        self.output_index = None
        self.call_id = None
        self.name = None
        self.args_buffer = ""
        self.requires_approval = False
        self.approval_request_id: Optional[str] = None

    def prework(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if self.item_id is not None:
            return events
        # initialize function-call item
        self.item_id = self.context.id_generator.generate_function_call_id()
        self.output_index = ctx._next_output_index
        ctx._next_output_index += 1

        self.call_id = self.call_id or str(uuid.uuid4())
        function_item = FunctionToolCallItemResource(
            id=self.item_id,
            status="in_progress",
            call_id=self.call_id,
            name=self.name or "",
            arguments="",
        )
        events.append(
            ResponseOutputItemAddedEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=function_item,
            )
        )
        return events

    def convert_content(self, ctx: Any, content: Content) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        # record identifiers (once available)
        self.name = getattr(content, "name", None) or self.name or ""
        self.call_id = getattr(content, "call_id", None) or self.call_id or str(uuid.uuid4())

        args_delta = content.arguments if isinstance(content.arguments, str) else json.dumps(content.arguments)
        args_delta = args_delta or ""
        self.args_buffer += args_delta
        assert self.item_id is not None and self.output_index is not None
        for ch in args_delta:
            events.append(
                ResponseFunctionCallArgumentsDeltaEvent(
                    sequence_number=ctx.next_sequence(),
                    item_id=self.item_id,
                    output_index=self.output_index,
                    delta=ch,
                )
            )

        # finalize if arguments are detected to be complete
        is_done = bool(
            getattr(content, "is_final", False)
            or getattr(content, "final", False)
            or getattr(content, "done", False)
            or getattr(content, "arguments_final", False)
            or getattr(content, "arguments_done", False)
            or getattr(content, "finish", False)
        )
        if not is_done and self.args_buffer:
            try:
                json.loads(self.args_buffer)
                is_done = True
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        if is_done:
            events.append(
                ResponseFunctionCallArgumentsDoneEvent(
                    sequence_number=ctx.next_sequence(),
                    item_id=self.item_id,
                    output_index=self.output_index,
                    arguments=self.args_buffer,
                )
            )
            events.extend(self.afterwork(ctx))
        return events

    def afterwork(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if not self.item_id:
            return events
        assert self.call_id is not None
        done_item = FunctionToolCallItemResource(
            id=self.item_id,
            status="completed",
            call_id=self.call_id,
            name=self.name or "",
            arguments=self.args_buffer,
        )
        assert self.output_index is not None
        events.append(
            ResponseOutputItemDoneEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=done_item,
            )
        )
        # store for final response
        ctx._completed_output_items.append(
            {
                "id": self.item_id,
                "type": "function_call",
                "call_id": self.call_id,
                "name": self.name or "",
                "arguments": self.args_buffer,
                "status": "requires_approval" if self.requires_approval else "completed",
                "requires_approval": self.requires_approval,
                "approval_request_id": self.approval_request_id,
            }
        )
        # reset
        self.item_id = None
        self.output_index = None
        self.args_buffer = ""
        self.call_id = None
        self.name = None
        self.requires_approval = False
        self.approval_request_id = None
        return events


class _FunctionCallOutputStreamingState(_BaseStreamingState):
    """Handles function_call_output items streaming (non-chunked simple output)."""

    def __init__(
        self,
        context: AgentRunContext,
        call_id: Optional[str] = None,
        output: Optional[List[str]] = None,
    ) -> None:
        # Avoid mutable default argument (Ruff B006)
        self.context = context
        self.item_id = None
        self.output_index = None
        self.call_id = call_id
        self.output = output if output is not None else []

    def prework(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if self.item_id is not None:
            return events
        self.item_id = self.context.id_generator.generate_function_output_id()
        self.output_index = ctx._next_output_index
        ctx._next_output_index += 1

        self.call_id = self.call_id or str(uuid.uuid4())
        item = FunctionToolCallOutputItemResource(
            id=self.item_id,
            status="in_progress",
            call_id=self.call_id,
            output="",
        )
        events.append(
            ResponseOutputItemAddedEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=item,
            )
        )
        return events

    def convert_content(self, ctx: Any, content: Any) -> List[ResponseStreamEvent]:  # no delta events for now
        events: List[ResponseStreamEvent] = []
        # treat entire output as final
        raw = getattr(content, "result", None)
        result: List[Union[str, Dict[str, Any]]] = []
        match raw:
            case str():
                result = [raw] if raw else [str(self.output)]
            case list():
                result = [self._coerce_result_text(item) for item in raw]
        self.output = json.dumps(result) if len(result) > 0 else ""

        events.extend(self.afterwork(ctx))
        return events

    def _coerce_result_text(self, value: Any) -> Union[str, Dict[str, Any]]:
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
                return {"type": "text", "text": getattr(value, "text", "")}
            case _:
                return ""

    def afterwork(self, ctx: Any) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if not self.item_id:
            return events
        # Ensure types conform: call_id must be str (guarantee non-None) and output is a single string
        str_call_id = self.call_id or ""
        single_output: str = cast(str, self.output[0]) if self.output else ""
        done_item = FunctionToolCallOutputItemResource(
            id=self.item_id,
            status="completed",
            call_id=str_call_id,
            output=single_output,
        )
        assert self.output_index is not None
        events.append(
            ResponseOutputItemDoneEvent(
                sequence_number=ctx.next_sequence(),
                output_index=self.output_index,
                item=done_item,
            )
        )
        ctx._completed_output_items.append(
            {
                "id": self.item_id,
                "type": "function_call_output",
                "status": "completed",
                "call_id": self.call_id,
                "output": self.output,
            }
        )
        self.item_id = None
        self.output_index = None
        return events


class AgentFrameworkOutputStreamingConverter:
    """Streaming converter using content-type-specific state handlers."""

    def __init__(self, context: AgentRunContext, *, hitl_helper: Optional[HumanInTheLoopHelper] = None) -> None:
        self._context = context
        self._hitl_helper = hitl_helper
        # sequence numbers must start at 0 for first emitted event
        self._sequence = 0
        self._response_id = None
        self._response_created_at = None
        self._next_output_index = 0
        self._last_completed_text = ""
        self._active_state: Optional[_BaseStreamingState] = None
        self._active_kind = None  # "text" | "function_call" | "error"
        # accumulate completed output items for final response
        self._completed_output_items: List[dict] = []

    def _ensure_response_started(self) -> None:
        if not self._response_id:
            self._response_id = self._context.response_id
        if not self._response_created_at:
            self._response_created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def _switch_state(self, kind: str) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if self._active_state and self._active_kind != kind:
            events.extend(self._active_state.afterwork(self))
            self._active_state = None
            self._active_kind = None

        if self._active_state is None:
            match kind:
                case "text":
                    self._active_state = _TextContentStreamingState(self._context)
                case "function_call":
                    self._active_state = _FunctionCallStreamingState(
                        self._context,
                        hitl_helper=self._hitl_helper,
                    )
                case "function_call_output":
                    self._active_state = _FunctionCallOutputStreamingState(self._context)
                case _:
                    self._active_state = None
            self._active_kind = kind
            if self._active_state:
                events.extend(self._active_state.prework(self))
        return events

    def transform_output_for_streaming(self, update: AgentResponseUpdate) -> List[ResponseStreamEvent]:
        logger.debug(
            "Transforming streaming update with %d contents",
            len(update.contents or []),
        )
        self._ensure_response_started()
        events: List[ResponseStreamEvent] = []

        if update.contents:
            for i, content in enumerate(update.contents):
                logger.debug("Processing content %d: %s", i, content.type)
                match content.type:
                    case "text" | "text_reasoning":
                        events.extend(self._switch_state("text"))
                        if isinstance(self._active_state, _TextContentStreamingState):
                            events.extend(self._active_state.convert_content(self, content))
                    case "function_call":
                        events.extend(self._switch_state("function_call"))
                        if isinstance(self._active_state, _FunctionCallStreamingState):
                            events.extend(self._active_state.convert_content(self, content))
                    case "function_result":
                        events.extend(self._switch_state("function_call_output"))
                        if isinstance(self._active_state, _FunctionCallOutputStreamingState):
                            call_id = getattr(content, "call_id", None)
                            if call_id:
                                self._active_state.call_id = call_id
                            events.extend(self._active_state.convert_content(self, content))
                    case "function_approval_request":
                        events.extend(self._switch_state("function_call"))
                        if isinstance(self._active_state, _FunctionCallStreamingState):
                            self._active_state.requires_approval = True
                            self._active_state.approval_request_id = content.id
                            function_call_content = content.function_call
                            if self._hitl_helper is not None:
                                converted_hitl = self._hitl_helper.convert_user_input_request_content(content)
                                function_call_content = SimpleNamespace(
                                    call_id=converted_hitl.get("call_id", ""),
                                    name=converted_hitl.get("name", ""),
                                    arguments=converted_hitl.get("arguments", ""),
                                )
                            if function_call_content is not None:
                                events.extend(self._active_state.convert_content(self, function_call_content))
                    case "error":
                        events.extend(self._switch_state("error"))
                        events.append(
                            ResponseErrorEvent(
                                sequence_number=self.next_sequence(),
                                code=getattr(content, "error_code", None) or "server_error",
                                message=getattr(content, "message", None) or "An error occurred",
                                param="",
                            )
                        )
                    case "usage":
                        # Usage metadata — not emitted as a stream event
                        logger.debug("Skipping usage content (input/output token counts)")
                    case _:
                        logger.warning("Unhandled content type in streaming: %s", content.type)
        return events

    def finalize_last_content(self) -> List[ResponseStreamEvent]:
        events: List[ResponseStreamEvent] = []
        if self._active_state:
            events.extend(self._active_state.afterwork(self))
            self._active_state = None
            self._active_kind = None
        return events

    def build_response(self, status: str) -> OpenAIResponse:
        self._ensure_response_started()
        agent_id = generate_agent_id(self._context)
        response_data = {
            "object": "response",
            "agent_id": agent_id,
            "id": self._response_id,
            "status": status,
            "created_at": self._response_created_at,
        }
        if status == "completed" and self._completed_output_items:
            response_data["output"] = self._completed_output_items
        return OpenAIResponse(response_data)

    # High-level helpers to emit lifecycle events for streaming
    def initial_events(self) -> List[ResponseStreamEvent]:
        """
        Emit ResponseCreatedEvent and an initial ResponseInProgressEvent.

        :return: List of initial response stream events.
        :rtype: List[ResponseStreamEvent]
        """
        self._ensure_response_started()
        events: List[ResponseStreamEvent] = []
        created_response = self.build_response(status="in_progress")
        events.append(
            ResponseCreatedEvent(
                sequence_number=self.next_sequence(),
                response=created_response,
            )
        )
        events.append(
            ResponseInProgressEvent(
                sequence_number=self.next_sequence(),
                response=self.build_response(status="in_progress"),
            )
        )
        return events

    def completion_events(self) -> List[ResponseStreamEvent]:
        """
        Finalize any active content and emit a single ResponseCompletedEvent.

        :return: List of completion response stream events.
        :rtype: List[ResponseStreamEvent]
        """
        self._ensure_response_started()
        events: List[ResponseStreamEvent] = []
        events.extend(self.finalize_last_content())
        completed_response = self.build_response(status="completed")
        events.append(
            ResponseCompletedEvent(
                sequence_number=self.next_sequence(),
                response=completed_response,
            )
        )
        return events

    def convert(self, updates: ResponseStream[AgentResponseUpdate, Any]) -> ResponseStream[ResponseStreamEvent, Any]:
        async def converted_events() -> AsyncIterable[ResponseStreamEvent]:
            for event in self.initial_events():
                yield event
            async for update in updates:
                for event in self.transform_output_for_streaming(update):
                    yield event
            for event in self.completion_events():
                yield event

        async def finalize_updates() -> None:
            await updates.get_final_response()

        return ResponseStream(converted_events()).with_cleanup_hook(finalize_updates)
