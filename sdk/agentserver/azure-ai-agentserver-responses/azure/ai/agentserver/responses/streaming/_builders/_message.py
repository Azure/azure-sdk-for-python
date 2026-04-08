# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Message-related builders: text content, refusal content, and message output item."""

from __future__ import annotations

from collections.abc import AsyncIterable
from copy import deepcopy
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator

from ._base import EVENT_TYPE, BaseOutputItemBuilder, BuilderLifecycleState

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class TextContentBuilder:
    """Scoped builder for a text content part within an output message item."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, content_index: int, item_id: str) -> None:
        """Initialize the text content builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of the parent output item.
        :type output_index: int
        :param content_index: Zero-based index of this content part.
        :type content_index: int
        :param item_id: Identifier of the parent output item.
        :type item_id: str
        """
        self._stream = stream
        self._output_index = output_index
        self._content_index = content_index
        self._item_id = item_id
        self._final_text: str | None = None
        self._delta_fragments: list[str] = []
        self._annotation_index = 0
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def final_text(self) -> str | None:
        """Return the final merged text, or ``None`` if not yet done.

        :returns: The final text string.
        :rtype: str | None
        """
        return self._final_text

    @property
    def content_index(self) -> int:
        """Return the zero-based content part index.

        :returns: The content index.
        :rtype: int
        """
        return self._content_index

    def emit_added(self) -> dict[str, Any]:
        """Emit a ``content_part.added`` event for this text content.

        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_CONTENT_PART_ADDED.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {"type": "output_text", "text": "", "annotations": [], "logprobs": []},
                },
            }
        )

    def emit_delta(self, text: str) -> dict[str, Any]:
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_delta in '{self._lifecycle_state.value}' state")
        self._delta_fragments.append(text)
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_TEXT_DELTA.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "delta": text,
                    "logprobs": [],
                },
            }
        )

    def emit_done(self, final_text: str | None = None) -> dict[str, Any]:
        """Emit a text done event with the merged final text.

        :param final_text: Optional override for the final text; uses merged deltas if ``None``.
        :type final_text: str | None
        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        :raises ValueError: If the builder is not in ``ADDED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        merged_text = "".join(self._delta_fragments)
        if not merged_text and final_text is not None:
            merged_text = final_text
        self._final_text = merged_text
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_TEXT_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "text": merged_text,
                    "logprobs": [],
                },
            }
        )

    def emit_annotation_added(self, annotation: dict[str, Any]) -> dict[str, Any]:
        """Emit a text annotation added event.

        :param annotation: The annotation dict to attach.
        :type annotation: dict[str, Any]
        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        """
        annotation_index = self._annotation_index
        self._annotation_index += 1
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "annotation_index": annotation_index,
                    "annotation": deepcopy(annotation),
                },
            }
        )


class RefusalContentBuilder:
    """Scoped builder for a refusal content part within an output message item."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, content_index: int, item_id: str) -> None:
        """Initialize the refusal content builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of the parent output item.
        :type output_index: int
        :param content_index: Zero-based index of this content part.
        :type content_index: int
        :param item_id: Identifier of the parent output item.
        :type item_id: str
        """
        self._stream = stream
        self._output_index = output_index
        self._content_index = content_index
        self._item_id = item_id
        self._final_refusal: str | None = None
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def final_refusal(self) -> str | None:
        """Return the final refusal text, or ``None`` if not yet done.

        :returns: The final refusal string.
        :rtype: str | None
        """
        return self._final_refusal

    @property
    def content_index(self) -> int:
        """Return the zero-based content part index.

        :returns: The content index.
        :rtype: int
        """
        return self._content_index

    def emit_added(self) -> dict[str, Any]:
        """Emit a ``content_part.added`` event for this refusal content.

        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_CONTENT_PART_ADDED.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {"type": "refusal", "refusal": ""},
                },
            }
        )

    def emit_delta(self, text: str) -> dict[str, Any]:
        """Emit a refusal delta event.

        :param text: The incremental refusal text fragment.
        :type text: str
        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        """
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REFUSAL_DELTA.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "delta": text,
                },
            }
        )

    def emit_done(self, final_refusal: str) -> dict[str, Any]:
        """Emit a refusal done event.

        :param final_refusal: The final, complete refusal text.
        :type final_refusal: str
        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        :raises ValueError: If the builder is not in ``ADDED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        self._final_refusal = final_refusal
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REFUSAL_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "refusal": final_refusal,
                },
            }
        )


