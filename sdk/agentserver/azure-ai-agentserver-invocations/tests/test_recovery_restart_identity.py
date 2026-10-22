# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Persisted function identity must survive a fresh Invocations-only process."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


_RESTART_PROBE = textwrap.dedent(
    """
    import asyncio
    from datetime import datetime, timedelta, timezone
    import json
    import os
    from pathlib import Path
    from unittest.mock import patch

    from azure.ai.agentserver.core.tasks import TaskContext, set_resilient_tasks_enabled, task
    from azure.ai.agentserver.core.tasks._decorator import _HOST_BOUND_TASK_NAMES, _REGISTERED_DESCRIPTORS
    from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager, _SCHEMA_VERSION, _SCHEMA_VERSION_KEY
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    from azure.ai.agentserver.invocations import InvocationAgentServerHost

    assert not _HOST_BOUND_TASK_NAMES
    assert not _REGISTERED_DESCRIPTORS
    seen = []

    @task(name="ordinary_invocations_work")
    async def work(ctx: TaskContext[dict]) -> None:
        seen.append(ctx.task_id)

    async def main():
        store = LocalFileTaskProvider(Path(os.environ["AGENTSERVER_STATE_ROOT"]) / "tasks")
        set_resilient_tasks_enabled(True)
        with patch.object(TaskManager, "_create_provider", staticmethod(lambda _: store)):
            host = InvocationAgentServerHost(configure_observability=None)
            for task_id, name in (
                ("known", work.name),
                ("responses", "responses_resilient_one_shot"),
                ("legacy", None),
            ):
                payload = {"input": {"original_task": task_id}, _SCHEMA_VERSION_KEY: _SCHEMA_VERSION}
                if task_id == "responses" and os.environ["PROBE_PRE_SCHEMA"] == "true":
                    payload.pop(_SCHEMA_VERSION_KEY)
                source = TaskManager._build_source(name) if name else {"type": "agentserver.task"}
                info = await store.create(
                    TaskCreateRequest(
                        id=task_id,
                        agent_name=host.config.agent_name or "default",
                        session_id=host.config.session_id or "local",
                        status="in_progress",
                        title="unrelated title",
                        payload=payload,
                        source=source,
                        lease_owner=derive_lease_owner(
                            host.config.agent_name or "unknown-agent", host.config.session_id or "local"
                        ),
                        lease_instance_id="interrupted-instance",
                        lease_duration_seconds=60,
                    )
                )
                info.lease.expires_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
                store._write_task(info)
            before = await store.get("responses")
            async with host.router.lifespan_context(host):
                executions = [
                    active.execution_task
                    for active in host._task_manager._active_tasks.values()
                    if active.execution_task is not None
                ]
                await asyncio.wait_for(asyncio.gather(*executions), timeout=5)
                after = await store.get("responses")
                print(json.dumps({"seen": seen, "responses_record_exists": after is not None}))
                assert set(seen) == {"known", "legacy"}, seen
                assert after is not None
                assert after.status == before.status == "in_progress"
                assert after.etag == before.etag
                assert after.lease.instance_id == before.lease.instance_id == "interrupted-instance"
                assert after.lease.generation == before.lease.generation
                assert after.payload == before.payload

    asyncio.run(main())
    """
)


@pytest.mark.parametrize("pre_schema", [False, True])
def test_restart_preserves_unregistered_responses_identity(tmp_path: Path, pre_schema: bool) -> None:
    env = {key: value for key, value in os.environ.items() if not key.startswith("FOUNDRY_")}
    env.update(
        AGENTSERVER_TASKS_BACKEND="local",
        AGENTSERVER_STATE_ROOT=str(tmp_path),
        PROBE_PRE_SCHEMA=str(pre_schema).lower(),
    )
    result = subprocess.run(
        [sys.executable, "-c", _RESTART_PROBE],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    evidence = json.loads(result.stdout.splitlines()[-1])
    assert set(evidence["seen"]) == {"known", "legacy"}
    assert evidence["responses_record_exists"]
