# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the LocalFileTaskProvider."""

import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.durable._local_provider import (
    LocalFileTaskProvider,
)
from azure.ai.agentserver.core.durable._models import (
    TaskCreateRequest,
    TaskPatchRequest,
)


@pytest.fixture
def provider(tmp_path: Path) -> LocalFileTaskProvider:
    """Create a local provider backed by a temp directory."""
    return LocalFileTaskProvider(base_dir=tmp_path)


@pytest.fixture
def sample_create_request() -> TaskCreateRequest:
    """A minimal task creation request."""
    return TaskCreateRequest(
        agent_name="test-agent",
        session_id="session-001",
        status="pending",
        payload={"input": {"data": "hello"}},
        lease_owner="owner-1",
        lease_instance_id="inst-1",
        lease_duration_seconds=60,
    )


class TestLocalProviderCRUD:
    """Create, read, update operations on the local provider."""

    @pytest.mark.asyncio
    async def test_create_and_get(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """create returns a TaskInfo; get retrieves it."""
        task_record = await provider.create(sample_create_request)
        assert task_record.id
        assert task_record.status == "pending"
        assert task_record.agent_name == "test-agent"

        fetched = await provider.get(task_record.id)
        assert fetched is not None
        assert fetched.id == task_record.id

    @pytest.mark.asyncio
    async def test_update_status(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """update changes the status."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match=task_record.etag,
        )
        updated = await provider.update(task_record.id, patch)
        assert updated.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_payload(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """update merges payload."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            payload={"output": {"result": 42}},
            if_match=task_record.etag,
        )
        updated = await provider.update(task_record.id, patch)
        assert updated.payload is not None
        assert updated.payload["output"]["result"] == 42
        # Original input preserved
        assert updated.payload["input"]["data"] == "hello"

    @pytest.mark.asyncio
    async def test_etag_mismatch_raises(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """update raises on ETag mismatch."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match="wrong-etag",
        )
        with pytest.raises(ValueError, match="ETag mismatch"):
            await provider.update(task_record.id, patch)

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(
        self, provider: LocalFileTaskProvider
    ) -> None:
        """get returns None for nonexistent task."""
        result = await provider.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """delete removes a task."""
        task_record = await provider.create(sample_create_request)
        await provider.delete(task_record.id)
        result = await provider.get(task_record.id)
        assert result is None


class TestLocalProviderListing:
    """Tests for listing/querying tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_by_agent(
        self, provider: LocalFileTaskProvider
    ) -> None:
        """list filters by agent_name and session_id."""
        req1 = TaskCreateRequest(
            agent_name="agent-a",
            session_id="s1",
            status="pending",
            payload={},
        )
        req2 = TaskCreateRequest(
            agent_name="agent-b",
            session_id="s1",
            status="pending",
            payload={},
        )
        await provider.create(req1)
        await provider.create(req2)

        tasks = await provider.list(agent_name="agent-a", session_id="s1")
        assert len(tasks) == 1
        assert tasks[0].agent_name == "agent-a"

    @pytest.mark.asyncio
    async def test_list_tasks_by_status(
        self, provider: LocalFileTaskProvider
    ) -> None:
        """list filters by status."""
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="s1",
            status="pending",
            payload={},
        )
        task_record = await provider.create(req)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match=task_record.etag,
        )
        await provider.update(task_record.id, patch)

        pending = await provider.list(
            agent_name="agent", session_id="s1", status="pending"
        )
        assert len(pending) == 0

        active = await provider.list(
            agent_name="agent", session_id="s1", status="in_progress"
        )
        assert len(active) == 1


# --------------------------------------------------------------------- #
# Spec 016 US3 / FR-004a / SC-005a — lease owner agent+session identity
# T047 / T048 / T049 / T050
# --------------------------------------------------------------------- #


