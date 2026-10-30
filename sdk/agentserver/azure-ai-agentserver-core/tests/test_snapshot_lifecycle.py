# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the private memory snapshot lifecycle endpoints."""

import asyncio
import os
from types import MappingProxyType
from unittest import mock

import httpx
import pytest
from starlette.responses import JSONResponse
from starlette.routing import Route

from azure.ai.agentserver.core import (
    AgentServerHost,
    AgentSessionContext,
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
from azure.ai.agentserver.core.tasks._manager import TaskManager, set_task_manager

_LIFECYCLE_TOKEN_ENV = "FOUNDRY_LIFECYCLE_TOKEN"
_LIFECYCLE_TOKEN_HEADER = "x-foundry-lifecycle-token"
_LIFECYCLE_TOKEN = "test-lifecycle-token"
_LIFECYCLE_HEADERS = {_LIFECYCLE_TOKEN_HEADER: _LIFECYCLE_TOKEN}
_LIFECYCLE_PATHS = [
    "/_agent/before-snapshot",
    "/_agent/after-restore",
    "/_before_snapshot",
    "/_after_restore",
]


@pytest.fixture(autouse=True)
def restore_process_environment():
    captured_environment = dict(os.environ)
    # Lifecycle routes are only registered when hosted or when a lifecycle
    # token is configured; tests opt in through the token.
    os.environ[_LIFECYCLE_TOKEN_ENV] = _LIFECYCLE_TOKEN
    yield
    os.environ.clear()
    os.environ.update(captured_environment)


@pytest.fixture()
def client(agent: AgentServerHost) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    )


def _after_restore_payload(
    *,
    session_id: str = "session-1",
    restore_id: str = "restore-1",
    overrides: dict[str, str] | None = None,
) -> dict[str, object]:
    return {
        "session_context": {
            "session_id": session_id,
            "restore_id": restore_id,
            "session_env_overrides": overrides or {},
        }
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("before_path", "after_path"),
    [
        ("/_agent/before-snapshot", "/_agent/after-restore"),
        ("/_before_snapshot", "/_after_restore"),
    ],
)
async def test_default_lifecycle_handlers_are_successful_noops(
    client: httpx.AsyncClient,
    before_path: str,
    after_path: str,
) -> None:
    before_response = await client.post(before_path, json={})
    after_response = await client.post(
        after_path,
        json=_after_restore_payload(),
    )

    assert before_response.status_code == 200
    assert before_response.json() == {"status": "ok"}
    assert after_response.status_code == 200
    assert after_response.json() == {"status": "ok"}
    assert "application/json" in before_response.headers["content-type"]
    assert "application/json" in after_response.headers["content-type"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        "/_agent/before-snapshot",
        "/_agent/after-restore",
        "/_before_snapshot",
        "/_after_restore",
    ],
)
async def test_lifecycle_routes_only_accept_post(
    client: httpx.AsyncClient,
    path: str,
) -> None:
    assert (await client.get(path)).status_code == 405


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "content", "headers"),
    [
        ("/_agent/before-snapshot", b"", {"content-type": "application/json"}),
        ("/_agent/before-snapshot", b"[]", {"content-type": "application/json"}),
        ("/_agent/before-snapshot", b"{", {"content-type": "application/json"}),
        ("/_agent/before-snapshot", b"{}", {"content-type": "text/plain"}),
        ("/_agent/after-restore", b"", {"content-type": "application/json"}),
        ("/_agent/after-restore", b"null", {"content-type": "application/json"}),
        ("/_agent/after-restore", b"{", {"content-type": "application/json"}),
        ("/_agent/after-restore", b"{}", {"content-type": "text/plain"}),
    ],
)
async def test_lifecycle_routes_reject_invalid_json_requests(
    client: httpx.AsyncClient,
    path: str,
    content: bytes,
    headers: dict[str, str],
) -> None:
    response = await client.post(path, content=content, headers=headers)

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"].startswith("invalid_")
    assert set(error) == {"code", "message"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"session_context": None},
        {"session_context": {}},
        {"session_context": {"session_id": "", "restore_id": "restore-1"}},
        _after_restore_payload(session_id="invalid\0session"),
        {"session_context": {"session_id": "session-1", "restore_id": ""}},
        {
            "session_context": {
                "session_id": "session-1",
                "restore_id": "restore-1",
                "session_env_overrides": [],
            }
        },
        {
            "session_context": {
                "session_id": "session-1",
                "restore_id": "restore-1",
                "session_env_overrides": {"COUNT": 1},
            }
        },
        _after_restore_payload(overrides={"": "value"}),
        _after_restore_payload(overrides={"INVALID=NAME": "value"}),
        _after_restore_payload(overrides={"VALUE": "invalid\0value"}),
        _after_restore_payload(
            session_id="session-1",
            overrides={"FOUNDRY_AGENT_SESSION_ID": "session-2"},
        ),
    ],
)
async def test_after_restore_rejects_invalid_session_context(
    client: httpx.AsyncClient,
    payload: dict[str, object],
) -> None:
    response = await client.post("/_agent/after-restore", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_after_restore_request",
            "message": "The after-restore request is invalid.",
        }
    }


