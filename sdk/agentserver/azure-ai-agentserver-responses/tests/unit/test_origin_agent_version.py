# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Responses handlers expose the persisted core task version, not request version."""

from __future__ import annotations

import time

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import TaskContext
from azure.ai.agentserver.responses import (
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses.models import CreateResponse
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags
from azure.ai.agentserver.responses.store._file import FileResponseStore


@pytest.mark.parametrize("origin", ["1", None])
@pytest.mark.parametrize("entry_mode", ["fresh", "resumed", "recovered"])
def test_response_context_forwards_same_read_only_task_version(origin: str | None, entry_mode: str) -> None:
    context = ResponseContext(
        response_id="response",
        request=CreateResponse(model="m", input="hello"),
        mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
    )
    assert context.origin_agent_version is None
    context._task_context = TaskContext(
        task_id="task", session_id="session", input={}, entry_mode=entry_mode, origin_agent_version=origin
    )
    assert context.origin_agent_version == origin
    with pytest.raises(AttributeError):
        context.origin_agent_version = "2"


def test_real_handler_uses_task_origin_not_request_agent_reference(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "1")
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True),
        store=FileResponseStore(storage_dir=tmp_path / "responses"),
        configure_observability=None,
    )
    observed = []

    @host.response_handler
    async def handler(request, context, cancellation_signal):
        observed.append(context.origin_agent_version)
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    with TestClient(host) as client:
        response = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hello",
                "store": True,
                "background": True,
                "agent_reference": {"type": "agent_reference", "name": "requested", "version": "2"},
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        deadline = time.monotonic() + 5
        while body["status"] == "in_progress":
            assert time.monotonic() < deadline, body
            time.sleep(0.01)
            body = client.get(f"/responses/{body['id']}").json()
        assert body["status"] == "completed", body
        assert observed == ["1"]
