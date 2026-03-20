"""Message-related builders: text content, refusal content, and message output item."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from ._base import BaseOutputItemBuilder, BuilderLifecycleState, EVENT_TYPE

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class TextContentBuilder:
    """Scoped builder for a text content part within an output message item."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, content_index: int, item_id: str) -> None:
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
        return self._final_text

    @property
    def content_index(self) -> int:
        return self._content_index

    def emit_added(self) -> dict[str, Any]:
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return self._stream._emit_event(
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
        return self._stream._emit_event(
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
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        merged_text = "".join(self._delta_fragments)
        if not merged_text and final_text is not None:
            merged_text = final_text
        self._final_text = merged_text
        return self._stream._emit_event(
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
        annotation_index = self._annotation_index
        self._annotation_index += 1
        return self._stream._emit_event(
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
        self._stream = stream
        self._output_index = output_index
        self._content_index = content_index
        self._item_id = item_id
        self._final_refusal: str | None = None
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def final_refusal(self) -> str | None:
        return self._final_refusal

    @property
    def content_index(self) -> int:
        return self._content_index

    def emit_added(self) -> dict[str, Any]:
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return self._stream._emit_event(
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
        return self._stream._emit_event(
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
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        self._final_refusal = final_refusal
        return self._stream._emit_event(
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
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._content_index = 0
        self._completed_contents: list[dict[str, Any]] = []

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "output_message",
                "id": self._item_id,
                "role": "assistant",
                "content": [],
                "status": "in_progress",
            }
        )

    def add_text_content(self) -> TextContentBuilder:
        content_index = self._content_index
        self._content_index += 1
        return TextContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )

    def add_refusal_content(self) -> RefusalContentBuilder:
        content_index = self._content_index
        self._content_index += 1
        return RefusalContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )

    def emit_content_done(self, content_builder: TextContentBuilder | RefusalContentBuilder) -> dict[str, Any]:
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
        return self._stream._emit_event(
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
        if len(self._completed_contents) == 0:
            raise ValueError("message output item requires at least one content part before emit_done")
        return self._emit_done(
            {
                "type": "output_message",
                "id": self._item_id,
                "role": "assistant",
                "content": deepcopy(self._completed_contents),
                "status": "completed",
            }
        )
