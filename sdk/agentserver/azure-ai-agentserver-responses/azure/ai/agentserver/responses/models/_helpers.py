# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Helper functions for CreateResponse and Response model expansion."""

from __future__ import annotations

from typing import Any, Optional, cast

from azure.ai.agentserver.responses.models._wire import get_field as _get_field
from azure.ai.agentserver.responses.models._wire import is_type as _is_wire_type
from azure.ai.agentserver.responses.models import (
    ConversationParam_2,
    CreateResponse,
    Item,
    ItemMessage,
    MessageContent,
    MessageContentInputTextContent,
    OutputItem,
    ResponseObject,
)


def _is_type(obj: Any, _model_cls: type, type_value: str) -> bool:
    """Check whether *obj* has a matching wire ``type`` discriminator.

    :param obj: The object to check.
    :type obj: Any
    :param _model_cls: Retained for call-site readability; ignored at runtime.
    :type _model_cls: type
    :param type_value: The string type discriminator to match in dicts.
    :type type_value: str
    :returns: True if *obj* matches the wire type value.
    :rtype: bool
    """
    return _is_wire_type(obj, type_value)


def is_item_reference(item: Any) -> bool:
    """Return whether *item* is an item reference payload.

    Item references are identified by OpenAI's typed ``item_reference`` shape,
    or by the legacy id-only shorthand.

    :param item: The item payload to inspect.
    :type item: Any
    :returns: ``True`` if the item is an item reference payload.
    :rtype: bool
    """
    if not isinstance(item, dict):
        return False
    if item.get("type") == "item_reference":
        return "id" in item
    return "id" in item and "type" not in item and "role" not in item and "content" not in item


def _ensure_item_type(data: dict[str, Any]) -> dict[str, Any]:
    if "type" in data or is_item_reference(data):
        return data
    if "role" in data or "content" in data:
        return {**data, "type": "message"}
    return data


# ---------------------------------------------------------------------------
# CreateResponse helpers
# ---------------------------------------------------------------------------


def get_conversation_id(request: CreateResponse | ResponseObject) -> Optional[str]:
    """Extract conversation ID from a request or response's ``conversation`` field.

    If conversation is a plain string, returns it directly.
    If it is a :class:`ConversationParam_2` object, returns its ``id`` field.

    :param request: The create-response request or response object.
    :type request: CreateResponse | ResponseObject
    :returns: The conversation ID, or ``None`` if no conversation is set.
    :rtype: str | None
    """
    conv = _get_field(request, "conversation")
    if conv is None:
        return None
    if isinstance(conv, str):
        return conv or None
    # Model instance or plain dict
    cid = _get_field(conv, "id")
    return str(cid) if cid else None


def get_input_expanded(request: CreateResponse) -> list[Item]:
    """Normalize ``CreateResponse.input`` into a list of :class:`Item`.

    - If input is ``None``, returns ``[]``.
    - If input is a string, wraps it as a single :class:`ItemMessage` with
      ``role=user`` and :class:`MessageContentInputTextContent`.
    - If input is already a list, each element is deserialized into the appropriate
      :class:`Item` subclass (e.g., :class:`ItemMessage`, :class:`FunctionCallOutputItemParam`).

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: A list of typed input items.
    :rtype: list[Item]
    """
    inp = _get_field(request, "input")
    if inp is None:
        return []
    if isinstance(inp, str):
        return [
            cast(
                Item,
                {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": inp}],
                },
            )
        ]
    # Normalize items: per the OpenAI spec, items without an explicit
    # ``type`` default to ``"message"`` (C-MSG-01 compliance).
    items: list[Item] = []
    for raw in inp:
        if isinstance(raw, dict):
            item_dict = _ensure_item_type(dict(raw))
            # Auto-expand string content on message items so downstream consumers
            # always see list[MessageContent] (matches .NET ExpandContent behaviour).
            if _is_type(item_dict, ItemMessage, "message") and isinstance(_get_field(item_dict, "content"), str):
                item_dict["content"] = get_content_expanded(cast(ItemMessage, item_dict))
            items.append(cast(Item, item_dict))
        else:
            items.append(raw)

    return items


