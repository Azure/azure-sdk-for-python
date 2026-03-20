"""Reasoning-related builders: summary parts and reasoning output items."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from ._base import BaseOutputItemBuilder, BuilderLifecycleState, EVENT_TYPE

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


class ReasoningSummaryPartBuilder:
    """Scoped builder for a single reasoning summary part."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, summary_index: int, item_id: str) -> None:
        self._stream = stream
        self._output_index = output_index
        self._summary_index = summary_index
        self._item_id = item_id
        self._final_text: str | None = None
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def final_text(self) -> str | None:
        return self._final_text

    @property
    def summary_index(self) -> int:
        return self._summary_index

    def emit_added(self) -> dict[str, Any]:
        if self._lifecycle_state is not BuilderLifecycleState.NOT_STARTED:
            raise ValueError(f"cannot call emit_added in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.ADDED
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REASONING_SUMMARY_PART_ADDED.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "part": {"type": "summary_text", "text": ""},
                },
            }
        )

    def emit_text_delta(self, text: str) -> dict[str, Any]:
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REASONING_SUMMARY_TEXT_DELTA.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "delta": text,
                },
            }
        )

    def emit_text_done(self, final_text: str) -> dict[str, Any]:
        self._final_text = final_text
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REASONING_SUMMARY_TEXT_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "text": final_text,
                },
            }
        )

    def emit_done(self) -> dict[str, Any]:
        if self._lifecycle_state is not BuilderLifecycleState.ADDED:
            raise ValueError(f"cannot call emit_done in '{self._lifecycle_state.value}' state")
        self._lifecycle_state = BuilderLifecycleState.DONE
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_REASONING_SUMMARY_PART_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "summary_index": self._summary_index,
                    "part": {"type": "summary_text", "text": self._final_text or ""},
                },
            }
        )


class OutputItemReasoningItemBuilder(BaseOutputItemBuilder):
    """Scoped builder for reasoning output items with summary part support."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._summary_index = 0
        self._completed_summaries: list[dict[str, Any]] = []

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added({"type": "reasoning", "id": self._item_id, "summary": [], "status": "in_progress"})

    def add_summary_part(self) -> ReasoningSummaryPartBuilder:
        summary_index = self._summary_index
        self._summary_index += 1
        return ReasoningSummaryPartBuilder(self._stream, self._output_index, summary_index, self._item_id)

    def emit_summary_part_done(self, summary_part: ReasoningSummaryPartBuilder) -> None:
        self._completed_summaries.append({"type": "summary_text", "text": summary_part.final_text or ""})

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "reasoning",
                "id": self._item_id,
                "summary": deepcopy(self._completed_summaries),
                "status": "completed",
            }
        )
