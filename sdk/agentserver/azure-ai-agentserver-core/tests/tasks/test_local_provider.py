# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the LocalFileTaskProvider."""

import datetime as _dt
import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest


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
        title="test task",
        payload={"input": {"data": "hello"}},
    )


class TestLocalProviderCRUD:
    """Create, read, update operations on the local provider."""

    @pytest.mark.asyncio
    async def test_create_and_get(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
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
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update changes the status."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(status="in_progress", if_match=task_record.etag)
        updated = await provider.update(task_record.id, patch)
        assert updated.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_payload(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update merges payload."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(payload={"output": {"result": 42}}, if_match=task_record.etag)
        updated = await provider.update(task_record.id, patch)
        assert updated.payload is not None
        assert updated.payload["output"]["result"] == 42
        # Original input preserved
        assert updated.payload["input"]["data"] == "hello"

    @pytest.mark.asyncio
    async def test_etag_mismatch_raises(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update raises on ETag mismatch."""
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(status="in_progress", if_match="wrong-etag")
        with pytest.raises(ValueError, match="ETag mismatch"):
            await provider.update(task_record.id, patch)

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, provider: LocalFileTaskProvider) -> None:
        """get returns None for nonexistent task."""
        result = await provider.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_task(self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest) -> None:
        """delete removes a task."""
        task_record = await provider.create(sample_create_request)
        await provider.delete(task_record.id, force=True)
        result = await provider.get(task_record.id)
        assert result is None


class TestLocalProviderListing:
    """Tests for listing/querying tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_by_agent(self, provider: LocalFileTaskProvider) -> None:
        """list filters by agent_name and session_id."""
        req1 = TaskCreateRequest(agent_name="agent-a", session_id="s1", status="pending", title="task a", payload={})
        req2 = TaskCreateRequest(agent_name="agent-b", session_id="s1", status="pending", title="task b", payload={})
        await provider.create(req1)
        await provider.create(req2)

        tasks = await provider.list(agent_name="agent-a", session_id="s1")
        assert len(tasks) == 1
        assert tasks[0].agent_name == "agent-a"

    @pytest.mark.asyncio
    async def test_list_tasks_by_status(self, provider: LocalFileTaskProvider) -> None:
        """list filters by status."""
        req = TaskCreateRequest(agent_name="agent", session_id="s1", status="pending", title="task", payload={})
        task_record = await provider.create(req)
        patch = TaskPatchRequest(status="in_progress", if_match=task_record.etag)
        await provider.update(task_record.id, patch)

        pending = await provider.list(agent_name="agent", session_id="s1", status="pending")
        assert len(pending) == 0

        active = await provider.list(agent_name="agent", session_id="s1", status="in_progress")
        assert len(active) == 1


# --------------------------------------------------------------------- #
#   /  / SC-005a — lease owner agent+session identity
# T047 / T048 / T049 / T050
# --------------------------------------------------------------------- #


class TestLeaseOwnerAgentAndSession:
    """: the stable lease owner string is derived
    from BOTH agent name AND session id — never the session id alone.

    Two different agents that happen to share a session id (a
    misconfiguration or a future multi-agent platform topology) MUST
    yield different lease owners so they cannot collide on lease
    ownership and step on each other's tasks. The platform's
    ``binding_mismatch`` protection  covers split-brain on the
    SAME ``(agent, session)`` pair; the agent-name component closes
    the orthogonal cross-agent collision hole at the framework layer.
    """

    def test_lease_owner_includes_agent_and_session(self) -> None:
        """SC-005a (a): different agent names with the same session yield
        different owner strings."""
        from azure.ai.agentserver.core.tasks._lease import derive_lease_owner

        owner_a = derive_lease_owner("agentA", "S1")
        owner_b = derive_lease_owner("agentB", "S1")

        assert owner_a != owner_b, (
            f"Lease owner MUST differentiate by agent name "
            f". Got identical owners {owner_a!r} for "
            f"both agentA and agentB sharing session S1."
        )

    def test_lease_owner_stable_across_restart(self) -> None:
        """SC-005a (b): same (agent, session) pair yields identical owner
        on every call (no per-process or per-call entropy)."""
        from azure.ai.agentserver.core.tasks._lease import derive_lease_owner

        owner_1 = derive_lease_owner("my-agent", "session-X")
        owner_2 = derive_lease_owner("my-agent", "session-X")
        owner_3 = derive_lease_owner("my-agent", "session-X")
        assert owner_1 == owner_2 == owner_3, (
            f"Lease owner MUST be stable across calls within the same "
            f"(agent, session) pair (/ SC-005a). "
            f"Got {owner_1!r} / {owner_2!r} / {owner_3!r}."
        )

    def test_lease_owner_unset_agent_falls_back(self) -> None:
        """SC-005a (c): when the agent name is unset/empty, the
        framework substitutes the documented fallback string. The
        fallback MUST be consistent with the rest of the framework's
        agent-name conventions so traces, logs, and lease ownership
        agree on the same identifier."""
        from azure.ai.agentserver.core.tasks._lease import derive_lease_owner

        # Empty string and None both produce the same fallback so callers
        # do not have to normalize before calling.
        owner_empty = derive_lease_owner("", "S1")
        owner_none = derive_lease_owner(None, "S1")  # type: ignore[arg-type]

        # Both fall back to the same well-defined string.
        assert owner_empty == owner_none, (
            "Empty agent name and None MUST produce the same fallback owner " "(— fallback must be deterministic)."
        )
        # Document the fallback by asserting the substring matches the
        # canonical 'unknown-agent' string used elsewhere in the framework.
        assert "unknown-agent" in owner_empty, (
            f"Fallback agent name MUST be 'unknown-agent' for log/trace " f"consistency. Got {owner_empty!r}."
        )

    def test_lease_owner_recoverable_both_components(self) -> None:
        """SC-005a (d): BOTH the agent name AND the session id are
        recoverable from the owner string by inspection.

        The format is chosen for operator readability — a human reading
        a log line MUST be able to see both components without consulting
        a parser. The exact serialization is plan-phase detail (see
        conformance-SOT.md §-owner-format); the contract is
        only that both substrings appear.
        """
        from azure.ai.agentserver.core.tasks._lease import derive_lease_owner

        owner = derive_lease_owner("my-cool-agent", "session-12345")
        assert "my-cool-agent" in owner, (
            f"agent_name substring MUST appear in the owner string " f"(SC-005a (d)). Got {owner!r}."
        )
        assert "session-12345" in owner, (
            f"session_id substring MUST appear in the owner string " f"(SC-005a (d)). Got {owner!r}."
        )


# --------------------------------------------------------------------- #
#   / SC-13 — local provider expiry_count parity
# --------------------------------------------------------------------- #


class TestTaskStreamsLocalProviderExpiryCountParity:
    """/ SC-13 — the local provider MUST bump ``lease.expiry_count``
    on a reclaim PATCH that completes a real expiry-driven ownership
    handoff (different ``lease_instance_id`` AND prior ``expires_at``
    has passed).

    Without this parity, ``TaskRun.lease_expiry_count`` is permanently
    stuck at 0 in local mode and tests asserting recovery behaviour
    cannot use the local provider.

    Reference: docs/task-and-streaming-spec.md §22 / §29 / §59 C-LSE-3.
    """

    @staticmethod
    def _leased_create_request() -> TaskCreateRequest:
        return TaskCreateRequest(
            agent_name="test-agent",
            session_id="session-001",
            title="lease test",
            status="in_progress",
            lease_owner="owner-1",
            lease_instance_id="inst-1",
            lease_duration_seconds=60,
        )

    @pytest.mark.asyncio
    async def test_local_provider_bumps_expiry_count_on_real_handoff(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """/ SC-13 — expired lease + different instance_id =>
        expiry_count += 1."""

        created = await provider.create(self._leased_create_request())
        assert created.lease is not None
        assert created.lease.expiry_count == 0

        # Force the lease to be in the past so the next reclaim PATCH
        # counts as an expiry-driven handoff.
        past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=10)).isoformat()
        created.lease.expires_at = past
        provider._write_task(created)  # noqa: SLF001

        # Reclaim with a DIFFERENT instance_id (same owner is fine —
        # both hosted and local treat instance_id change as handoff).
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner, lease_instance_id="reclaimer-instance", lease_duration_seconds=60
            ),
        )

        after = await provider.get(created.id)
        assert after is not None
        assert after.lease is not None
        assert after.lease.expiry_count == 1, (
            f"after expired-lease reclaim with a different "
            f"instance_id, expiry_count MUST bump from 0 to 1 "
            f"(/ SC-13). Got {after.lease.expiry_count}."
        )

    @pytest.mark.asyncio
    async def test_local_provider_no_bump_on_same_instance_renewal(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """— same-instance lease renewal MUST NOT bump
        expiry_count.
        """
        created = await provider.create(self._leased_create_request())
        assert created.lease is not None
        prior_count = created.lease.expiry_count

        # Renew the lease with the same instance_id.
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner, lease_instance_id=created.lease.instance_id, lease_duration_seconds=60
            ),
        )

        after = await provider.get(created.id)
        assert after is not None and after.lease is not None
        assert after.lease.expiry_count == prior_count, "same-instance renewal must not bump expiry_count " "."

    @pytest.mark.asyncio
    async def test_local_provider_no_bump_on_unexpired_handoff(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """— handoff to a new instance BEFORE the prior
        lease has expired (same-owner-different-instance restart;
        the prior lease was still valid) MUST NOT bump expiry_count.
        """
        created = await provider.create(self._leased_create_request())
        assert created.lease is not None
        prior_count = created.lease.expiry_count

        # Reclaim with new instance_id BEFORE the existing lease
        # has expired. Both hosted and local treat this as the
        # restart-handoff case, not an expiry event.
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner, lease_instance_id="reclaimer-fresh", lease_duration_seconds=60
            ),
        )

        after = await provider.get(created.id)
        assert after is not None and after.lease is not None
        assert after.lease.expiry_count == prior_count, (
            "handoff before lease expiry must not bump expiry_count " "(— only real expiry-driven handoffs count)."
        )