@pytest.mark.asyncio
async def test_after_restore_validates_explicit_session_guid_in_hosted_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_GUID", raising=False)
    agent = AgentServerHost()
    callback_count = 0

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        nonlocal callback_count
        callback_count += 1
        assert context.session_env_overrides["FOUNDRY_AGENT_SESSION_GUID"] == "a" * 32

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        invalid = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                overrides={"FOUNDRY_AGENT_SESSION_GUID": "invalid-guid"},
            ),
        )

        assert invalid.status_code == 400
        assert invalid.json()["error"]["code"] == "invalid_after_restore_request"
        assert callback_count == 0
        assert "FOUNDRY_AGENT_SESSION_GUID" not in os.environ
        assert agent.config.session_guid == ""

        valid = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                overrides={"FOUNDRY_AGENT_SESSION_GUID": "a" * 32},
            ),
        )

    assert valid.status_code == 200
    assert callback_count == 1
    assert agent.config.session_guid == "a" * 32


@pytest.mark.asyncio
async def test_after_restore_allows_non_guid_session_value_outside_hosted_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    agent = AgentServerHost()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                overrides={"FOUNDRY_AGENT_SESSION_GUID": "legacy-session-value"},
            ),
        )

    assert response.status_code == 200
    assert agent.config.session_guid == "legacy-session-value"


@pytest.mark.asyncio
async def test_unknown_request_fields_are_ignored(client: httpx.AsyncClient) -> None:
    before_response = await client.post(
        "/_agent/before-snapshot",
        json={"future_context": {"enabled": True}},
    )
    payload = _after_restore_payload()
    payload["future_top_level"] = True
    session_context = payload["session_context"]
    assert isinstance(session_context, dict)
    session_context["future_nested"] = {"value": 1}

    after_response = await client.post("/_agent/after-restore", json=payload)

    assert before_response.status_code == 200
    assert after_response.status_code == 200


@pytest.mark.asyncio
async def test_after_restore_applies_environment_before_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "captured-session")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "captured-guid")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "captured-version")
    monkeypatch.delenv("RESTORED_VALUE", raising=False)
    agent = AgentServerHost()
    config = agent.config
    observed: dict[str, object] = {}

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        observed["session_id"] = os.environ["FOUNDRY_AGENT_SESSION_ID"]
        observed["session_guid"] = os.environ["FOUNDRY_AGENT_SESSION_GUID"]
        observed["restored_value"] = os.environ["RESTORED_VALUE"]
        observed["config_session_id"] = agent.config.session_id
        observed["config_session_guid"] = agent.config.session_guid
        observed["config_agent_version"] = agent.config.agent_version
        observed["config_identity_preserved"] = agent.config is config
        observed["context"] = context

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                session_id="restored-session",
                overrides={
                    "FOUNDRY_AGENT_SESSION_GUID": "restored-guid",
                    "FOUNDRY_AGENT_VERSION": "restored-version",
                    "RESTORED_VALUE": "available",
                },
            ),
        )

    assert response.status_code == 200
    assert observed["session_id"] == "restored-session"
    assert observed["session_guid"] == "restored-guid"
    assert observed["restored_value"] == "available"
    assert observed["config_session_id"] == "restored-session"
    assert observed["config_session_guid"] == "restored-guid"
    assert observed["config_agent_version"] == "restored-version"
    assert observed["config_identity_preserved"] is True
    context = observed["context"]
    assert isinstance(context, AgentSessionContext)
    assert isinstance(context.session_env_overrides, MappingProxyType)
    assert context.session_env_overrides == {
        "FOUNDRY_AGENT_SESSION_GUID": "restored-guid",
        "FOUNDRY_AGENT_VERSION": "restored-version",
        "RESTORED_VALUE": "available",
    }


