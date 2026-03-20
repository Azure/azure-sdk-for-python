"""Internal helper functions extracted from ResponseEventStream.

These are pure or near-pure functions that operate on event dicts
and generated model objects. They carry no mutable state of their own.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import GeneratorType
from typing import Any

from ..models import _generated as generated_models

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


# ---------------------------------------------------------------------------
# Pure / near-pure helpers
# ---------------------------------------------------------------------------


def enum_value(value: Any) -> Any:
    """Return the ``.value`` of an enum member, or the value itself."""
    return getattr(value, "value", value)


def coerce_model_mapping(value: Any) -> dict[str, Any] | None:
    """Normalise a generated model, dict, or ``None`` to a plain dict copy."""
    if value is None:
        return None
    if isinstance(value, dict):
        return deepcopy(value)
    if hasattr(value, "as_dict"):
        payload = value.as_dict()
        if isinstance(payload, dict):
            return deepcopy(payload)
    return None


def materialize_generated_payload(value: Any) -> Any:
    """Recursively resolve generators/tuples to plain lists/dicts."""
    if isinstance(value, dict):
        return {key: materialize_generated_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [materialize_generated_payload(item) for item in value]
    if isinstance(value, tuple):
        return [materialize_generated_payload(item) for item in value]
    if isinstance(value, GeneratorType):
        return [materialize_generated_payload(item) for item in value]
    return value


def coerce_event_with_generated_class(event: dict[str, Any]) -> dict[str, Any]:
    """Round-trip an event dict through the corresponding generated model class."""
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
        model_data = materialize_generated_payload(model_event.as_dict())
        model_type = model_data.pop("type", event_type)
        return {"type": model_type, "payload": model_data}
    except Exception:
        return event


def apply_common_defaults(
    events: list[dict[str, Any]],
    *,
    response_id: str,
    agent_reference: dict[str, Any] | None,
    model: str | None,
) -> None:
    """Stamp every event payload with response-level defaults."""
    for event in events:
        payload = event.get("payload")
        if not isinstance(payload, dict):
            payload = {}
            event["payload"] = payload
        payload.setdefault("id", response_id)
        payload.setdefault("response_id", response_id)
        payload.setdefault("object", "response")
        if agent_reference is not None:
            payload.setdefault("agent_reference", deepcopy(agent_reference))
        if model is not None:
            payload.setdefault("model", model)


def assign_sequence_numbers(events: list[dict[str, Any]]) -> None:
    """Assign deterministic ``sequence_number`` to every payload."""
    for index, event in enumerate(events):
        payload = event.get("payload")
        if isinstance(payload, dict):
            payload["sequence_number"] = index


def track_completed_output_item(
    response: generated_models.Response,
    event: dict[str, Any],
) -> None:
    """When an output-item-done event arrives, persist the item on the response."""
    if event.get("type") != EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
        return

    payload = event.get("payload")
    if not isinstance(payload, dict):
        return

    output_index = payload.get("output_index")
    item = payload.get("item")
    if not isinstance(output_index, int) or output_index < 0 or not isinstance(item, dict):
        return

    output_items = response.output
    if not isinstance(output_items, list):
        output_items = []
        response.output = output_items

    try:
        typed_item: Any = generated_models.OutputItem(deepcopy(item))
    except Exception:
        typed_item = deepcopy(item)

    while len(output_items) <= output_index:
        output_items.append(None)

    output_items[output_index] = typed_item


def coerce_usage(
    usage: generated_models.ResponseUsage | dict[str, Any] | None,
) -> generated_models.ResponseUsage | None:
    """Normalise a usage value to a generated ``ResponseUsage`` instance."""
    if usage is None:
        return None
    if isinstance(usage, dict):
        return generated_models.ResponseUsage(deepcopy(usage))
    if hasattr(usage, "as_dict"):
        return generated_models.ResponseUsage(deepcopy(usage.as_dict()))
    raise TypeError("usage must be a dict or a generated ResponseUsage model")


def compute_output_text(response: generated_models.Response) -> str | None:
    """Concatenate all ``output_text`` content parts from message output items."""
    output = response.output
    if not isinstance(output, list):
        return None

    fragments: list[str] = []
    for item in output:
        item_payload = coerce_model_mapping(item)
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


def extract_agent_reference(response: generated_models.Response) -> dict[str, Any] | None:
    """Pull the ``agent_reference`` dict from a response, if present."""
    payload = coerce_model_mapping(response)
    if not isinstance(payload, dict):
        return None
    agent_reference = payload.get("agent_reference")
    if isinstance(agent_reference, dict):
        return agent_reference
    return None


def extract_model(response: generated_models.Response) -> str | None:
    """Pull the ``model`` string from a response, if present."""
    payload = coerce_model_mapping(response)
    if not isinstance(payload, dict):
        return None
    model = payload.get("model")
    if isinstance(model, str) and model:
        return model
    return None
