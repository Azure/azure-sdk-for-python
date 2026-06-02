# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tool call builders: file search, web search, code interpreter, image gen, MCP, and custom tools."""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, AsyncIterator, Iterator, cast

from ...models import _generated as generated_models
from ._base import BaseOutputItemBuilder, _require_non_empty

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class OutputItemFileSearchCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for file search tool call events."""

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for a file search call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "file_search_call",
                "id": self._item_id,
                "status": "in_progress",
                "queries": [],
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseFileSearchCallInProgressEvent:
        """Emit a file-search in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseFileSearchCallInProgressEvent
        """
        return cast(
            generated_models.ResponseFileSearchCallInProgressEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS.value
            ),
        )

    def emit_searching(self) -> generated_models.ResponseFileSearchCallSearchingEvent:
        """Emit a file-search searching state event.

        :returns: The emitted event dict.
        :rtype: ResponseFileSearchCallSearchingEvent
        """
        return cast(
            generated_models.ResponseFileSearchCallSearchingEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_SEARCHING.value
            ),
        )

    def emit_completed(self) -> generated_models.ResponseFileSearchCallCompletedEvent:
        """Emit a file-search completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseFileSearchCallCompletedEvent
        """
        return cast(
            generated_models.ResponseFileSearchCallCompletedEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_COMPLETED.value
            ),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this file search call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done({"type": "file_search_call", "id": self._item_id, "status": "completed", "queries": []})


class OutputItemWebSearchCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for web search tool call events."""

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for a web search call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added({"type": "web_search_call", "id": self._item_id, "status": "in_progress", "action": {}})

    def emit_in_progress(self) -> generated_models.ResponseWebSearchCallInProgressEvent:
        """Emit a web-search in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseWebSearchCallInProgressEvent
        """
        return cast(
            generated_models.ResponseWebSearchCallInProgressEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS.value
            ),
        )

    def emit_searching(self) -> generated_models.ResponseWebSearchCallSearchingEvent:
        """Emit a web-search searching state event.

        :returns: The emitted event dict.
        :rtype: ResponseWebSearchCallSearchingEvent
        """
        return cast(
            generated_models.ResponseWebSearchCallSearchingEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_SEARCHING.value
            ),
        )

    def emit_completed(self) -> generated_models.ResponseWebSearchCallCompletedEvent:
        """Emit a web-search completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseWebSearchCallCompletedEvent
        """
        return cast(
            generated_models.ResponseWebSearchCallCompletedEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_COMPLETED.value
            ),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this web search call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done({"type": "web_search_call", "id": self._item_id, "status": "completed", "action": {}})


class OutputItemCodeInterpreterCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for code interpreter tool call events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        """Initialize the code-interpreter call builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._final_code: str | None = None

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for a code interpreter call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "code_interpreter_call",
                "id": self._item_id,
                "status": "in_progress",
                "container_id": "",
                "code": "",
                "outputs": [],
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseCodeInterpreterCallInProgressEvent:
        """Emit a code-interpreter in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseCodeInterpreterCallInProgressEvent
        """
        return cast(
            generated_models.ResponseCodeInterpreterCallInProgressEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS.value
            ),
        )

    def emit_interpreting(self) -> generated_models.ResponseCodeInterpreterCallInterpretingEvent:
        """Emit a code-interpreter interpreting state event.

        :returns: The emitted event dict.
        :rtype: ResponseCodeInterpreterCallInterpretingEvent
        """
        return cast(
            generated_models.ResponseCodeInterpreterCallInterpretingEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING.value
            ),
        )

    def emit_code_delta(self, delta: str) -> generated_models.ResponseCodeInterpreterCallCodeDeltaEvent:
        """Emit a code-interpreter code delta event.

        :param delta: The incremental code fragment.
        :type delta: str
        :returns: The emitted event dict.
        :rtype: ResponseCodeInterpreterCallCodeDeltaEvent
        """
        return cast(
            generated_models.ResponseCodeInterpreterCallCodeDeltaEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA.value,
                extra_payload={"delta": delta},
            ),
        )

    def emit_code_done(self, code: str) -> generated_models.ResponseCodeInterpreterCallCodeDoneEvent:
        """Emit a code-interpreter code done event.

        :param code: The final, complete code string.
        :type code: str
        :returns: The emitted event dict.
        :rtype: ResponseCodeInterpreterCallCodeDoneEvent
        """
        self._final_code = code
        return cast(
            generated_models.ResponseCodeInterpreterCallCodeDoneEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE.value,
                extra_payload={"code": code},
            ),
        )

    def emit_completed(self) -> generated_models.ResponseCodeInterpreterCallCompletedEvent:
        """Emit a code-interpreter completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseCodeInterpreterCallCompletedEvent
        """
        return cast(
            generated_models.ResponseCodeInterpreterCallCompletedEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_COMPLETED.value
            ),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this code interpreter call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "code_interpreter_call",
                "id": self._item_id,
                "status": "completed",
                "container_id": "",
                "code": self._final_code or "",
                "outputs": [],
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def code(self, code_text: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the code delta and code done events.

        Emits ``code_interpreter_call.code.delta`` followed by
        ``code_interpreter_call.code.done``.

        :param code_text: The complete code string.
        :type code_text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[ResponseStreamEvent]
        """
        yield self.emit_code_delta(code_text)
        yield self.emit_code_done(code_text)

    async def acode(self, code_text: str | AsyncIterable[str]) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`code` with streaming support.

        When *code_text* is a string, behaves identically to :meth:`code`.
        When *code_text* is an async iterable of string chunks, emits one
        ``code_interpreter_call.code.delta`` per chunk in real time (S-055),
        then ``code_interpreter_call.code.done`` with the accumulated text.

        :param code_text: Complete code string or async iterable of chunks.
        :type code_text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(code_text, str):
            for event in self.code(code_text):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in code_text:
            accumulated.append(chunk)
            yield self.emit_code_delta(chunk)
        yield self.emit_code_done("".join(accumulated))


class OutputItemImageGenCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for image generation tool call events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        """Initialize the image-generation call builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._partial_image_index = 0

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for an image generation call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "image_generation_call",
                "id": self._item_id,
                "status": "in_progress",
                "result": "",
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseImageGenCallInProgressEvent:
        """Emit an image-generation in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseImageGenCallInProgressEvent
        """
        return cast(
            generated_models.ResponseImageGenCallInProgressEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS.value
            ),
        )

    def emit_generating(self) -> generated_models.ResponseImageGenCallGeneratingEvent:
        """Emit an image-generation generating state event.

        :returns: The emitted event dict.
        :rtype: ResponseImageGenCallGeneratingEvent
        """
        return cast(
            generated_models.ResponseImageGenCallGeneratingEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_GENERATING.value
            ),
        )

    def emit_partial_image(self, partial_image_b64: str) -> generated_models.ResponseImageGenCallPartialImageEvent:
        """Emit a partial image event with base64-encoded image data.

        :param partial_image_b64: Base64-encoded partial image data.
        :type partial_image_b64: str
        :returns: The emitted event dict.
        :rtype: ResponseImageGenCallPartialImageEvent
        """
        partial_index = self._partial_image_index
        self._partial_image_index += 1
        return cast(
            generated_models.ResponseImageGenCallPartialImageEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE.value,
                extra_payload={"partial_image_index": partial_index, "partial_image_b64": partial_image_b64},
            ),
        )

    def emit_completed(self) -> generated_models.ResponseImageGenCallCompletedEvent:
        """Emit an image-generation completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseImageGenCallCompletedEvent
        """
        return cast(
            generated_models.ResponseImageGenCallCompletedEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_COMPLETED.value
            ),
        )

    def emit_done(self, result: str) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this image generation call.

        :param result: The base64-encoded image result.
        :type result: str
        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "image_generation_call",
                "id": self._item_id,
                "status": "completed",
                "result": result,
            }
        )


class OutputItemMcpCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for MCP tool call events."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        server_label: str,
        name: str,
    ) -> None:
        """Initialize the MCP call builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        :param server_label: Label identifying the MCP server.
        :type server_label: str
        :param name: Name of the MCP tool being called.
        :type name: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._server_label = _require_non_empty(server_label, "server_label")
        self._name = _require_non_empty(name, "name")
        self._final_arguments: str | None = None
        self._terminal_status: str | None = None

    @property
    def server_label(self) -> str:
        """Return the MCP server label.

        :returns: The server label.
        :rtype: str
        """
        return self._server_label

    @property
    def name(self) -> str:
        """Return the MCP tool name.

        :returns: The tool name.
        :rtype: str
        """
        return self._name

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for an MCP call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "mcp_call",
                "id": self._item_id,
                "server_label": self._server_label,
                "name": self._name,
                "arguments": "",
                "status": "in_progress",
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseMCPCallInProgressEvent:
        """Emit an MCP call in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPCallInProgressEvent
        """
        return cast(
            generated_models.ResponseMCPCallInProgressEvent,
            self._emit_item_state_event(generated_models.ResponseStreamEventType.RESPONSE_MCP_CALL_IN_PROGRESS.value),
        )

    def emit_arguments_delta(self, delta: str) -> generated_models.ResponseMCPCallArgumentsDeltaEvent:
        """Emit an MCP call arguments delta event.

        :param delta: The incremental arguments text fragment.
        :type delta: str
        :returns: The emitted event dict.
        :rtype: ResponseMCPCallArgumentsDeltaEvent
        """
        return cast(
            generated_models.ResponseMCPCallArgumentsDeltaEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA.value,
                extra_payload={"delta": delta},
            ),
        )

    def emit_arguments_done(self, arguments: str) -> generated_models.ResponseMCPCallArgumentsDoneEvent:
        """Emit an MCP call arguments done event.

        :param arguments: The final, complete arguments string.
        :type arguments: str
        :returns: The emitted event dict.
        :rtype: ResponseMCPCallArgumentsDoneEvent
        """
        self._final_arguments = arguments
        return cast(
            generated_models.ResponseMCPCallArgumentsDoneEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE.value,
                extra_payload={"arguments": arguments},
            ),
        )

    def emit_completed(self) -> generated_models.ResponseMCPCallCompletedEvent:
        """Emit an MCP call completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPCallCompletedEvent
        """
        self._terminal_status = "completed"
        return cast(
            generated_models.ResponseMCPCallCompletedEvent,
            self._emit_item_state_event(generated_models.ResponseStreamEventType.RESPONSE_MCP_CALL_COMPLETED.value),
        )

    def emit_failed(self) -> generated_models.ResponseMCPCallFailedEvent:
        """Emit an MCP call failed state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPCallFailedEvent
        """
        self._terminal_status = "failed"
        return cast(
            generated_models.ResponseMCPCallFailedEvent,
            self._emit_item_state_event(generated_models.ResponseStreamEventType.RESPONSE_MCP_CALL_FAILED.value),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this MCP call.

        The ``status`` field reflects the most recent terminal state event
        (``emit_completed`` or ``emit_failed``). Defaults to ``"completed"``
        if neither was called.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "mcp_call",
                "id": self._item_id,
                "server_label": self._server_label,
                "name": self._name,
                "arguments": self._final_arguments or "",
                "status": self._terminal_status or "completed",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def arguments(self, args: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the argument delta and done events.

        Emits ``mcp_call_arguments.delta`` followed by
        ``mcp_call_arguments.done``.

        :param args: The complete arguments string.
        :type args: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[ResponseStreamEvent]
        """
        yield self.emit_arguments_delta(args)
        yield self.emit_arguments_done(args)

    async def aarguments(self, args: str | AsyncIterable[str]) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`arguments` with streaming support.

        When *args* is a string, behaves identically to :meth:`arguments`.
        When *args* is an async iterable of string chunks, emits one
        ``mcp_call_arguments.delta`` per chunk in real time (S-055),
        then ``mcp_call_arguments.done`` with the accumulated text.

        :param args: Complete arguments string or async iterable of chunks.
        :type args: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(args, str):
            for event in self.arguments(args):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in args:
            accumulated.append(chunk)
            yield self.emit_arguments_delta(chunk)
        yield self.emit_arguments_done("".join(accumulated))


class OutputItemMcpListToolsBuilder(BaseOutputItemBuilder):
    """Scoped builder for MCP list-tools lifecycle events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str, server_label: str) -> None:
        """Initialize the MCP list-tools builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        :param server_label: Label identifying the MCP server.
        :type server_label: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._server_label = _require_non_empty(server_label, "server_label")

    @property
    def server_label(self) -> str:
        """Return the MCP server label.

        :returns: The server label.
        :rtype: str
        """
        return self._server_label

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for MCP list-tools.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "mcp_list_tools",
                "id": self._item_id,
                "server_label": self._server_label,
                "tools": [],
            }
        )

    def emit_in_progress(self) -> generated_models.ResponseMCPListToolsInProgressEvent:
        """Emit an MCP list-tools in-progress state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPListToolsInProgressEvent
        """
        return cast(
            generated_models.ResponseMCPListToolsInProgressEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS.value
            ),
        )

    def emit_completed(self) -> generated_models.ResponseMCPListToolsCompletedEvent:
        """Emit an MCP list-tools completed state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPListToolsCompletedEvent
        """
        return cast(
            generated_models.ResponseMCPListToolsCompletedEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_COMPLETED.value
            ),
        )

    def emit_failed(self) -> generated_models.ResponseMCPListToolsFailedEvent:
        """Emit an MCP list-tools failed state event.

        :returns: The emitted event dict.
        :rtype: ResponseMCPListToolsFailedEvent
        """
        return cast(
            generated_models.ResponseMCPListToolsFailedEvent,
            self._emit_item_state_event(generated_models.ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_FAILED.value),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for MCP list-tools.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "mcp_list_tools",
                "id": self._item_id,
                "server_label": self._server_label,
                "tools": [],
            }
        )


class OutputItemCustomToolCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for custom tool call events."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        call_id: str,
        name: str,
    ) -> None:
        """Initialize the custom tool call builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param name: Name of the custom tool being called.
        :type name: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._call_id = _require_non_empty(call_id, "call_id")
        self._name = _require_non_empty(name, "name")
        self._final_input: str | None = None

    @property
    def call_id(self) -> str:
        """Return the tool call identifier.

        :returns: The call ID.
        :rtype: str
        """
        return self._call_id

    @property
    def name(self) -> str:
        """Return the custom tool name.

        :returns: The tool name.
        :rtype: str
        """
        return self._name

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for a custom tool call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "custom_tool_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "input": "",
            }
        )

    def emit_input_delta(self, delta: str) -> generated_models.ResponseCustomToolCallInputDeltaEvent:
        """Emit a custom tool call input delta event.

        :param delta: The incremental input text fragment.
        :type delta: str
        :returns: The emitted event dict.
        :rtype: ResponseCustomToolCallInputDeltaEvent
        """
        return cast(
            generated_models.ResponseCustomToolCallInputDeltaEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA.value,
                extra_payload={"delta": delta},
            ),
        )

    def emit_input_done(self, input_text: str) -> generated_models.ResponseCustomToolCallInputDoneEvent:
        """Emit a custom tool call input done event.

        :param input_text: The final, complete input text.
        :type input_text: str
        :returns: The emitted event dict.
        :rtype: ResponseCustomToolCallInputDoneEvent
        """
        self._final_input = input_text
        return cast(
            generated_models.ResponseCustomToolCallInputDoneEvent,
            self._emit_item_state_event(
                generated_models.ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE.value,
                extra_payload={"input": input_text},
            ),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this custom tool call.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "custom_tool_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "input": self._final_input or "",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def input(self, input_text: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the input delta and input done events.

        Emits ``custom_tool_call_input.delta`` followed by
        ``custom_tool_call_input.done``.

        :param input_text: The complete input text.
        :type input_text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[ResponseStreamEvent]
        """
        yield self.emit_input_delta(input_text)
        yield self.emit_input_done(input_text)

    async def ainput(self, input_text: str | AsyncIterable[str]) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`input` with streaming support.

        When *input_text* is a string, behaves identically to :meth:`input`.
        When *input_text* is an async iterable of string chunks, emits one
        ``custom_tool_call_input.delta`` per chunk in real time (S-055),
        then ``custom_tool_call_input.done`` with the accumulated text.

        :param input_text: Complete input text or async iterable of chunks.
        :type input_text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(input_text, str):
            for event in self.input(input_text):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in input_text:
            accumulated.append(chunk)
            yield self.emit_input_delta(chunk)
        yield self.emit_input_done("".join(accumulated))
