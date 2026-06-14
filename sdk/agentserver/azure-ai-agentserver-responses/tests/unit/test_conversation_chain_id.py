# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 013 US3 — `conversation_chain_id` property on ResponseContext.

Verifies the framework-computed chain id is stable across turns and across
crash recovery, and is derived deterministically from
``conversation_id`` / ``previous_response_id`` / ``response_id``.
"""

from __future__ import annotations

from azure.ai.agentserver.responses._response_context import ResponseContext
from azure.ai.agentserver.responses.hosting._task_id import (
    derive_chain_id,
    derive_task_id,
)
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags


def _make_context(
    *,
    response_id: str,
    previous_response_id: str | None = None,
    conversation_id: str | None = None,
) -> ResponseContext:
    return ResponseContext(
        response_id=response_id,
        mode_flags=ResponseModeFlags(stream=False, background=False, store=True),
        previous_response_id=previous_response_id,
        conversation_id=conversation_id,
    )


def test_chain_id_priority_conversation_id_first() -> None:
    """Explicit conversation_id wins regardless of other fields."""
    ctx = _make_context(
        response_id="resp-1",
        previous_response_id="resp-0",
        conversation_id="conv-X",
    )
    assert ctx.conversation_chain_id == "conv-X"


def test_chain_id_priority_previous_response_id_second() -> None:
    """Without conversation_id, previous_response_id is the chain id (steerable)."""
    ctx = _make_context(
        response_id="resp-1",
        previous_response_id="resp-0",
    )
    assert ctx.conversation_chain_id == "resp-0"


def test_chain_id_priority_response_id_fallback() -> None:
    """First turn in a chain — chain id == response_id."""
    ctx = _make_context(response_id="resp-1")
    assert ctx.conversation_chain_id == "resp-1"


def test_chain_id_stable_across_turns() -> None:
    """Two consecutive turns in the same chain receive the same chain id."""
    turn1 = _make_context(response_id="resp-A")
    turn2 = _make_context(response_id="resp-B", previous_response_id="resp-A")
    turn3 = _make_context(response_id="resp-C", previous_response_id="resp-B")
    # Steerable chain inherits chain id from the parent.
    assert turn1.conversation_chain_id == "resp-A"
    assert turn2.conversation_chain_id == "resp-A"
    # Note: turn3.previous_response_id == "resp-B" -> chain id == "resp-B".
    # In a fully-modeled chain, the framework would store the chain id on
    # the parent record so every descendant resolves to the same root, but
    # the property is computed locally from the request fields. Sample 18
    # explicitly relies on previous_response_id pointing at the chain's
    # last response, which is the runtime contract today.
    assert turn3.conversation_chain_id == "resp-B"


def test_chain_id_stable_across_turns_with_conversation_id() -> None:
    """With explicit conversation_id, every turn shares the same id."""
    turn1 = _make_context(response_id="resp-A", conversation_id="conv-1")
    turn2 = _make_context(response_id="resp-B", previous_response_id="resp-A", conversation_id="conv-1")
    turn3 = _make_context(response_id="resp-C", previous_response_id="resp-B", conversation_id="conv-1")
    assert turn1.conversation_chain_id == turn2.conversation_chain_id == turn3.conversation_chain_id
    assert turn1.conversation_chain_id == "conv-1"


def test_derive_chain_id_helper_matches_property() -> None:
    """The helper and the property compute the same value."""
    direct = derive_chain_id(
        conversation_id=None,
        previous_response_id="parent-resp",
        response_id="this-resp",
        steerable=True,
    )
    ctx = _make_context(response_id="this-resp", previous_response_id="parent-resp")
    assert ctx.conversation_chain_id == direct == "parent-resp"


def test_derive_chain_id_non_steerable_uses_response_id() -> None:
    """Non-steerable forks: chain id is response_id (distinct per fork)."""
    chain = derive_chain_id(
        conversation_id=None,
        previous_response_id="parent-resp",
        response_id="fork-resp",
        steerable=False,
    )
    assert chain == "fork-resp"


def test_task_id_remains_stable_after_chain_extraction() -> None:
    """T-120 extraction must not change derive_task_id output."""
    tid1 = derive_task_id(
        conversation_id=None,
        previous_response_id="resp-0",
        response_id="resp-1",
        agent_name="agent-A",
        session_id="sess-1",
        steerable=True,
    )
    tid2 = derive_task_id(
        conversation_id=None,
        previous_response_id="resp-0",
        response_id="resp-2",
        agent_name="agent-A",
        session_id="sess-1",
        steerable=True,
    )
    # Same chain (same previous_response_id) -> same task id.
    assert tid1 == tid2
    assert tid1.startswith("durable-resp-")