@pytest.mark.asyncio
async def test_subclass_hooks_run_before_application_callbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    events: list[str] = []

    class ExtendedAgentServerHost(AgentServerHost):
        async def _before_snapshot(self) -> None:
            events.append("subclass-before-snapshot")

        async def _after_restore(self, context: AgentSessionContext) -> None:
            assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == context.session_id
            assert self.config.session_id == context.session_id
            events.append("subclass-after-restore")

    agent = ExtendedAgentServerHost()

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        events.append("application-before-snapshot")

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == context.session_id
        assert agent.config.session_id == context.session_id
        events.append("application-after-restore")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        before_response = await lifecycle_client.post(
            "/_agent/before-snapshot",
            json={},
        )
        after_response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(),
        )

    assert before_response.status_code == 200
    assert after_response.status_code == 200
    assert events == [
        "subclass-before-snapshot",
        "application-before-snapshot",
        "subclass-after-restore",
        "application-after-restore",
    ]


@pytest.mark.asyncio
async def test_subclass_before_snapshot_failure_skips_application_callback_and_retries() -> None:
    events: list[str] = []

    class ExtendedAgentServerHost(AgentServerHost):
        async def _before_snapshot(self) -> None:
            events.append("subclass")
            if events.count("subclass") == 1:
                raise RuntimeError("subclass failure")

    agent = ExtendedAgentServerHost()

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        events.append("application")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        failed = await lifecycle_client.post("/_agent/before-snapshot", json={})
        retried = await lifecycle_client.post("/_agent/before-snapshot", json={})

    assert failed.status_code == 500
    assert retried.status_code == 200
    assert events == ["subclass", "subclass", "application"]


@pytest.mark.asyncio
async def test_subclass_after_restore_failure_rolls_back_and_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "captured-session")
    events: list[str] = []

    class ExtendedAgentServerHost(AgentServerHost):
        async def _after_restore(self, context: AgentSessionContext) -> None:
            assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == context.session_id
            assert self.config.session_id == context.session_id
            events.append("subclass")
            if events.count("subclass") == 1:
                raise RuntimeError("subclass failure")

        def _restore_lifecycle_environment(self, *_args, **_kwargs) -> None:
            raise AssertionError("subclasses must not replace framework rollback")

    agent = ExtendedAgentServerHost()

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == context.session_id
        events.append("application")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        failed = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(session_id="restored-session"),
        )
        assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == "captured-session"
        assert agent.config.session_id == "captured-session"

        different_session = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                session_id="different-session",
                restore_id="restore-2",
            ),
        )
        retried = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(session_id="restored-session"),
        )

    assert failed.status_code == 500
    assert different_session.status_code == 409
    assert different_session.json()["error"]["code"] == "session_mismatch"
    assert retried.status_code == 200
    assert events == ["subclass", "subclass", "application"]


@pytest.mark.asyncio
async def test_after_restore_rehydrates_task_manager_session_state_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "captured-session")
    agent = AgentServerHost()
    task_manager = TaskManager(config=agent.config, provider=mock.Mock())
    agent._task_manager = task_manager  # pylint: disable=protected-access
    set_task_manager(task_manager)
    captured_instance_id = task_manager._instance_id  # pylint: disable=protected-access
    restored_instance_ids: list[str] = []
    callback_count = 0

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        nonlocal callback_count
        callback_count += 1
        assert task_manager._lease_owner == derive_lease_owner(  # pylint: disable=protected-access
            "test-agent",
            context.session_id,
        )
        restored_instance_ids.append(task_manager._instance_id)  # pylint: disable=protected-access
        if callback_count == 1:
            raise RuntimeError("restore failed")

    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=agent),
            base_url="http://testserver",
            headers=_LIFECYCLE_HEADERS,
        ) as lifecycle_client:
            failed = await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(session_id="restored-session"),
            )

            assert failed.status_code == 500
            assert task_manager._lease_owner == derive_lease_owner(  # pylint: disable=protected-access
                "test-agent",
                "captured-session",
            )

            retried = await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(session_id="restored-session"),
            )
    finally:
        set_task_manager(None)

    assert retried.status_code == 200
    assert task_manager._lease_owner == derive_lease_owner(  # pylint: disable=protected-access
        "test-agent",
        "restored-session",
    )
    assert restored_instance_ids[0] != captured_instance_id
    assert restored_instance_ids == [restored_instance_ids[0]] * 2


