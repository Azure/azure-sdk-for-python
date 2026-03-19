"""Streaming output-item builders aligned with .NET builder semantics."""

from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Any

from .models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType

if TYPE_CHECKING:
    from ._event_stream import ResponseEventStream


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

    def add_refusal_content(self) -> "RefusalContentBuilder":
        content_index = self._content_index
        self._content_index += 1
        return RefusalContentBuilder(
            stream=self._stream,
            output_index=self._output_index,
            content_index=content_index,
            item_id=self._item_id,
        )

    def emit_content_done(self, content_builder: TextContentBuilder | "RefusalContentBuilder") -> dict[str, Any]:
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


class OutputItemFileSearchCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for file search tool call events."""

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "file_search_call",
                "id": self._item_id,
                "status": "in_progress",
                "queries": [],
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS.value)

    def emit_searching(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_SEARCHING.value)

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_COMPLETED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done({"type": "file_search_call", "id": self._item_id, "status": "completed", "queries": []})


class OutputItemWebSearchCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for web search tool call events."""

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added({"type": "web_search_call", "id": self._item_id, "status": "in_progress", "action": {}})

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS.value)

    def emit_searching(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_SEARCHING.value)

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_COMPLETED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done({"type": "web_search_call", "id": self._item_id, "status": "completed", "action": {}})


class OutputItemCodeInterpreterCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for code interpreter tool call events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._final_code: str | None = None

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "code_interpreter_call",
                "id": self._item_id,
                "status": "in_progress",
                "container_id": "",
                "code": "",
                "outputs": [],
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS.value)

    def emit_interpreting(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING.value)

    def emit_code_delta(self, delta: str) -> dict[str, Any]:
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA.value,
            extra_payload={"delta": delta},
        )

    def emit_code_done(self, code: str) -> dict[str, Any]:
        self._final_code = code
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE.value,
            extra_payload={"code": code},
        )

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_COMPLETED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "code_interpreter_call",
                "id": self._item_id,
                "status": "completed",
                "container_id": "",
                "code": self._final_code or "",
                "outputs": [],
            }
        )


class OutputItemImageGenCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for image generation tool call events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._partial_image_index = 0

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "image_generation_call",
                "id": self._item_id,
                "status": "in_progress",
                "result": "",
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS.value)

    def emit_generating(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_GENERATING.value)

    def emit_partial_image(self, partial_image_b64: str) -> dict[str, Any]:
        partial_index = self._partial_image_index
        self._partial_image_index += 1
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE.value,
            extra_payload={"partial_image_index": partial_index, "partial_image_b64": partial_image_b64},
        )

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_COMPLETED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "image_generation_call",
                "id": self._item_id,
                "status": "completed",
                "result": "",
            }
        )


class OutputItemMcpCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for MCP tool call events."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        server_label: str,
        name: str,
    ) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._server_label = _require_non_empty(server_label, "server_label")
        self._name = _require_non_empty(name, "name")
        self._final_arguments: str | None = None

    @property
    def server_label(self) -> str:
        return self._server_label

    @property
    def name(self) -> str:
        return self._name

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "mcp_call",
                "id": self._item_id,
                "server_label": self._server_label,
                "name": self._name,
                "arguments": "",
                "status": "in_progress",
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_CALL_IN_PROGRESS.value)

    def emit_arguments_delta(self, delta: str) -> dict[str, Any]:
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_MCP_CALL_ARGUMENTS_DELTA.value,
            extra_payload={"delta": delta},
        )

    def emit_arguments_done(self, arguments: str) -> dict[str, Any]:
        self._final_arguments = arguments
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_MCP_CALL_ARGUMENTS_DONE.value,
            extra_payload={"arguments": arguments},
        )

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_CALL_COMPLETED.value)

    def emit_failed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_CALL_FAILED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "mcp_call",
                "id": self._item_id,
                "server_label": self._server_label,
                "name": self._name,
                "arguments": self._final_arguments or "",
                "status": "completed",
            }
        )


class OutputItemMcpListToolsBuilder(BaseOutputItemBuilder):
    """Scoped builder for MCP list-tools lifecycle events."""

    def __init__(self, stream: "ResponseEventStream", output_index: int, item_id: str, server_label: str) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._server_label = _require_non_empty(server_label, "server_label")

    @property
    def server_label(self) -> str:
        return self._server_label

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "mcp_list_tools",
                "id": self._item_id,
                "server_label": self._server_label,
                "tools": [],
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS.value)

    def emit_completed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_COMPLETED.value)

    def emit_failed(self) -> dict[str, Any]:
        return self._emit_item_state_event(EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_FAILED.value)

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "mcp_list_tools",
                "id": self._item_id,
                "server_label": self._server_label,
                "tools": [],
            }
        )


class OutputItemCustomToolCallBuilder(BaseOutputItemBuilder):
    """Scoped builder for custom tool call events."""

    def __init__(
        self,
        stream: "ResponseEventStream",
        output_index: int,
        item_id: str,
        call_id: str,
        name: str,
    ) -> None:
        super().__init__(stream=stream, output_index=output_index, item_id=item_id)
        self._call_id = _require_non_empty(call_id, "call_id")
        self._name = _require_non_empty(name, "name")
        self._final_input: str | None = None

    @property
    def call_id(self) -> str:
        return self._call_id

    @property
    def name(self) -> str:
        return self._name

    def emit_added(self) -> dict[str, Any]:
        return self._emit_added(
            {
                "type": "custom_tool_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "input": "",
            }
        )

    def emit_input_delta(self, delta: str) -> dict[str, Any]:
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA.value,
            extra_payload={"delta": delta},
        )

    def emit_input_done(self, input_text: str) -> dict[str, Any]:
        self._final_input = input_text
        return self._emit_item_state_event(
            EVENT_TYPE.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE.value,
            extra_payload={"input": input_text},
        )

    def emit_done(self) -> dict[str, Any]:
        return self._emit_done(
            {
                "type": "custom_tool_call",
                "id": self._item_id,
                "call_id": self._call_id,
                "name": self._name,
                "input": self._final_input or "",
            }
        )
