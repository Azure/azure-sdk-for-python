# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Helper functions for CreateResponse and Response model expansion."""

from __future__ import annotations

from typing import Any, Literal, Optional, cast

from ._generated import (
    ConversationParam_2,
    CreateResponse,
    Item,
    ItemMessage,
    MessageContent,
    MessageContentInputTextContent,
    MessageRole,
    OutputItem,
    ResponseObject,
    ToolChoiceAllowed,
    ToolChoiceOptions,
    ToolChoiceParam,
)
from ._generated.sdk.models._utils.model_base import _deserialize

# ---------------------------------------------------------------------------
# Internal utilities for dict-safe field access
# ---------------------------------------------------------------------------


def _get_field(obj: Any, field: str, default: Any = None) -> Any:
    """Get *field* from a model instance or a plain dict.

    :param obj: The model instance or dict to read from.
    :type obj: Any
    :param field: The field name to retrieve.
    :type field: str
    :param default: The default value if the field is missing.
    :type default: Any
    :returns: The field value, or *default*.
    :rtype: Any
    """
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def _is_type(obj: Any, model_cls: type, type_value: str) -> bool:
    """Check whether *obj* is *model_cls* or a dict with matching ``type``.

    :param obj: The object to check.
    :type obj: Any
    :param model_cls: The model class to check against.
    :type model_cls: type
    :param type_value: The string type discriminator to match in dicts.
    :type type_value: str
    :returns: True if *obj* matches the model class or type value.
    :rtype: bool
    """
    if isinstance(obj, model_cls):
        return True
    if isinstance(obj, dict):
        return obj.get("type") == type_value
    return False


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
    conv = request.conversation
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
    inp = request.input
    if inp is None:
        return []
    if isinstance(inp, str):
        return [
            ItemMessage(
                role=MessageRole.USER,
                content=[MessageContentInputTextContent(text=inp)],
            )
        ]
    # Normalize items: per the OpenAI spec, items without an explicit
    # ``type`` default to ``"message"`` (C-MSG-01 compliance).
    items: list[Item] = []
    for raw in inp:
        d = dict(raw) if isinstance(raw, dict) else raw
        if isinstance(d, dict) and "type" not in d:
            d = {**d, "type": "message"}
        if isinstance(d, Item):
            items.append(d)
        else:
            items.append(_deserialize(Item, d))

    # Auto-expand string content on message items so downstream consumers
    # always see list[MessageContent] (matches .NET ExpandContent behaviour).
    for item in items:
        if isinstance(item, ItemMessage) and isinstance(item.content, str):
            item.content = get_content_expanded(item)

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


def get_tool_choice_expanded(request: CreateResponse) -> Optional[ToolChoiceParam]:
    """Expand ``CreateResponse.tool_choice`` into a typed :class:`ToolChoiceParam`.

    String shorthands (``"auto"``, ``"required"``) are expanded to
    :class:`ToolChoiceAllowed` with the corresponding mode.
    ``"none"`` returns ``None``.

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: The typed tool choice, or ``None`` if unset or ``"none"``.
    :rtype: ToolChoiceParam | None
    :raises ValueError: If the tool_choice value is an unrecognized string.
    """
    tc = request.tool_choice
    if tc is None:
        return None
    if isinstance(tc, ToolChoiceParam):
        return tc
    if isinstance(tc, str):
        normalized = tc if not isinstance(tc, ToolChoiceOptions) else tc.value
        if normalized in ("auto", "required"):
            return ToolChoiceAllowed(mode=cast(Literal["auto", "required"], normalized), tools=[])
        if normalized == "none":
            return None
        raise ValueError(
            f"Unrecognized tool_choice string value: '{normalized}'. Expected 'auto', 'required', or 'none'."
        )
    # dict fallback — wrap in ToolChoiceParam if it has a "type" key
    if isinstance(tc, dict) and "type" in tc:
        return ToolChoiceParam(tc)
    return None


def get_conversation_expanded(request: CreateResponse) -> Optional[ConversationParam_2]:
    """Expand ``CreateResponse.conversation`` into a typed :class:`ConversationParam_2`.

    A plain string is treated as the conversation ID.

    :param request: The create-response request.
    :type request: CreateResponse
    :returns: The typed conversation parameter, or ``None``.
    :rtype: ConversationParam_2 | None
    """
    conv = request.conversation
    if conv is None:
        return None
    if isinstance(conv, ConversationParam_2):
        return conv
    if isinstance(conv, str):
        return ConversationParam_2(id=conv) if conv else None
    # dict fallback
    if isinstance(conv, dict):
        cid = conv.get("id")
        return ConversationParam_2(id=cid) if cid else None
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
    instr = response.instructions
    if instr is None:
        return []
    if isinstance(instr, str):
        return [
            ItemMessage(
                {
                    "id": "",
                    "status": "completed",
                    "role": MessageRole.DEVELOPER.value,
                    "content": [{"type": "input_text", "text": instr}],
                }
            )
        ]
    return list(instr)


# ---------------------------------------------------------------------------
# OutputItem helpers
# ---------------------------------------------------------------------------


def get_output_item_id(item: OutputItem) -> str:
    """Extract the ``id`` field from any :class:`OutputItem` subtype.

    The base :class:`OutputItem` class does not define ``id``, but all
    concrete subtypes do. Falls back to dict-style access for unknown
    subtypes.

    :param item: The output item to extract the ID from.
    :type item: OutputItem
    :returns: The item's ID.
    :rtype: str
    :raises ValueError: If the item has no valid ``id``.
    """
    item_id = _get_field(item, "id")
    if item_id is not None:
        return str(item_id)

    # Fallback: Model subclass supports Mapping protocol
    try:
        raw_id = item["id"]  # type: ignore[index]
        if raw_id is not None:
            return str(raw_id)
    except (KeyError, TypeError):
        pass

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
        return [MessageContentInputTextContent(text=content)] if content else []
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

    The conversion leverages ``_deserialize(OutputItem, data)`` which
    resolves the correct subtype via the ``type`` discriminator.  All 24
    input/output discriminator pairs share the same string values, so the
    dict representation produced by ``dict(item)`` is directly compatible
    with ``OutputItem`` deserialization.

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

    data = dict(item)
    data["id"] = item_id

    item_type = data.get("type", "")

    # ── Status handling (opt-in) ─────────────────────────────────────
    if item_type in _COMPLETED_STATUS_ITEM_TYPES:
        data["status"] = "completed"
    elif item_type in _PRESERVE_STATUS_ITEM_TYPES:
        pass  # keep the original status from the input item

    return _deserialize(OutputItem, data)


def to_item(output_item: OutputItem) -> Item | None:
    """Convert an :class:`OutputItem` back to the corresponding :class:`Item`.

    Both hierarchies share the same ``type`` discriminator values, so
    serialising an :class:`OutputItem` to a dict and deserializing as
    :class:`Item` produces the correct concrete subtype (e.g.
    :class:`OutputItemMessage` → :class:`ItemMessage`).

    Returns ``None`` if the output item type has no :class:`Item` counterpart.

    :param output_item: The output item to convert.
    :type output_item: OutputItem
    :returns: The corresponding input item, or ``None``.
    :rtype: Item | None
    """
    try:
        data = dict(output_item)
        return _deserialize(Item, data)
    except Exception:  # pylint: disable=broad-except
        return None
