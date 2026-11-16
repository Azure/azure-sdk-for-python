# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for deterministic task ID derivation."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.hosting._chain_id import derive_conversation_chain_id
from azure.ai.agentserver.responses.hosting._task_id import (
    derive_lifecycle_id,
    derive_task_id,
    derive_task_session_scope,
)


def test_lifecycle_id_keeps_anonymous_compatibility_and_separates_user_keys():
    response_id = "caresp_shared"
    assert derive_lifecycle_id(response_id, None) == response_id
    keys = [derive_lifecycle_id(response_id, user) for user in [None, "", "anonymous", "user-A", "user-B", "\u00e9"]]
    assert len(set(keys)) == len(keys)
    assert derive_lifecycle_id("bc", "a") != derive_lifecycle_id("c", "ab")
    assert derive_lifecycle_id(response_id, "user-A") == derive_lifecycle_id(response_id, "user-A")


@pytest.mark.asyncio
async def test_user_scoped_file_replay_survives_restart_without_legacy_fallback(tmp_path):
    from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry
    from azure.ai.agentserver.core.streaming import EventStreamNotFoundError

    response_id = "caresp_shared"
    first = _StreamsRegistry()
    first.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=lambda event: event["sequence_number"])
    for user in [None, "user-A", "user-B"]:
        stream = await first.get_or_create(derive_lifecycle_id(response_id, user))
        await stream.emit({"sequence_number": 0, "owner": user})
        await stream.close()
        # Release process-owned handles without deleting the persisted replay.
        stream._cleanup_locks()

    restarted = _StreamsRegistry()
    restarted.use_file_backed_replay(storage_dir=tmp_path, cursor_fn=lambda event: event["sequence_number"])
    for user in [None, "user-A", "user-B"]:
        stream = await restarted.get(derive_lifecycle_id(response_id, user))
        events = [event async for event in stream.subscribe()]
        assert events == [{"sequence_number": 0, "owner": user}]
    await restarted.delete(derive_lifecycle_id(response_id, "user-A"))
    with pytest.raises(EventStreamNotFoundError):
        await restarted.get(derive_lifecycle_id(response_id, "user-A"))
    other = await restarted.get(derive_lifecycle_id(response_id, "user-B"))
    assert [event async for event in other.subscribe()] == [{"sequence_number": 0, "owner": "user-B"}]
    await restarted.delete(derive_lifecycle_id(response_id, "user-B"))
    await restarted.delete(response_id)


