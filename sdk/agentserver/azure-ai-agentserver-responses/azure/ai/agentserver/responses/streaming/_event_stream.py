# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Response event stream builders for lifecycle and output item events."""

from __future__ import annotations

from collections.abc import AsyncIterable
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterator

from .._id_generator import IdGenerator
from ..models import _generated as generated_models
from ..models._generated import AgentReference
from . import _internals
from ._builders import (
    OutputItemBuilder,
    OutputItemCodeInterpreterCallBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemMessageBuilder,
    OutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
)
from ._internals import construct_event_model
from ._state_machine import EventStreamValidator

EVENT_TYPE = generated_models.ResponseStreamEventType

# Event types whose payload is a full Response snapshot.
# Lifecycle events nest under a "response" key on the wire.
_RESPONSE_SNAPSHOT_EVENT_TYPES = _internals._RESPONSE_SNAPSHOT_EVENT_TYPES


def _resolve_conversation_param(raw: Any) -> str | None:
    """Normalize a polymorphic conversation value to a plain string ID.

    The input side of ``CreateResponse.conversation`` is ``Union[str, ConversationParam_2]``
    whereas the output side ``ResponseObject.conversation`` is always a ``ConversationReference``
    (object form ``{"id": "..."}``.  This helper extracts the string ID from whichever
    form was supplied.

    :param raw: The raw conversation value from the request (string, dict, model, or None).
    :type raw: Any
    :returns: The conversation ID string, or ``None`` if absent/empty.
    :rtype: str | None
    """
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw or None
    if isinstance(raw, dict):
        cid = raw.get("id")
        return str(cid) if cid else None
    if hasattr(raw, "id"):
        cid = raw.id
        return str(cid) if cid else None
    return None


