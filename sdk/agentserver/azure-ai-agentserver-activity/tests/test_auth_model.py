# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the outbound-auth model selection (simple vs digital worker).

``ActivityAgentServerHost`` defaults to the *simple* Teams agent model (the
agent instance identity mints the Bot Connector token directly). Passing
``digital_worker=True`` switches to the blueprint + federated-identity model.
These tests pin the connection env vars and bridge flag each mode produces.
"""

import pytest

from azure.ai.agentserver.activity import ActivityAgentServerHost
from azure.ai.agentserver.activity import _m365_bridge as bridge

_CONN_PREFIX = "CONNECTIONS"
_FOUNDRY_PREFIX = "FOUNDRY_AGENT"

_AUTHTYPE = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE"
_CLIENTID = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID"
_TENANTID = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID"
_AUTHORITY = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY"
_SCOPE0 = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__SCOPES__0"

_BOTFRAMEWORK_SCOPE = "https://api.botframework.com/.default"
_AGENTIC_SCOPE = "5a807f24-c9de-44ee-a3a7-329e88a00ffc/.default"


class _StubAgentApp:
    """Minimal stand-in for the M365 AgentApplication (avoids a real build)."""

    def __init__(self):
        self.adapter = object()
        self.registered = []

    def activity(self, activity_type):
        def decorator(fn):
            self.registered.append(("activity", activity_type, fn))
            return fn
        return decorator

    def error(self, fn):
        self.registered.append(("error", None, fn))
        return fn


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove all CONNECTIONS__* / FOUNDRY_AGENT_* env before each test."""
    import os

    for key in list(os.environ):
        if key.startswith(_CONN_PREFIX) or key.startswith(_FOUNDRY_PREFIX) or key.startswith("CONNECTIONSMAP"):
            monkeypatch.delenv(key, raising=False)
    yield


def _make_host(monkeypatch, *, digital_worker):
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")
    monkeypatch.setenv("FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID", "blueprint-bbb")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")
    # Inject a stub AgentApplication so construction does not require a live
    # M365 SDK build; we only assert env-seeding / mode selection here.
    return ActivityAgentServerHost.from_agent_application(
        _StubAgentApp(),
        digital_worker=digital_worker,
        configure_observability=None,
    )


def test_simple_is_the_default(monkeypatch):
    """digital_worker defaults to False; the injected-app path seeds no env
    (the app already owns its connection manager)."""
    import os

    host = _make_host(monkeypatch, digital_worker=False)

    assert host._digital_worker is False
    assert _CLIENTID not in os.environ


def test_digital_worker_opt_in(monkeypatch):
    """digital_worker=True is recorded on the host; the injected-app path seeds no env."""
    import os

    host = _make_host(monkeypatch, digital_worker=True)

    assert host._digital_worker is True
    assert _CLIENTID not in os.environ


def test_default_keyword_matches_explicit_false(monkeypatch):
    # No digital_worker kwarg at all -> must behave exactly like False.
    host = ActivityAgentServerHost.from_agent_application(_StubAgentApp(), configure_observability=None)

    assert host._digital_worker is False


def test_simple_mode_does_not_apply_fmi_patch(monkeypatch):
    """In simple mode the MSAL FMI/DefaultAzureCredential patch must not run."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    bridge.build_m365_app(digital_worker=False, agent_app=_StubAgentApp())

    assert applied["called"] is False


def test_digital_worker_applies_fmi_patch(monkeypatch):
    """In digital-worker mode the MSAL FMI patch is applied during build."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    bridge.build_m365_app(digital_worker=True, agent_app=_StubAgentApp())

    assert applied["called"] is True


def test_build_m365_app_rejects_conflicting_kwargs():
    """Injecting agent_app= alongside component kwargs raises ValueError."""
    with pytest.raises(ValueError, match="agent_app="):
        bridge.build_m365_app(agent_app=_StubAgentApp(), storage=object())


def test_seed_connection_env_public_helper(monkeypatch):
    """seed_connection_env populates CLIENTID from the Foundry instance identity."""
    import os

    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")

    ActivityAgentServerHost.seed_connection_env()

    assert os.environ[_AUTHTYPE] == "UserManagedIdentity"
    assert os.environ[_CLIENTID] == "instance-aaa"
    assert os.environ[_SCOPE0] == _BOTFRAMEWORK_SCOPE
    assert os.environ[_TENANTID] == "tenant-ccc"
    assert os.environ[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"


def test_seed_connection_env_digital_worker(monkeypatch):
    """seed_connection_env(digital_worker=True) uses the blueprint identity + scope."""
    import os

    monkeypatch.setenv("FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID", "blueprint-bbb")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")

    ActivityAgentServerHost.seed_connection_env(digital_worker=True)

    assert os.environ[_CLIENTID] == "blueprint-bbb"
    assert os.environ[_SCOPE0] == _AGENTIC_SCOPE


def test_seed_connection_env_does_not_overwrite(monkeypatch):
    """seed_connection_env never overwrites an explicitly-set value."""
    import os

    monkeypatch.setenv(_CLIENTID, "preset-client")
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")

    ActivityAgentServerHost.seed_connection_env()

    assert os.environ[_CLIENTID] == "preset-client"