class TestLeaseOwnerAgentAndSession:
    """Spec 016 FR-004a (US3): the stable lease owner string is derived
    from BOTH agent name AND session id — never the session id alone.

    Two different agents that happen to share a session id (a
    misconfiguration or a future multi-agent platform topology) MUST
    yield different lease owners so they cannot collide on lease
    ownership and step on each other's tasks. The platform's
    ``binding_mismatch`` protection (FR-006) covers split-brain on the
    SAME ``(agent, session)`` pair; the agent-name component closes
    the orthogonal cross-agent collision hole at the framework layer.
    """

    def test_lease_owner_includes_agent_and_session(self) -> None:
        """SC-005a (a): different agent names with the same session yield
        different owner strings."""
        from azure.ai.agentserver.core.durable._lease import derive_lease_owner

        owner_a = derive_lease_owner("agentA", "S1")
        owner_b = derive_lease_owner("agentB", "S1")

        assert owner_a != owner_b, (
            f"Lease owner MUST differentiate by agent name "
            f"(spec 016 FR-004a). Got identical owners {owner_a!r} for "
            f"both agentA and agentB sharing session S1."
        )

    def test_lease_owner_stable_across_restart(self) -> None:
        """SC-005a (b): same (agent, session) pair yields identical owner
        on every call (no per-process or per-call entropy)."""
        from azure.ai.agentserver.core.durable._lease import derive_lease_owner

        owner_1 = derive_lease_owner("my-agent", "session-X")
        owner_2 = derive_lease_owner("my-agent", "session-X")
        owner_3 = derive_lease_owner("my-agent", "session-X")
        assert owner_1 == owner_2 == owner_3, (
            f"Lease owner MUST be stable across calls within the same "
            f"(agent, session) pair (spec 016 FR-004a / SC-005a). "
            f"Got {owner_1!r} / {owner_2!r} / {owner_3!r}."
        )

    def test_lease_owner_unset_agent_falls_back(self) -> None:
        """SC-005a (c): when the agent name is unset/empty, the
        framework substitutes the documented fallback string. The
        fallback MUST be consistent with the rest of the framework's
        agent-name conventions so traces, logs, and lease ownership
        agree on the same identifier."""
        from azure.ai.agentserver.core.durable._lease import derive_lease_owner

        # Empty string and None both produce the same fallback so callers
        # do not have to normalize before calling.
        owner_empty = derive_lease_owner("", "S1")
        owner_none = derive_lease_owner(None, "S1")  # type: ignore[arg-type]

        # Both fall back to the same well-defined string.
        assert owner_empty == owner_none, (
            "Empty agent name and None MUST produce the same fallback owner "
            "(spec 016 FR-004a — fallback must be deterministic)."
        )
        # Document the fallback by asserting the substring matches the
        # canonical 'unknown-agent' string used elsewhere in the framework.
        assert "unknown-agent" in owner_empty, (
            f"Fallback agent name MUST be 'unknown-agent' for log/trace "
            f"consistency. Got {owner_empty!r}."
        )

    def test_lease_owner_recoverable_both_components(self) -> None:
        """SC-005a (d): BOTH the agent name AND the session id are
        recoverable from the owner string by inspection.

        The format is chosen for operator readability — a human reading
        a log line MUST be able to see both components without consulting
        a parser. The exact serialization is plan-phase detail (see
        conformance-gap-list.md §FR-004a-owner-format); the contract is
        only that both substrings appear.
        """
        from azure.ai.agentserver.core.durable._lease import derive_lease_owner

        owner = derive_lease_owner("my-cool-agent", "session-12345")
        assert "my-cool-agent" in owner, (
            f"agent_name substring MUST appear in the owner string "
            f"(spec 016 SC-005a (d)). Got {owner!r}."
        )
        assert "session-12345" in owner, (
            f"session_id substring MUST appear in the owner string "
            f"(spec 016 SC-005a (d)). Got {owner!r}."
        )


# --------------------------------------------------------------------- #
# Spec 019 FR-D-006 / SC-13 — local provider expiry_count parity
# --------------------------------------------------------------------- #


class TestSpec019LocalProviderExpiryCountParity:
    """FR-D-006 / SC-13 — the local provider MUST bump ``lease.expiry_count``
    on a reclaim PATCH that completes a real expiry-driven ownership
    handoff (different ``lease_instance_id`` AND prior ``expires_at``
    has passed).

    Without this parity, ``TaskRun.lease_expiry_count`` is permanently
    stuck at 0 in local mode and tests asserting recovery behaviour
    cannot use the local provider.

    Reference: docs/task-and-streaming-spec.md §22 / §29 / §59 C-LSE-3.
    """

    @pytest.mark.asyncio
    async def test_local_provider_bumps_expiry_count_on_real_handoff(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """FR-D-006 / SC-13 — expired lease + different instance_id =>
        expiry_count += 1."""
        import datetime as _dt

        created = await provider.create(sample_create_request)
        assert created.lease is not None
        assert created.lease.expiry_count == 0

        # Force the lease to be in the past so the next reclaim PATCH
        # counts as an expiry-driven handoff.
        past = (
            _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=10)
        ).isoformat()
        created.lease.expires_at = past
        provider._write_task(created)  # noqa: SLF001

        # Reclaim with a DIFFERENT instance_id (same owner is fine —
        # both hosted and local treat instance_id change as handoff).
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner,
                lease_instance_id="reclaimer-instance",
                lease_duration_seconds=60,
            ),
        )

        after = await provider.get(created.id)
        assert after is not None
        assert after.lease is not None
        assert after.lease.expiry_count == 1, (
            f"after expired-lease reclaim with a different "
            f"instance_id, expiry_count MUST bump from 0 to 1 "
            f"(FR-D-006 / SC-13). Got {after.lease.expiry_count}."
        )

    @pytest.mark.asyncio
    async def test_local_provider_no_bump_on_same_instance_renewal(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """FR-D-006 — same-instance lease renewal MUST NOT bump
        expiry_count.
        """
        created = await provider.create(sample_create_request)
        assert created.lease is not None
        prior_count = created.lease.expiry_count

        # Renew the lease with the same instance_id.
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner,
                lease_instance_id=created.lease.instance_id,
                lease_duration_seconds=60,
            ),
        )

        after = await provider.get(created.id)
        assert after is not None and after.lease is not None
        assert after.lease.expiry_count == prior_count, (
            "same-instance renewal must not bump expiry_count "
            "(FR-D-006)."
        )

    @pytest.mark.asyncio
    async def test_local_provider_no_bump_on_unexpired_handoff(
        self,
        provider: LocalFileTaskProvider,
        sample_create_request: TaskCreateRequest,
    ) -> None:
        """FR-D-006 — handoff to a new instance BEFORE the prior
        lease has expired (same-owner-different-instance restart;
        the prior lease was still valid) MUST NOT bump expiry_count.
        """
        created = await provider.create(sample_create_request)
        assert created.lease is not None
        prior_count = created.lease.expiry_count

        # Reclaim with new instance_id BEFORE the existing lease
        # has expired. Both hosted and local treat this as the
        # restart-handoff case, not an expiry event.
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner,
                lease_instance_id="reclaimer-fresh",
                lease_duration_seconds=60,
            ),
        )

        after = await provider.get(created.id)
        assert after is not None and after.lease is not None
        assert after.lease.expiry_count == prior_count, (
            "handoff before lease expiry must not bump expiry_count "
            "(FR-D-006 — only real expiry-driven handoffs count)."
        )
