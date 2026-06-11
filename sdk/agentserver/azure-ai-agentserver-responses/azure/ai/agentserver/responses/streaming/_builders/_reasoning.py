# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Reasoning-related builders: summary parts and reasoning output items."""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, AsyncIterator, Iterator, cast

from ...models import _generated as generated_models
from ._base import BaseOutputItemBuilder, BuilderLifecycleState

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class ReasoningSummaryPartBuilder:
    """Scoped builder for a single reasoning summary part."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, summary_index: int, item_id: str) -> None:
        """Initialize the reasoning summary part builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of the parent output item.
        :type output_index: int
        :param summary_index: Zero-based index of this summary part.
        :type summary_index: int
        :param item_id: Identifier of the parent output item.
        :type item_id: str
        """
        self._stream = stream
        self._output_index = output_index
        self._summary_index = summary_index
        self._item_id = item_id
        self._final_text: str | None = None
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def final_text(self) -> str | None:
        """Return the final summary text, or ``None`` if not yet done.

        :returns: The final text string.
        :rtype: str | None
        """
        return self._final_text

    @property
    def summary_index(self) -> int:
        """Return the zero-based summary part index.

        :returns: The summary index.
        :rtype: int
        """
        return self._summary_index

    def emit_added(self) -> generated_models.ResponseReasoningSummaryPartAddedEvent:
        """Emit a ``reasoning_summary_part.added`` event.

        :returns: The emitted event.
        :rtype: ResponseReasoningSummaryPartAddedEvent
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return cast(
            generated_models.ResponseReasoningSummaryPartAddedEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_ADDED.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "part": {"type": "summary_text", "text": ""},
                }
            ),
        )

    def emit_text_delta(self, text: str) -> generated_models.ResponseReasoningSummaryTextDeltaEvent:
        """Emit a reasoning summary text delta event.

        :param text: The incremental summary text fragment.
        :type text: str
        :returns: The emitted event.
        :rtype: ResponseReasoningSummaryTextDeltaEvent
        """
        return cast(
            generated_models.ResponseReasoningSummaryTextDeltaEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DELTA.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "delta": text,
                }
            ),
        )

    def emit_text_done(self, final_text: str) -> generated_models.ResponseReasoningSummaryTextDoneEvent:
        """Emit a reasoning summary text done event.

        :param final_text: The final, complete summary text.
        :type final_text: str
        :returns: The emitted event.
        :rtype: ResponseReasoningSummaryTextDoneEvent
        """
        self._final_text = final_text
        return cast(
            generated_models.ResponseReasoningSummaryTextDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "text": final_text,
                }
            ),
        )

    def emit_done(self) -> generated_models.ResponseReasoningSummaryPartDoneEvent:
        """Emit a ``reasoning_summary_part.done`` event.

        :returns: The emitted event.
        :rtype: ResponseReasoningSummaryPartDoneEvent
        :raises ValueError: If the builder is not in ``ADDED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        return cast(
            generated_models.ResponseReasoningSummaryPartDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "part": {"type": "summary_text", "text": self._final_text or ""},
                }
            ),
        )


class OutputItemReasoningItemBuilder(BaseOutputItemBuilder):
    """Scoped builder for reasoning output items with summary part support."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        """Initialize the reasoning output item builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._summary_index = 0
        self._summary_builders: list[ReasoningSummaryPartBuilder] = []

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for this reasoning item.

        :returns: The emitted event.
        :rtype: ResponseOutputItemAddedEvent
        """
        return self._emit_added({"type": "reasoning", "id": self._item_id, "summary": [], "status": "in_progress"})

    def add_summary_part(self) -> ReasoningSummaryPartBuilder:
        """Create and return a reasoning summary part builder.

        :returns: A new summary part builder scoped to this reasoning item.
        :rtype: ReasoningSummaryPartBuilder
        """
        summary_index = self._summary_index
        self._summary_index += 1
        part = ReasoningSummaryPartBuilder(self._stream, self._output_index, summary_index, self._item_id)
        self._summary_builders.append(part)
        return part

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this reasoning item.

        :returns: The emitted event.
        :rtype: ResponseOutputItemDoneEvent
        """
        summary_list = [{"type": "summary_text", "text": b.final_text or ""} for b in self._summary_builders]
        return self._emit_done(
            {
                "type": "reasoning",
                "id": self._item_id,
                "summary": summary_list,
                "status": "completed",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def summary_part(self, text: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a reasoning summary part.

        Creates the sub-builder, emits ``reasoning_summary_part.added``,
        ``reasoning_summary_text.delta``, ``reasoning_summary_text.done``,
        and ``reasoning_summary_part.done``.

        :param text: The complete summary text.
        :type text: str
        :returns: An iterator of events.
        :rtype: Iterator[ResponseStreamEvent]
        """
        part = self.add_summary_part()
        yield part.emit_added()
        yield part.emit_text_delta(text)
        yield part.emit_text_done(text)
        yield part.emit_done()

    async def asummary_part(
        self,
        text: str | AsyncIterable[str],
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`summary_part` with streaming support.

        When *text* is a string, behaves identically to :meth:`summary_part`.
        When *text* is an async iterable of string chunks, emits one
        ``reasoning_summary_text.delta`` per chunk in real time (S-055),
        then ``reasoning_summary_text.done`` with the accumulated text.

        :param text: Complete summary text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in self.summary_part(text):
                yield event
            return
        part = self.add_summary_part()
        yield part.emit_added()
        accumulated: list[str] = []
        async for chunk in text:
            accumulated.append(chunk)
            yield part.emit_text_delta(chunk)
        final = "".join(accumulated)
        yield part.emit_text_done(final)
        yield part.emit_done()
