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
from azure.ai.agentserver.activity._config import get_hosted_agent_env, use_anonymous_outbound

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
    return ActivityAgentServerHost(
        agent_app=_StubAgentApp(),
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
    host = ActivityAgentServerHost(agent_app=_StubAgentApp(), configure_observability=None)

    assert host._digital_worker is False


def test_simple_mode_does_not_apply_fmi_patch(monkeypatch):
    """In simple mode the MSAL FMI/DefaultAzureCredential patch must not run."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    bridge.build_m365_app(digital_worker=False, connection_config={}, storage=None, agent_app=_StubAgentApp())

    assert applied["called"] is False


def test_digital_worker_applies_fmi_patch(monkeypatch):
    """In digital-worker mode the MSAL FMI patch is applied during build."""
    applied = {"called": False}

    def _fake_patch():
        applied["called"] = True

    monkeypatch.setattr(bridge, "_apply_msal_patches", _fake_patch)
    bridge.build_m365_app(digital_worker=True, connection_config={}, storage=None, agent_app=_StubAgentApp())

    assert applied["called"] is True


def test_get_hosted_agent_env_public_helper(monkeypatch):
    """get_hosted_agent_env derives CLIENTID from the Foundry instance identity
    and returns it in a NEW mapping without mutating os.environ."""
    import os

    from azure.ai.agentserver.activity import get_hosted_agent_env

    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")

    env = get_hosted_agent_env()

    assert env[_AUTHTYPE] == "UserManagedIdentity"
    assert env[_CLIENTID] == "instance-aaa"
    assert env[_SCOPE0] == _BOTFRAMEWORK_SCOPE
    assert env[_TENANTID] == "tenant-ccc"
    assert env[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"
    # os.environ must NOT be mutated by the helper.
    assert _CLIENTID not in os.environ
    assert _AUTHTYPE not in os.environ


def test_get_hosted_agent_env_digital_worker(monkeypatch):
    """get_hosted_agent_env(digital_worker=True) uses the blueprint identity + scope."""
    from azure.ai.agentserver.activity import get_hosted_agent_env

    monkeypatch.setenv("FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID", "blueprint-bbb")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "tenant-ccc")

    env = get_hosted_agent_env(digital_worker=True)

    assert env[_CLIENTID] == "blueprint-bbb"
    assert env[_SCOPE0] == _AGENTIC_SCOPE


def test_get_hosted_agent_env_does_not_overwrite(monkeypatch):
    """get_hosted_agent_env never overwrites an explicitly-set value."""
    monkeypatch.setenv(_CLIENTID, "preset-client")
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")

    from azure.ai.agentserver.activity import get_hosted_agent_env

    env = get_hosted_agent_env()

    assert env[_CLIENTID] == "preset-client"


# ---------------------------------------------------------------------------
# Local anonymous-outbound auto-detection (simple model only).
#
# Simple model + not hosted + no Bot Connector credential -> anonymous outbound
# (so local runs round-trip via the M365 Agents Playground). A hosted container
# OR a configured credential keeps the real authenticated Bearer path. The
# decision is a pure function over values resolved once at build time.
# ---------------------------------------------------------------------------

_HOSTING = "FOUNDRY_HOSTING_ENVIRONMENT"


@pytest.fixture(autouse=True)
def _clean_hosting_env(monkeypatch):
    """Ensure FOUNDRY_HOSTING_ENVIRONMENT starts unset for these tests."""
    monkeypatch.delenv(_HOSTING, raising=False)
    yield


def test_local_no_creds_uses_anonymous():
    """Simple model, local (not hosted), no credential -> anonymous."""
    assert use_anonymous_outbound(digital_worker=False, bot_app_id="", is_hosted=False) is True


def test_hosted_uses_authenticated():
    """Hosted container -> authenticated path (even with no credential)."""
    assert use_anonymous_outbound(digital_worker=False, bot_app_id="", is_hosted=True) is False


def test_local_with_credential_uses_authenticated():
    """Local but a Bot Connector credential is configured -> authenticated path."""
    assert use_anonymous_outbound(digital_worker=False, bot_app_id="some-client-id", is_hosted=False) is False


def test_digital_worker_never_uses_anonymous_fallback():
    """Digital-worker model must never take the local anonymous fallback path
    (its FMI patch supplies the outbound token)."""
    assert use_anonymous_outbound(digital_worker=True, bot_app_id="", is_hosted=False) is False


def test_outbound_bot_app_id_derived_from_env(monkeypatch):
    """get_hosted_agent_env derives the client id without mutating env."""
    import os

    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "instance-aaa")

    settings = get_hosted_agent_env(digital_worker=False)

    assert settings[_CLIENTID] == "instance-aaa"
    assert _CLIENTID not in os.environ


def test_user_connection_config_drives_outbound_bot_app_id():
    """A caller-supplied connection config drives the outbound client id, so the
    outbound auth stays consistent with the stack the caller configured."""
    bot_app_id = {_CLIENTID: "custom-xyz"}.get(_CLIENTID, "").strip()

    assert bot_app_id == "custom-xyz"
    assert use_anonymous_outbound(digital_worker=False, is_hosted=True, bot_app_id=bot_app_id) is False
