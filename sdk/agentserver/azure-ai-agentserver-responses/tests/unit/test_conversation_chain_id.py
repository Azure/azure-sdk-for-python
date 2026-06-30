# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 013 US3 + Spec 036 — `conversation_chain_id` on ResponseContext.

The chain id is the stable, agent/session-scoped hash of the partition key
embedded in a chain's response IDs. Because chained response IDs all inherit one
partition key, every turn resolves to the SAME chain id — the property the
earlier raw-``previous_response_id`` derivation failed to provide. ``task_id`` is
the same hash with a fixed prefix.
"""

from __future__ import annotations

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses._response_context import ResponseContext
from azure.ai.agentserver.responses.hosting._chain_id import derive_conversation_chain_id
from azure.ai.agentserver.responses.hosting._task_id import derive_task_id
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

_AGENT = "agent-A"
_SESSION = "sess-1"


def _make_context(
    *,
    response_id: str,
    previous_response_id: str | None = None,
    conversation_id: str | None = None,
    steerable: bool = True,
    agent_name: str = _AGENT,
    session_id: str = _SESSION,
) -> ResponseContext:
    """Build a context with default ``steerable=True`` (sequential-chain semantics)."""
    return ResponseContext(
        response_id=response_id,
        mode_flags=ResponseModeFlags(stream=False, background=False, store=True),
        previous_response_id=previous_response_id,
        conversation_id=conversation_id,
        steerable=steerable,
        agent_name=agent_name,
        session_id=session_id,
    )


def _chain_id(**kw) -> str:
    return derive_conversation_chain_id(agent_name=_AGENT, session_id=_SESSION, **kw)


def test_chain_id_priority_conversation_id_first() -> None:
    """conversation_id wins over previous_response_id."""
    ctx = _make_context(response_id="resp-1", previous_response_id="resp-0", conversation_id="conv-X")
    assert ctx.conversation_chain_id == _chain_id(
        conversation_id="conv-X", previous_response_id="resp-0", response_id="resp-1", steerable=True
    )


def test_chain_id_stable_across_real_chain() -> None:
    """A real previous_response_id chain shares ONE chain id across ALL turns.

    Regression for the old bug where the chain id flipped from turn 3 onward
    (it returned the raw immediate predecessor instead of the shared partition).
    """
    root = IdGenerator.new_response_id("")
    turn2 = IdGenerator.new_response_id(root)
    turn3 = IdGenerator.new_response_id(turn2)
    turn4 = IdGenerator.new_response_id(turn3)

    c1 = _make_context(response_id=root).conversation_chain_id
    c2 = _make_context(response_id=turn2, previous_response_id=root).conversation_chain_id
    c3 = _make_context(response_id=turn3, previous_response_id=turn2).conversation_chain_id
    c4 = _make_context(response_id=turn4, previous_response_id=turn3).conversation_chain_id

    assert c1 == c2 == c3 == c4


def test_chain_id_stable_with_conversation_id() -> None:
    """Explicit conversation_id → identical chain id every turn."""
    turn1 = _make_context(response_id="r-A", conversation_id="conv-1")
    turn2 = _make_context(response_id="r-B", previous_response_id="r-A", conversation_id="conv-1")
    turn3 = _make_context(response_id="r-C", previous_response_id="r-B", conversation_id="conv-1")
    assert turn1.conversation_chain_id == turn2.conversation_chain_id == turn3.conversation_chain_id


def test_chain_id_scoped_by_agent_and_session() -> None:
    """The same chain partition under a different agent or session → different id."""
    kw = dict(conversation_id="conv-1", previous_response_id=None, response_id="r", steerable=True)
    base = derive_conversation_chain_id(agent_name=_AGENT, session_id=_SESSION, **kw)
    other_agent = derive_conversation_chain_id(agent_name="other-agent", session_id=_SESSION, **kw)
    other_session = derive_conversation_chain_id(agent_name=_AGENT, session_id="other-sess", **kw)
    assert base != other_agent
    assert base != other_session


def test_chain_id_non_steerable_forks_distinct() -> None:
    """Non-steerable forks (real ids, same parent) → distinct chain ids (FR-013)."""
    parent = IdGenerator.new_response_id("")
    fork_a = IdGenerator.new_response_id(parent)
    fork_b = IdGenerator.new_response_id(parent)
    ca = _make_context(response_id=fork_a, previous_response_id=parent, steerable=False).conversation_chain_id
    cb = _make_context(response_id=fork_b, previous_response_id=parent, steerable=False).conversation_chain_id
    assert ca != cb


def test_chain_id_property_matches_helper() -> None:
    """The property and the standalone helper agree."""
    ctx = _make_context(response_id="this-resp", previous_response_id="parent-resp")
    assert ctx.conversation_chain_id == _chain_id(
        conversation_id=None, previous_response_id="parent-resp", response_id="this-resp", steerable=True
    )


def test_chain_id_is_opaque_hex() -> None:
    """The chain id is a fixed-length lowercase hex digest (opaque)."""
    cid = _make_context(response_id="resp-1").conversation_chain_id
    assert len(cid) == 32
    assert all(c in "0123456789abcdef" for c in cid)


def test_task_id_is_prefixed_chain_id() -> None:
    """task_id == 'resilient-resp-' + conversation_chain_id (one shared identity)."""
    kw = dict(conversation_id=None, previous_response_id="resp-0", response_id="resp-1", steerable=True)
    chain = _chain_id(**kw)
    task = derive_task_id(agent_name=_AGENT, session_id=_SESSION, **kw)
    assert task == f"resilient-resp-{chain}"
