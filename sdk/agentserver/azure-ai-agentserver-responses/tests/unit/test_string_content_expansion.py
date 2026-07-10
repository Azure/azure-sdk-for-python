# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for string-content handling in _get_input_text and get_content_expanded.

ItemMessage.content is Union[str, list[MessageContent]].  These tests verify
that string shorthand is correctly expanded into MessageContentInputTextContent
rather than being iterated character-by-character.
"""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.models._generated import (
    CreateResponse,
    ItemMessage,
    MessageContentInputTextContent,
    MessageRole,
)
from azure.ai.agentserver.responses.models._helpers import (
    _get_input_text,
    get_content_expanded,
    get_input_expanded,
)


# ---------------------------------------------------------------------------
# get_content_expanded — string content
# ---------------------------------------------------------------------------


def test_get_content_expanded__string_content_wraps_as_input_text() -> None:
    """A plain string content should become a single MessageContentInputTextContent."""
    msg = ItemMessage(role=MessageRole.USER, content="Hello world")
    parts = get_content_expanded(msg)

    assert len(parts) == 1
    assert isinstance(parts[0], MessageContentInputTextContent)
    assert parts[0].text == "Hello world"


def test_get_content_expanded__empty_string_returns_empty_list() -> None:
    """An empty string content should return an empty list."""
    msg = ItemMessage(role=MessageRole.USER, content="")
    parts = get_content_expanded(msg)

    assert parts == []


def test_get_content_expanded__list_content_passes_through() -> None:
    """A list[MessageContent] should pass through unchanged."""
    msg = ItemMessage(
        role=MessageRole.USER,
        content=[MessageContentInputTextContent(text="part1")],
    )
    parts = get_content_expanded(msg)

    assert len(parts) == 1
    assert parts[0].text == "part1"


def test_get_content_expanded__none_content_returns_empty() -> None:
    """None content should return an empty list."""
    msg = ItemMessage({"role": "user", "content": None})
    parts = get_content_expanded(msg)

    assert parts == []


# ---------------------------------------------------------------------------
# get_content_expanded — dict-based ItemMessage
# ---------------------------------------------------------------------------


def test_get_content_expanded__dict_with_string_content() -> None:
    """A dict-based ItemMessage with string content expands correctly."""
    msg = ItemMessage({"role": "user", "content": "dict string content"})
    parts = get_content_expanded(msg)

    assert len(parts) == 1
    assert isinstance(parts[0], MessageContentInputTextContent)
    assert parts[0].text == "dict string content"


# ---------------------------------------------------------------------------
# _get_input_text — string content inside ItemMessage
# ---------------------------------------------------------------------------


def test_get_input_text__message_with_string_content() -> None:
    """_get_input_text extracts text from a message whose content is a plain string."""
    request = CreateResponse(
        model="test",
        input=[
            ItemMessage(role=MessageRole.USER, content="Hello from string content"),
        ],
    )
    result = _get_input_text(request)
    assert result == "Hello from string content"


def test_get_input_text__mixed_string_and_list_content() -> None:
    """_get_input_text handles a mix of string-content and list-content messages."""
    request = CreateResponse(
        model="test",
        input=[
            ItemMessage(role=MessageRole.USER, content="First message"),
            ItemMessage(
                role=MessageRole.USER,
                content=[MessageContentInputTextContent(text="Second message")],
            ),
        ],
    )
    result = _get_input_text(request)
    assert result == "First message\nSecond message"


def test_get_input_text__string_input_shorthand() -> None:
    """When CreateResponse.input is a plain string, _get_input_text returns it."""
    request = CreateResponse(model="test", input="Just a string")
    result = _get_input_text(request)
    assert result == "Just a string"


def test_get_input_text__empty_string_content_skipped() -> None:
    """An empty-string content message contributes nothing to the result."""
    request = CreateResponse(
        model="test",
        input=[
            ItemMessage(role=MessageRole.USER, content=""),
            ItemMessage(role=MessageRole.USER, content="Real text"),
        ],
    )
    result = _get_input_text(request)
    assert result == "Real text"


def test_get_input_text__dict_message_with_string_content() -> None:
    """A raw dict message with string content is correctly extracted."""
    request = CreateResponse(
        model="test",
        input=[
            {"type": "message", "role": "user", "content": "dict string"},
        ],
    )
    result = _get_input_text(request)
    assert result == "dict string"


# ---------------------------------------------------------------------------
# get_input_expanded — auto-expands string content on ItemMessage items
# ---------------------------------------------------------------------------


def test_get_input_expanded__normalizes_string_content_to_list() -> None:
    """get_input_expanded auto-expands string content to list[MessageContent]."""
    request = CreateResponse(
        model="test",
        input=[
            ItemMessage(role=MessageRole.USER, content="expanded text"),
        ],
    )
    items = get_input_expanded(request)

    assert len(items) == 1
    msg = items[0]
    assert isinstance(msg, ItemMessage)
    # content should now be a list, not a string
    assert isinstance(msg.content, list)
    assert len(msg.content) == 1
    assert isinstance(msg.content[0], MessageContentInputTextContent)
    assert msg.content[0].text == "expanded text"


def test_get_input_expanded__list_content_unchanged() -> None:
    """get_input_expanded leaves list content untouched."""
    request = CreateResponse(
        model="test",
        input=[
            ItemMessage(
                role=MessageRole.USER,
                content=[MessageContentInputTextContent(text="already a list")],
            ),
        ],
    )
    items = get_input_expanded(request)

    msg = items[0]
    assert isinstance(msg.content, list)
    assert msg.content[0].text == "already a list"


def test_get_input_expanded__string_input_shorthand_already_list() -> None:
    """When input is a plain string, the generated ItemMessage already has list content."""
    request = CreateResponse(model="test", input="plain string input")
    items = get_input_expanded(request)

    msg = items[0]
    assert isinstance(msg, ItemMessage)
    assert isinstance(msg.content, list)
    assert msg.content[0].text == "plain string input"
