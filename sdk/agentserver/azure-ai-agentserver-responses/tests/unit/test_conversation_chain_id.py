# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 013 US3 + Spec 036 + Spec 038 — `conversation_chain_id` on ResponseContext.

The chain id is the stable, agent/session-scoped identity of a conversation
chain. Since Spec 038 it follows the native IdGenerator convention
(``cchain_…`` / ``rchain_…``), or is the ``response_id`` verbatim for a
non-steerable one-shot. Because chained response IDs all inherit one partition
key, every turn of a chain resolves to the SAME chain id, and
``task_id == conversation_chain_id`` exactly.
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


def test_chain_id_native_format_conv_and_resp() -> None:
    """Chain ids follow the native IdGenerator convention.

    Conversation → ``cchain_{18-char pkey}{32-char scope}``; steerable →
    ``rchain_…``; both are ~56 chars and within the Task API charset.
    """
    import re

    conv_cid = _make_context(response_id="r-1", conversation_id="conv-X").conversation_chain_id
    resp_cid = _make_context(response_id=IdGenerator.new_response_id("")).conversation_chain_id
    for cid, prefix in ((conv_cid, "cchain_"), (resp_cid, "rchain_")):
        assert cid.startswith(prefix)
        assert len(cid) == len(prefix) + 18 + 32
        assert re.fullmatch(r"[A-Za-z0-9_-]{1,128}", cid)


def test_chain_id_case3_is_response_id_verbatim() -> None:
    """Non-steerable (no conversation_id) → the chain id IS the response id."""
    rid = IdGenerator.new_response_id("")
    cid = _make_context(response_id=rid, steerable=False).conversation_chain_id
    assert cid == rid


def test_task_id_rejects_charset_invalid_case3_response_id() -> None:
    """Case 3 returns response_id verbatim; a charset-invalid one must be
    rejected (the Task API charset is stricter than upstream response-id
    validation, which does not check charset)."""
    import pytest

    # '.' and ':' pass the core primitive's looser _validate_task_id but violate
    # the Public Task API contract ^[a-zA-Z0-9_-]{1,128}$.
    for bad in ("caresp_bad.id", "caresp_bad:id", "caresp_bad!id"):
        with pytest.raises(ValueError):
            derive_task_id(
                agent_name=_AGENT,
                session_id=_SESSION,
                conversation_id=None,
                previous_response_id=None,
                response_id=bad,
                steerable=False,  # case 3 → response_id verbatim
            )


def test_task_id_equals_chain_id() -> None:
    """task_id == conversation_chain_id (one shared identity; no wrapper)."""
    kw = dict(conversation_id=None, previous_response_id="resp-0", response_id="resp-1", steerable=True)
    chain = _chain_id(**kw)
    task = derive_task_id(agent_name=_AGENT, session_id=_SESSION, **kw)
    assert task == chain


def test_task_id_within_task_api_limits() -> None:
    """Every case stays within ``^[a-zA-Z0-9_-]{1,128}$`` — incl. a 63-char
    agent_name, a 128-char session_id, and a full 57-char response_id fork."""
    import re

    long_agent = "a" * 63
    long_session = "s" * 128
    full_resp = IdGenerator.new_response_id("")
    cases = [
        dict(conversation_id="conv-1", previous_response_id=None, response_id="r", steerable=True),
        dict(conversation_id=None, previous_response_id=None, response_id=full_resp, steerable=True),
        dict(conversation_id=None, previous_response_id=None, response_id=full_resp, steerable=False),
    ]
    for kw in cases:
        tid = derive_task_id(agent_name=long_agent, session_id=long_session, **kw)
        assert 1 <= len(tid) <= 128
        assert re.fullmatch(r"[A-Za-z0-9_-]{1,128}", tid)


def test_chain_id_steered_turn_shares_first_turn() -> None:
    """A steered turn (previous_response_id = turn 1) attaches to turn 1's id."""
    turn1_resp = IdGenerator.new_response_id("")
    turn1 = _make_context(response_id=turn1_resp).conversation_chain_id
    turn2 = _make_context(
        response_id=IdGenerator.new_response_id(turn1_resp),
        previous_response_id=turn1_resp,
    ).conversation_chain_id
    assert turn1 == turn2


def test_resolve_session_id_steerable_first_turn_matches_later_turn() -> None:
    """A steerable first turn derives its session from its own response_id, so a
    later steered turn (previous_response_id = turn 1) resolves the SAME session.

    Exercises the real ``_resolve_session_id`` derivation (not a fixed session),
    covering the regression where a first turn's random session could never be
    reproduced by later steered turns — giving them a different resilient task.
    """
    from azure.ai.agentserver.responses.hosting._request_parsing import _resolve_session_id

    agent_ref = {"name": "agentX", "version": "1"}
    turn1_resp = IdGenerator.new_response_id("")

    # Turn 1: no conversation_id / previous_response_id — steerable first turn.
    s1 = _resolve_session_id({}, {}, agent_reference=agent_ref, response_id=turn1_resp, steerable=True)
    # Turn 2: references turn 1 via previous_response_id.
    turn2_resp = IdGenerator.new_response_id(turn1_resp)
    s2 = _resolve_session_id(
        {"previous_response_id": turn1_resp},
        {"previous_response_id": turn1_resp},
        agent_reference=agent_ref,
        response_id=turn2_resp,
        steerable=True,
    )
    assert s1 == s2, "steerable first turn must share the session later steered turns derive"

    # Non-steerable first turns keep the original random behavior (independent of response_id).
    r1 = _resolve_session_id({}, {}, agent_reference=agent_ref, response_id=turn1_resp, steerable=False)
    r2 = _resolve_session_id({}, {}, agent_reference=agent_ref, response_id=turn1_resp, steerable=False)
    assert r1 != r2, "non-steerable first turns must stay random"
