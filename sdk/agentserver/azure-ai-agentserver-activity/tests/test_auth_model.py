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


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove all CONNECTIONS__* / FOUNDRY_AGENT_* env and reset bridge state."""
    import os

    for key in list(os.environ):
        if key.startswith(_CONN_PREFIX) or key.startswith(_FOUNDRY_PREFIX) or key.startswith("CONNECTIONSMAP"):
            monkeypatch.delenv(key, raising=False)
    bridge._reset_for_testing()
    yield
    bridge._reset_for_testing()


def _make_host(monkeypatch, *, digital_worker):
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")
    monkeypatch.setenv("FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID", "blueprint-bbb")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")
    return ActivityAgentServerHost(digital_worker=digital_worker, configure_observability=None)


def test_simple_is_the_default(monkeypatch):
    import os

    _make_host(monkeypatch, digital_worker=False)

    assert bridge._digital_worker_mode is False
    assert os.environ[_AUTHTYPE] == "UserManagedIdentity"
    assert os.environ[_CLIENTID] == "instance-aaa"  # instance identity, not blueprint
    assert os.environ[_SCOPE0] == _BOTFRAMEWORK_SCOPE
    assert os.environ[_TENANTID] == "tenant-ccc"
    assert os.environ[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"


def test_digital_worker_opt_in(monkeypatch):
    import os

    _make_host(monkeypatch, digital_worker=True)

    assert bridge._digital_worker_mode is True
    assert os.environ[_AUTHTYPE] == "UserManagedIdentity"
    assert os.environ[_CLIENTID] == "blueprint-bbb"  # blueprint identity
    assert os.environ[_SCOPE0] == _AGENTIC_SCOPE
    assert os.environ[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"


def test_default_keyword_matches_explicit_false(monkeypatch):
    import os

    # No digital_worker kwarg at all -> must behave exactly like False.
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")
    monkeypatch.setenv("FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID", "blueprint-bbb")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")
    ActivityAgentServerHost(configure_observability=None)

    assert bridge._digital_worker_mode is False
    assert os.environ[_CLIENTID] == "instance-aaa"
    assert os.environ[_SCOPE0] == _BOTFRAMEWORK_SCOPE


def test_explicit_connection_env_wins_over_mode_defaults(monkeypatch):
    import os

    # An explicitly-set connection env var must not be overwritten by either mode.
    monkeypatch.setenv(_CLIENTID, "preset-client")
    monkeypatch.setenv(_SCOPE0, "preset/scope/.default")
    _make_host(monkeypatch, digital_worker=False)

    assert os.environ[_CLIENTID] == "preset-client"
    assert os.environ[_SCOPE0] == "preset/scope/.default"


def test_simple_mode_does_not_apply_fmi_patch(monkeypatch):
    """In simple mode the MSAL FMI/DefaultAzureCredential patch must not run."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    _make_host(monkeypatch, digital_worker=False)
    try:
        bridge._ensure_m365_initialized()
    except Exception:
        # M365 SDK init may fail in a bare test env; we only assert the patch gate.
        pass

    assert applied["called"] is False


def test_digital_worker_applies_fmi_patch(monkeypatch):
    """In digital-worker mode the MSAL FMI patch is applied during init."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    _make_host(monkeypatch, digital_worker=True)
    try:
        bridge._ensure_m365_initialized()
    except Exception:
        pass

    assert applied["called"] is True