class OutputItemMessageBuilder(BaseOutputItemBuilder):
    """Scoped builder for a message output item in stream mode."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
    ) -> None:
        """Initialize the message output item builder.

        :param stream: The parent event stream.
        :type stream: ResponseEventStream
        :param output_index: Zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        """
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._content_index = 0
        self._completed_contents: list[dict[str, Any]] = []

    def emit_added(self) -> dict[str, Any]:
        """Emit an ``output_item.added`` event for this message item.

        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        """
        return self._emit_added(
            {
                "type": "message",
                "id": self._item_id,
                "role": "assistant",
                "content": [],
                "status": "in_progress",
            }
        )

    def add_text_content(self) -> TextContentBuilder:
        """Create and return a text content part builder.

        :returns: A new text content builder scoped to this message.
        :rtype: TextContentBuilder
        """
        content_index = self._content_index
        self._content_index += 1
        return TextContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )

    def add_refusal_content(self) -> RefusalContentBuilder:
        """Create and return a refusal content part builder.

        :returns: A new refusal content builder scoped to this message.
        :rtype: RefusalContentBuilder
        """
        content_index = self._content_index
        self._content_index += 1
        return RefusalContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )

    def emit_content_done(self, content_builder: TextContentBuilder | RefusalContentBuilder) -> dict[str, Any]:
        """Emit a ``content_part.done`` event for a completed content part.

        :param content_builder: The content builder whose final state to emit.
        :type content_builder: TextContentBuilder | RefusalContentBuilder
        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        """
        if isinstance(content_builder, TextContentBuilder):
            part = {
                "type": "output_text",
                "text": content_builder.final_text or "",
                "annotations": [],
                "logprobs": [],
            }
            content_index = content_builder.content_index
        else:
            part = {
                "type": "refusal",
                "refusal": content_builder.final_refusal or "",
            }
            content_index = content_builder.content_index

        self._completed_contents.append(deepcopy(part))
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_CONTENT_PART_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": content_index,
                    "part": deepcopy(part),
                },
            }
        )

    def emit_done(self) -> dict[str, Any]:
        """Emit an ``output_item.done`` event for this message item.

        :returns: The emitted event dict.
        :rtype: dict[str, Any]
        :raises ValueError: If no content parts have been completed.
        """
        if len(self._completed_contents) == 0:
            raise ValueError("message output item requires at least one content part before emit_done")
        return self._emit_done(
            {
                "type": "message",
                "id": self._item_id,
                "role": "assistant",
                "content": deepcopy(self._completed_contents),
                "status": "completed",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def text_content(self, text: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a text content part.

        Creates the sub-builder, emits ``content_part.added``,
        ``output_text.delta``, ``output_text.done``, and ``content_part.done``.

        :param text: The complete text content.
        :type text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        tc = self.add_text_content()
        yield tc.emit_added()
        yield tc.emit_delta(text)
        yield tc.emit_done(text)
        yield self.emit_content_done(tc)

    async def atext_content(self, text: str | AsyncIterable[str]) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`text_content` with streaming support.

        When *text* is a string, behaves identically to :meth:`text_content`.
        When *text* is an async iterable of string chunks, emits one
        ``output_text.delta`` per chunk in real time (S-055), then
        ``output_text.done`` with the accumulated text.

        :param text: Complete text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        if isinstance(text, str):
            for event in self.text_content(text):
                yield event
            return
        tc = self.add_text_content()
        yield tc.emit_added()
        async for chunk in text:
            yield tc.emit_delta(chunk)
        yield tc.emit_done()
        yield self.emit_content_done(tc)

    def refusal_content(self, text: str) -> Iterator[dict[str, Any]]:
        """Yield the full lifecycle for a refusal content part.

        Creates the sub-builder, emits ``content_part.added``,
        ``refusal.delta``, ``refusal.done``, and ``content_part.done``.

        :param text: The complete refusal text.
        :type text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[dict[str, Any]]
        """
        rc = self.add_refusal_content()
        yield rc.emit_added()
        yield rc.emit_delta(text)
        yield rc.emit_done(text)
        yield self.emit_content_done(rc)

    async def arefusal_content(self, text: str | AsyncIterable[str]) -> AsyncIterator[dict[str, Any]]:
        """Async variant of :meth:`refusal_content` with streaming support.

        When *text* is a string, behaves identically to :meth:`refusal_content`.
        When *text* is an async iterable of string chunks, emits one
        ``refusal.delta`` per chunk in real time (S-055), then
        ``refusal.done`` with the accumulated text.

        :param text: Complete refusal text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        if isinstance(text, str):
            for event in self.refusal_content(text):
                yield event
            return
        rc = self.add_refusal_content()
        yield rc.emit_added()
        accumulated: list[str] = []
        async for chunk in text:
            accumulated.append(chunk)
            yield rc.emit_delta(chunk)
        yield rc.emit_done("".join(accumulated))
        yield self.emit_content_done(rc)