@pytest.mark.asyncio
async def test_protocol_subclass_hooks_compose_through_super() -> None:
    events: list[str] = []

    class BaseProtocolHost(AgentServerHost):
        async def _before_snapshot(self) -> None:
            await super()._before_snapshot()
            events.append("base-before")

        async def _after_restore(self, context: AgentSessionContext) -> None:
            await super()._after_restore(context)
            events.append("base-after")

    class DerivedProtocolHost(BaseProtocolHost):
        async def _before_snapshot(self) -> None:
            await super()._before_snapshot()
            events.append("derived-before")

        async def _after_restore(self, context: AgentSessionContext) -> None:
            await super()._after_restore(context)
            events.append("derived-after")

    agent = DerivedProtocolHost()

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        events.append("application-before")

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        del context
        events.append("application-after")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        assert (await lifecycle_client.post("/_agent/before-snapshot", json={})).status_code == 200
        assert (
            await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(),
            )
        ).status_code == 200

    assert events == [
        "base-before",
        "derived-before",
        "application-before",
        "base-after",
        "derived-after",
        "application-after",
    ]


@pytest.mark.asyncio
async def test_lifecycle_routes_cannot_be_overridden_by_subclasses() -> None:
    events: list[str] = []

    class EndpointOverrideHost(AgentServerHost):
        async def _before_snapshot_endpoint(self, _request):
            return JSONResponse({"overridden": True}, status_code=418)

        async def _after_restore_endpoint(self, _request):
            return JSONResponse({"overridden": True}, status_code=418)

        @staticmethod
        async def _read_json_object(_request):
            raise AssertionError("subclasses must not replace framework parsing")

        @staticmethod
        def _parse_session_context(_payload):
            raise AssertionError("subclasses must not replace framework parsing")

        async def _before_snapshot(self) -> None:
            events.append("before")

        async def _after_restore(self, context: AgentSessionContext) -> None:
            events.append(context.session_id)

    agent = EndpointOverrideHost()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        before_response = await lifecycle_client.post(
            "/_agent/before-snapshot",
            json={},
        )
        after_response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(),
        )

    assert before_response.status_code == 200
    assert after_response.status_code == 200
    assert events == ["before", "session-1"]


@pytest.mark.asyncio
async def test_after_restore_resets_omitted_overrides_to_captured_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CAPTURED_VALUE", "captured")
    monkeypatch.delenv("ADDED_VALUE", raising=False)
    agent = AgentServerHost()
    observed: list[tuple[str, str | None]] = []

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        del context
        observed.append(
            (
                os.environ["CAPTURED_VALUE"],
                os.environ.get("ADDED_VALUE"),
            )
        )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        first = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-1",
                overrides={
                    "CAPTURED_VALUE": "first-restore",
                    "ADDED_VALUE": "added",
                },
            ),
        )
        second = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(restore_id="restore-2"),
        )
        os.environ["ADDED_VALUE"] = "application-change"
        third = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(restore_id="restore-3"),
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 200
    assert observed == [
        ("first-restore", "added"),
        ("captured", None),
        ("captured", None),
    ]
    assert os.environ["CAPTURED_VALUE"] == "captured"
    assert "ADDED_VALUE" not in os.environ


