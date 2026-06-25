# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Function call builders: function-call and function-call-output output items."""

from __future__ import annotations

from collections.abc import AsyncIterable
from copy import deepcopy
from typing import TYPE_CHECKING, AsyncIterator, Iterator, cast

from ...models import _generated as generated_models
from ._base import BaseOutputItemBuilder, _require_non_empty

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class OutputItemFunctionCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for a function-call output item in stream mode."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        name: str,
        call_id: str,
    ) -> None:
        """Initialize the function-call output item builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._name = _require_non_empty(name, "name")
        self._call_id = _require_non_empty(call_id, "call_id")
        self._final_arguments: str | None = None

    @property
    def name(self) -> str:
        """Return the function name.

        :returns: The function name.
        :rtype: str
        """
        return self._name

    @property
    def call_id(self) -> str:
        """Return the function call identifier.

        :returns: The call ID.
        :rtype: str
        """
        return self._call_id

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for this function call.

        :returns: The emitted event.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "function_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "arguments": "",
                "status": "in_progress",
            }
        )

    def emit_arguments_delta(self, delta: str) -> generated_models.ResponseFunctionCallArgumentsDeltaEvent:
        """Emit a function-call arguments delta event.

        :param delta: The incremental arguments text fragment.
        :type delta: str
        :returns: The emitted event.
        :rtype: ResponseFunctionCallArgumentsDeltaEvent
        """
        return cast(
            generated_models.ResponseFunctionCallArgumentsDeltaEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "delta": delta,
                }
            ),
        )

    def emit_arguments_done(self, arguments: str) -> generated_models.ResponseFunctionCallArgumentsDoneEvent:
        """Emit a function-call arguments done event.

        :param arguments: The final, complete arguments string.
        :type arguments: str
        :returns: The emitted event.
        :rtype: ResponseFunctionCallArgumentsDoneEvent
        """
        self._final_arguments = arguments
        return cast(
            generated_models.ResponseFunctionCallArgumentsDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "name": self._name,
                    "arguments": arguments,
                }
            ),
        )

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this function call.

        :returns: The emitted event.
        :rtype: ResponseOutputItemDoneEvent
        """
        return self._emit_done(
            {
                "type": "function_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "arguments": self._final_arguments or "",
                "status": "completed",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def arguments(self, args: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the argument delta and done events.

        Emits ``function_call_arguments.delta`` followed by
        ``function_call_arguments.done``.

        :param args: The complete arguments string.
        :type args: str
        :returns: An iterator of events.
        :rtype: Iterator[ResponseStreamEvent]
        """
        yield self.emit_arguments_delta(args)
        yield self.emit_arguments_done(args)

    async def aarguments(self, args: str | AsyncIterable[str]) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`arguments` with streaming support.

        When *args* is a string, behaves identically to :meth:`arguments`.
        When *args* is an async iterable of string chunks, emits one
        ``function_call_arguments.delta`` per chunk in real time (S-055),
        then ``function_call_arguments.done`` with the accumulated text.

        :param args: Complete arguments string or async iterable of chunks.
        :type args: str | AsyncIterable[str]
        :returns: An async iterator of events.
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


class OutputItemFunctionCallOutputBuilder(BaseOutputItemBuilder):
    """Scoped builder for a function-call-output item in stream mode."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        call_id: str,
    ) -> None:
        """Initialize the function-call-output item builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        :param call_id: The call ID of the function call this output belongs to.
        :type call_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._call_id = _require_non_empty(call_id, "call_id")
        self._final_output: (
            str
            | list[
                generated_models.InputTextContentParam
                | generated_models.InputImageContentParamAutoParam
                | generated_models.InputFileContentParam
            ]
            | None
        ) = None

    @property
    def call_id(self) -> str:
        """Return the function call identifier.

        :returns: The call ID.
        :rtype: str
        """
        return self._call_id

    def emit_added(
        self,
        output: str
        | list[
            generated_models.InputTextContentParam
            | generated_models.InputImageContentParamAutoParam
            | generated_models.InputFileContentParam
        ]
        | None = None,
    ) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for this function-call output.

        :param output: Optional initial output value.
        :type output: str | list[InputTextContentParam | InputImageContentParamAutoParam | InputFileContentParam] | None
        :returns: The emitted event.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added(
            {
                "type": "function_call_output",
                "id": self._item_id,
                "call_id": self._call_id,
                "output": deepcopy(output) if output is not None else "",
                "status": "in_progress",
            }
        )

    def emit_done(
        self,
        output: str
        | list[
            generated_models.InputTextContentParam
            | generated_models.InputImageContentParamAutoParam
            | generated_models.InputFileContentParam
        ]
        | None = None,
    ) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this function-call output.

        :param output: Optional final output value. Uses previously set output if ``None``.
        :type output: str | list[InputTextContentParam | InputImageContentParamAutoParam | InputFileContentParam] | None
        :returns: The emitted event.
        :rtype: ResponseOutputItemDoneEvent
        """
        if output is not None:
            self._final_output = deepcopy(output)

        return self._emit_done(
            {
                "type": "function_call_output",
                "id": self._item_id,
                "call_id": self._call_id,
                "output": deepcopy(self._final_output) if self._final_output is not None else "",
                "status": "completed",
            }
        )