def _get_input_text(request: CreateResponse) -> str:
    """Extract all text content from ``CreateResponse.input`` as a single string.

    Internal helper — callers should use :meth:`ResponseContext.get_input_text`.

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: The combined text content, or ``""`` if no text found.
    :rtype: str
    """
    items = get_input_expanded(request)
    texts: list[str] = []
    for item in items:
        if _is_type(item, ItemMessage, "message"):
            for part in _get_field(item, "content") or []:
                if _is_type(part, MessageContentInputTextContent, "input_text"):
                    text = _get_field(part, "text")
                    if text is not None:
                        texts.append(text)
    return "\n".join(texts)


def get_tool_choice_expanded(request: CreateResponse) -> dict[str, Any] | None:
    """Expand ``CreateResponse.tool_choice`` into a tool choice payload.

    String shorthands (``"auto"``, ``"required"``) are expanded to
    :class:`ToolChoiceAllowed` with the corresponding mode.
    ``"none"`` returns ``None``.

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: The tool choice payload, or ``None`` if unset or ``"none"``.
    :rtype: dict[str, Any] | None
    :raises ValueError: If the tool_choice value is an unrecognized string.
    """
    tc = _get_field(request, "tool_choice")
    if tc is None:
        return None
    if isinstance(tc, dict) and "type" in tc:
        return cast(dict[str, Any], tc)
    if isinstance(tc, str):
        normalized = getattr(tc, "value", tc)
        if normalized in ("auto", "required"):
            return {"type": "allowed_tools", "mode": normalized, "tools": []}
        if normalized == "none":
            return None
        raise ValueError(
            f"Unrecognized tool_choice string value: '{normalized}'. Expected 'auto', 'required', or 'none'."
        )
    return None


def get_conversation_expanded(request: CreateResponse) -> Optional[ConversationParam_2]:
    """Expand ``CreateResponse.conversation`` into a typed :class:`ConversationParam_2`.

    A plain string is treated as the conversation ID.

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: The typed conversation parameter, or ``None``.
    :rtype: ConversationParam_2 | None
    """
    conv = _get_field(request, "conversation")
    if conv is None:
        return None
    if isinstance(conv, dict) and conv.get("id"):
        return cast(ConversationParam_2, conv)
    if isinstance(conv, str):
        return cast(ConversationParam_2, {"id": conv}) if conv else None
    return None


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------


def get_instruction_items(response: ResponseObject) -> list[Item]:
    """Expand ``Response.instructions`` into a list of :class:`Item`.

    - If instructions is ``None``, returns ``[]``.
    - If instructions is a string, wraps it as a single :class:`ItemMessage`
      with ``role=developer`` and :class:`MessageContentInputTextContent`.
    - If instructions is already a list, returns a shallow copy.

    :param response: The response object.
    :type response: ResponseObject
    :returns: A list of instruction items.
    :rtype: list[Item]
    """
    instr = _get_field(response, "instructions")
    if instr is None:
        return []
    if isinstance(instr, str):
        return [
            {
                "type": "message",
                "role": "developer",
                "content": [{"type": "input_text", "text": instr}],
            }
        ]
    return list(instr)


# ---------------------------------------------------------------------------
# OutputItem helpers
# ---------------------------------------------------------------------------


def get_output_item_id(item: OutputItem) -> str:
    """Extract the ``id`` field from any :class:`OutputItem` subtype.

    All concrete output item wire payloads must include an ``id`` field.

    :param item: The output item to extract the ID from.
    :type item: OutputItem
    :returns: The item's ID.
    :rtype: str
    :raises ValueError: If the item has no valid ``id``.
    """
    item_id = _get_field(item, "id")
    if item_id is not None:
        return str(item_id)

    raise ValueError(
        f"OutputItem of type '{type(item).__name__}' does not have a valid id. "
        "Ensure the id property is set before accessing it."
    )


# ---------------------------------------------------------------------------
# ItemMessage helpers
# ---------------------------------------------------------------------------


def get_content_expanded(message: ItemMessage) -> list[MessageContent]:
    """Return the typed content list from an :class:`ItemMessage`.

    If ``content`` is a plain string (the API allows a string shorthand),
    it is wrapped as a single :class:`MessageContentInputTextContent`.
    If it is already a list, returns a shallow copy.
    Returns an empty list when content is ``None``.

    :param message: The item message.
    :type message: ItemMessage
    :returns: The message content parts.
    :rtype: list[MessageContent]
    """
    content = _get_field(message, "content")
    if content is None:
        return []
    if isinstance(content, str):
        return cast(list[MessageContent], [{"type": "input_text", "text": content}]) if content else []
    return list(content)


# ---------------------------------------------------------------------------
# Item → OutputItem conversion
# ---------------------------------------------------------------------------

