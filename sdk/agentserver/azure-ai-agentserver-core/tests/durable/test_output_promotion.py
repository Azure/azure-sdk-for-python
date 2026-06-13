# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 019 Area C — Output always-attachment + cap (FR-C-005..007,
SC-8 / SC-8b / SC-9 / SC-10).

Verifies:

- The framework ALWAYS stores output via the ``_output`` attachment
  when non-null — even for tiny outputs (no inline threshold)
  (FR-C-005 / SC-8b).
- ``payload["output"]`` ALWAYS holds a ref or ``null``; never an
  inline value (FR-C-005).
- Output > 2 MB raises ``OutputTooLarge`` BEFORE the PATCH lands
  (FR-C-006 / SC-9).
- Suspend with ``output=None`` after a prior ``suspend(output=A)``
  durably writes ``None`` — no stale ``A`` remains (FR-C-007 /
  SC-10).

Reference: docs/task-and-streaming-spec.md §20, §23.2, §23.8, §53,
§59 C-OUT-1..6.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    Suspended,
    TaskContext,
    task,
)
import azure.ai.agentserver.core.durable._manager as mgr_mod
from azure.ai.agentserver.core.durable._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.durable._manager import TaskManager


def _config_stub():
    return type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest.fixture
def local(tmp_path: Path) -> LocalFileTaskProvider:
    return LocalFileTaskProvider(base_dir=tmp_path)


def _payload_output_is_ref(payload_output) -> bool:
    """Detect whether a `payload['output']` slot is a ref shape per §23.3."""
    return (
        isinstance(payload_output, dict)
        and len(payload_output) == 1
        and "__attachment_ref__" in payload_output
        and isinstance(payload_output["__attachment_ref__"], dict)
        and "key" in payload_output["__attachment_ref__"]
        and "hash" in payload_output["__attachment_ref__"]
    )