class TestTaskIdDerivation:
    """Verify deterministic task ID generation."""

    def test_same_inputs_same_id(self) -> None:
        """Deterministic: identical inputs always produce identical IDs."""
        id1 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="my-agent",
            session_id="sess_789",
        )
        id2 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="my-agent",
            session_id="sess_789",
        )
        assert id1 == id2

    def test_different_inputs_different_id(self) -> None:
        """Different inputs produce different IDs."""
        id1 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="my-agent",
            session_id="sess_789",
        )
        id2 = derive_task_id(
            conversation_id="conv_999",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="my-agent",
            session_id="sess_789",
        )
        assert id1 != id2

    def test_conversation_id_takes_priority(self) -> None:
        """conversation_id is the primary key when present."""
        id_with_conv = derive_task_id(
            conversation_id="conv_123",
            previous_response_id="prev_456",
            response_id="resp_789",
            agent_name="agent",
            session_id="sess",
        )
        # Same conversation_id, different previous_response_id → same task
        id_same_conv = derive_task_id(
            conversation_id="conv_123",
            previous_response_id="prev_999",
            response_id="resp_other",
            agent_name="agent",
            session_id="sess",
        )
        assert id_with_conv == id_same_conv

    def test_previous_response_id_used_when_no_conversation(self) -> None:
        """previous_response_id is used when conversation_id is absent."""
        id1 = derive_task_id(
            conversation_id=None,
            previous_response_id="prev_456",
            response_id="resp_789",
            agent_name="agent",
            session_id="sess",
        )
        id2 = derive_task_id(
            conversation_id=None,
            previous_response_id="prev_456",
            response_id="resp_other",
            agent_name="agent",
            session_id="sess",
        )
        # Same previous_response_id → same task ID (stable across chain)
        assert id1 == id2

    def test_response_id_fallback(self) -> None:
        """response_id used when both conversation_id and previous_response_id are None."""
        id1 = derive_task_id(
            conversation_id=None,
            previous_response_id=None,
            response_id="resp_unique",
            agent_name="agent",
            session_id="sess",
        )
        id2 = derive_task_id(
            conversation_id=None,
            previous_response_id=None,
            response_id="resp_unique",
            agent_name="agent",
            session_id="sess",
        )
        assert id1 == id2

    def test_includes_agent_name_in_hash(self) -> None:
        """Different agent names produce different IDs (no collisions)."""
        id1 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent-a",
            session_id="sess",
        )
        id2 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent-b",
            session_id="sess",
        )
        assert id1 != id2

    def test_includes_session_in_hash(self) -> None:
        """Different sessions produce different IDs."""
        id1 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent",
            session_id="sess-1",
        )
        id2 = derive_task_id(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent",
            session_id="sess-2",
        )
        assert id1 != id2

    def test_private_task_session_scope_decouples_public_chain_id(self) -> None:
        """A session GUID changes only the physical task namespace."""
        kwargs = dict(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent",
            session_id="same-public-name",
        )

        public_chain_id = derive_conversation_chain_id(**kwargs)
        task_id = derive_task_id(
            **kwargs,
            task_session_id="11111111111111111111111111111111",
        )

        assert task_id != public_chain_id

    def test_different_session_guids_produce_different_task_ids(self) -> None:
        """Recreated same-name sessions do not collide with tombstoned task IDs."""
        kwargs = dict(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent",
            session_id="same-public-name",
        )

        first = derive_task_id(**kwargs, task_session_id="1" * 32)
        recreated = derive_task_id(**kwargs, task_session_id="2" * 32)

        assert first != recreated

    def test_missing_private_scope_preserves_legacy_task_id(self) -> None:
        """Absent session GUID keeps the pre-rollout derivation."""
        kwargs = dict(
            conversation_id="conv_123",
            previous_response_id=None,
            response_id="resp_456",
            agent_name="agent",
            session_id="same-public-name",
        )

        assert derive_task_id(**kwargs) == derive_task_id(**kwargs, task_session_id=None)

    def test_task_session_scope_includes_guid_and_public_session(self) -> None:
        """One GUID cannot collapse distinct resolved public sessions."""
        guid = "1" * 32

        first = derive_task_session_scope(session_id="session-a", session_guid=guid)
        second = derive_task_session_scope(session_id="session-b", session_guid=guid)

        assert first != second

    def test_task_session_scope_without_guid_is_legacy_session(self) -> None:
        assert derive_task_session_scope(session_id="public-session", session_guid=None) == "public-session"

    def test_parallel_forks_get_distinct_ids(self) -> None:
        """Two requests with same previous_response_id but steerable=False
        use response_id as key → distinct task IDs (FR-013)."""
        # When steerable is False and there's no conversation_id,
        # parallel forks each use their own response_id
        id1 = derive_task_id(
            conversation_id=None,
            previous_response_id="parent_resp",
            response_id="fork_a",
            agent_name="agent",
            session_id="sess",
            steerable=False,
        )
        id2 = derive_task_id(
            conversation_id=None,
            previous_response_id="parent_resp",
            response_id="fork_b",
            agent_name="agent",
            session_id="sess",
            steerable=False,
        )
        assert id1 != id2

    def test_steerable_true_same_previous_response_id_same_task(self) -> None:
        """When steerable=True, same previous_response_id → same task (steer)."""
        id1 = derive_task_id(
            conversation_id=None,
            previous_response_id="parent_resp",
            response_id="resp_a",
            agent_name="agent",
            session_id="sess",
            steerable=True,
        )
        id2 = derive_task_id(
            conversation_id=None,
            previous_response_id="parent_resp",
            response_id="resp_b",
            agent_name="agent",
            session_id="sess",
            steerable=True,
        )
        assert id1 == id2

    def test_returns_string(self) -> None:
        """Task ID is always a string."""
        result = derive_task_id(
            conversation_id="conv",
            previous_response_id=None,
            response_id="resp",
            agent_name="agent",
            session_id="sess",
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestTaskIdRealChain:
    """Spec 036 — real IdGenerator-chained ids collapse / fork correctly."""

    def test_real_steerable_chain_collapses_to_one_task(self) -> None:
        """A real previous_response_id chain → ONE task id across all turns."""
        root = IdGenerator.new_response_id("")
        turn2 = IdGenerator.new_response_id(root)
        turn3 = IdGenerator.new_response_id(turn2)

        ids = [
            derive_task_id(
                conversation_id=None,
                previous_response_id=prev,
                response_id=rid,
                agent_name="agent",
                session_id="sess",
                steerable=True,
            )
            for prev, rid in [(None, root), (root, turn2), (turn2, turn3)]
        ]
        assert ids[0] == ids[1] == ids[2]

    def test_real_non_steerable_forks_distinct(self) -> None:
        """Real concurrent forks (same parent) → distinct task ids (FR-013)."""
        parent = IdGenerator.new_response_id("")
        fork_a = IdGenerator.new_response_id(parent)
        fork_b = IdGenerator.new_response_id(parent)
        id_a = derive_task_id(
            conversation_id=None,
            previous_response_id=parent,
            response_id=fork_a,
            agent_name="agent",
            session_id="sess",
            steerable=False,
        )
        id_b = derive_task_id(
            conversation_id=None,
            previous_response_id=parent,
            response_id=fork_b,
            agent_name="agent",
            session_id="sess",
            steerable=False,
        )
        assert id_a != id_b

    def test_task_id_equals_chain_id(self) -> None:
        """task_id == conversation_chain_id (one shared identity; no wrapper)."""
        kw = dict(
            conversation_id=None,
            previous_response_id=IdGenerator.new_response_id(""),
            response_id=IdGenerator.new_response_id(""),
            agent_name="agent",
            session_id="sess",
            steerable=True,
        )
        chain = derive_conversation_chain_id(**kw)
        task = derive_task_id(**kw)
        assert task == chain
