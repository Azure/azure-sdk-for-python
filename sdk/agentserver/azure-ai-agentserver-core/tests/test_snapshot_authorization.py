# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Lifecycle routes trust only the hosted platform's /_agent/ calls; everything else needs an authorizer."""

import os
from unittest import mock

import httpx
import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from azure.ai.agentserver.core import AgentServerHost


_PLATFORM_PATHS = ["/_agent/before-snapshot", "/_agent/after-restore"]
_ALIAS_PATHS = ["/_before_snapshot", "/_after_restore"]
_LIFECYCLE_PATHS = _PLATFORM_PATHS + _ALIAS_PATHS


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
@pytest.mark.parametrize(
    ("path", "hosted"),
    [(path, False) for path in _LIFECYCLE_PATHS] + [(path, True) for path in _ALIAS_PATHS],
)
@pytest.mark.parametrize("decision", [False, 1, "true", RuntimeError("private-authorizer-detail")])
async def test_lifecycle_authorization_fails_closed_before_any_effect(monkeypatch, caplog, path, hosted, decision):
    if hosted:
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    else:
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", str(hosted).lower())
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    authorizer = mock.AsyncMock(
        return_value=decision,
        side_effect=decision if isinstance(decision, Exception) else None,
    )
    shadow = mock.AsyncMock(return_value=JSONResponse({"shadowed": True}))
    agent = AgentServerHost(
        configure_observability=None,
        routes=[Route(path, shadow, methods=["POST"])],
        lifecycle_authorizer=authorizer,
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
    authorizer.assert_awaited_once()
    request = authorizer.await_args.args[0]
    assert isinstance(request, Request)
    assert request.url.path == path


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
@pytest.mark.parametrize("snapshot", [None, "true", "false"])
async def test_lifecycle_routes_without_authorizer_return_404_outside_hosted(monkeypatch, path, snapshot):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    if snapshot is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", snapshot)
    catch_all = mock.AsyncMock(return_value=JSONResponse({"status": "ok"}))
    agent = AgentServerHost(
        configure_observability=None,
        routes=[Route("/_agent/{name}", catch_all, methods=["POST"])],
    )
    before_callback, after_callback = mock.AsyncMock(), mock.AsyncMock()
    agent.before_snapshot_handler(before_callback)
    agent.after_restore_handler(after_callback)
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    environment = dict(os.environ)
    config = vars(agent.config).copy()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        response = await client.post(path, json=_payload())
        assert (await client.get("/readiness")).status_code == 200

    assert response.status_code == 404
    assert os.environ == environment
    assert vars(agent.config) == config
    assert agent._lifecycle.assigned_session_id is None
    assert not agent._lifecycle.before_snapshot_completed
    for callback in (catch_all, before_callback, after_callback):
        callback.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("platform_route", [False, True])
async def test_untrusted_endpoint_without_authorizer_still_denies(monkeypatch, platform_route):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    agent = AgentServerHost(configure_observability=None)
    request = Request({"type": "http", "method": "POST", "path": "/_agent/after-restore", "headers": []})

    response = await agent._authorize_lifecycle_request(request, platform_route=platform_route)

    assert response is not None
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
@pytest.mark.parametrize("snapshot", [None, "true"])
async def test_hosted_without_authorizer_processes_only_platform_paths(monkeypatch, path, snapshot):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    if snapshot is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", snapshot)
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    agent = AgentServerHost(configure_observability=None)
    callback = mock.AsyncMock()
    if "before" in path:
        agent.before_snapshot_handler(callback)
    else:
        agent.after_restore_handler(callback)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        response = await client.post(path, json=_payload())

    if path in _PLATFORM_PATHS:
        assert response.status_code == 200
        callback.assert_awaited_once()
    else:
        assert response.status_code == 404
        callback.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
async def test_hosted_platform_paths_bypass_authorizer_but_aliases_require_it(monkeypatch, path):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    authorizer = mock.AsyncMock(return_value=False)
    agent = AgentServerHost(configure_observability=None, lifecycle_authorizer=authorizer)
    callback = mock.AsyncMock()
    if "before" in path:
        agent.before_snapshot_handler(callback)
    else:
        agent.after_restore_handler(callback)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=agent), base_url="http://testserver") as client:
        response = await client.post(path, json=_payload())

    if path in _PLATFORM_PATHS:
        assert response.status_code == 200
        callback.assert_awaited_once()
        authorizer.assert_not_awaited()
    else:
        assert response.status_code == 403
        callback.assert_not_awaited()
        authorizer.assert_awaited_once()


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
