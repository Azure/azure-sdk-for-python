# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=too-many-return-statements
import json
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4

from agent_framework import Content, Message
from openai.types.conversations import ConversationItem

from azure.ai.agentserver.core.logger import get_logger

logger = get_logger()

_ROLE_MAP = {
    "assistant": "assistant",
    "system": "system",
    "user": "user",
    "tool": "tool",
    "developer": "system",
    "critic": "assistant",
    "discriminator": "assistant",
    "unknown": "user",
}
_TOOL_CALL_TYPES = {
    "function_call",
    "web_search_call",
    "computer_call",
    "local_shell_call",
    "custom_tool_call",
    "mcp_approval_request",
}
_TOOL_RESULT_TYPES = {
    "function_call_output",
    "computer_call_output",
    "local_shell_call_output",
    "custom_tool_call_output",
    "file_search_call",
    "image_generation_call",
    "code_interpreter_call",
    "mcp_list_tools",
    "mcp_call",
    "mcp_approval_response",
}
_RESULT_HINT_FIELDS = (
    "output",
    "outputs",
    "result",
    "results",
    "summary",
    "tools",
    "encrypted_content",
    "error",
)


def to_chat_message(item: ConversationItem) -> Optional[Message]:
    """Convert a ConversationItem from the Conversations API to an AF Message."""
    if item is None:
        return None

    item_type = getattr(item, "type", None)
    if item_type == "message":
        return _convert_message_item(item)
    if item_type == "reasoning":
        return _convert_reasoning_item(item)

    if item_type in _TOOL_RESULT_TYPES or _has_result_payload(item):
        return _convert_tool_result_item(item)
    if item_type in _TOOL_CALL_TYPES:
        return _convert_tool_call_item(item)

    logger.debug("Unsupported conversation item type: %s", item_type)
    return None


def _convert_message_item(item: Any) -> Optional[Message]:
    role_value = _ROLE_MAP.get(str(getattr(item, "role", "user")).lower(), "user")
    raw_contents = getattr(item, "content", None) or []

    converted_contents: List[Any] = []
    for content in raw_contents:
        converted = _convert_message_content(content)
        if converted:
            converted_contents.append(converted)

    if not converted_contents:
        return None

    return Message(role=role_value, contents=converted_contents)


def _convert_tool_call_item(item: Any) -> Optional[Message]:
    data = _model_dump(item)
    if not data:
        return None

    call_id = _resolve_call_id(data, getattr(item, "type", "tool_call"))
    name = str(data.get("name") or _infer_action_name(data) or data.get("type") or "tool_call")
    arguments = _extract_call_arguments(data)
    normalized_arguments = _normalize_arguments(arguments)

    content = Content.from_function_call(
        call_id=call_id,
        name=name,
        arguments=normalized_arguments,
    )
    return Message(role="assistant", contents=[content])


def _convert_tool_result_item(item: Any) -> Optional[Message]:
    data = _model_dump(item)
    if not data:
        return None

    call_id = _resolve_call_id(data, getattr(item, "type", "tool"))
    result_payload = _extract_result_payload(data)
    if result_payload is None:
        return None

    content = Content.from_function_result(call_id=call_id, result=result_payload)
    return Message(role="tool", contents=[content])


def _convert_reasoning_item(item: Any) -> Optional[Message]:
    data = _model_dump(item)
    summaries = data.get("summary", []) or []
    content_items = data.get("content", []) or []

    reasoning_contents: List[Any] = []
    for content in content_items:
        text = content.get("text") if isinstance(content, Mapping) else None
        if text:
            reasoning_contents.append(Content.from_text_reasoning(text=text))

    summary_text = " \n".join(
        summary.get("text")
        for summary in summaries
        if isinstance(summary, Mapping) and summary.get("text")
    )

    if not reasoning_contents and not summary_text:
        return None

    kwargs: Dict[str, Any] = {}
    if summary_text:
        kwargs["text"] = summary_text
    if reasoning_contents:
        kwargs["contents"] = reasoning_contents
    return Message(role="assistant", **kwargs)


def _convert_message_content(content: Any) -> Optional[Any]:
    content_type = str(getattr(content, "type", "")).lower()

    if content_type in {"input_text", "output_text", "text", "summary_text"}:
        text_value = getattr(content, "text", None)
        if text_value:
            return Content.from_text(text=text_value)

    if content_type == "reasoning_text":
        text_value = getattr(content, "text", None)
        if text_value:
            return Content.from_text_reasoning(text=text_value)

    if content_type == "refusal":
        refusal_text = getattr(content, "refusal", None)
        if refusal_text:
            return Content.from_text(text=refusal_text)

    return None


def _extract_call_arguments(data: Mapping[str, Any]) -> Any:
    if data.get("arguments") not in (None, ""):
        return data.get("arguments")
    if data.get("action") not in (None, {}):
        return data.get("action")

    payload = {
        key: value
        for key, value in data.items()
        if key not in {"id", "type", "status", "call_id", "name"}
    }
    return payload or None


def _extract_result_payload(data: Mapping[str, Any]) -> Any:
    for key in (
        "output",
        "outputs",
        "result",
        "results",
        "content",
    ):
        value = data.get(key)
        if value not in (None, [], {}, ""):
            return _normalize_result(value)

    payload = {
        key: value
        for key, value in data.items()
        if key not in {"id", "type", "status", "call_id", "name"}
    }
    return _normalize_result(payload) if payload else None


def _normalize_arguments(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        stripped_value = value.strip()
        return _normalize_result(stripped_value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="python", exclude_none=True)
    if isinstance(value, Mapping):
        return {key: _normalize_result(val) for key, val in value.items()}
    if isinstance(value, list):
        return {"items": [_normalize_result(item) for item in value]}
    return _normalize_result(value)


def _normalize_result(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_json_loads(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="python", exclude_none=True)
    if isinstance(value, list):
        return [_normalize_result(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _normalize_result(val) for key, val in value.items()}
    return value


def _safe_json_loads(value: str) -> Any:
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def _model_dump(item: Any) -> Mapping[str, Any]:
    if hasattr(item, "model_dump"):
        return item.model_dump(mode="python", exclude_none=True)
    if hasattr(item, "dict"):
        return item.dict()
    if hasattr(item, "__dict__"):
        return {
            key: value
            for key, value in item.__dict__.items()
            if not key.startswith("_")
        }
    return {}


def _resolve_call_id(data: Mapping[str, Any], default_prefix: str) -> str:
    candidate = data.get("call_id") or data.get("id")
    if candidate:
        return str(candidate)
    return f"{default_prefix or 'tool'}-{uuid4().hex}"


def _infer_action_name(data: Mapping[str, Any]) -> Optional[str]:
    action = data.get("action")
    if hasattr(action, "model_dump"):
        action = action.model_dump(mode="python", exclude_none=True)
    if isinstance(action, Mapping):
        return str(action.get("type") or action.get("name") or "").strip() or None
    return None


def _has_result_payload(item: Any) -> bool:
    for field in _RESULT_HINT_FIELDS:
        value = getattr(item, field, None)
        if value not in (None, [], {}, ""):
            return True
    return False
