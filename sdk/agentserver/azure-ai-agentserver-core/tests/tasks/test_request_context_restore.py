# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pytest

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core.tasks import TaskContext, task
import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, _call_id_from_input


class TaskInput(TypedDict):
    call_id: str
    prompt: str


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


def test_call_id_extraction_accepts_mapping_and_typed_object() -> None:
    class InputObject:
        call_id = "object-call"

    assert _call_id_from_input({"call_id": "mapping-call"}) == "mapping-call"
    assert _call_id_from_input(InputObject()) == "object-call"
    assert _call_id_from_input({"call_id": ""}) is None
    assert _call_id_from_input({"call_id": 42}) is None


@pytest.mark.asyncio
async def test_task_handler_restores_only_call_id_and_resets_outer_context(tmp_path: Path) -> None:
    @task(name="request-context-restore")
    async def handler(ctx: TaskContext[TaskInput]) -> tuple[str | None, str | None, str | None]:
        request_context = get_request_context()
        return request_context.call_id, request_context.user_id, request_context.session_id

    manager = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(base_dir=tmp_path))
    mgr_mod._manager = manager
    outer_token = set_request_context(FoundryAgentRequestContext(call_id="outer-call", user_id="outer-user"))
    await manager.startup()
    try:
        result = await handler.run(
            task_id="request-context-task",
            input={"call_id": "persisted-call", "prompt": "hello"},
        )
        assert result == ("persisted-call", None, None)
        assert get_request_context().call_id == "outer-call"
        assert get_request_context().user_id == "outer-user"
    finally:
        await manager.shutdown()
        reset_request_context(outer_token)
        mgr_mod._manager = None
