"""Response event stream builders for lifecycle and output item events."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import GeneratorType
from typing import Any

from ._builders import (
    OutputItemCodeInterpreterCallBuilder,
    OutputItemBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemMessageBuilder,
    OutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
)
from ._id_generator import IdGenerator
from ._state_machine import normalize_lifecycle_events, validate_response_event_stream
from .models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType


_EVENT_MODEL_CLASS_NAMES: dict[str, str] = {
    EVENT_TYPE.RESPONSE_QUEUED.value: "ResponseQueuedEvent",
    EVENT_TYPE.RESPONSE_CREATED.value: "ResponseCreatedEvent",
    EVENT_TYPE.RESPONSE_IN_PROGRESS.value: "ResponseInProgressEvent",
    EVENT_TYPE.RESPONSE_COMPLETED.value: "ResponseCompletedEvent",
    EVENT_TYPE.RESPONSE_FAILED.value: "ResponseFailedEvent",
    EVENT_TYPE.RESPONSE_INCOMPLETE.value: "ResponseIncompleteEvent",
    EVENT_TYPE.RESPONSE_CONTENT_PART_ADDED.value: "ResponseContentPartAddedEvent",
    EVENT_TYPE.RESPONSE_CONTENT_PART_DONE.value: "ResponseContentPartDoneEvent",
    EVENT_TYPE.RESPONSE_OUTPUT_TEXT_DELTA.value: "ResponseTextDeltaEvent",
    EVENT_TYPE.RESPONSE_OUTPUT_TEXT_DONE.value: "ResponseTextDoneEvent",
    EVENT_TYPE.RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED.value: "ResponseOutputTextAnnotationAddedEvent",
    EVENT_TYPE.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA.value: "ResponseFunctionCallArgumentsDeltaEvent",
    EVENT_TYPE.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE.value: "ResponseFunctionCallArgumentsDoneEvent",
    EVENT_TYPE.RESPONSE_REFUSAL_DELTA.value: "ResponseRefusalDeltaEvent",
    EVENT_TYPE.RESPONSE_REFUSAL_DONE.value: "ResponseRefusalDoneEvent",
    EVENT_TYPE.RESPONSE_REASONING_SUMMARY_PART_ADDED.value: "ResponseReasoningSummaryPartAddedEvent",
    EVENT_TYPE.RESPONSE_REASONING_SUMMARY_PART_DONE.value: "ResponseReasoningSummaryPartDoneEvent",
    EVENT_TYPE.RESPONSE_REASONING_SUMMARY_TEXT_DELTA.value: "ResponseReasoningSummaryTextDeltaEvent",
    EVENT_TYPE.RESPONSE_REASONING_SUMMARY_TEXT_DONE.value: "ResponseReasoningSummaryTextDoneEvent",
    EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS.value: "ResponseFileSearchCallInProgressEvent",
    EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_SEARCHING.value: "ResponseFileSearchCallSearchingEvent",
    EVENT_TYPE.RESPONSE_FILE_SEARCH_CALL_COMPLETED.value: "ResponseFileSearchCallCompletedEvent",
    EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS.value: "ResponseWebSearchCallInProgressEvent",
    EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_SEARCHING.value: "ResponseWebSearchCallSearchingEvent",
    EVENT_TYPE.RESPONSE_WEB_SEARCH_CALL_COMPLETED.value: "ResponseWebSearchCallCompletedEvent",
    EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS.value: "ResponseCodeInterpreterCallInProgressEvent",
    EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING.value: "ResponseCodeInterpreterCallInterpretingEvent",
    EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_COMPLETED.value: "ResponseCodeInterpreterCallCompletedEvent",
    EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA.value: "ResponseCodeInterpreterCallCodeDeltaEvent",
    EVENT_TYPE.RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE.value: "ResponseCodeInterpreterCallCodeDoneEvent",
    EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS.value: "ResponseImageGenCallInProgressEvent",
    EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_GENERATING.value: "ResponseImageGenCallGeneratingEvent",
    EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE.value: "ResponseImageGenCallPartialImageEvent",
    EVENT_TYPE.RESPONSE_IMAGE_GENERATION_CALL_COMPLETED.value: "ResponseImageGenCallCompletedEvent",
    EVENT_TYPE.RESPONSE_MCP_CALL_IN_PROGRESS.value: "ResponseMCPCallInProgressEvent",
    EVENT_TYPE.RESPONSE_MCP_CALL_COMPLETED.value: "ResponseMCPCallCompletedEvent",
    EVENT_TYPE.RESPONSE_MCP_CALL_FAILED.value: "ResponseMCPCallFailedEvent",
    EVENT_TYPE.RESPONSE_MCP_CALL_ARGUMENTS_DELTA.value: "ResponseMCPCallArgumentsDeltaEvent",
    EVENT_TYPE.RESPONSE_MCP_CALL_ARGUMENTS_DONE.value: "ResponseMCPCallArgumentsDoneEvent",
    EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS.value: "ResponseMCPListToolsInProgressEvent",
    EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_COMPLETED.value: "ResponseMCPListToolsCompletedEvent",
    EVENT_TYPE.RESPONSE_MCP_LIST_TOOLS_FAILED.value: "ResponseMCPListToolsFailedEvent",
    EVENT_TYPE.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA.value: "ResponseCustomToolCallInputDeltaEvent",
    EVENT_TYPE.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE.value: "ResponseCustomToolCallInputDoneEvent",
}


class ResponseEventStream:
    """.NET-aligned response event stream with deterministic sequence numbers."""

    def __init__(
        self,
        *,
        response_id: str | None = None,
        agent_reference: dict[str, Any] | None = None,
        model: str | None = None,
        request: generated_models.CreateResponse | dict[str, Any] | None = None,
        response: generated_models.Response | dict[str, Any] | None = None,
    ) -> None:
        if request is not None and response is not None:
            raise ValueError("request and response cannot both be provided")

        request_mapping = self._coerce_model_mapping(request)
        response_mapping = self._coerce_model_mapping(response)

        resolved_response_id = response_id
        if resolved_response_id is None and response_mapping is not None:
            candidate_id = response_mapping.get("id")
            if isinstance(candidate_id, str) and candidate_id:
                resolved_response_id = candidate_id

        if not isinstance(resolved_response_id, str) or not resolved_response_id:
            raise ValueError("response_id is required")

        self._response_id = resolved_response_id

        if response_mapping is not None:
            payload = deepcopy(response_mapping)
            payload["id"] = self._response_id
            payload.setdefault("object", "response")
            payload.setdefault("output", [])
            self._response = generated_models.Response(payload)
        else:
            self._response = generated_models.Response(
                {
                    "id": self._response_id,
                    "object": "response",
                    "output": [],
                }
            )
            if request_mapping is not None:
                for field_name in ("metadata", "background", "conversation", "previous_response_id"):
                    value = request_mapping.get(field_name)
                    if value is not None:
                        setattr(self._response, field_name, deepcopy(value))
                request_model = request_mapping.get("model")
                if isinstance(request_model, str) and request_model:
                    self._response.model = request_model
                request_agent_reference = request_mapping.get("agent_reference")
                if isinstance(request_agent_reference, dict):
                    self._response.agent_reference = deepcopy(request_agent_reference)

        if model is not None:
            self._response.model = model

        if agent_reference is not None:
            self._response.agent_reference = deepcopy(agent_reference)

        self._agent_reference = self._extract_agent_reference(self._response)
        self._model = self._extract_model(self._response)
        self._events: list[dict[str, Any]] = []
        self._output_index = 0

    @property
    def response(self) -> generated_models.Response:
        return self._response

    def emit_queued(self) -> dict[str, Any]:
        self._response.status = "queued"
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_QUEUED.value,
                "payload": self._response_payload(),
            }
        )

    def emit_created(self, *, status: str = "in_progress") -> dict[str, Any]:
        self._response.status = status
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_CREATED.value,
                "payload": self._response_payload(),
            }
        )

    def emit_in_progress(self) -> dict[str, Any]:
        self._response.status = "in_progress"
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_IN_PROGRESS.value,
                "payload": self._response_payload(),
            }
        )

    def emit_completed(self, *, usage: generated_models.ResponseUsage | dict[str, Any] | None = None) -> dict[str, Any]:
        self._response.status = "completed"
        self._response.error = None
        self._response.incomplete_details = None
        self._set_terminal_fields(usage=usage)
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_COMPLETED.value,
                "payload": self._response_payload(),
            }
        )

    def emit_failed(
        self,
        *,
        code: str | generated_models.ResponseErrorCode = "server_error",
        message: str = "An internal server error occurred.",
        usage: generated_models.ResponseUsage | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._response.status = "failed"
        self._response.incomplete_details = None
        self._response.error = generated_models.ResponseError(
            {
                "code": self._enum_value(code),
                "message": message,
            }
        )
        self._set_terminal_fields(usage=usage)
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_FAILED.value,
                "payload": self._response_payload(),
            }
        )

    def emit_incomplete(
        self,
        *,
        reason: str | generated_models.ResponseIncompleteDetailsReason | None = None,
        usage: generated_models.ResponseUsage | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._response.status = "incomplete"
        self._response.error = None
        if reason is None:
            self._response.incomplete_details = None
        else:
            self._response.incomplete_details = generated_models.ResponseIncompleteDetails(
                {
                    "reason": self._enum_value(reason),
                }
            )
        self._set_terminal_fields(usage=usage)
        return self._emit_event(
            {
                "type": EVENT_TYPE.RESPONSE_INCOMPLETE.value,
                "payload": self._response_payload(),
            }
        )

    def add_output_item(self, item_id: str) -> OutputItemBuilder:
        if item_id is None:
            raise TypeError("item_id must not be None")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("item_id must be a non-empty string")

        is_valid_id, error = IdGenerator.is_valid(item_id)
        if not is_valid_id:
            raise ValueError(f"invalid item_id '{item_id}': {error}")

        output_index = self._output_index
        self._output_index += 1
        return OutputItemBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_message(self) -> OutputItemMessageBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_message_item_id(self._response_id)
        return OutputItemMessageBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_function_call(self, name: str, call_id: str) -> OutputItemFunctionCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_function_call_item_id(self._response_id)
        return OutputItemFunctionCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            name=name,
            call_id=call_id,
        )

    def add_output_item_function_call_output(self, call_id: str) -> OutputItemFunctionCallOutputBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_function_call_output_item_id(self._response_id)
        return OutputItemFunctionCallOutputBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            call_id=call_id,
        )

    def add_output_item_reasoning_item(self) -> OutputItemReasoningItemBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_reasoning_item_id(self._response_id)
        return OutputItemReasoningItemBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_file_search_call(self) -> OutputItemFileSearchCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_file_search_call_item_id(self._response_id)
        return OutputItemFileSearchCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_web_search_call(self) -> OutputItemWebSearchCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_web_search_call_item_id(self._response_id)
        return OutputItemWebSearchCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_code_interpreter_call(self) -> OutputItemCodeInterpreterCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_code_interpreter_call_item_id(self._response_id)
        return OutputItemCodeInterpreterCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_image_gen_call(self) -> OutputItemImageGenCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_image_gen_call_item_id(self._response_id)
        return OutputItemImageGenCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_mcp_call(self, server_label: str, name: str) -> OutputItemMcpCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_mcp_call_item_id(self._response_id)
        return OutputItemMcpCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            server_label=server_label,
            name=name,
        )

    def add_output_item_mcp_list_tools(self, server_label: str) -> OutputItemMcpListToolsBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_mcp_list_tools_item_id(self._response_id)
        return OutputItemMcpListToolsBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            server_label=server_label,
        )

    def add_output_item_custom_tool_call(self, call_id: str, name: str) -> OutputItemCustomToolCallBuilder:
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_custom_tool_call_item_id(self._response_id)
        return OutputItemCustomToolCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            call_id=call_id,
            name=name,
        )

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

    def _emit_event(self, event: dict[str, Any]) -> dict[str, Any]:
        candidate = deepcopy(event)
        self._apply_common_defaults([candidate])
        self._track_completed_output_item(candidate)
        payload = candidate.get("payload")
        if isinstance(payload, dict):
            payload["sequence_number"] = len(self._events)

        candidate = self._coerce_event_with_generated_class(candidate)

        self._events.append(candidate)
        validate_response_event_stream(self._events)
        return deepcopy(candidate)

    def _response_payload(self) -> dict[str, Any]:
        return self._materialize_generated_payload(self._response.as_dict())

    def _track_completed_output_item(self, event: dict[str, Any]) -> None:
        if event.get("type") != EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
            return

        payload = event.get("payload")
        if not isinstance(payload, dict):
            return

        output_index = payload.get("output_index")
        item = payload.get("item")
        if not isinstance(output_index, int) or output_index < 0 or not isinstance(item, dict):
            return

        output_items = self._response.output
        if not isinstance(output_items, list):
            output_items = []
            self._response.output = output_items

        try:
            typed_item: Any = generated_models.OutputItem(deepcopy(item))
        except Exception:
            typed_item = deepcopy(item)

        while len(output_items) <= output_index:
            output_items.append(None)

        output_items[output_index] = typed_item

    def _with_output_item_defaults(self, item: dict[str, Any]) -> dict[str, Any]:
        stamped_item = deepcopy(item)
        stamped_item.setdefault("response_id", self._response_id)
        if self._agent_reference is not None:
            stamped_item.setdefault("agent_reference", deepcopy(self._agent_reference))
        return stamped_item

    def _coerce_event_with_generated_class(self, event: dict[str, Any]) -> dict[str, Any]:
        event_type = event.get("type")
        if not isinstance(event_type, str) or not event_type:
            return event

        class_name = _EVENT_MODEL_CLASS_NAMES.get(event_type)
        if class_name is None:
            return event

        event_class = getattr(generated_models, class_name, None)
        if event_class is None:
            return event

        payload = event.get("payload")
        flattened: dict[str, Any] = {"type": event_type}
        if isinstance(payload, dict):
            flattened.update(deepcopy(payload))

        try:
            model_event = event_class(flattened)
            model_data = self._materialize_generated_payload(model_event.as_dict())
            model_type = model_data.pop("type", event_type)
            return {"type": model_type, "payload": model_data}
        except Exception:
            return event

    def _materialize_generated_payload(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._materialize_generated_payload(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._materialize_generated_payload(item) for item in value]
        if isinstance(value, tuple):
            return [self._materialize_generated_payload(item) for item in value]
        if isinstance(value, GeneratorType):
            return [self._materialize_generated_payload(item) for item in value]
        return value

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

    def _set_terminal_fields(self, *, usage: generated_models.ResponseUsage | dict[str, Any] | None) -> None:
        self._response.completed_at = datetime.now(timezone.utc)
        self._response.usage = self._coerce_usage(usage)
        self._response.output_text = self._compute_output_text()

    def _coerce_usage(self, usage: generated_models.ResponseUsage | dict[str, Any] | None) -> generated_models.ResponseUsage | None:
        if usage is None:
            return None
        if isinstance(usage, dict):
            return generated_models.ResponseUsage(deepcopy(usage))
        if hasattr(usage, "as_dict"):
            return generated_models.ResponseUsage(deepcopy(usage.as_dict()))
        raise TypeError("usage must be a dict or a generated ResponseUsage model")

    def _compute_output_text(self) -> str | None:
        output = self._response.output
        if not isinstance(output, list):
            return None

        fragments: list[str] = []
        for item in output:
            item_payload = self._coerce_model_mapping(item)
            if not isinstance(item_payload, dict):
                continue
            if item_payload.get("type") not in ("output_message", "message"):
                continue

            content = item_payload.get("content")
            if not isinstance(content, list):
                continue

            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") != "output_text":
                    continue
                text = part.get("text")
                if isinstance(text, str) and text:
                    fragments.append(text)

        if not fragments:
            return None
        return "".join(fragments)

    def _coerce_model_mapping(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        if isinstance(value, dict):
            return deepcopy(value)
        if hasattr(value, "as_dict"):
            payload = value.as_dict()
            if isinstance(payload, dict):
                return deepcopy(payload)
        return None

    def _extract_agent_reference(self, response: generated_models.Response) -> dict[str, Any] | None:
        payload = self._coerce_model_mapping(response)
        if not isinstance(payload, dict):
            return None
        agent_reference = payload.get("agent_reference")
        if isinstance(agent_reference, dict):
            return agent_reference
        return None

    def _extract_model(self, response: generated_models.Response) -> str | None:
        payload = self._coerce_model_mapping(response)
        if not isinstance(payload, dict):
            return None
        model = payload.get("model")
        if isinstance(model, str) and model:
            return model
        return None

    def _enum_value(self, value: Any) -> Any:
        return getattr(value, "value", value)