@pytest.mark.asyncio
async def test_before_snapshot_refreshes_environment_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("UPDATED_VALUE", "captured")
    monkeypatch.setenv("REMOVED_VALUE", "captured")
    agent = AgentServerHost()
    observed: list[tuple[str, str | None]] = []

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        os.environ.pop("REMOVED_VALUE")

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        del context
        observed.append(
            (
                os.environ["UPDATED_VALUE"],
                os.environ.get("REMOVED_VALUE"),
            )
        )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        first = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-1",
                overrides={
                    "UPDATED_VALUE": "snapshot-value",
                    "REMOVED_VALUE": "restored-value",
                },
            ),
        )
        before = await lifecycle_client.post("/_agent/before-snapshot", json={})
        second = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(restore_id="restore-2"),
        )

    assert first.status_code == 200
    assert before.status_code == 200
    assert second.status_code == 200
    assert observed == [
        ("snapshot-value", "restored-value"),
        ("snapshot-value", None),
    ]


@pytest.mark.asyncio
async def test_after_restore_hydrates_ambient_request_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    outer_context = FoundryAgentRequestContext(
        call_id="call-1",
        user_id="user-1",
        session_id="captured-session",
    )
    token = set_request_context(outer_context)
    observed: list[tuple[str | None, str | None, str | None]] = []

    class ExtendedAgentServerHost(AgentServerHost):
        async def _after_restore(self, context: AgentSessionContext) -> None:
            current = get_request_context()
            observed.append((current.call_id, current.user_id, current.session_id))
            assert current.session_id == context.session_id

    agent = ExtendedAgentServerHost()

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        current = get_request_context()
        observed.append((current.call_id, current.user_id, current.session_id))
        assert current.session_id == context.session_id

    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=agent),
            base_url="http://testserver",
            headers=_LIFECYCLE_HEADERS,
        ) as lifecycle_client:
            response = await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(session_id="restored-session"),
            )

        assert response.status_code == 200
        assert observed == [
            ("call-1", "user-1", "restored-session"),
            ("call-1", "user-1", "restored-session"),
        ]
        assert get_request_context() is outer_context
    finally:
        reset_request_context(token)


@pytest.mark.asyncio
async def test_after_restore_retry_and_new_materialization_are_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    agent = AgentServerHost()
    restores: list[tuple[str, str]] = []

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        restores.append((context.restore_id, os.environ["RESTORE_VALUE"]))

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        first = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-1",
                overrides={"RESTORE_VALUE": "first"},
            ),
        )
        retry = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-1",
                overrides={"RESTORE_VALUE": "first"},
            ),
        )
        later_restore = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-2",
                overrides={"RESTORE_VALUE": "second"},
            ),
        )
        delayed_retry = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                restore_id="restore-1",
                overrides={"RESTORE_VALUE": "first"},
            ),
        )

    assert first.status_code == 200
    assert retry.status_code == 200
    assert later_restore.status_code == 200
    assert delayed_retry.status_code == 200
    assert restores == [
        ("restore-1", "first"),
        ("restore-2", "second"),
    ]
    assert os.environ["RESTORE_VALUE"] == "second"


@pytest.mark.asyncio
async def test_after_restore_rejects_a_different_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    agent = AgentServerHost()
    callback_count = 0

    @agent.after_restore_handler
    async def after_restore(
        context: AgentSessionContext,
    ) -> None:  # pylint: disable=unused-argument
        nonlocal callback_count
        callback_count += 1

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        assert (
            await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(session_id="session-1"),
            )
        ).status_code == 200
        response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(session_id="session-2", restore_id="restore-2"),
        )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "session_mismatch"
    assert callback_count == 1
    assert agent.config.session_id == "session-1"


@pytest.mark.asyncio
async def test_before_snapshot_retries_once_and_resets_after_restore(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    agent = AgentServerHost()
    callback_count = 0

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        nonlocal callback_count
        callback_count += 1

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        assert (await lifecycle_client.post("/_agent/before-snapshot", json={})).status_code == 200
        assert (await lifecycle_client.post("/_agent/before-snapshot", json={})).status_code == 200
        assert callback_count == 1

        assert (
            await lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(),
            )
        ).status_code == 200
        assert (await lifecycle_client.post("/_agent/before-snapshot", json={})).status_code == 200

    assert callback_count == 2


