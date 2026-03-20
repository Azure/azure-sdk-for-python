"""Function call builders: function-call and function-call-output output items."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from ._base import BaseOutputItemBuilder, EVENT_TYPE, _require_non_empty

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
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._name = _require_non_empty(name, "name")
        self._call_id = _require_non_empty(call_id, "call_id")
        self._final_arguments: str | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def call_id(self) -> str:
        return self._call_id

    def emit_added(self) -> dict[str, Any]:
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

    def emit_arguments_delta(self, delta: str) -> dict[str, Any]:
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "delta": delta,
                },
            }
        )

    def emit_arguments_done(self, arguments: str) -> dict[str, Any]:
        self._final_arguments = arguments
        return self._stream._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE.value,
                "payload": {
                    "item_id": self._item_id,
                    "output_index": self._output_index,
                    "name": self._name,
                    "arguments": arguments,
                },
            }
        )

    def emit_done(self) -> dict[str, Any]:
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


class OutputItemFunctionCallOutputBuilder(BaseOutputItemBuilder):
    """Scoped builder for a function-call-output item in stream mode."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        call_id: str,
    ) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._call_id = _require_non_empty(call_id, "call_id")
        self._final_output: str | list[Any] | None = None

    @property
    def call_id(self) -> str:
        return self._call_id

    def emit_added(self, output: str | list[Any] | None = None) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "function_call_output",
                "id": self._item_id,
                "call_id": self._call_id,
                "output": deepcopy(output) if output is not None else "",
                "status": "in_progress",
            }
        )

    def emit_done(self, output: str | list[Any] | None = None) -> dict[str, Any]:
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
