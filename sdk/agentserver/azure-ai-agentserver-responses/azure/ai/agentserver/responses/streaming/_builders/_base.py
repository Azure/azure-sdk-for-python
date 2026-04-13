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
    """Validate that a string value is non-empty.

    :param value: The string value to check.
    :type value: str
    :param field_name: The field name to include in the error message.
    :type field_name: str
    :returns: The validated non-empty string.
    :rtype: str
    :raises ValueError: If *value* is not a non-empty string.
    """
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
        """Initialize the base output-item builder.

        :param stream: The parent event stream to emit events into.
        :type stream: ResponseEventStream
        :param output_index: The zero-based index of this output item.
        :type output_index: int
        :param item_id: Unique identifier for this output item.
        :type item_id: str
        """
        self._stream = stream
        self._output_index = output_index
        self._item_id = item_id
        self._lifecycle_state = BuilderLifecycleState.NOT_STARTED

    @property
    def item_id(self) -> str:
        """Return the output item identifier.

        :returns: The item ID.
        :rtype: str
        """
        return self._item_id

    @property
    def output_index(self) -> int:
        """Return the zero-based output index.

        :returns: The output index.
        :rtype: int
        """
        return self._output_index

    def _ensure_transition(self, expected: BuilderLifecycleState, new_state: BuilderLifecycleState) -> None:
        """Guard a lifecycle state transition.

        :param expected: The expected current lifecycle state.
        :type expected: BuilderLifecycleState
        :param new_state: The target state to transition to.
        :type new_state: BuilderLifecycleState
        :rtype: None
        :raises ValueError: If the current state does not match *expected*.
        """
        if self._lifecycle_state is not expected:
            raise ValueError(
                "cannot transition to "
                f"'{new_state.value}' from '{self._lifecycle_state.value}' "
                f"(expected '{expected.value}')"
            )
        self._lifecycle_state = new_state

    def _emit_added(self, item: dict[str, Any]) -> generated_models.ResponseStreamEvent:
        """Emit an ``output_item.added`` event with lifecycle guard.

        :param item: The output item dict to include in the event.
        :type item: dict[str, Any]
        :returns: The emitted event.
        :rtype: ResponseStreamEvent
        :raises ValueError: If the builder is not in ``NOT_STARTED`` state.
        """
        self._ensure_transition(BuilderLifecycleState.NOT_STARTED, BuilderLifecycleState.ADDED)
        stamped_item = self._stream.with_output_item_defaults(item)
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value,
                "output_index": self._output_index,
                "item": stamped_item,
            }
        )

    def _emit_done(self, item: dict[str, Any]) -> generated_models.ResponseStreamEvent:
        """Emit an ``output_item.done`` event with lifecycle guard.

        :param item: The completed output item dict to include in the event.
        :type item: dict[str, Any]
        :returns: The emitted event.
        :rtype: ResponseStreamEvent
        :raises ValueError: If the builder is not in ``ADDED`` state.
        """
        self._ensure_transition(BuilderLifecycleState.ADDED, BuilderLifecycleState.DONE)
        stamped_item = self._stream.with_output_item_defaults(item)
        return self._stream.emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value,
                "output_index": self._output_index,
                "item": stamped_item,
            }
        )

    def _emit_item_state_event(
        self, event_type: str, *, extra_payload: dict[str, Any] | None = None
    ) -> generated_models.ResponseStreamEvent:
        """Emit an item-level state event (e.g., in-progress, searching, completed).

        :param event_type: The event type string.
        :type event_type: str
        :keyword extra_payload: Optional additional fields to merge.
        :paramtype extra_payload: dict[str, Any] | None
        :returns: The emitted event.
        :rtype: ResponseStreamEvent
        """
        event: dict[str, Any] = {
            "type": event_type,
            "item_id": self._item_id,
            "output_index": self._output_index,
        }
        if extra_payload:
            event.update(deepcopy(extra_payload))
        return self._stream.emit_event(event)


class OutputItemBuilder(BaseOutputItemBuilder):
    """Generic output-item builder for item types without dedicated scoped builders."""

    def _coerce_item(self, item: generated_models.OutputItem | dict[str, Any]) -> dict[str, Any]:
        """Coerce an item to a plain dict.

        :param item: A dict or a generated model with ``as_dict()``.
        :type item: OutputItem | dict[str, Any]
        :returns: A deep-copied dict representation of the item.
        :rtype: dict[str, Any]
        :raises TypeError: If *item* is not a dict or model with ``as_dict()``.
        """
        if isinstance(item, dict):
            return deepcopy(item)
        if hasattr(item, "as_dict"):
            return item.as_dict()
        raise TypeError("item must be a dict or a generated model with as_dict()")

    def emit_added(self, item: generated_models.OutputItem | dict[str, Any]) -> generated_models.ResponseStreamEvent:
        """Emit an ``output_item.added`` event for a generic item.

        :param item: The output item (dict or model with ``as_dict()``).
        :type item: OutputItem | dict[str, Any]
        :returns: The emitted event.
        :rtype: ResponseStreamEvent
        """
        return self._emit_added(self._coerce_item(item))

    def emit_done(self, item: generated_models.OutputItem | dict[str, Any]) -> generated_models.ResponseStreamEvent:
        """Emit an ``output_item.done`` event for a generic item.

        :param item: The completed output item (dict or model with ``as_dict()``).
        :type item: OutputItem | dict[str, Any]
        :returns: The emitted event.
        :rtype: ResponseStreamEvent
        """
        return self._emit_done(self._coerce_item(item))
