# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="no-redef"
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from agent_framework import Content, Message

from azure.ai.agentserver.core.logger import get_logger

logger = get_logger()


class AgentFrameworkInputConverter:
    """Normalize inputs for agent.run with optional Human-In-The-Loop handling."""

    def __init__(self, *, hitl_helper=None) -> None:
        self._hitl_helper = hitl_helper

    async def transform_input(  # pylint: disable=too-many-return-statements
        self,
        input_item: Optional[Union[str, List[Dict]]],
        agent_session: Any = None,
        checkpoint: Any = None,
    ) -> Optional[Union[str, Message, List[Union[str, Message]]]]:
        if self._hitl_helper and isinstance(input_item, list):
            session_messages: List[Message] = []
            if agent_session is not None:
                message_store = getattr(agent_session, "message_store", None)
                if message_store and hasattr(message_store, "list_messages"):
                    session_messages = await message_store.list_messages()
                else:
                    session_messages = getattr(agent_session, "messages", None) or []

            pending_hitl_requests = self._hitl_helper.get_pending_hitl_request(session_messages, checkpoint)
            if pending_hitl_requests:
                hitl_response = self._hitl_helper.validate_and_convert_hitl_response(
                    input_item,
                    pending_requests=pending_hitl_requests,
                )
                if hitl_response:
                    return hitl_response

        return transform_input(input_item)


def transform_input(  # pylint: disable=too-many-return-statements
    input_item: Optional[Union[str, List[Dict]]],
) -> Optional[Union[str, Message, List[Union[str, Message]]]]:
    """Normalize inputs for agent.run.

    Accepts: Optional[Union[str, List]]
    Returns: Optional[Union[str, Message, List[Union[str, Message]]]]

    :param input_item: The raw input to normalize.
    :type input_item: str or List[Dict] or None
    """
    logger.debug("Transforming input of type: %s", type(input_item))

    if input_item is None:
        return None

    if isinstance(input_item, str):
        return input_item

    try:
        if isinstance(input_item, list):
            messages: List[Union[str, Message]] = []

            for item in input_item:
                match item:
                    # Case 1: ImplicitUserMessage — no "role" or "type" key
                    case {"content": content} if "role" not in item and "type" not in item:
                        messages.extend(_parse_implicit_user_content(content))

                    # Case 2: Explicit message with role
                    case {"type": "message", "role": role, "content": content}:
                        _parse_explicit_message(role, content, messages)

            # Determine the most natural return type
            if not messages:
                return None
            if len(messages) == 1:
                return messages[0]
            if all(isinstance(m, str) for m in messages):
                return [m for m in messages if isinstance(m, str)]
            if all(isinstance(m, Message) for m in messages):
                return [m for m in messages if isinstance(m, Message)]

            # Mixed content: coerce Message to str by extracting text content parts
            return _coerce_to_strings(messages)

        raise TypeError(f"Unsupported input type: {type(input_item)}")
    except Exception as e:
        logger.debug("Error processing messages: %s", e, exc_info=True)
        raise Exception(f"Error processing messages: {e}") from e  # pylint: disable=broad-exception-raised


def _parse_implicit_user_content(content: Optional[Union[str, List[Any]]]) -> List[str]:
    """Extract text from an implicit user message (no role/type keys).

    :param content: The content to parse.
    :type content: str or list or None
    :return: A list of extracted text strings.
    :rtype: List[str]
    """
    match content:
        case str():
            return [content]
        case list():
            text_parts = [_extract_input_text(item) for item in content]
            joined = " ".join(t for t in text_parts if t)
            return [joined] if joined else []
        case _:
            return []


def _parse_explicit_message(
    role: str,
    content: Optional[Union[str, List[Any]]],
    sink: List[Union[str, Message]],
) -> None:
    """Parse an explicit message dict and append to sink.

    :param role: The role of the message sender.
    :type role: str
    :param content: The message content.
    :type content: str or list or None
    :param sink: The list to append parsed messages to.
    :type sink: List[Union[str, Message]]
    """
    match role:
        case "user" | "assistant" | "system" | "tool":
            pass
        case _:
            raise ValueError(f"Unsupported message role: {role!r}")

    content_text = ""
    match content:
        case str():
            content_text = content
        case list():
            text_parts = [_extract_input_text(item) for item in content]
            content_text = " ".join(t for t in text_parts if t)

    if content_text:
        sink.append(Message(role=role, contents=[Content.from_text(content_text)]))


def _coerce_to_strings(messages: List[Union[str, Message]]) -> List[Union[str, Message]]:
    """Coerce a mixed list of str/Message into all strings.

    :param messages: The mixed list of strings and Messages.
    :type messages: List[Union[str, Message]]
    :return: A list with Messages coerced to strings.
    :rtype: List[Union[str, Message]]
    """
    result: List[Union[str, Message]] = []
    for msg in messages:
        match msg:
            case Message():
                text_parts = [c.text for c in (getattr(msg, "contents", None) or []) if c.type == "text"]
                result.append(" ".join(text_parts) if text_parts else str(msg))
            case str():
                result.append(msg)
    return result


def _extract_input_text(content_item: Dict) -> Optional[str]:
    match content_item:
        case {"type": "input_text", "text": str() as text}:
            return text
        case _:
            return None
