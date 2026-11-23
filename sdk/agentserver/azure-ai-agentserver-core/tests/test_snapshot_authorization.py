# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Authorization must precede all snapshot lifecycle effects."""

import os
from unittest import mock

import httpx
import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from azure.ai.agentserver.core import AgentServerHost


_LIFECYCLE_PATHS = [
    "/_agent/before-snapshot",
    "/_before_snapshot",
    "/_agent/after-restore",
    "/_after_restore",
]


@pytest.fixture(autouse=True)
def restore_process_environment():
    with mock.patch.dict(os.environ):
        yield


def _payload():
    return {
        "session_context": {
            "session_id": "authorized-session",
            "restore_id": "restore-1",
            "session_env_overrides": {
                "FOUNDRY_PROJECT_ENDPOINT": "https://restored.example",
                "LIFECYCLE_TEST_VALUE": "restored",
            },
        }
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
@pytest.mark.parametrize("hosted", [False, True])
@pytest.mark.parametrize("decision", [None, False, 1, "true", RuntimeError("private-authorizer-detail")])
async def test_lifecycle_authorization_fails_closed_before_any_effect(monkeypatch, caplog, path, hosted, decision):
    if hosted:
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    else:
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", str(hosted).lower())
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    authorizer = None
    if decision is not None:
        authorizer = mock.AsyncMock(
            return_value=decision,
            side_effect=decision if isinstance(decision, Exception) else None,
        )
    shadow = mock.AsyncMock(return_value=JSONResponse({"shadowed": True}))
    options = {"lifecycle_authorizer": authorizer} if authorizer is not None else {}
    agent = AgentServerHost(
        configure_observability=None,
        routes=[Route(path, shadow, methods=["POST"])],
        **options,
    )
    before_callback, after_callback = mock.AsyncMock(), mock.AsyncMock()
    agent.before_snapshot_handler(before_callback)
    agent.after_restore_handler(after_callback)
    before_hook, after_hook = mock.AsyncMock(), mock.AsyncMock()
    monkeypatch.setattr(agent, "_before_snapshot", before_hook)
    monkeypatch.setattr(agent, "_after_restore", after_hook)
    activate = mock.AsyncMock()
    monkeypatch.setattr(agent, "_activate_task_manager", activate)
    read_body = mock.AsyncMock(side_effect=AssertionError("unauthorized body read"))
    monkeypatch.setattr(AgentServerHost, "_read_json_object", read_body)
    environment = dict(os.environ)
    config = vars(agent.config).copy()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        response = await client.post(path, json=_payload())

    assert response.status_code == (500 if isinstance(decision, Exception) else 403)
    assert response.json()["error"]["code"] == (
        "lifecycle_authorization_failed" if isinstance(decision, Exception) else "lifecycle_forbidden"
    )
    assert "private-authorizer-detail" not in response.text
    assert "private-authorizer-detail" not in caplog.text
    assert os.environ == environment
    assert vars(agent.config) == config
    assert agent._lifecycle.assigned_session_id is None
    assert not agent._lifecycle.before_snapshot_completed
    assert not agent._lifecycle.completed_restore_ids
    assert agent._lifecycle.pending_rollback is None
    assert agent._task_manager is None
    for callback in (shadow, before_callback, after_callback, before_hook, after_hook, activate, read_body):
        callback.assert_not_awaited()
    if authorizer is not None:
        authorizer.assert_awaited_once()
        request = authorizer.await_args.args[0]
        assert isinstance(request, Request)
        assert request.url.path == path


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
async def test_cached_lifecycle_success_still_requires_authorization(path):
    authorizer = mock.AsyncMock(side_effect=[True, False])
    agent = AgentServerHost(configure_observability=None, lifecycle_authorizer=authorizer)
    callback = mock.AsyncMock()
    if "before" in path:
        agent.before_snapshot_handler(callback)
    else:
        agent.after_restore_handler(callback)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        response = await client.post(path, json=_payload())
        assert response.status_code == 200
        environment = dict(os.environ)
        config = vars(agent.config).copy()
        denied = await client.post(path, json=_payload())

    assert denied.status_code == 403
    assert os.environ == environment
    assert vars(agent.config) == config
    callback.assert_awaited_once()
    assert authorizer.await_count == 2


@pytest.mark.asyncio
async def test_lifecycle_authorization_does_not_intercept_other_routes():
    authorizer = mock.AsyncMock(return_value=False)

    async def invoke(_request):
        return JSONResponse({"status": "ok"})

    agent = AgentServerHost(
        configure_observability=None,
        lifecycle_authorizer=authorizer,
        routes=[Route("/invoke-test", invoke, methods=["POST"])],
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        assert (await client.get("/readiness")).status_code == 200
        assert (await client.post("/invoke-test", json={})).status_code == 200

    authorizer.assert_not_awaited()
