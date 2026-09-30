# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Robustness tests for :func:`get_hosted_agent_env`.

These pin the guarantees the helper must uphold as a *public*, standalone API:

* It is a pure function of ``os.environ`` at call time — no host/construction
  state is required, so it is safe to call before (or without) any host.
* It never mutates ``os.environ`` and returns an independent snapshot copy.
* Missing Foundry identity env simply omits the optional ``CLIENTID`` /
  ``TENANTID`` / ``AUTHORITY`` keys (never emits malformed values); the four
  static connection keys are always present.
* Explicit, caller-set values are preserved and never overwritten; whitespace
  is treated as unset.
"""

import os

import pytest

from azure.ai.agentserver.activity import get_hosted_agent_env
from azure.ai.agentserver.activity._constants import (
    ConnectionSettings,
    FoundryEnv,
    OutboundAuth,
)

# Foundry identity env keys (inputs).
_ENV_INSTANCE = FoundryEnv.INSTANCE_CLIENT_ID
_ENV_BLUEPRINT = "FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID"
_ENV_TENANT = "FOUNDRY_AGENT_TENANT_ID"

# Resolved connection keys (outputs).
_AUTHTYPE = ConnectionSettings.AUTH_TYPE
_CLIENTID = ConnectionSettings.CLIENT_ID
_TENANTID = ConnectionSettings.TENANT_ID
_AUTHORITY = ConnectionSettings.AUTHORITY
_SCOPE0 = ConnectionSettings.SCOPE_0
_MAP_URL = ConnectionSettings.MAP_0_SERVICE_URL
_MAP_CONN = ConnectionSettings.MAP_0_CONNECTION

_STATIC_KEYS = (_AUTHTYPE, _SCOPE0, _MAP_URL, _MAP_CONN)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove all inputs/outputs so each test starts from a known-empty state."""
    for key in list(os.environ):
        if key.startswith("CONNECTIONS") or key.startswith("FOUNDRY_AGENT") or key.startswith("CONNECTIONSMAP"):
            monkeypatch.delenv(key, raising=False)
    yield


# ---------------------------------------------------------------------------
# Static keys + simple/digital-worker identity selection.
# ---------------------------------------------------------------------------


def test_static_keys_always_present_even_with_no_identity_env():
    """With NO Foundry identity env set, the four static connection keys are
    still emitted and the optional identity keys are omitted (not blank)."""
    env = get_hosted_agent_env()

    assert env[_AUTHTYPE] == ConnectionSettings.AUTH_TYPE_USER_MANAGED_IDENTITY
    assert env[_SCOPE0] == OutboundAuth.BOTFRAMEWORK_SCOPE
    assert env[_MAP_URL] == ConnectionSettings.MAP_SERVICE_URL_WILDCARD
    assert env[_MAP_CONN] == ConnectionSettings.SERVICE_CONNECTION_NAME
    # Optional identity-derived keys must be ABSENT (never empty-string noise).
    assert _CLIENTID not in env
    assert _TENANTID not in env
    assert _AUTHORITY not in env


