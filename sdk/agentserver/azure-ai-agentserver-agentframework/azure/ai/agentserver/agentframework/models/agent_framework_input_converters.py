# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=too-many-nested-blocks,too-many-return-statements,too-many-branches
# mypy: disable-error-code="no-redef"
from __future__ import annotations

from typing import Dict, List

from agent_framework import ChatMessage, Role as ChatRole
from agent_framework._types import TextContent

from azure.ai.agentserver.core.logger import get_logger

logger = get_logger()


class AgentFrameworkInputConverter:
    """Normalize inputs for agent.run.

    Accepts: str | List | None
    Returns: None | str | ChatMessage | list[str] | list[ChatMessage]
    """

    def transform_input(
        self,
        input: str | List[Dict] | None,
    ) -> str | ChatMessage | list[str] | list[ChatMessage] | None:
        logger.debug("Transforming input of type: %s", type(input))

        if input is None:
            return None

        if isinstance(input, str):
            return input

        try:
            if isinstance(input, list):
                messages: list[str | ChatMessage] = []

                for item in input:
                    # Case 1: ImplicitUserMessage with content as str or list of ItemContentInputText
                    if self._is_implicit_user_message(item):
                        content = item.get("content", None)
                        if isinstance(content, str):
                            messages.append(content)
                        elif isinstance(content, list):
                            text_parts: list[str] = []
                            for content_item in content:
                                text_content = self._extract_input_text(content_item)
                                if text_content:
                                    text_parts.append(text_content)
                            if text_parts:
                                messages.append(" ".join(text_parts))

                    # Case 2: Explicit message params (user/assistant/system)
                    elif (
                        item.get("type") == "message"
                        and item.get("role") is not None
                        and item.get("content") is not None
                    ):
                        role_map = {
                            "user": ChatRole.USER,
                            "assistant": ChatRole.ASSISTANT,
                            "system": ChatRole.SYSTEM,
                        }
                        role = role_map.get(item.get("role", "user"), ChatRole.USER)

                        content_text = ""
                        item_content = item.get("content", None)
                        if item_content and isinstance(item_content, list):
                            text_parts: list[str] = []
                            for content_item in item_content:
                                item_text = self._extract_input_text(content_item)
                                if item_text:
                                    text_parts.append(item_text)
                            content_text = " ".join(text_parts) if text_parts else ""
                        elif item_content and isinstance(item_content, str):
                            content_text = str(item_content)

                        if content_text:
                            messages.append(ChatMessage(role=role, text=content_text))

                # Determine the most natural return type
                if not messages:
                    return None
                if len(messages) == 1:
                    return messages[0]
                if all(isinstance(m, str) for m in messages):
                    return [m for m in messages if isinstance(m, str)]
                if all(isinstance(m, ChatMessage) for m in messages):
                    return [m for m in messages if isinstance(m, ChatMessage)]

                # Mixed content: coerce ChatMessage to str by extracting TextContent parts
                result: list[str] = []
                for msg in messages:
                    if isinstance(msg, ChatMessage):
                        text_parts: list[str] = []
                        for c in getattr(msg, "contents", []) or []:
                            if isinstance(c, TextContent):
                                text_parts.append(c.text)
                        result.append(" ".join(text_parts) if text_parts else str(msg))
                    else:
                        result.append(str(msg))
                return result

            raise TypeError(f"Unsupported input type: {type(input)}")
        except Exception as e:
            logger.error("Error processing messages: %s", e, exc_info=True)
            raise Exception(f"Error processing messages: {e}") from e  # pylint: disable=broad-exception-raised

    def _is_implicit_user_message(self, item: Dict) -> bool:
        return "content" in item and "role" not in item and "type" not in item

    def _extract_input_text(self, content_item: Dict) -> str:
        if content_item.get("type") == "input_text" and "text" in content_item:
            text_content = content_item.get("text")
            if isinstance(text_content, str):
                return text_content
        return None  # type: ignore