@pytest.mark.asyncio
async def test_after_restore_failure_is_sanitized_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "captured-session")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "captured-version")
    monkeypatch.setenv("RESTORED_VALUE", "captured-value")
    agent = AgentServerHost()

    @agent.after_restore_handler
    async def after_restore(
        context: AgentSessionContext,
    ) -> None:  # pylint: disable=unused-argument
        raise RuntimeError("secret connection string")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        response = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                session_id="restored-session",
                overrides={
                    "FOUNDRY_AGENT_VERSION": "restored-version",
                    "RESTORED_VALUE": "restored-value",
                },
            ),
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "after_restore_failed",
            "message": "The after-restore hook failed.",
        }
    }
    assert "secret" not in response.text
    assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == "captured-session"
    assert os.environ["RESTORED_VALUE"] == "captured-value"
    assert agent.config.session_id == "captured-session"
    assert agent.config.agent_version == "captured-version"


@pytest.mark.asyncio
async def test_after_restore_cancellation_rolls_back_and_can_be_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "captured-session")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "captured-version")
    monkeypatch.setenv("RESTORED_VALUE", "captured-value")
    agent = AgentServerHost()
    callback_started = asyncio.Event()
    callback_count = 0

    @agent.after_restore_handler
    async def after_restore(context: AgentSessionContext) -> None:
        nonlocal callback_count
        callback_count += 1
        assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == context.session_id
        assert os.environ["RESTORED_VALUE"] == "restored-value"
        assert agent.config.agent_version == "restored-version"
        if callback_count == 1:
            callback_started.set()
            await asyncio.Event().wait()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        request_task = asyncio.create_task(
            lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(
                    session_id="restored-session",
                    overrides={
                        "FOUNDRY_AGENT_VERSION": "restored-version",
                        "RESTORED_VALUE": "restored-value",
                    },
                ),
            )
        )
        await callback_started.wait()
        request_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await request_task

        assert os.environ["FOUNDRY_AGENT_SESSION_ID"] == "captured-session"
        assert os.environ["RESTORED_VALUE"] == "captured-value"
        assert agent.config.session_id == "captured-session"
        assert agent.config.agent_version == "captured-version"

        retried = await lifecycle_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(
                session_id="restored-session",
                overrides={
                    "FOUNDRY_AGENT_VERSION": "restored-version",
                    "RESTORED_VALUE": "restored-value",
                },
            ),
        )

    assert retried.status_code == 200
    assert callback_count == 2


@pytest.mark.asyncio
async def test_before_snapshot_failure_can_be_retried() -> None:
    agent = AgentServerHost()
    callback_count = 0

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        nonlocal callback_count
        callback_count += 1
        if callback_count == 1:
            raise RuntimeError("secret failure")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        failed = await lifecycle_client.post("/_agent/before-snapshot", json={})
        retried = await lifecycle_client.post("/_agent/before-snapshot", json={})

    assert failed.status_code == 500
    assert failed.json()["error"]["code"] == "before_snapshot_failed"
    assert "secret" not in failed.text
    assert retried.status_code == 200
    assert callback_count == 2


@pytest.mark.asyncio
async def test_lifecycle_hooks_are_serialized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    agent = AgentServerHost()
    before_started = asyncio.Event()
    release_before = asyncio.Event()
    after_called = asyncio.Event()

    @agent.before_snapshot_handler
    async def before_snapshot() -> None:
        before_started.set()
        await release_before.wait()

    @agent.after_restore_handler
    async def after_restore(
        context: AgentSessionContext,
    ) -> None:  # pylint: disable=unused-argument
        after_called.set()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        before_task = asyncio.create_task(lifecycle_client.post("/_agent/before-snapshot", json={}))
        await before_started.wait()
        after_task = asyncio.create_task(
            lifecycle_client.post(
                "/_agent/after-restore",
                json=_after_restore_payload(),
            )
        )
        await asyncio.sleep(0)
        assert not after_called.is_set()

        release_before.set()
        before_response, after_response = await asyncio.gather(before_task, after_task)

    assert before_response.status_code == 200
    assert after_response.status_code == 200
    assert after_called.is_set()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        "/_agent/before-snapshot",
        "/_before_snapshot",
    ],
)
async def test_reserved_lifecycle_route_cannot_be_shadowed(path: str) -> None:
    async def shadowed_route(_request):
        return JSONResponse({"shadowed": True}, status_code=418)

    agent = AgentServerHost(
        routes=[
            Route(
                path,
                shadowed_route,
                methods=["POST"],
            )
        ]
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
        headers=_LIFECYCLE_HEADERS,
    ) as lifecycle_client:
        response = await lifecycle_client.post(path, json={})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_agent_session_context_defensively_copies_overrides() -> None:
    overrides = {"VALUE": "original"}
    context = AgentSessionContext(
        session_id="session-1",
        restore_id="restore-1",
        session_env_overrides=overrides,
    )

    overrides["VALUE"] = "changed"

    assert context.session_env_overrides == {"VALUE": "original"}
    with pytest.raises(TypeError):
        context.session_env_overrides["VALUE"] = "changed"  # type: ignore[index]


