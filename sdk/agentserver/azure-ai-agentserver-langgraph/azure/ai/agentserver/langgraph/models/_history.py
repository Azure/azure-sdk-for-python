# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helpers for merging and filtering LangGraph message history."""

import logging
from typing import Any

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage

logger = logging.getLogger(__name__)


def normalize_content(content: Any) -> str:
    """Normalize message content to a string for comparison.

    Handles both plain strings and structured content lists.

    :param content: The message content (string or list of content items).
    :type content: Any
    :return: Normalized string content.
    :rtype: str
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") in ("text", "input_text", "output_text"):
                    text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        return "".join(text_parts)
    return str(content) if content else ""


def merge_messages_without_duplicates(
    historical_messages: list[AnyMessage],
    current_messages: list[AnyMessage],
    conversation_id: str,
) -> list[AnyMessage]:
    """Merge historical messages with current messages, filtering out trailing duplicates.

    Only considers it a duplicate if the last N historical messages match exactly
    with all N current messages as a whole sequence.

    :param historical_messages: Messages fetched from historical conversation items.
    :type historical_messages: list[AnyMessage]
    :param current_messages: Messages from the current request input.
    :type current_messages: list[AnyMessage]
    :param conversation_id: The conversation ID (used for logging).
    :type conversation_id: str
    :return: Merged list with historical messages prepended, duplicates removed.
    :rtype: list[AnyMessage]
    """
    if not current_messages or not historical_messages:
        merged = list(historical_messages) + list(current_messages)
        logger.info(
            "Merged %d historical items with %d current items for conversation %s",
            len(historical_messages), len(current_messages), conversation_id,
        )
        return merged

    n = len(current_messages)
    filtered_historical = list(historical_messages)

    if len(filtered_historical) >= n:
        last_n_historical = filtered_historical[-n:]
        all_match = True
        for i in range(n):
            hist_msg = last_n_historical[i]
            curr_msg = current_messages[i]
            hist_type = type(hist_msg).__name__
            curr_type = type(curr_msg).__name__
            hist_content = normalize_content(hist_msg.content if hasattr(hist_msg, "content") else "")
            curr_content = normalize_content(curr_msg.content if hasattr(curr_msg, "content") else "")
            logger.debug(
                "Comparing message %d: historical(%s, '%s') vs current(%s, '%s')",
                i, hist_type, hist_content, curr_type, curr_content,
            )
            if hist_type != curr_type:
                logger.debug("Message %d type mismatch: %s != %s", i, hist_type, curr_type)
                all_match = False
                break
            if hist_content != curr_content:
                logger.debug("Message %d content mismatch", i)
                all_match = False
                break

        if all_match:
            filtered_historical = filtered_historical[:-n]
            logger.info("Filtered %d duplicate items from end of historical items", n)

    merged = filtered_historical + list(current_messages)
    logger.info(
        "Merged %d historical items with %d current items for conversation %s",
        len(filtered_historical), len(current_messages), conversation_id,
    )
    return merged


def filter_incomplete_tool_calls(messages: list[AnyMessage]) -> list[AnyMessage]:
    """Filter out incomplete tool call sequences and reorder messages.

    ToolMessages are placed immediately after their corresponding AIMessage
    with ``tool_calls``. AIMessages whose tool calls have no matching
    ToolMessage response are dropped entirely.

    :param messages: List of messages to filter and reorder.
    :type messages: list[AnyMessage]
    :return: Filtered and reordered list of messages.
    :rtype: list[AnyMessage]
    """
    tool_responses: dict[str, ToolMessage] = {}
    for msg in messages:
        if isinstance(msg, ToolMessage) and hasattr(msg, "tool_call_id"):
            tool_responses[msg.tool_call_id] = msg

    result: list[AnyMessage] = []
    removed_count = 0

    for msg in messages:
        if isinstance(msg, ToolMessage):
            # Skip here; added after their AIMessage below
            continue

        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_call_ids = []
            for tc in msg.tool_calls:
                tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                if tc_id:
                    tool_call_ids.append(tc_id)

            if not all(tc_id in tool_responses for tc_id in tool_call_ids):
                removed_count += 1
                continue

            result.append(msg)
            for tc_id in tool_call_ids:
                if tc_id in tool_responses:
                    result.append(tool_responses[tc_id])
        else:
            result.append(msg)

    if removed_count > 0:
        logger.info("Filtered %d messages with incomplete tool call sequences", removed_count)

    return result