def test_simple_model_uses_instance_client_id_and_botframework_scope(monkeypatch):
    """Simple model derives CLIENTID from the instance identity + BF scope."""
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")
    monkeypatch.setenv(_ENV_TENANT, "tenant-ccc")

    env = get_hosted_agent_env()

    assert env[_CLIENTID] == "instance-aaa"
    assert env[_SCOPE0] == OutboundAuth.BOTFRAMEWORK_SCOPE
    assert env[_TENANTID] == "tenant-ccc"
    assert env[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"


def test_digital_worker_uses_blueprint_client_id_and_agentic_scope(monkeypatch):
    """Digital-worker model derives CLIENTID from the blueprint identity + agentic scope."""
    monkeypatch.setenv(_ENV_BLUEPRINT, "blueprint-bbb")
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")  # must be ignored
    monkeypatch.setenv(_ENV_TENANT, "tenant-ccc")

    env = get_hosted_agent_env(digital_worker=True)

    assert env[_CLIENTID] == "blueprint-bbb"
    assert env[_SCOPE0] == OutboundAuth.AGENTIC_SCOPE


def test_simple_model_ignores_blueprint_id(monkeypatch):
    """The simple model must not pick up the blueprint id."""
    monkeypatch.setenv(_ENV_BLUEPRINT, "blueprint-bbb")
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env(digital_worker=False)

    assert env[_CLIENTID] == "instance-aaa"


# ---------------------------------------------------------------------------
# Missing-value handling (the "may not have values" concern).
# ---------------------------------------------------------------------------


def test_no_tenant_omits_authority_and_tenant_keys(monkeypatch):
    """No tenant env -> AUTHORITY is not emitted (never a malformed bare URL)."""
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env()

    assert env[_CLIENTID] == "instance-aaa"
    assert _TENANTID not in env
    assert _AUTHORITY not in env


def test_no_client_id_still_emits_tenant_and_authority(monkeypatch):
    """Tenant present but no client id -> tenant/authority still resolve; the
    absent client id is simply omitted."""
    monkeypatch.setenv(_ENV_TENANT, "tenant-ccc")

    env = get_hosted_agent_env()

    assert _CLIENTID not in env
    assert env[_TENANTID] == "tenant-ccc"
    assert env[_AUTHORITY] == "https://login.microsoftonline.com/tenant-ccc"


def test_whitespace_identity_env_treated_as_unset(monkeypatch):
    """A whitespace-only identity value is treated as unset (key omitted)."""
    monkeypatch.setenv(_ENV_INSTANCE, "   ")
    monkeypatch.setenv(_ENV_TENANT, "\t")

    env = get_hosted_agent_env()

    assert _CLIENTID not in env
    assert _TENANTID not in env
    assert _AUTHORITY not in env


# ---------------------------------------------------------------------------
# Explicit-value precedence (never overwrite caller-provided settings).
# ---------------------------------------------------------------------------


def test_explicit_client_id_is_preserved(monkeypatch):
    """A pre-set CONNECTIONS__*__CLIENTID is preserved over the derived value."""
    monkeypatch.setenv(_CLIENTID, "preset-client")
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env()

    assert env[_CLIENTID] == "preset-client"


def test_explicit_static_keys_are_preserved(monkeypatch):
    """Pre-set static keys (auth type / scope) are not overwritten."""
    monkeypatch.setenv(_AUTHTYPE, "CustomAuthType")
    monkeypatch.setenv(_SCOPE0, "custom-scope")

    env = get_hosted_agent_env()

    assert env[_AUTHTYPE] == "CustomAuthType"
    assert env[_SCOPE0] == "custom-scope"


def test_whitespace_explicit_value_is_overwritten_with_derived(monkeypatch):
    """A whitespace-only explicit value is treated as missing and gets the
    derived value (so blank platform injection cannot suppress resolution)."""
    monkeypatch.setenv(_CLIENTID, "   ")
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env()

    assert env[_CLIENTID] == "instance-aaa"


# ---------------------------------------------------------------------------
# Purity: no mutation, snapshot independence, standalone/repeatable.
# ---------------------------------------------------------------------------


def test_does_not_mutate_os_environ(monkeypatch):
    """The helper must never write derived keys back into os.environ."""
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")
    monkeypatch.setenv(_ENV_TENANT, "tenant-ccc")

    get_hosted_agent_env()

    for key in (_AUTHTYPE, _CLIENTID, _TENANTID, _AUTHORITY, _SCOPE0, _MAP_URL, _MAP_CONN):
        assert key not in os.environ


def test_returned_mapping_is_an_independent_snapshot(monkeypatch):
    """Mutating os.environ after the call must not change a returned mapping,
    and mutating the returned mapping must not touch os.environ."""
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env()

    monkeypatch.setenv(_ENV_INSTANCE, "changed-after-call")
    monkeypatch.setenv("SOME_NEW_VAR", "later")
    env["INJECTED_BY_TEST"] = "x"

    assert env[_CLIENTID] == "instance-aaa"  # frozen at call time
    assert "SOME_NEW_VAR" not in env
    assert "INJECTED_BY_TEST" not in os.environ


def test_callable_standalone_without_any_host_construction():
    """No host/initialization is required to call the helper (pure function)."""
    # Nothing constructed; a bare call must succeed and return a dict.
    env = get_hosted_agent_env()

    assert isinstance(env, dict)
    assert env[_AUTHTYPE] == ConnectionSettings.AUTH_TYPE_USER_MANAGED_IDENTITY


def test_repeated_calls_are_independent(monkeypatch):
    """Each call re-snapshots env; mutating one result does not affect the next."""
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    first = get_hosted_agent_env()
    first["INJECTED"] = "x"
    second = get_hosted_agent_env()

    assert "INJECTED" not in second
    assert second[_CLIENTID] == "instance-aaa"


def test_result_includes_unrelated_process_env(monkeypatch):
    """The snapshot overlays derived keys on the full process env (so downstream
    SDK config that reads other env vars still sees them)."""
    monkeypatch.setenv("UNRELATED_APP_VAR", "keep-me")
    monkeypatch.setenv(_ENV_INSTANCE, "instance-aaa")

    env = get_hosted_agent_env()

    assert env["UNRELATED_APP_VAR"] == "keep-me"
    assert env[_CLIENTID] == "instance-aaa"
