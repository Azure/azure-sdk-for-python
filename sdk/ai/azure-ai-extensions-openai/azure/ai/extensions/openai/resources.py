# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Accessors for OpenAI SDK resource classes used by Azure AI instrumentation."""

from __future__ import annotations

from typing import Any


def responses_module() -> Any:
    """Return the OpenAI responses resources module."""
    import openai.resources.responses as module

    return module


def conversations_class() -> type[Any]:
    """Return the synchronous OpenAI conversations resource class."""
    from openai.resources.conversations.conversations import Conversations

    return Conversations


def async_conversations_class() -> type[Any]:
    """Return the asynchronous OpenAI conversations resource class."""
    from openai.resources.conversations.conversations import AsyncConversations

    return AsyncConversations


def conversation_items_class() -> type[Any]:
    """Return the synchronous OpenAI conversation items resource class."""
    from openai.resources.conversations.items import Items

    return Items


def async_conversation_items_class() -> type[Any]:
    """Return the asynchronous OpenAI conversation items resource class."""
    from openai.resources.conversations.items import AsyncItems

    return AsyncItems


__all__ = [
    "async_conversation_items_class",
    "async_conversations_class",
    "conversation_items_class",
    "conversations_class",
    "responses_module",
]
