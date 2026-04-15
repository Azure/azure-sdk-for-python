# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Message-related builders: text content, refusal content, and message output item."""

from __future__ import annotations

from collections.abc import AsyncIterable
from copy import deepcopy
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator, cast

from ...models import _generated as generated_models
from ._base import BaseOutputItemBuilder, BuilderLifecycleState

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class TextContentBuilder:
    """Scoped builder for a text content part within an output message item.

    Lifecycle: ``emit_added()`` → ``emit_delta()`` (0+) → ``emit_text_done()``
    → ``emit_annotation_added()`` (0+) → ``emit_done()``.
    """

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
        self._text_done = False
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

    def emit_added(self) -> generated_models.ResponseContentPartAddedEvent:
        """Emit a ``content_part.added`` event for this text content.

        :returns: The emitted event dict.
        :rtype: ResponseContentPartAddedEvent
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return cast(
            generated_models.ResponseContentPartAddedEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_CONTENT_PART_ADDED.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {"type": "output_text", "text": "", "annotations": [], "logprobs": []},
                }
            ),
        )

    def emit_delta(self, text: str) -> generated_models.ResponseTextDeltaEvent:
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_delta in '{self._lifecycle_state.value}' state")
        self._delta_fragments.append(text)
        return cast(
            generated_models.ResponseTextDeltaEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "delta": text,
                    "logprobs": [],
                }
            ),
        )

    def emit_text_done(self, final_text: str | None = None) -> generated_models.ResponseTextDoneEvent:
        """Emit an ``output_text.done`` event with the merged final text.

        Call this after all deltas have been emitted. After this, you may
        call ``emit_annotation_added()`` and then ``emit_done()``.

        :param final_text: Optional override for the final text; uses merged deltas if ``None``.
        :type final_text: str | None
        :returns: The emitted event dict.
        :rtype: ResponseTextDoneEvent
        :raises ValueError: If the builder is not in ``ADDED`` state or text is already done.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_text_done in '{self._lifecycle_state.value}' state")
        if self._text_done:
            raise ValueError("emit_text_done has already been called")
        self._text_done = True
        merged_text = "".join(self._delta_fragments)
        if not merged_text and final_text is not None:
            merged_text = final_text
        self._final_text = merged_text
        return cast(
            generated_models.ResponseTextDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "text": merged_text,
                    "logprobs": [],
                }
            ),
        )

    def emit_done(self) -> generated_models.ResponseContentPartDoneEvent:
        """Emit a ``content_part.done`` event, closing this content part.

        Must be called after ``emit_text_done()``.

        :returns: The emitted event dict.
        :rtype: ResponseContentPartDoneEvent
        :raises ValueError: If text has not been finalized or builder is already done.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        if not self._text_done:
            raise ValueError("must call emit_text_done() before emit_done()")
        self._lifecycle_state = BuilderLifecycleState.DONE
        return cast(
            generated_models.ResponseContentPartDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_CONTENT_PART_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {
                        "type": "output_text",
                        "text": self._final_text or "",
                        "annotations": [],
                        "logprobs": [],
                    },
                }
            ),
        )

    def emit_annotation_added(
        self, annotation: generated_models.Annotation
    ) -> generated_models.ResponseOutputTextAnnotationAddedEvent:
        """Emit a text annotation added event.

        :param annotation: The annotation to attach—a typed
            :class:`~azure.ai.agentserver.responses.models.Annotation` subclass.
        :type annotation: Annotation
        :returns: The emitted event dict.
        :rtype: ResponseOutputTextAnnotationAddedEvent
        """
        annotation_index = self._annotation_index
        self._annotation_index += 1
        annotation_payload = deepcopy(annotation.as_dict())
        return cast(
            generated_models.ResponseOutputTextAnnotationAddedEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "annotation_index": annotation_index,
                    "annotation": annotation_payload,
                }
            ),
        )


class RefusalContentBuilder:
    """Scoped builder for a refusal content part within an output message item.

    Lifecycle: ``emit_added()`` → ``emit_delta()`` (0+) → ``emit_refusal_done()``
    → ``emit_done()``.
    """

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
        self._refusal_done = False
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

    def emit_added(self) -> generated_models.ResponseContentPartAddedEvent:
        """Emit a ``content_part.added`` event for this refusal content.

        :returns: The emitted event dict.
        :rtype: ResponseContentPartAddedEvent
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return cast(
            generated_models.ResponseContentPartAddedEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_CONTENT_PART_ADDED.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {"type": "refusal", "refusal": ""},
                }
            ),
        )

    def emit_delta(self, text: str) -> generated_models.ResponseRefusalDeltaEvent:
        """Emit a refusal delta event.

        :param text: The incremental refusal text fragment.
        :type text: str
        :returns: The emitted event dict.
        :rtype: ResponseRefusalDeltaEvent
        """
        return cast(
            generated_models.ResponseRefusalDeltaEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REFUSAL_DELTA.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "delta": text,
                }
            ),
        )

    def emit_refusal_done(self, final_refusal: str) -> generated_models.ResponseRefusalDoneEvent:
        """Emit a ``refusal.done`` event.

        Call this after all deltas have been emitted and before ``emit_done()``.

        :param final_refusal: The final, complete refusal text.
        :type final_refusal: str
        :returns: The emitted event dict.
        :rtype: ResponseRefusalDoneEvent
        :raises ValueError: If the builder is not in ``ADDED`` state or refusal is already done.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_refusal_done in '{self._lifecycle_state.value}' state")
        if self._refusal_done:
            raise ValueError("emit_refusal_done has already been called")
        self._refusal_done = True
        self._final_refusal = final_refusal
        return cast(
            generated_models.ResponseRefusalDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_REFUSAL_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "refusal": final_refusal,
                }
            ),
        )

    def emit_done(self) -> generated_models.ResponseContentPartDoneEvent:
        """Emit a ``content_part.done`` event, closing this content part.

        Must be called after ``emit_refusal_done()``.

        :returns: The emitted event dict.
        :rtype: ResponseContentPartDoneEvent
        :raises ValueError: If refusal has not been finalized or builder is already done.
        """
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        if not self._refusal_done:
            raise ValueError("must call emit_refusal_done() before emit_done()")
        self._lifecycle_state = BuilderLifecycleState.DONE
        return cast(
            generated_models.ResponseContentPartDoneEvent,
            self._stream._emit_event(  # pylint: disable=protected-access
                {
                    "type": generated_models.ResponseStreamEventType.RESPONSE_CONTENT_PART_DONE.value,
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "content_index": self._content_index,
                    "part": {
                        "type": "refusal",
                        "refusal": self._final_refusal or "",
                    },
                }
            ),
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
        self._content_builders: list[TextContentBuilder | RefusalContentBuilder] = []

    def emit_added(self) -> generated_models.ResponseOutputItemAddedEvent:
        """Emit an ``output_item.added`` event for this message item.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemAddedEvent
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
        tc = TextContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )
        self._content_builders.append(tc)
        return tc

    def add_refusal_content(self) -> RefusalContentBuilder:
        """Create and return a refusal content part builder.

        :returns: A new refusal content builder scoped to this message.
        :rtype: RefusalContentBuilder
        """
        content_index = self._content_index
        self._content_index += 1
        rc = RefusalContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )
        self._content_builders.append(rc)
        return rc

    def emit_done(self) -> generated_models.ResponseOutputItemDoneEvent:
        """Emit an ``output_item.done`` event for this message item.

        Builds the content list from the tracked child content builders.

        :returns: The emitted event dict.
        :rtype: ResponseOutputItemDoneEvent
        :raises ValueError: If no content parts have been created.
        """
        if len(self._content_builders) == 0:
            raise ValueError("message output item requires at least one content part before emit_done")
        content_list: list[dict[str, Any]] = []
        for builder in self._content_builders:
            if isinstance(builder, TextContentBuilder):
                content_list.append(
                    {
                        "type": "output_text",
                        "text": builder.final_text or "",
                        "annotations": [],
                        "logprobs": [],
                    }
                )
            else:
                content_list.append(
                    {
                        "type": "refusal",
                        "refusal": builder.final_refusal or "",
                    }
                )
        return self._emit_done(
            {
                "type": "message",
                "id": self._item_id,
                "role": "assistant",
                "content": content_list,
                "status": "completed",
            }
        )

    # ---- Sub-item convenience generators (S-053) ----

    def text_content(self, text: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a text content part.

        Creates the sub-builder, emits ``content_part.added``,
        ``output_text.delta``, ``output_text.done``, and ``content_part.done``.

        :param text: The complete text content.
        :type text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[ResponseStreamEvent]
        """
        tc = self.add_text_content()
        yield tc.emit_added()
        yield tc.emit_delta(text)
        yield tc.emit_text_done(text)
        yield tc.emit_done()

    async def atext_content(
        self, text: str | AsyncIterable[str]
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`text_content` with streaming support.

        When *text* is a string, behaves identically to :meth:`text_content`.
        When *text* is an async iterable of string chunks, emits one
        ``output_text.delta`` per chunk in real time (S-055), then
        ``output_text.done`` with the accumulated text.

        :param text: Complete text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in self.text_content(text):
                yield event
            return
        tc = self.add_text_content()
        yield tc.emit_added()
        async for chunk in text:
            yield tc.emit_delta(chunk)
        yield tc.emit_text_done()
        yield tc.emit_done()

    def refusal_content(self, text: str) -> Iterator[generated_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a refusal content part.

        Creates the sub-builder, emits ``content_part.added``,
        ``refusal.delta``, ``refusal.done``, and ``content_part.done``.

        :param text: The complete refusal text.
        :type text: str
        :returns: An iterator of event dicts.
        :rtype: Iterator[ResponseStreamEvent]
        """
        rc = self.add_refusal_content()
        yield rc.emit_added()
        yield rc.emit_delta(text)
        yield rc.emit_refusal_done(text)
        yield rc.emit_done()

    async def arefusal_content(
        self, text: str | AsyncIterable[str]
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Async variant of :meth:`refusal_content` with streaming support.

        When *text* is a string, behaves identically to :meth:`refusal_content`.
        When *text* is an async iterable of string chunks, emits one
        ``refusal.delta`` per chunk in real time (S-055), then
        ``refusal.done`` with the accumulated text.

        :param text: Complete refusal text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
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
        yield rc.emit_refusal_done("".join(accumulated))
        yield rc.emit_done()
