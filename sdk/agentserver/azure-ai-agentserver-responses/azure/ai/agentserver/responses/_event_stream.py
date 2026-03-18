"""Response event stream builders for lifecycle and output item events."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ._state_machine import normalize_lifecycle_events, validate_response_event_stream


class OutputItemBuilder:
    """Builds output-item lifecycle events in .NET-like Emit* style."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        *,
        output_index: int,
    ) -> None:
        self._stream = stream
        self._output_index = output_index
        self._added = False
        self._done = False

    def emit_added(self, *, item: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._added:
            raise ValueError("output item has already emitted added")
        self._added = True
        return self._stream._emit_output_item_event(
            "response.output_item.added",
            item=item,
            output_index=self._output_index,
        )

    def emit_delta(self, *, item: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._added:
            raise ValueError("output item delta requires added first")
        if self._done:
            raise ValueError("output item is already done")
        return self._stream._emit_output_item_event(
            "response.output_item.delta",
            item=item,
            output_index=self._output_index,
        )

    def emit_done(self, *, item: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._added:
            raise ValueError("output item done requires added first")
        if self._done:
            raise ValueError("output item is already done")
        self._done = True
        return self._stream._emit_output_item_event(
            "response.output_item.done",
            item=item,
            output_index=self._output_index,
        )

class ResponseEventStream:
    """.NET-aligned response event stream with deterministic sequence numbers."""

    def __init__(
        self,
        *,
        response_id: str,
        agent_reference: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> None:
        self._response_id = response_id
        self._agent_reference = deepcopy(agent_reference) if agent_reference is not None else None
        self._model = model
        self._events: list[dict[str, Any]] = []
        self._output_index = 0

    def emit_queued(self) -> dict[str, Any]:
        return self._emit_lifecycle("response.queued", status="queued")

    def emit_created(self, *, status: str = "in_progress") -> dict[str, Any]:
        return self._emit_lifecycle("response.created", status=status)

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_lifecycle("response.in_progress", status="in_progress")

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_lifecycle("response.completed", status="completed")

    def emit_failed(self) -> dict[str, Any]:
        return self._emit_lifecycle("response.failed", status="failed")

    def emit_incomplete(self) -> dict[str, Any]:
        return self._emit_lifecycle("response.incomplete", status="incomplete")

    def add_output_item(self, *, output_index: int | None = None) -> OutputItemBuilder:
        if output_index is None:
            output_index = self._output_index
            self._output_index += 1
        return OutputItemBuilder(self, output_index=output_index)

    def build(self) -> list[dict[str, Any]]:
        events = [deepcopy(event) for event in self._events]

        if not events:
            events = normalize_lifecycle_events(response_id=self._response_id, events=[], default_model=self._model)
            self._apply_common_defaults(events)
            self._assign_sequence_numbers(events)
            validate_response_event_stream(events)
            return events

        lifecycle_events = [
            event for event in events if event["type"].startswith("response.") and "output_item" not in event["type"]
        ]
        if lifecycle_events:
            normalized_lifecycle = normalize_lifecycle_events(
                response_id=self._response_id,
                events=lifecycle_events,
                default_model=self._model,
            )
            lifecycle_iter = iter(normalized_lifecycle)
            stitched_events: list[dict[str, Any]] = []
            for event in events:
                if event["type"].startswith("response.") and "output_item" not in event["type"]:
                    stitched_events.append(next(lifecycle_iter))
                else:
                    stitched_events.append(event)
            remaining_lifecycle = list(lifecycle_iter)
            stitched_events.extend(remaining_lifecycle)
            events = stitched_events

        self._apply_common_defaults(events)
        self._assign_sequence_numbers(events)
        validate_response_event_stream(events)
        return events

    def events(self) -> list[dict[str, Any]]:
        return [deepcopy(event) for event in self._events]

    def _emit_lifecycle(self, event_type: str, *, status: str) -> dict[str, Any]:
        event = {
            "type": event_type,
            "payload": {
                "status": status,
            },
        }
        return self._emit_event(event)

    def _emit_output_item_event(
        self,
        event_type: str,
        *,
        item: dict[str, Any] | None,
        output_index: int,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"output_index": output_index}
        if item is not None:
            payload["item"] = deepcopy(item)

        event: dict[str, Any] = {"type": event_type, "payload": payload}
        return self._emit_event(event)

    def _emit_event(self, event: dict[str, Any]) -> dict[str, Any]:
        candidate = deepcopy(event)
        self._apply_common_defaults([candidate])
        payload = candidate.get("payload")
        if isinstance(payload, dict):
            payload["sequence_number"] = len(self._events)

        self._events.append(candidate)
        validate_response_event_stream(self._events)
        return deepcopy(candidate)

    def _apply_common_defaults(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            payload = event.get("payload")
            if not isinstance(payload, dict):
                payload = {}
                event["payload"] = payload
            payload.setdefault("id", self._response_id)
            payload.setdefault("response_id", self._response_id)
            payload.setdefault("object", "response")
            if self._agent_reference is not None:
                payload.setdefault("agent_reference", deepcopy(self._agent_reference))
            if self._model is not None:
                payload.setdefault("model", self._model)

    def _assign_sequence_numbers(self, events: list[dict[str, Any]]) -> None:
        for index, event in enumerate(events):
            payload = event.get("payload")
            if isinstance(payload, dict):
                payload["sequence_number"] = index