# Item types whose OutputItem counterpart has a ``status`` field AND should
# be set to ``"completed"`` during conversion.  This is an **opt-in** list:
# any item type NOT listed here will NOT receive a status value.  This
# prevents newly-added item types from accidentally gaining a status field.
_COMPLETED_STATUS_ITEM_TYPES = frozenset(
    {
        "message",  # OutputItemMessage
        "function_call",  # OutputItemFunctionToolCall
        "function_call_output",  # FunctionToolCallOutputResource
        "computer_call",  # OutputItemComputerToolCall
        "computer_call_output",  # OutputItemComputerToolCallOutputResource
        "file_search_call",  # OutputItemFileSearchToolCall
        "web_search_call",  # OutputItemWebSearchToolCall
        "image_generation_call",  # OutputItemImageGenToolCall
        "code_interpreter_call",  # OutputItemCodeInterpreterToolCall
        "local_shell_call",  # OutputItemLocalShellToolCall
        "local_shell_call_output",  # OutputItemLocalShellToolCallOutput
        "shell_call",  # OutputItemFunctionShellCall
        "shell_call_output",  # OutputItemFunctionShellCallOutput
        "mcp_call",  # OutputItemMcpToolCall
        "reasoning",  # OutputItemReasoningItem
    }
)

# Item types whose original status should be preserved as-is rather than
# overwritten.  The enum string values are identical between Param and
# Output models (e.g. ``"in_progress"``, ``"completed"``), so the dict
# representation transfers directly.
_PRESERVE_STATUS_ITEM_TYPES = frozenset(
    {
        "output_message",  # ItemOutputMessage – status semantics preserved
        "apply_patch_call",  # ApplyPatchToolCallItemParam → ApplyPatchCallStatus
        "apply_patch_call_output",  # ApplyPatchToolCallOutputItemParam → ApplyPatchCallOutputStatus
    }
)


def to_output_item(item: Item, response_id: str | None = None) -> OutputItem | None:
    """Convert an :class:`Item` to the corresponding :class:`OutputItem`.

    Generates a type-specific ID via :meth:`IdGenerator.new_item_id` and
    applies status according to per-type rules:

    * **Completed** — explicitly listed types get ``status = "completed"``.
    * **Preserve status** — types whose original status must be kept
      (``ItemOutputMessage``, ``ApplyPatch*``).
    * **No status** — all other types (including any future types) receive
      no status value.  This opt-in design prevents newly-added item types
      from accidentally gaining a status field.

    Returns ``None`` for :class:`ItemReferenceParam` or unrecognised types.

    The input/output discriminator pairs share the same string values, so the
    item wire payload is directly compatible with the output item wire contract.

    :param item: The input item to convert.
    :type item: Item
    :param response_id: An existing ID (typically the response ID) used as
        a partition-key hint for the generated item ID.
    :type response_id: str | None
    :returns: The converted output item, or ``None`` if non-convertible.
    :rtype: OutputItem | None
    """
    # Avoid circular import — IdGenerator lives one level up.
    from .._id_generator import IdGenerator

    item_id = IdGenerator.new_item_id(item, response_id)
    if item_id is None:
        return None  # ItemReferenceParam or unrecognised

    data = _ensure_item_type(dict(item))
    data["id"] = item_id

    item_type = data.get("type", "")

    # ── Status handling (opt-in) ─────────────────────────────────────
    if item_type in _COMPLETED_STATUS_ITEM_TYPES:
        data["status"] = "completed"
    elif item_type in _PRESERVE_STATUS_ITEM_TYPES:
        pass  # keep the original status from the input item

    return cast(OutputItem, data)


def to_item(output_item: OutputItem) -> Item | None:
    """Convert an :class:`OutputItem` back to the corresponding :class:`Item`.

    Both hierarchies share the same ``type`` discriminator values, so the
    output item's wire dict is directly compatible with the input item contract
    (e.g. ``OutputItemMessage`` → ``ItemMessage``).

    Returns ``None`` if the output item type has no :class:`Item` counterpart.

    :param output_item: The output item to convert.
    :type output_item: OutputItem
    :returns: The corresponding input item, or ``None``.
    :rtype: Item | None
    """
    if not isinstance(output_item, dict):
        return None
    if output_item.get("type") == "output_message":
        return cast(Item, {**output_item, "type": "message"})
    item = _ensure_item_type(dict(output_item))
    if "type" not in item:
        return None
    return cast(Item, item)