class ResponseEventStream:  # pylint: disable=too-many-public-methods
    """Response event stream with deterministic sequence numbers."""

    def __init__(
        self,
        *,
        response_id: str | None = None,
        agent_reference: AgentReference | dict[str, Any] | None = None,
        model: str | None = None,
        request: generated_models.CreateResponse | dict[str, Any] | None = None,
        response: generated_models.ResponseObject | dict[str, Any] | None = None,
    ) -> None:
        """Initialize a new response event stream.

        :param response_id: Unique identifier for the response. Inferred from *response* if omitted.
        :type response_id: str | None
        :param agent_reference: Optional agent reference model or metadata dict.
        :type agent_reference: AgentReference | dict[str, Any] | None
        :param model: Optional model identifier to stamp on the response.
        :type model: str | None
        :param request: Optional create-response request to seed the response envelope from.
        :type request: ~azure.ai.agentserver.responses.models._generated.CreateResponse | dict[str, Any] | None
        :param response: Optional pre-existing response envelope to build upon.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject | dict[str, Any] | None
        :raises ValueError: If both *request* and *response* are provided, or if *response_id* cannot be resolved.
        """
        if request is not None and response is not None:
            raise ValueError("request and response cannot both be provided")

        request_mapping = _internals.coerce_model_mapping(request)
        response_mapping = _internals.coerce_model_mapping(response)

        resolved_response_id = response_id
        if resolved_response_id is None and response_mapping is not None:
            candidate_id = response_mapping.get("id")
            if isinstance(candidate_id, str) and candidate_id:
                resolved_response_id = candidate_id

        if not isinstance(resolved_response_id, str) or not resolved_response_id:
            raise ValueError("response_id is required")

        self._response_id = resolved_response_id

        if response_mapping is not None:
            payload = deepcopy(response_mapping)
            payload["id"] = self._response_id
            payload.setdefault("object", "response")
            payload.setdefault("output", [])
            self._response = generated_models.ResponseObject(payload)
        else:
            self._response = generated_models.ResponseObject(
                {
                    "id": self._response_id,
                    "object": "response",
                    "output": [],
                    "created_at": datetime.now(timezone.utc),
                }
            )
            if request_mapping is not None:
                for field_name in ("metadata", "background", "previous_response_id"):
                    value = request_mapping.get(field_name)
                    if value is not None:
                        setattr(self._response, field_name, deepcopy(value))
                # Normalize polymorphic conversation (str | ConversationParam_2)
                # to the response-side ConversationReference object form.
                conversation_id = _resolve_conversation_param(request_mapping.get("conversation"))
                if conversation_id is not None:
                    self._response.conversation = generated_models.ConversationReference(id=conversation_id)
                request_model = request_mapping.get("model")
                if isinstance(request_model, str) and request_model:
                    self._response.model = request_model
                request_agent_reference = request_mapping.get("agent_reference")
                if isinstance(request_agent_reference, dict):
                    self._response.agent_reference = deepcopy(request_agent_reference)  # type: ignore[assignment]

        if model is not None:
            self._response.model = model

        if agent_reference is not None:
            self._response.agent_reference = deepcopy(agent_reference)  # type: ignore[assignment]

        self._agent_reference, self._model = _internals.extract_response_fields(self._response)
        self._events: list[generated_models.ResponseStreamEvent] = []
        self._validator = EventStreamValidator()
        self._output_index = 0

    @property
    def response(self) -> generated_models.ResponseObject:
        """Return the current response envelope.

        :returns: The mutable response envelope being built by this stream.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        """
        return self._response

    def emit_queued(self) -> generated_models.ResponseStreamEvent:
        """Emit a ``response.queued`` lifecycle event.

        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = "queued"
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_QUEUED.value,
                "response": self._response_payload(),
            }
        )

    def emit_created(self, *, status: str = "in_progress") -> generated_models.ResponseStreamEvent:
        """Emit a ``response.created`` lifecycle event.

        :keyword status: Initial status to set on the response. Defaults to ``"in_progress"``.
        :keyword type status: str
        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = status  # type: ignore[assignment]
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_CREATED.value,
                "response": self._response_payload(),
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseStreamEvent:
        """Emit a ``response.in_progress`` lifecycle event.

        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = "in_progress"
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_IN_PROGRESS.value,
                "response": self._response_payload(),
            }
        )

    def emit_completed(
        self, *, usage: generated_models.ResponseUsage | dict[str, Any] | None = None
    ) -> generated_models.ResponseStreamEvent:
        """Emit a ``response.completed`` terminal lifecycle event.

        :keyword usage: Optional usage statistics to attach to the response.
        :keyword type usage: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | dict[str, Any] | None
        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = "completed"
        self._response.error = None  # type: ignore[assignment]
        self._response.incomplete_details = None  # type: ignore[assignment]
        self._set_terminal_fields(usage=usage)
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_COMPLETED.value,
                "response": self._response_payload(),
            }
        )

    def emit_failed(
        self,
        *,
        code: str | generated_models.ResponseErrorCode = "server_error",
        message: str = "An internal server error occurred.",
        usage: generated_models.ResponseUsage | dict[str, Any] | None = None,
    ) -> generated_models.ResponseStreamEvent:
        """Emit a ``response.failed`` terminal lifecycle event.

        :keyword code: Error code describing the failure.
        :keyword type code: str | ~azure.ai.agentserver.responses.models._generated.ResponseErrorCode
        :keyword message: Human-readable error message.
        :keyword type message: str
        :keyword usage: Optional usage statistics to attach to the response.
        :keyword type usage: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | dict[str, Any] | None
        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = "failed"
        self._response.incomplete_details = None  # type: ignore[assignment]
        self._response.error = generated_models.ResponseErrorInfo(
            {
                "code": _internals.enum_value(code),
                "message": message,
            }
        )
        self._set_terminal_fields(usage=usage)
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_FAILED.value,
                "response": self._response_payload(),
            }
        )

    def emit_incomplete(
        self,
        *,
        reason: str | None = None,
        usage: generated_models.ResponseUsage | dict[str, Any] | None = None,
    ) -> generated_models.ResponseStreamEvent:
        """Emit a ``response.incomplete`` terminal lifecycle event.

        :keyword reason: Optional reason for incompleteness.
        :keyword type reason: str | ~azure.ai.agentserver.responses.models._generated.ResponseIncompleteReason
                                | None
        :keyword usage: Optional usage statistics to attach to the response.
        :keyword type usage: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | dict[str, Any]
                                | None
        :returns: The emitted event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        self._response.status = "incomplete"
        self._response.error = None  # type: ignore[assignment]
        if reason is None:
            self._response.incomplete_details = None  # type: ignore[assignment]
        else:
            self._response.incomplete_details = generated_models.ResponseIncompleteDetails(
                {
                    "reason": _internals.enum_value(reason),
                }
            )
        self._set_terminal_fields(usage=usage)
        return self.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_INCOMPLETE.value,
                "response": self._response_payload(),
            }
        )

    def add_output_item(self, item_id: str) -> OutputItemBuilder:
        """Add a generic output item and return its builder.

        :param item_id: Unique identifier for the output item.
        :type item_id: str
        :returns: A builder for emitting added/done events for the output item.
        :rtype: OutputItemBuilder
        :raises TypeError: If *item_id* is None.
        :raises ValueError: If *item_id* is empty or has an invalid format.
        """
        if item_id is None:
            raise TypeError("item_id must not be None")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("item_id must be a non-empty string")

        is_valid_id, error = IdGenerator.is_valid(item_id)
        if not is_valid_id:
            raise ValueError(f"invalid item_id '{item_id}': {error}")

        output_index = self._output_index
        self._output_index += 1
        return OutputItemBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_message(self) -> OutputItemMessageBuilder:
        """Add a message output item and return its scoped builder.

        :returns: A builder for emitting message content, text deltas, and lifecycle events.
        :rtype: OutputItemMessageBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_message_item_id(self._response_id)
        return OutputItemMessageBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_function_call(self, name: str, call_id: str) -> OutputItemFunctionCallBuilder:
        """Add a function-call output item and return its scoped builder.

        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        :returns: A builder for emitting function-call argument deltas and lifecycle events.
        :rtype: OutputItemFunctionCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_function_call_item_id(self._response_id)
        return OutputItemFunctionCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            name=name,
            call_id=call_id,
        )

    def add_output_item_function_call_output(self, call_id: str) -> OutputItemFunctionCallOutputBuilder:
        """Add a function-call-output item and return its scoped builder.

        :param call_id: The call ID of the function call this output belongs to.
        :type call_id: str
        :returns: A builder for emitting function-call output lifecycle events.
        :rtype: OutputItemFunctionCallOutputBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_function_call_output_item_id(self._response_id)
        return OutputItemFunctionCallOutputBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            call_id=call_id,
        )

    def add_output_item_reasoning_item(self) -> OutputItemReasoningItemBuilder:
        """Add a reasoning output item and return its scoped builder.

        :returns: A builder for emitting reasoning summary parts and lifecycle events.
        :rtype: OutputItemReasoningItemBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_reasoning_item_id(self._response_id)
        return OutputItemReasoningItemBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_file_search_call(self) -> OutputItemFileSearchCallBuilder:
        """Add a file-search tool call output item and return its scoped builder.

        :returns: A builder for emitting file-search call lifecycle events.
        :rtype: OutputItemFileSearchCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_file_search_call_item_id(self._response_id)
        return OutputItemFileSearchCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_web_search_call(self) -> OutputItemWebSearchCallBuilder:
        """Add a web-search tool call output item and return its scoped builder.

        :returns: A builder for emitting web-search call lifecycle events.
        :rtype: OutputItemWebSearchCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_web_search_call_item_id(self._response_id)
        return OutputItemWebSearchCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_code_interpreter_call(self) -> OutputItemCodeInterpreterCallBuilder:
        """Add a code-interpreter tool call output item and return its scoped builder.

        :returns: A builder for emitting code-interpreter call lifecycle events.
        :rtype: OutputItemCodeInterpreterCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_code_interpreter_call_item_id(self._response_id)
        return OutputItemCodeInterpreterCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_image_gen_call(self) -> OutputItemImageGenCallBuilder:
        """Add an image-generation tool call output item and return its scoped builder.

        :returns: A builder for emitting image-generation call lifecycle events.
        :rtype: OutputItemImageGenCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_image_gen_call_item_id(self._response_id)
        return OutputItemImageGenCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_mcp_call(self, server_label: str, name: str) -> OutputItemMcpCallBuilder:
        """Add an MCP tool call output item and return its scoped builder.

        :param server_label: Label identifying the MCP server.
        :type server_label: str
        :param name: Name of the MCP tool being called.
        :type name: str
        :returns: A builder for emitting MCP call argument deltas and lifecycle events.
        :rtype: OutputItemMcpCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_mcp_call_item_id(self._response_id)
        return OutputItemMcpCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            server_label=server_label,
            name=name,
        )

    def add_output_item_mcp_list_tools(self, server_label: str) -> OutputItemMcpListToolsBuilder:
        """Add an MCP list-tools output item and return its scoped builder.

        :param server_label: Label identifying the MCP server.
        :type server_label: str
        :returns: A builder for emitting MCP list-tools lifecycle events.
        :rtype: OutputItemMcpListToolsBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_mcp_list_tools_item_id(self._response_id)
        return OutputItemMcpListToolsBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            server_label=server_label,
        )

    def add_output_item_custom_tool_call(self, call_id: str, name: str) -> OutputItemCustomToolCallBuilder:
        """Add a custom tool call output item and return its scoped builder.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param name: Name of the custom tool being called.
        :type name: str
        :returns: A builder for emitting custom tool call input deltas and lifecycle events.
        :rtype: OutputItemCustomToolCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_custom_tool_call_item_id(self._response_id)
        return OutputItemCustomToolCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            call_id=call_id,
            name=name,
        )

    def events(self) -> list[generated_models.ResponseStreamEvent]:
        """Return copies of all events emitted so far as typed model instances.

        :returns: A list of ``ResponseStreamEvent`` model instances.
        :rtype: list[~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent]
        """
        return [construct_event_model(event.as_dict()) for event in self._events]

    def emit_event(self, event: dict[str, Any]) -> generated_models.ResponseStreamEvent:
        """Emit a single event, applying defaults and validating the stream.

        Accepts a **wire-format** dict (no ``"payload"`` wrapper), constructs
        a typed ``ResponseStreamEvent`` model instance via polymorphic
        deserialization, stamps defaults and sequence number, stores the
        model, and returns it.

        :param event: A wire-format event dict.
        :type event: dict[str, Any]
        :returns: The typed event model instance.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
        """
        candidate = deepcopy(event)
        # Stamp sequence number before model construction
        candidate["sequence_number"] = len(self._events)

        # Construct typed model via polymorphic deserialization
        model = construct_event_model(candidate)

        # Apply response-level defaults to lifecycle events
        _internals.apply_common_defaults(
            [model], response_id=self._response_id, agent_reference=self._agent_reference, model=self._model
        )
        # Track completed output items on the response envelope
        _internals.track_completed_output_item(self._response, model)

        self._events.append(model)
        self._validator.validate_next(model)
        return model

    # ---- Generator convenience methods (S-056/S-057) ----
    # Output-item convenience generators that encapsulate the full lifecycle.
    # Names mirror the add_* factories with the add_ prefix removed.

    def output_item_message(self, text: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a text message output item.

        Emits output_item.added, content_part.added, output_text.delta,
        output_text.done, content_part.done, and output_item.done.

        :param text: The text content of the message.
        :type text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        message = self.add_output_item_message()
        yield message.emit_added()
        yield from message.text_content(text)
        yield message.emit_done()

    def output_item_function_call(self, name: str, call_id: str, arguments: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a function call output item.

        Emits output_item.added, function_call_arguments.delta,
        function_call_arguments.done, and output_item.done.

        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        :param arguments: The function call arguments as a string.
        :type arguments: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        fc = self.add_output_item_function_call(name=name, call_id=call_id)
        yield fc.emit_added()
        yield from fc.arguments(arguments)
        yield fc.emit_done()

    def output_item_function_call_output(self, call_id: str, output: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a function call output item.

        Emits output_item.added and output_item.done.

        :param call_id: The call ID of the function call this output belongs to.
        :type call_id: str
        :param output: The output value for the function call.
        :type output: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        fco = self.add_output_item_function_call_output(call_id=call_id)
        yield fco.emit_added(output)
        yield fco.emit_done(output)

    def output_item_reasoning_item(self, summary_text: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a reasoning output item.

        Emits output_item.added, reasoning_summary_part.added,
        reasoning_summary_text.delta, reasoning_summary_text.done,
        reasoning_summary_part.done, and output_item.done.

        :param summary_text: The reasoning summary text.
        :type summary_text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        item = self.add_output_item_reasoning_item()
        yield item.emit_added()
        yield from item.summary_part(summary_text)
        yield item.emit_done()

    # ---- Async generator convenience methods (S-058) ----
    # Async variants with AsyncIterable[str] support for real-time delta streaming.

    async def aoutput_item_message(self, text: str | AsyncIterable[str]) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`output_item_message` with streaming support.

        When *text* is a string, emits the same events as the sync variant.
        When *text* is an async iterable of string chunks, emits one
        ``output_text.delta`` per chunk in real time, enabling token-by-token
        streaming from upstream LLMs.

        :param text: Complete text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        if isinstance(text, str):
            for event in self.output_item_message(text):
                yield event
            return
        message = self.add_output_item_message()
        yield message.emit_added()
        async for event in message.atext_content(text):
            yield event
        yield message.emit_done()

    async def aoutput_item_function_call(
        self, name: str, call_id: str, arguments: str | AsyncIterable[str]
    ) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`output_item_function_call` with streaming support.

        When *arguments* is a string, emits the same events as the sync variant.
        When *arguments* is an async iterable of string chunks, emits one
        ``function_call_arguments.delta`` per chunk in real time.

        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        :param arguments: Complete arguments string or async iterable of chunks.
        :type arguments: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        if isinstance(arguments, str):
            for event in self.output_item_function_call(name, call_id, arguments):
                yield event
            return
        fc = self.add_output_item_function_call(name=name, call_id=call_id)
        yield fc.emit_added()
        async for event in fc.aarguments(arguments):
            yield event
        yield fc.emit_done()

    async def aoutput_item_function_call_output(self, call_id: str, output: str) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`output_item_function_call_output`.

        :param call_id: The call ID of the function call this output belongs to.
        :type call_id: str
        :param output: The output value for the function call.
        :type output: str
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        for event in self.output_item_function_call_output(call_id, output):
            yield event

    async def aoutput_item_reasoning_item(
        self, summary_text: str | AsyncIterable[str]
    ) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`output_item_reasoning_item` with streaming support.

        When *summary_text* is a string, emits the same events as the sync variant.
        When *summary_text* is an async iterable of string chunks, emits one
        ``reasoning_summary_text.delta`` per chunk in real time.

        :param summary_text: Complete summary text or async iterable of chunks.
        :type summary_text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        if isinstance(summary_text, str):
            for event in self.output_item_reasoning_item(summary_text):
                yield event
            return
        item = self.add_output_item_reasoning_item()
        yield item.emit_added()
        async for event in item.asummary_part(summary_text):
            yield event
        yield item.emit_done()

    # ---- Private helpers ----

    def _response_payload(self) -> dict[str, Any]:
        """Serialize the current response envelope to a plain dict.

        :returns: A materialized dict representation of the response.
        :rtype: dict[str, Any]
        """
        return _internals.materialize_generated_payload(self._response.as_dict())

    def with_output_item_defaults(self, item: dict[str, Any]) -> dict[str, Any]:
        """Stamp an output item dict with response-level defaults.

        :param item: The item dict to stamp.
        :type item: dict[str, Any]
        :returns: A deep copy of the item with ``response_id`` and ``agent_reference`` defaults applied.
        :rtype: dict[str, Any]
        """
        stamped = deepcopy(item)
        if "response_id" not in stamped or stamped["response_id"] is None:
            stamped["response_id"] = self._response_id
        if "agent_reference" not in stamped or stamped["agent_reference"] is None:
            stamped["agent_reference"] = self._agent_reference
        return stamped

    def _set_terminal_fields(self, *, usage: generated_models.ResponseUsage | dict[str, Any] | None) -> None:
        """Set terminal fields on the response envelope (completed_at, usage).

        :keyword usage: Optional usage statistics to attach.
        :keyword type usage: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | dict[str, Any] | None
        :rtype: None
        """
        # B6: completed_at is non-null only for completed status
        if self._response.status == "completed":
            self._response.completed_at = datetime.now(timezone.utc)
        else:
            self._response.completed_at = None  # type: ignore[assignment]
        self._response.usage = _internals.coerce_usage(usage)