def test_agent_session_context_repr_excludes_environment_overrides() -> None:
    secret = "sentinel-secret-override"
    context = AgentSessionContext(
        session_id="session-1",
        restore_id="restore-1",
        session_env_overrides={"CONNECTION_STRING": secret},
    )

    assert secret not in repr(context)
    assert "session_env_overrides" not in repr(context)


def test_lifecycle_decorators_return_original_functions() -> None:
    agent = AgentServerHost()

    async def before_snapshot() -> None:
        pass

    async def after_restore(context: AgentSessionContext) -> None:
        del context

    assert agent.before_snapshot_handler(before_snapshot) is before_snapshot
    assert agent.after_restore_handler(after_restore) is after_restore


def test_lifecycle_routes_are_registered_before_user_routes() -> None:
    agent = AgentServerHost()

    assert [route.path for route in agent.routes[:4]] == [
        "/_agent/before-snapshot",
        "/_agent/after-restore",
        "/_before_snapshot",
        "/_after_restore",
    ]


def test_agent_session_context_defaults_to_immutable_empty_overrides() -> None:
    context = AgentSessionContext(session_id="session-1", restore_id="restore-1")

    assert context.session_env_overrides == {}
    assert isinstance(context.session_env_overrides, MappingProxyType)


# ----------------------------------------------------------------------
# Lifecycle endpoint authentication and override validation
# ----------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
@pytest.mark.parametrize(
    "headers",
    [
        {},
        {_LIFECYCLE_TOKEN_HEADER: ""},
        {_LIFECYCLE_TOKEN_HEADER: "wrong-token"},
        {_LIFECYCLE_TOKEN_HEADER: _LIFECYCLE_TOKEN + "x"},
    ],
)
async def test_lifecycle_routes_reject_missing_or_invalid_token(
    agent: AgentServerHost,
    path: str,
    headers: dict[str, str],
) -> None:
    events: list[str] = []
    agent.after_restore_handler(lambda context: _record(events, context.session_id))
    os.environ.pop("CUSTOM_VALUE", None)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
    ) as anonymous_client:
        response = await anonymous_client.post(
            path,
            json=_after_restore_payload(overrides={"CUSTOM_VALUE": "injected"}),
            headers=headers,
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized_lifecycle_request"
    assert "CUSTOM_VALUE" not in os.environ
    assert agent._lifecycle.assigned_session_id is None  # pylint: disable=protected-access
    assert events == []


async def _record(events: list[str], value: str) -> None:
    events.append(value)


@pytest.mark.asyncio
async def test_after_restore_with_valid_token_applies_overrides(client: httpx.AsyncClient) -> None:
    os.environ.pop("CUSTOM_VALUE", None)

    response = await client.post(
        "/_agent/after-restore",
        json=_after_restore_payload(overrides={"CUSTOM_VALUE": "restored"}),
    )

    assert response.status_code == 200
    assert os.environ["CUSTOM_VALUE"] == "restored"


def test_lifecycle_token_is_fixed_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = AgentServerHost()
    monkeypatch.setenv(_LIFECYCLE_TOKEN_ENV, "rotated-after-startup")

    assert agent._lifecycle_token == _LIFECYCLE_TOKEN  # pylint: disable=protected-access


@pytest.mark.parametrize("path", _LIFECYCLE_PATHS)
def test_lifecycle_routes_are_absent_when_not_hosted_and_no_token(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    monkeypatch.delenv(_LIFECYCLE_TOKEN_ENV, raising=False)
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    agent = AgentServerHost()

    assert path not in [route.path for route in agent.routes]


@pytest.mark.asyncio
async def test_lifecycle_routes_return_404_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_LIFECYCLE_TOKEN_ENV, raising=False)
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    agent = AgentServerHost()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
    ) as anonymous_client:
        response = await anonymous_client.post(
            "/_agent/after-restore",
            json=_after_restore_payload(overrides={"CUSTOM_VALUE": "injected"}),
        )

    assert response.status_code == 404
    assert "CUSTOM_VALUE" not in os.environ