# --------------------------------------------------------------------- #
# `started_at` immutability — set once on first ``in_progress``
# transition, never updated thereafter. Bug: ``_apply_lease_acquisition``
# used to overwrite it on expired-lease reclaim (recovery scanner takeover
# or same-owner restart), violating the contract documented at
# ``TaskInfo.started_at``.
# --------------------------------------------------------------------- #


class TestStartedAtImmutability:
    """``TaskInfo.started_at`` MUST be set once when the task first enters
    ``in_progress`` and MUST NOT change after that — not on lease renewal,
    not on lease re-acquisition after expiry, not on recovery scanner
    takeover, not on suspend/resume cycles.
    """

    @staticmethod
    def _leased_create_request() -> TaskCreateRequest:
        return TaskCreateRequest(
            agent_name="test-agent",
            session_id="session-started-at",
            title="started_at test",
            status="in_progress",
            lease_owner="owner-1",
            lease_instance_id="inst-1",
            lease_duration_seconds=60,
        )

    @pytest.mark.asyncio
    async def test_started_at_set_on_create_in_progress(self, provider: LocalFileTaskProvider) -> None:
        """Creating a task already in ``in_progress`` with a lease sets
        ``started_at`` to the creation timestamp."""
        created = await provider.create(self._leased_create_request())
        assert created.started_at is not None, "started_at must be set when a task is created in_progress"

    @pytest.mark.asyncio
    async def test_started_at_set_on_pending_to_in_progress(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """The first ``pending → in_progress`` PATCH stamps ``started_at``."""
        created = await provider.create(sample_create_request)
        assert created.started_at is None, "pending create should not set started_at"

        await provider.update(
            created.id,
            TaskPatchRequest(
                status="in_progress", lease_owner="owner-1", lease_instance_id="inst-1", lease_duration_seconds=60
            ),
        )
        after = await provider.get(created.id)
        assert after is not None
        assert after.started_at is not None, "started_at must be set on first pending→in_progress transition"

    @pytest.mark.asyncio
    async def test_started_at_unchanged_on_expired_lease_reclaim(self, provider: LocalFileTaskProvider) -> None:
        """Expired-lease reclaim by a different instance (recovery scanner
        takeover) MUST NOT reset ``started_at``. Regression for the
        ``_apply_lease_acquisition`` bug that overwrote it."""

        created = await provider.create(self._leased_create_request())
        original_started_at = created.started_at
        assert original_started_at is not None

        # Force lease expiry so the next reclaim is an expiry-driven handoff.
        past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=10)).isoformat()
        assert created.lease is not None
        created.lease.expires_at = past
        provider._write_task(created)  # noqa: SLF001

        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner, lease_instance_id="reclaimer-instance", lease_duration_seconds=60
            ),
        )

        after = await provider.get(created.id)
        assert after is not None
        # Sanity check the reclaim happened: expiry_count bumped.
        assert after.lease is not None and after.lease.expiry_count == 1
        assert after.started_at == original_started_at, (
            f"started_at MUST be immutable on expired-lease reclaim "
            f"(contract per TaskInfo.started_at docstring). "
            f"Original: {original_started_at!r}, after reclaim: "
            f"{after.started_at!r}."
        )

    @pytest.mark.asyncio
    async def test_started_at_unchanged_on_same_owner_expired_reacquire(self, provider: LocalFileTaskProvider) -> None:
        """Same owner, new instance, expired lease (process restart) MUST
        NOT reset ``started_at``. Regression for the second buggy line in
        ``_apply_lease_acquisition``."""

        created = await provider.create(self._leased_create_request())
        original_started_at = created.started_at
        assert original_started_at is not None
        assert created.lease is not None

        past = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=10)).isoformat()
        created.lease.expires_at = past
        provider._write_task(created)  # noqa: SLF001

        # Same owner, new instance — represents process restart.
        await provider.update(
            created.id,
            TaskPatchRequest(
                lease_owner=created.lease.owner, lease_instance_id="inst-2-restarted", lease_duration_seconds=60
            ),
        )

        after = await provider.get(created.id)
        assert after is not None
        assert after.started_at == original_started_at, "started_at MUST be immutable on same-owner expired reacquire."

    @pytest.mark.asyncio
    async def test_started_at_unchanged_on_suspend_then_resume(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """A suspend → in_progress cycle (e.g., multi-turn next-turn entry)
        MUST NOT reset ``started_at`` to the resume time."""
        created = await provider.create(sample_create_request)

        # First in_progress transition — stamps started_at.
        await provider.update(
            created.id,
            TaskPatchRequest(
                status="in_progress", lease_owner="owner-1", lease_instance_id="inst-1", lease_duration_seconds=60
            ),
        )
        after_first = await provider.get(created.id)
        assert after_first is not None
        original_started_at = after_first.started_at
        assert original_started_at is not None

        # Suspend.
        await provider.update(created.id, TaskPatchRequest(status="suspended"))

        # Resume — second in_progress entry; started_at must not change.
        await provider.update(
            created.id,
            TaskPatchRequest(
                status="in_progress", lease_owner="owner-1", lease_instance_id="inst-1", lease_duration_seconds=60
            ),
        )
        after_resume = await provider.get(created.id)
        assert after_resume is not None
        assert (
            after_resume.started_at == original_started_at
        ), "started_at MUST be immutable across suspend/resume cycles."


# ===========================================================================
#: Local-provider ↔ service parity — RED-first tests
# ===========================================================================
#
# Per Constitution Principle VII (TDD) +  Workstream A.
# Each test asserts ONE conformance item from the SOT spec
# (sdk/agentserver/azure-ai-agentserver-core/docs/task-and-streaming-spec.md).
# Tests are RED first; implementation lands in Phase 2.


class TestLocalProviderValidation:
    """V1-V12 — field validation (§28a / C-VAL-*)."""

    @pytest.mark.asyncio
    async def test_v1_task_id_must_match_regex(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-1: task id must match `^[a-zA-Z0-9_-]{1,128}$`."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", id="bad id with spaces", title="t")
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v1_task_id_too_long_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-1: task id length > 128 rejected."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", id="x" * 129, title="t")
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v2_agent_name_required(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-2: agent_name required on create."""
        bad = TaskCreateRequest(agent_name="", session_id="s", title="t")
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v2_session_id_required(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-2: session_id required on create."""
        bad = TaskCreateRequest(agent_name="a", session_id="", title="t")
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v2_title_required(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-2: title required on create."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="")
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v2_title_none_required(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-2: title=None is rejected the same as an empty title."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title=None)
        with pytest.raises(_HostedConflict) as exc_info:
            await provider.create(bad)
        assert exc_info.value._code == "invalid_request"

    @pytest.mark.asyncio
    async def test_real_world_title_gets_same_lease_validation(self, provider: LocalFileTaskProvider) -> None:
        """Validation applies to every title value, not only the spec test title."""
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="customer import",
            lease_owner="owner",
            lease_instance_id="instance",
            lease_duration_seconds=60,
        )
        with pytest.raises(_HostedConflict) as exc_info:
            await provider.create(bad)
        assert exc_info.value._code == "invalid_request"

    @pytest.mark.asyncio
    async def test_v3_tag_key_regex(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-5: tag keys must match `^[a-zA-Z0-9_.\\-]{1,64}$`."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="t", tags={"bad key with spaces": "v"})
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v4_tag_value_max_256(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-5: tag values must be ≤ 256 chars."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="t", tags={"k": "x" * 257})
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v5_tag_count_max_16(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-5: at most 16 tag entries."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="t", tags={f"k{i}": "v" for i in range(17)})
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v6_payload_max_1mb(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-6: payload ≤ 1 MB."""
        big = "x" * (1024 * 1024 + 100)
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="t", payload={"big": big})
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v7_error_max_64kb(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-6: error ≤ 64 KB."""
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(Exception):
            await provider.update(created.id, TaskPatchRequest(error={"type": "E", "message": "x" * (64 * 1024 + 100)}))

    @pytest.mark.asyncio
    async def test_v8_source_max_4kb(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-6: source ≤ 4 KB."""
        bad = TaskCreateRequest(agent_name="a", session_id="s", title="t", source={"type": "t", "blob": "x" * 5000})
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v9_suspension_reason_max_256(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-4: suspension_reason ≤ 256 chars."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        with pytest.raises(Exception):
            await provider.update(created.id, TaskPatchRequest(status="suspended", suspension_reason="x" * 257))

    @pytest.mark.asyncio
    async def test_v10_source_type_required(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-7: source.type required when source provided."""
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="t",
            source={"routine_name": "r"},  # no type
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v11_failed_status_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-9: status 'failed' rejected on input."""
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="t",
            status="failed",  # type: ignore[arg-type]
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_v12_done_normalized_to_completed(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-9: legacy 'done' status normalized to 'completed' on read."""
        # Create a task and then patch with status="done" — provider should
        # normalize to "completed" so consumers always see canonical value.
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(
            created.id,
            TaskPatchRequest(status="done"),  # type: ignore[arg-type]
        )
        got = await provider.get(created.id)
        assert got is not None and got.status == "completed"


class TestLocalProviderStateMachine:
    """B1-B8 — state transition matrix, terminal immutability,
    delete force semantics (§24.1/24.2/24.3, C-LCM-5..8)."""

    @pytest.mark.asyncio
    async def test_b1_invalid_transition_pending_to_suspended(self, provider: LocalFileTaskProvider) -> None:
        """C-LCM-5: pending → suspended is not in the matrix."""
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(Exception):
            await provider.update(created.id, TaskPatchRequest(status="suspended"))

    @pytest.mark.asyncio
    async def test_b2_terminal_task_immutable(self, provider: LocalFileTaskProvider) -> None:
        """C-LCM-6: PATCH on completed task rejected."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="completed"))
        with pytest.raises(Exception):
            await provider.update(created.id, TaskPatchRequest(payload={"new": "data"}))

    @pytest.mark.asyncio
    async def test_b2_terminal_noop_allowed(self, provider: LocalFileTaskProvider) -> None:
        """C-LCM-6: completed → completed with no other changes is a no-op."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="completed"))
        # No-op completed → completed should NOT raise.
        result = await provider.update(created.id, TaskPatchRequest(status="completed"))
        assert result.status == "completed"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("id", "other"),
            ("agent_name", "other-agent"),
            ("session_id", "other-session"),
            ("title", "other-title"),
            ("description", "other-description"),
            ("source", {"type": "other"}),
        ],
    )
    async def test_b3_immutable_fields_rejected(
        self, provider: LocalFileTaskProvider, field_name: str, value: Any
    ) -> None:
        """C-LCM-8: id/agent_name/session_id/title/description/source can't be
        PATCHed.

        Note: today's TaskPatchRequest doesn't expose these as fields; this test
        documents that the provider rejects them at the JSON-layer in case
        anyone constructs the underlying patch dict directly."""
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(_HostedConflict) as exc_info:
            provider._reject_immutable_patch_fields({field_name: value}, created.id)  # noqa: SLF001
        assert exc_info.value._code == "invalid_request"

    @pytest.mark.asyncio
    async def test_b4_suspension_reason_only_with_suspended(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-4 / §28a: suspension_reason only allowed with status=suspended."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        with pytest.raises(Exception):
            await provider.update(created.id, TaskPatchRequest(status="pending", suspension_reason="why"))

    @pytest.mark.asyncio
    async def test_b5_delete_without_force_on_nonterminal_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-LCM-7: delete non-terminal task without force=true rejected."""
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(Exception):
            await provider.delete(created.id, force=False)

    @pytest.mark.asyncio
    async def test_b5_delete_terminal_without_force_ok(self, provider: LocalFileTaskProvider) -> None:
        """C-LCM-7: delete terminal task without force succeeds."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="completed"))
        await provider.delete(created.id, force=False)  # should not raise

    @pytest.mark.asyncio
    async def test_b7_error_patch_requires_message_and_type(self, provider: LocalFileTaskProvider) -> None:
        """C-VAL-8: error PATCH requires non-empty message + type."""
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(Exception):
            await provider.update(
                created.id,
                TaskPatchRequest(error={"code": "x"}),  # missing message+type
            )


class TestLocalProviderLease:
    """C1-C10 — lease semantics (§22.1, C-LSE-6..14)."""

    @pytest.mark.asyncio
    async def test_l1_duration_must_be_zero_or_in_range(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-6: lease_duration_seconds must be 0 or 10..3600."""
        # 5 seconds is below the floor.
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="t",
            status="in_progress",
            lease_owner="o",
            lease_instance_id="i",
            lease_duration_seconds=5,
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_l1_duration_too_large_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-6: lease_duration_seconds > 3600 rejected."""
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="t",
            status="in_progress",
            lease_owner="o",
            lease_instance_id="i",
            lease_duration_seconds=4000,
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_l2_all_or_nothing_lease_params(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-7: supplying lease_owner without lease_instance_id rejected."""
        bad = TaskCreateRequest(
            agent_name="a",
            session_id="s",
            title="t",
            status="in_progress",
            lease_owner="o",  # missing instance_id and duration
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_l3_different_owner_takeover_when_live_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-8: different-owner takeover against a live lease rejected."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="owner-A",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        with pytest.raises(Exception):
            await provider.update(
                created.id,
                TaskPatchRequest(lease_owner="owner-B", lease_instance_id="i-other", lease_duration_seconds=60),
            )

    @pytest.mark.asyncio
    async def test_l4_in_progress_to_pending_requires_matching_lease(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-9: in_progress → pending requires matching (owner, instance_id)."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="owner-A",
                lease_instance_id="i-1",
                lease_duration_seconds=60,
            )
        )
        with pytest.raises(Exception):
            await provider.update(
                created.id,
                TaskPatchRequest(
                    status="pending",
                    lease_owner="owner-A",
                    lease_instance_id="i-other",  # mismatch
                    lease_duration_seconds=60,
                ),
            )

    @pytest.mark.asyncio
    async def test_l5_renewal_only_on_in_progress(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-10: lease renewal (no status change) rejected on non-in_progress."""
        # Create as pending (no lease) then attempt renewal — should reject.
        created = await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title="t"))
        with pytest.raises(Exception):
            await provider.update(
                created.id, TaskPatchRequest(lease_owner="o", lease_instance_id="i", lease_duration_seconds=60)
            )

    @pytest.mark.asyncio
    async def test_l10_heartbeat_at_stamped(self, provider: LocalFileTaskProvider) -> None:
        """C-LSE-14: heartbeat_at stamped on every lease write."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        assert created.lease is not None
        # LeaseInfo today does not have heartbeat_at; assertion will fail
        # with AttributeError — that's the RED signal.
        assert hasattr(created.lease, "heartbeat_at")
        assert created.lease.heartbeat_at  # type: ignore[attr-defined]


class TestLocalProviderAttachments:
    """D1, D3, D4, D5 — attachment key validation + clear-all + omit values + delete cleanup."""

    @pytest.mark.asyncio
    async def test_d1_attachment_key_regex(self, provider: LocalFileTaskProvider) -> None:
        """C-ATT-8: attachment key must match regex."""
        bad = TaskCreateRequest(
            agent_name="a", session_id="s", title="t", attachments={"bad key with spaces": {"x": 1}}
        )
        with pytest.raises(Exception):
            await provider.create(bad)

    @pytest.mark.asyncio
    async def test_d3_clear_attachments_wipes_all(self, provider: LocalFileTaskProvider) -> None:
        """C-ATT-9: TaskPatchRequest.clear_attachments=True wipes all attachments."""
        created = await provider.create(
            TaskCreateRequest(agent_name="a", session_id="s", title="t", attachments={"k1": {"v": 1}, "k2": {"v": 2}})
        )
        assert created.attachments and len(created.attachments) == 2
        # clear_attachments doesn't exist on TaskPatchRequest yet — RED via TypeError
        patch = TaskPatchRequest()
        setattr(patch, "clear_attachments", True)  # AttributeError if not in __slots__
        await provider.update(created.id, patch)
        got = await provider.get(created.id)
        assert got is not None
        assert not got.attachments

    @pytest.mark.asyncio
    async def test_d5_delete_removes_attachments(self, provider: LocalFileTaskProvider, tmp_path: Path) -> None:
        """C-ATT-10: DELETE removes all attachments along with the task."""
        created = await provider.create(
            TaskCreateRequest(agent_name="a", session_id="s", title="t", attachments={"k": {"v": 1}})
        )
        await provider.delete(created.id, force=True)
        # File should be gone (which removes the inline attachments dict).
        assert await provider.get(created.id) is None


class TestLocalProviderSideEffects:
    """E1-E4 — status transition side effects."""

    @pytest.mark.asyncio
    async def test_e1_pending_clears_suspension_reason(self, provider: LocalFileTaskProvider) -> None:
        """T1: transition to pending clears suspension_reason."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="suspended", suspension_reason="paused"))
        await provider.update(created.id, TaskPatchRequest(status="pending"))
        got = await provider.get(created.id)
        assert got is not None
        assert got.suspension_reason is None

    @pytest.mark.asyncio
    async def test_e2_in_progress_clears_suspension_reason_and_completed_at(
        self, provider: LocalFileTaskProvider
    ) -> None:
        """T2: transition to in_progress clears suspension_reason + completed_at."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        # Suspend (sets reason), then transition back to in_progress.
        await provider.update(created.id, TaskPatchRequest(status="suspended", suspension_reason="paused"))
        await provider.update(
            created.id,
            TaskPatchRequest(status="in_progress", lease_owner="o", lease_instance_id="i", lease_duration_seconds=60),
        )
        got = await provider.get(created.id)
        assert got is not None
        assert got.suspension_reason is None
        assert got.completed_at is None

    @pytest.mark.asyncio
    async def test_e3_completed_clears_suspension_reason(self, provider: LocalFileTaskProvider) -> None:
        """T3: transition to completed clears suspension_reason."""
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="suspended", suspension_reason="paused"))
        await provider.update(created.id, TaskPatchRequest(status="completed"))
        got = await provider.get(created.id)
        assert got is not None
        assert got.suspension_reason is None
        assert got.completed_at is not None

    @pytest.mark.asyncio
    async def test_e4_suspended_clears_completed_at(self, provider: LocalFileTaskProvider) -> None:
        """T4: transition to suspended clears completed_at if previously set."""
        # Note: this requires a path where completed_at could be set on
        # a non-completed task. In practice the framework only sets
        # completed_at on the completed transition, but the rule says
        # suspended should clear it regardless. Sketch the test to assert
        # this for whatever state the provider is in.
        created = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(created.id, TaskPatchRequest(status="suspended", suspension_reason="paused"))
        got = await provider.get(created.id)
        assert got is not None
        assert got.completed_at is None
        assert got.suspension_reason == "paused"


class TestLocalProviderPayloadPatch:
    """F1 — payload PATCH semantics."""

    @pytest.mark.asyncio
    async def test_f1_payload_object_shallow_merge(self, provider: LocalFileTaskProvider) -> None:
        """F1: payload PATCH with object shallow-merges."""
        created = await provider.create(
            TaskCreateRequest(agent_name="a", session_id="s", title="t", payload={"k1": "v1", "k2": "v2"})
        )
        await provider.update(created.id, TaskPatchRequest(payload={"k2": "new", "k3": "v3"}))
        got = await provider.get(created.id)
        assert got is not None and got.payload == {"k1": "v1", "k2": "new", "k3": "v3"}


class TestLocalProviderListParity:
    """G1-G7 — list filter parity."""

    @pytest.mark.asyncio
    async def test_g1_has_error_filter(self, provider: LocalFileTaskProvider) -> None:
        """C-PRV-9: list supports has_error filter."""
        await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t1",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        c2 = await provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                title="t2",
                status="in_progress",
                lease_owner="o",
                lease_instance_id="i",
                lease_duration_seconds=60,
            )
        )
        await provider.update(c2.id, TaskPatchRequest(status="completed", error={"type": "E", "message": "m"}))
        # `has_error` filter not implemented in local provider — RED.
        results = await provider.list(
            agent_name="a",
            session_id="s",
            has_error=True,  # type: ignore[call-arg]
        )
        assert len(results) == 1 and results[0].id == c2.id

    @pytest.mark.asyncio
    async def test_g3_pagination_limit_and_after(self, provider: LocalFileTaskProvider) -> None:
        """C-PRV-10: list supports after cursor + limit pagination."""
        for i in range(5):
            await provider.create(TaskCreateRequest(agent_name="a", session_id="s", title=f"t{i}"))
        # `limit` / `after` not implemented yet — RED.
        page1 = await provider.list(
            agent_name="a",
            session_id="s",
            limit=2,  # type: ignore[call-arg]
        )
        assert len(page1) == 2

    @pytest.mark.asyncio
    async def test_g5_before_rejected(self, provider: LocalFileTaskProvider) -> None:
        """C-PRV-10: list with `before` rejected."""
        with pytest.raises(Exception):
            await provider.list(
                agent_name="a",
                session_id="s",
                before="some-id",  # type: ignore[call-arg]
            )

    @pytest.mark.asyncio
    async def test_g7_agent_name_optional(self, provider: LocalFileTaskProvider) -> None:
        """C-PRV-8: agent_name + session_id optional (workspace-wide listing)."""
        await provider.create(TaskCreateRequest(agent_name="a1", session_id="s", title="t1"))
        await provider.create(TaskCreateRequest(agent_name="a2", session_id="s", title="t2"))
        # Today both are required positional args — RED via TypeError.
        results = await provider.list()  # type: ignore[call-arg]
        assert len(results) >= 2


class TestLocalProviderHostedParity:
    """Spec 031 / FR-008 — the local/file provider is a faithful double for
    the hosted store's If-Match optimistic concurrency: a stale-if_match write
    is classified IDENTICALLY to the hosted ``etag_mismatch``/412, and EVERY
    successful update (including lease-only) bumps the etag. Pins existing
    behavior so the framework's conflict handling stays provider-agnostic."""

    @pytest.mark.asyncio
    async def test_stale_if_match_classified_like_hosted(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        task_record = await provider.create(sample_create_request)
        patch = TaskPatchRequest(status="in_progress", if_match="stale-etag")
        with pytest.raises(_HostedConflict) as ei:
            await provider.update(task_record.id, patch)
        exc = ei.value
        # Hosted-identical classification: a _HostedConflict that ALSO behaves
        # as a ValueError (so callers catching either type converge), carrying
        # the hosted error code + 412 status.
        assert isinstance(exc, ValueError)
        assert getattr(exc, "_code", None) == "etag_mismatch"
        assert getattr(exc, "status_code", None) == 412

    @pytest.mark.asyncio
    async def test_lease_only_update_bumps_etag(
        self, provider: LocalFileTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        task_record = await provider.create(sample_create_request)
        # Lease renewal is only valid on an in_progress task — move it there first.
        moved = await provider.update(task_record.id, TaskPatchRequest(status="in_progress", if_match=task_record.etag))
        before = moved.etag
        # A lease-only PATCH (no status/payload change) MUST still move the etag,
        # exactly like the hosted store — otherwise a concurrent pinned-etag
        # writer would not detect the heartbeat's write.
        patch = TaskPatchRequest(
            lease_owner=moved.lease.owner if moved.lease else "owner-x",
            lease_instance_id=moved.lease.instance_id if moved.lease else "inst-x",
            lease_duration_seconds=60,
            if_match=before,
        )
        updated = await provider.update(task_record.id, patch)
        assert updated.etag and updated.etag != before, "lease-only update MUST bump the etag (hosted parity)"

    @pytest.mark.asyncio
    async def test_two_managers_one_store_cross_process_conflict(self, tmp_path: Path) -> None:
        """FR-009 — two independent providers bound to ONE store directory
        contend exactly as two hosted workers would: the second pinned-etag
        write loses with a hosted-identical conflict (deterministic, no OS
        write-atomicity reliance — the operations are sequenced)."""
        store = tmp_path / "shared"
        worker_a = LocalFileTaskProvider(base_dir=store)
        worker_b = LocalFileTaskProvider(base_dir=store)

        created = await worker_a.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                status="in_progress",
                title="t",
                payload={"input": {"n": 0}},
            )
        )
        tid, etag0 = created.id, created.etag

        # Both workers read the same etag, then both try to write pinned to it.
        a_view = await worker_a.get(tid)
        b_view = await worker_b.get(tid)
        assert a_view.etag == b_view.etag == etag0

        # Worker A writes first -> wins, etag advances.
        await worker_a.update(tid, TaskPatchRequest(payload={"a": 1}, if_match=a_view.etag))
        # Worker B writes pinned to the now-stale etag -> hosted-identical conflict.
        with pytest.raises(_HostedConflict) as ei:
            await worker_b.update(tid, TaskPatchRequest(payload={"b": 1}, if_match=b_view.etag))
        assert getattr(ei.value, "_code", None) == "etag_mismatch"
        # B recovers by re-reading the NEW state and retrying (optimistic concurrency).
        b_fresh = await worker_b.get(tid)
        recovered = await worker_b.update(tid, TaskPatchRequest(payload={"b": 1}, if_match=b_fresh.etag))
        assert recovered.payload.get("a") == 1 and recovered.payload.get("b") == 1
