# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Helper functions for CreateResponse and Response model expansion."""

from __future__ import annotations

from typing import Any, Optional

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
    """Get *field* from a model instance or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def _is_type(obj: Any, model_cls: type, type_value: str) -> bool:
    """Check whether *obj* is *model_cls* or a dict with matching ``type``."""
    if isinstance(obj, model_cls):
        return True
    if isinstance(obj, dict):
        return obj.get("type") == type_value
    return False


# ---------------------------------------------------------------------------
# CreateResponse helpers
# ---------------------------------------------------------------------------


def get_conversation_id(request: CreateResponse) -> Optional[str]:
    """Extract conversation ID from ``CreateResponse.conversation``.

    If conversation is a plain string, returns it directly.
    If it is a :class:`ConversationParam_2` object, returns its ``id`` field.

    :param request: The create-response request.
    :type request: CreateResponse
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
    return items


def get_input_text(request: CreateResponse) -> str:
    """Extract all text content from ``CreateResponse.input`` as a single string.

    Expands input via :func:`get_input_expanded`, filters for
    :class:`ItemMessage` items, and joins all
    :class:`MessageContentInputTextContent` text values with newlines.

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
            return ToolChoiceAllowed(mode=normalized, tools=[])
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
                id="",
                status="completed",
                role=MessageRole.DEVELOPER,
                content=[MessageContentInputTextContent(text=instr)],
            ).as_dict()
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

    In Python the generated ``ItemMessage.content`` is already
    ``list[MessageContent]``, so this is a convenience passthrough that
    returns an empty list when content is ``None``.

    :param message: The item message.
    :type message: ItemMessage
    :returns: The message content parts.
    :rtype: list[MessageContent]
    """
    content = _get_field(message, "content")
    return list(content) if content else []
