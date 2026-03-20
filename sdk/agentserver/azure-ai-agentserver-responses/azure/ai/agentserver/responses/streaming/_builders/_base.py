# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Base builder infrastructure: lifecycle state, base class, and generic builder."""

from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Any

from ...models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType

if TYPE_CHECKING:
    from .._event_stream import ResponseEventStream


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


class BuilderLifecycleState(Enum):
    NOT_STARTED = "not_started"
    ADDED = "added"
    DONE = "done"


class BaseOutputItemBuilder:
    """Base output-item builder with lifecycle guards for added/done events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        self._stream = stream
        self._output_index = output_index
        self._item_id = item_id
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def output_index(self) -> int:
        return self._output_index

    def _ensure_transition(self, expected: BuilderLifecycleState, new_state: BuilderLifecycleState) -> None:
        if self._lifecycle_state is not expected:
            raise ValueError(
                "cannot transition to "
                f"'{new_state.value}' from '{self._lifecycle_state.value}' "
                f"(expected '{expected.value}')"
            )
        self._lifecycle_state = new_state

    def _emit_added(self, item: dict[str, Any]) -> dict[str, Any]:
        self._ensure_transition(BuilderLifecycleState.NOT_STARTED, BuilderLifecycleState.ADDED)
        stamped_item = self._stream._with_output_item_defaults(item)
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value,
                "payload": {
                    "output_index": self._output_index,
                    "item": stamped_item,
                },
            }
        )

    def _emit_done(self, item: dict[str, Any]) -> dict[str, Any]:
        self._ensure_transition(BuilderLifecycleState.ADDED, BuilderLifecycleState.DONE)
        stamped_item = self._stream._with_output_item_defaults(item)
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value,
                "payload": {
                    "output_index": self._output_index,
                    "item": stamped_item,
                },
            }
        )

    def _emit_item_state_event(self, event_type: str, *, extra_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "item_id": self._item_id,
            "output_index": self._output_index,
        }
        if extra_payload:
            payload.update(deepcopy(extra_payload))
        return self._stream._emit_event({"type": event_type, "payload": payload})


class OutputItemBuilder(BaseOutputItemBuilder):
    """Generic output-item builder for item types without dedicated scoped builders."""

    def _coerce_item(self, item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            return deepcopy(item)
        if hasattr(item, "as_dict"):
            return deepcopy(item.as_dict())
        raise TypeError("item must be a dict or a generated model with as_dict()")

    def emit_added(self, item: Any) -> dict[str, Any]:
        return self._emit_added(self._coerce_item(item))

    def emit_done(self, item: Any) -> dict[str, Any]:
        return self._emit_done(self._coerce_item(item))