@pytest.mark.asyncio
async def test_suspend_output_always_uses_attachment(local) -> None:
    """FR-C-005 / SC-8b — suspend with even a tiny output MUST use
    the ``_output`` attachment; ``payload["output"]`` MUST be a ref,
    never the inline value.
    """
    @task(name="suspend_attach", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[dict]:
        return await ctx.suspend(output={"k": "v"}, reason="tiny")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        result = await my_task.run(task_id="t-tiny-suspend", input="x")
    # spec 022: result is raw output (Suspended wrapper removed)
        raw = await local.get("t-tiny-suspend")
        assert raw is not None
        assert raw.payload is not None
        assert _payload_output_is_ref(raw.payload.get("output")), (
            f"FR-C-005 / SC-8b — payload['output'] MUST be an "
            f"attachment ref, not an inline value; got "
            f"{raw.payload.get('output')!r}"
        )
        assert raw.attachments is not None
        assert "_output" in raw.attachments, (
            f"FR-C-005 — _output attachment MUST be present; got "
            f"attachments keys: {list(raw.attachments.keys())}"
        )
        assert raw.attachments["_output"] == {"k": "v"}
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_complete_output_always_uses_attachment(local) -> None:
    """FR-C-005 — ``_handle_success`` for non-ephemeral tasks must also
    write output via ``_output`` attachment, not inline.
    """
    @task(name="complete_attach", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "done"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-complete", input="x")
        raw = await local.get("t-complete")
        assert raw is not None
        assert raw.payload is not None
        assert _payload_output_is_ref(raw.payload.get("output")), (
            f"FR-C-005 — even completed-task output must be an "
            f"attachment ref; got {raw.payload.get('output')!r}"
        )
        assert raw.attachments is not None
        assert raw.attachments.get("_output") == "done"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.skip(reason="spec 022 FR-025: payload[output] no longer written")
@pytest.mark.asyncio
async def test_suspend_output_none_writes_explicit_null(local) -> None:
    """FR-C-007 / SC-10 / US-C4 — suspend with output=None after a
    prior suspend(output=A) MUST write explicit ``None`` — no stale
    ``A`` remains in the record.
    """
    turn_count = 0

    @task(name="output_none_writes", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[str]:
        nonlocal turn_count
        turn_count += 1
        if turn_count == 1:
            return await ctx.suspend(output="A", reason="first")
        return await ctx.suspend(output=None, reason="second")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        r1 = await my_task.run(task_id="t-none-explicit", input="x")
    # spec 022: result is raw output (Suspended wrapper removed)
        snap1 = await my_task.get("t-none-explicit")
        assert snap1 is not None and snap1.output == "A"

        r2 = await my_task.run(task_id="t-none-explicit", input="y")
    # spec 022: result is raw output (Suspended wrapper removed)
        snap2 = await my_task.get("t-none-explicit")
        assert snap2 is not None
        assert snap2.output is None, (
            f"FR-C-007 / SC-10 — after suspend(output=None) the "
            f"persisted output MUST be None; got {snap2.output!r}"
        )
        # And the raw payload's output slot is explicit null, not
        # absent (so a future re-read cannot trip over the difference).
        raw = await local.get("t-none-explicit")
        assert raw is not None
        assert raw.payload is not None
        assert raw.payload.get("output") is None, (
            f"FR-C-007 — payload['output'] should be explicit null; "
            f"got {raw.payload.get('output')!r}"
        )
        # _output attachment must be absent (was deleted in the
        # second suspend's PATCH).
        if raw.attachments is not None:
            assert "_output" not in raw.attachments, (
                "_output attachment leaked across a suspend(None) write"
            )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_output_over_cap_raises_output_too_large_pre_patch(local) -> None:
    """FR-C-006 / SC-9 — suspend / complete with output > 2 MB MUST
    raise ``OutputTooLarge`` BEFORE the PATCH lands.

    Strategy: build a payload that serializes > 2 MB; complete the
    task; verify ``OutputTooLarge`` is raised AND no terminal PATCH
    landed in the store (record stays in_progress with the prior
    lease).
    """
    from azure.ai.agentserver.core.durable._exceptions import OutputTooLarge

    # ~3 MB of JSON-serializable data.
    big_blob = "X" * (3 * 1024 * 1024)

    @task(name="output_too_large", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return big_blob

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        with pytest.raises(OutputTooLarge) as excinfo:
            await my_task.run(task_id="t-too-big", input="x")
    # spec 022 FR-077: exception.task_id removed
        assert excinfo.value.size_bytes > 2 * 1024 * 1024
        # No _output attachment should have landed.
        raw = await local.get("t-too-big")
        assert raw is not None
        if raw.attachments is not None:
            assert "_output" not in raw.attachments, (
                "_output attachment leaked despite OutputTooLarge — "
                "FR-C-006 requires the check to fire BEFORE the PATCH."
            )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_suspend_with_oversized_output_raises_output_too_large(local) -> None:
    """FR-C-006 / SC-9 — suspend path equivalent of the
    output-too-large test. Spec §39 lists ``ctx.suspend(output=...)``
    explicitly as a raise site; this guards the symmetric path
    (handler returns vs. handler suspends).

    Without the matching arm around ``_handle_suspend`` in
    ``_execute_task_loop``, the suspend-path OutputTooLarge would
    propagate up to the broad ``except Exception`` handler and be
    wrapped in ``TaskFailed`` — a developer-facing regression of the
    spec contract.
    """
    from azure.ai.agentserver.core.durable._exceptions import OutputTooLarge

    big_blob = "Y" * (3 * 1024 * 1024)

    @task(name="suspend_output_too_large", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[str]:
        return await ctx.suspend(output=big_blob, reason="oversized")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        with pytest.raises(OutputTooLarge) as excinfo:
            await my_task.run(task_id="t-suspend-too-big", input="x")
    # spec 022 FR-077: exception.task_id removed
        assert excinfo.value.size_bytes > 2 * 1024 * 1024
        # No _output attachment should have landed.
        raw = await local.get("t-suspend-too-big")
        assert raw is not None
        if raw.attachments is not None:
            assert "_output" not in raw.attachments, (
                "_output attachment leaked despite OutputTooLarge on "
                "the suspend path."
            )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