def test_lifecycle_routes_are_registered_when_hosted_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(_LIFECYCLE_TOKEN_ENV, raising=False)
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "foundry")

    agent = AgentServerHost()

    assert [route.path for route in agent.routes[:4]] == _LIFECYCLE_PATHS


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "denied_key",
    [
        "LD_PRELOAD",
        "ld_preload",
        "DYLD_INSERT_LIBRARIES",
        "PATH",
        "HOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "HTTPS_PROXY",
        "https_proxy",
        "ALL_PROXY",
        "NO_PROXY",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "REQUESTS_CA_BUNDLE",
        "CURL_CA_BUNDLE",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "FOUNDRY_HOSTING_ENVIRONMENT",
        "FOUNDRY_PROJECT_ENDPOINT",
        "FOUNDRY_LIFECYCLE_TOKEN",
        "AZURE_CLIENT_SECRET",
        "MSI_ENDPOINT",
        "IDENTITY_HEADER",
    ],
)
async def test_after_restore_rejects_reserved_override_keys(
    client: httpx.AsyncClient,
    agent: AgentServerHost,
    denied_key: str,
) -> None:
    os.environ.pop("CUSTOM_VALUE", None)
    previous = os.environ.get(denied_key)

    response = await client.post(
        "/_agent/after-restore",
        json=_after_restore_payload(overrides={"CUSTOM_VALUE": "injected", denied_key: "injected"}),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_after_restore_request"
    assert os.environ.get(denied_key) == previous
    assert "CUSTOM_VALUE" not in os.environ
    assert agent._lifecycle.assigned_session_id is None  # pylint: disable=protected-access


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "overrides",
    [
        {"": "value"},
        {"1LEADING_DIGIT": "value"},
        {"HAS-DASH": "value"},
        {"HAS SPACE": "value"},
        {"HAS=EQUALS": "value"},
        {"HAS\0NUL": "value"},
        {"HAS.DOT": "value"},
        {"CUSTOM_VALUE": "has\0nul"},
        {"K" * 257: "value"},
        {"CUSTOM_VALUE": "v" * (32 * 1024 + 1)},
        {f"CUSTOM_{index}": "value" for index in range(257)},
    ],
)
async def test_after_restore_rejects_malformed_or_oversized_overrides(
    client: httpx.AsyncClient,
    agent: AgentServerHost,
    overrides: dict[str, str],
) -> None:
    os.environ.pop("CUSTOM_VALUE", None)
    baseline = dict(os.environ)

    response = await client.post(
        "/_agent/after-restore",
        json=_after_restore_payload(overrides={"SAFE_VALUE": "safe", **overrides}),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_after_restore_request"
    assert dict(os.environ) == baseline
    assert agent._lifecycle.assigned_session_id is None  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_after_restore_accepts_boundary_sized_overrides(client: httpx.AsyncClient) -> None:
    key = "K" * 256
    overrides = {f"CUSTOM_{index}": "value" for index in range(255)}
    overrides[key] = "v" * (32 * 1024)

    response = await client.post("/_agent/after-restore", json=_after_restore_payload(overrides=overrides))

    assert response.status_code == 200
    assert os.environ[key] == "v" * (32 * 1024)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/_agent/before-snapshot", "/_agent/after-restore"])
async def test_lifecycle_routes_reject_oversized_bodies(client: httpx.AsyncClient, path: str) -> None:
    padding = "p" * (1024 * 1024)
    body = ('{"padding": "' + padding + '"}').encode("utf-8")

    response = await client.post(path, content=body, headers={"content-type": "application/json"})

    assert response.status_code == 400
    assert response.json()["error"]["code"].startswith("invalid_")


@pytest.mark.asyncio
async def test_lifecycle_routes_reject_oversized_declared_length(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/_agent/before-snapshot",
        content=b"{}",
        headers={"content-type": "application/json", "content-length": str(2 * 1024 * 1024)},
    )

    assert response.status_code == 400
