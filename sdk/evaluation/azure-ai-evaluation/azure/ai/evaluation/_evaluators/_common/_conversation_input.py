# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Shared normalization for evaluators that accept a bare ``messages=[...]``
kwarg alongside optional scalar ``context``, ``ground_truth``, and
``tool_definitions`` kwargs. This is the shape produced by the SDK batch
engine when a customer's evaluation ``data_mapping`` targets ``messages``
plus adjunct fields; without normalization, evaluators whose ``__call__``
overloads only cover ``(query, response)`` + ``(conversation)`` reject the
input with either "No data to process" or
"Cannot provide both 'conversation' and individual inputs at the same time".
"""

from typing import Any, Dict


def hoist_messages_to_conversation(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Promote a bare ``messages=[...]`` kwarg into a
    ``conversation={"messages": [...], ...}`` dict so the base
    ``_derive_conversation_converter`` extracts per-turn ``query``/``response``
    for the judge.

    Behavior:

    - If ``conversation`` is already provided, or ``messages`` is not provided,
      ``kwargs`` is returned unchanged.
    - ``messages`` is moved to ``conversation["messages"]``.
    - ``context`` and ``tool_definitions`` scalars (if present) are moved into
      the same conversation dict so ``_derive_conversation_converter`` sees
      them as conversation-level attributes.
    - A top-level ``ground_truth`` scalar is stamped onto each ``assistant``
      turn that does not already carry a per-turn ``ground_truth`` field, so
      the base converter picks it up on the per-response extraction path.

    ``kwargs`` is modified in place; the same dict is returned for chaining.
    """
    if kwargs.get("conversation") is not None:
        return kwargs
    messages = kwargs.get("messages")
    if messages is None:
        return kwargs

    conv: Dict[str, Any] = {"messages": messages}

    context = kwargs.pop("context", None)
    if context is not None:
        conv["context"] = context

    tool_definitions = kwargs.pop("tool_definitions", None)
    if tool_definitions is not None:
        conv["tool_definitions"] = tool_definitions

    ground_truth = kwargs.pop("ground_truth", None)
    if ground_truth is not None and isinstance(messages, list):
        for message in messages:
            if (
                isinstance(message, dict)
                and message.get("role") == "assistant"
                and "ground_truth" not in message
            ):
                message["ground_truth"] = ground_truth

    kwargs["conversation"] = conv
    kwargs.pop("messages", None)
    return kwargs
